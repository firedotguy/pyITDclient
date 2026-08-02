"""Хелперы для оффлайн тестов (без сети и без TOKEN)"""

from base64 import urlsafe_b64encode
from datetime import datetime, timedelta
from json import dumps
from uuid import uuid4

from requests import Response

from itd.client import Client, Config


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


def make_client(access: str | None = None, refresh: str | None = 'refresh-token') -> Client:
    # timers are disabled so client doesnt go to network
    return Client(refresh, access, config=Config(dwell_send_interval=0, post_update_stats=False, dwell_check_active=False))
