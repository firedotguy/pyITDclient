from os import getenv

import pytest
from dotenv import load_dotenv

from helpers import make_response, make_token

from itd import ITDClient, ITDConfig
from itd.enums import RateLimitMode
from itd.post import Post


load_dotenv()
config = ITDConfig(RateLimitMode.NO)


@pytest.fixture(scope="session")
def client():
    token = getenv('TOKEN')
    if not token:
        pytest.skip('TOKEN not set in .env')
    return ITDClient(token, config=config)


@pytest.fixture(scope="session")
def client2(client):
    token = getenv('TOKEN_2')
    if not token:
        pytest.skip('TOKEN_2 not set in .env')
    return ITDClient(token, config=config)


@pytest.fixture(scope="session")
def client_sub(client):
    token = getenv('TOKEN_SUB')
    if not token:
        pytest.skip('TOKEN_SUB not set in .env')
    return ITDClient(token, config=config)


@pytest.fixture(scope="session")
def redis_post(client):  # думаешь redis это какое нибудь заумное важное название? а нет, это просто редис зплвца
    return Post('1cbe5926-2d08-4e17-879d-7732b94ed354')


# фикстуры для оффлайн тестов (test_auth, test_endpoint, test_errors)


@pytest.fixture
def keep_default_client():
    """Клиенты оффлайн тестов не должны становиться дефолтными для остальных"""
    from itd import _default

    previous = _default._default_client
    yield
    _default._default_client = previous


@pytest.fixture
def fetches(monkeypatch):
    """Перехватить запросы вместо отправки"""
    calls = []

    def fake_fetch(client, method, url, params={}, files={}, send_token=True):
        calls.append({'method': method, 'url': url, 'params': params, 'files': files, 'send_token': send_token})
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
