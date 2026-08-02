from logging import WARNING, getLogger

import pytest
from helpers import make_client, make_response, make_token

from itd.core.client import Client
from itd.enums import AuthLevel
from itd.exceptions import AccessTokenExpiredError
from itd.core.request import api_wrapper

pytestmark = pytest.mark.usefixtures('keep_default_client')


def test_is_token_expired():
    assert make_client(make_token(-10)).is_token_expired()
    assert make_client(make_token(30)).is_token_expired()  # expires sooner than token_expiry_margin
    assert not make_client(make_token(900)).is_token_expired()
    assert make_client(None).is_token_expired()


def test_public_endpoint_refreshes_expired_token(fetches, refreshes):
    """Токен подставляется и в запросы без авторизации (search, hashtags, profile), поэтому его надо обновлять и для них"""
    client = make_client(make_token(-10))
    expired = client.access_token

    client.request('get', 'search', {'q': 'итд'}, level=AuthLevel.NO)

    assert refreshes == [expired]
    assert fetches[0]['send_token'] is True
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
    assert fetches[0]['url'] == 'v1/auth/refresh'


def test_refresh_auth_skips_request_if_token_is_fresh(refreshes):
    client = make_client(make_token(900))

    assert client.refresh_auth() == client.access_token
    assert refreshes == []  # already fresh (eg refreshed by another thread)

    client.refresh_auth(force=True)
    assert len(refreshes) == 1


def test_expired_token_without_refresh_token_is_not_sent(fetches):
    """Обновить токен нечем - для эндпоинта без авторизации лучше сходить анонимно, чем послать протухший токен"""
    client = make_client(make_token(-10), refresh=None)

    client.request('get', 'search', {'q': 'итд'}, level=AuthLevel.NO)

    assert fetches[0]['send_token'] is False


def test_api_wrapper_retries_after_token_expired(fetches, refreshes):
    """Сервер может отвергнуть токен, который по нашим часам еще жив"""
    client = make_client(make_token(900))
    responses = [make_response(401, {'error': 'token expired'}), make_response(200, {'data': {}})]

    @api_wrapper()
    def get_something(client: Client):
        return responses.pop(0)

    assert get_something(client).status_code == 200
    assert len(refreshes) == 1


@pytest.mark.parametrize(('expires_in', 'warned'), [(900, True), (-10, False)])
def test_api_wrapper_warns_if_token_rejected_but_not_expired(fetches, refreshes, caplog, expires_in, warned):
    """Если по нашим часам токен еще жив, а сервер его отверг - предупреждаем (расхождение часов / отозванная сессия)"""
    getLogger('itd').propagate = True
    client = make_client(make_token(expires_in))
    responses = [make_response(401, {'error': 'token expired'}), make_response(200, {'data': {}})]

    @api_wrapper()
    def get_something(client: Client):
        return responses.pop(0)

    with caplog.at_level(WARNING, logger='itd.core.request'):
        get_something(client)

    assert any('clock skew' in record.getMessage() for record in caplog.records) is warned
    assert len(refreshes) == 1


def test_api_wrapper_raises_if_retry_failed(fetches, refreshes):
    client = make_client(make_token(900))

    @api_wrapper()
    def get_something(client: Client):
        return make_response(401, {'error': 'token expired'})

    with pytest.raises(AccessTokenExpiredError):
        get_something(client)

    assert len(refreshes) == 1  # refresh and retry only once


def test_api_wrapper_does_not_retry_without_refresh_token(fetches, refreshes):
    client = make_client(make_token(900), refresh=None)

    @api_wrapper()
    def get_something(client: Client):
        return make_response(401, {'error': 'token expired'})

    with pytest.raises(AccessTokenExpiredError):
        get_something(client)

    assert refreshes == []
