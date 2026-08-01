from base64 import urlsafe_b64encode
from datetime import datetime, timedelta
from json import dumps
from uuid import uuid4

import pytest
from requests import Response

from itd.base import api_wrapper
from itd.client import Client, Config
from itd.enums import AuthLevel
from itd.exceptions import AccessTokenExpiredError


def make_token(expires_in: float) -> str:
    """Собрать access token (jwt), который истечет через `expires_in` секунд"""
    payload = {
        'sid': str(uuid4()),
        'sub': str(uuid4()),
        'iat': datetime.now().timestamp(),
        'exp': (datetime.now() + timedelta(seconds=expires_in)).timestamp()
    }
    encoded = urlsafe_b64encode(dumps(payload).encode()).decode().rstrip('=')
    return f'header.{encoded}.signature'


def make_response(status: int, json: dict) -> Response:
    res = Response()
    res.status_code = status
    res._content = dumps(json).encode()
    return res


@pytest.fixture(autouse=True)
def keep_default_client():
    """Клиенты из этого файла не должны становиться дефолтными для остальных тестов"""
    from itd import _default

    previous = _default._default_client
    yield
    _default._default_client = previous


def make_client(access: str | None = None, refresh: str | None = 'refresh-token') -> Client:
    # таймеры выключены, чтобы клиент не ходил в сеть
    return Client(refresh, access, config=Config(dwell_send_interval=0, post_update_stats=False, dwell_check_active=False))


@pytest.fixture
def fetches(monkeypatch):
    """Перехватить запросы вместо отправки"""
    calls = []

    def fake_fetch(client, method, url, params={}, files={}, send_token=True):
        calls.append({'method': method, 'url': url, 'send_token': send_token})
        return make_response(200, {'data': {}})

    monkeypatch.setattr('itd.client.fetch', fake_fetch)
    return calls


@pytest.fixture
def refreshes(monkeypatch):
    """Перехватить обновление токена вместо запроса в v1/auth/refresh"""
    calls = []

    def fake_refresh_token(client):
        calls.append(client.access_token)
        return make_response(200, {'accessToken': make_token(900)})

    monkeypatch.setattr('itd.client.refresh_token', fake_refresh_token)
    return calls


def test_is_token_expired():
    assert make_client(make_token(-10)).is_token_expired()
    assert make_client(make_token(30)).is_token_expired()  # истечет раньше, чем пройдет запас (token_expiry_margin)
    assert not make_client(make_token(900)).is_token_expired()
    assert make_client(None).is_token_expired()


def test_public_endpoint_refreshes_expired_token(fetches, refreshes):
    """Токен подставляется и в запросы без авторизации (search, hashtags, profile), поэтому его надо обновлять и для них"""
    client = make_client(make_token(-10))
    expired = client.access_token

    client.request('get', 'search', {'q': 'итд'}, level=AuthLevel.NO)

    assert refreshes == [expired]
    assert fetches == [{'method': 'get', 'url': 'search', 'send_token': True}]
    assert not client.is_token_expired()


def test_endpoint_with_auth_refreshes_expired_token(fetches, refreshes):
    client = make_client(make_token(-10))

    client.request('get', 'profile/me', level=AuthLevel.ACCESS)

    assert len(refreshes) == 1
    assert not client.is_token_expired()


def test_fresh_token_is_not_refreshed(fetches, refreshes):
    client = make_client(make_token(900))

    client.request('get', 'search', {'q': 'итд'}, level=AuthLevel.NO)
    client.request('get', 'profile/me', level=AuthLevel.ACCESS)

    assert refreshes == []
    assert len(fetches) == 2


def test_refresh_endpoint_does_not_recurse(fetches, refreshes):
    client = make_client(make_token(-10))

    client.request('post', 'v1/auth/refresh', level=AuthLevel.REFRESH)

    assert refreshes == []
    assert fetches == [{'method': 'post', 'url': 'v1/auth/refresh', 'send_token': True}]


def test_refresh_auth_skips_request_if_token_is_fresh(refreshes):
    client = make_client(make_token(900))

    assert client.refresh_auth() == client.access_token
    assert refreshes == []  # уже обновлен (например другим потоком)

    client.refresh_auth(force=True)
    assert len(refreshes) == 1


def test_expired_token_without_refresh_token_is_not_sent(fetches):
    """Обновить токен нечем - для эндпоинта без авторизации лучше сходить анонимно, чем послать протухший токен"""
    client = make_client(make_token(-10), refresh=None)

    client.request('get', 'search', {'q': 'итд'}, level=AuthLevel.NO)

    assert fetches == [{'method': 'get', 'url': 'search', 'send_token': False}]


def test_api_wrapper_retries_after_token_expired(fetches, refreshes):
    """Сервер может отвергнуть токен, который по нашим часам еще жив"""
    client = make_client(make_token(900))
    responses = [make_response(401, {'error': 'token expired'}), make_response(200, {'data': {}})]

    @api_wrapper()
    def get_something(client: Client):
        return responses.pop(0)

    assert get_something(client).status_code == 200
    assert len(refreshes) == 1


def test_api_wrapper_raises_if_retry_failed(fetches, refreshes):
    client = make_client(make_token(900))

    @api_wrapper()
    def get_something(client: Client):
        return make_response(401, {'error': 'token expired'})

    with pytest.raises(AccessTokenExpiredError):
        get_something(client)

    assert len(refreshes) == 1  # обновляем и повторяем только один раз


def test_api_wrapper_does_not_retry_without_refresh_token(fetches, refreshes):
    client = make_client(make_token(900), refresh=None)

    @api_wrapper()
    def get_something(client: Client):
        return make_response(401, {'error': 'token expired'})

    with pytest.raises(AccessTokenExpiredError):
        get_something(client)

    assert refreshes == []
