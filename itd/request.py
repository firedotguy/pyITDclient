from _io import BufferedReader
from base64 import urlsafe_b64decode
from dataclasses import dataclass, field
from datetime import datetime
from functools import wraps
from inspect import signature
from json import loads
from time import sleep, time
from typing import TYPE_CHECKING, Any, Callable
from urllib.parse import quote

from requests import Response, Session
from requests.exceptions import JSONDecodeError

from itd._default import get_config, limiters, limits
from itd.enums import AuthLevel, DebugResponseMode
from itd.exceptions import DEFAULT_ERRORS, AccessTokenExpiredError, ITDException, InvalidAccessTokenError
from itd.logger import get_logger

if TYPE_CHECKING:
    from itd.client import Client

l = get_logger('request')  # noqa: E741


# ai begin ---


def _get_jhash(b: int) -> int:
    """Calculate DDoS-Guard challenge hash (JS get_jhash port)."""
    x = 123456789
    k = 0
    for i in range(1677696):
        x = ((x + b) ^ (x + (x % 3) + (x % 17) + b) ^ i) % 16776960
        if x % 117 == 0:
            k = (k + 1) % 1111
    return k


def _solve_ddos_guard(session: Session, response: Response, user_agent: str = '') -> bool:
    """Solve DDoS-Guard JS challenge. Returns True if solved (duplicate request required)."""
    if '<html>' not in response.text[:500] or 'get_jhash' not in response.text:
        return False

    js_p = session.cookies.get('__js_p_')
    if not js_p:
        return False

    params = js_p.split(',')
    code = int(params[0])

    l.info('solve challenge code=%s', code)
    jhash = _get_jhash(code)
    l.info('solved jhash=%s', jhash)

    session.cookies.set('__jhash_', str(jhash), path='/')
    session.cookies.set('__jua_', quote(user_agent, safe=''), path='/')

    return True


# --- ai end


def decode_jwt_payload(jwt_token: str) -> dict[str, Any]:
    """Декодирует payload jwt.

    Args:
        jwt_token: jwt токен

    Returns:
        jwt payload
    """
    parts = jwt_token.split('.')
    if len(parts) != 3:
        raise ValueError("Not enough parts in access token")
    payload = parts[1]
    payload += '=' * ((4 - len(payload) % 4) % 4)
    decoded = urlsafe_b64decode(payload).decode('utf-8')
    return loads(decoded)


def is_token_expired(access_token: str) -> bool:
    """Истёк ли `access_token`.

    Args:
        access_token: access токен

    Returns:
        Истёк ли токен

    """
    payload = decode_jwt_payload(access_token)
    return time() - 1 >= payload['exp']


def fetch(
    client: 'Client',
    method: str,
    url: str,
    params: dict = {},
    files: dict[str, tuple[str, BufferedReader | bytes]] = {},
    send_token: bool = True
) -> Response:
    headers = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3"}
    if client.config._user_agent:
        headers['User-Agent'] = client.config._user_agent
    if client.access_token and send_token:
        headers['Authorization'] = 'Bearer ' + client.access_token

    # ai begin ---
    def _do_request():
        m = method.lower()
        if m == "get":
            return client.session.get(f'{client.config.url}/{url}', timeout=client.config._timeout, params=params, headers=headers)

        return client.session.request(
            m.upper(),
            f'{client.config.url}/{url}',
            timeout=client.config.timeout_file if files else client.config._timeout,
            json=params,
            headers=headers,
            files=files
        )

    res = _do_request()
    if client.config.solve_challenge:
        for _ in range(3):
            if not _solve_ddos_guard(client.session, res, client.config._user_agent):
                break
            l.debug('ddos-guard cookies: %s', {c.name: c.value for c in client.session.cookies if c.name.startswith('__')})
            res = _do_request()
        else:
            l.warning('ddos-guard challenge not solved')
    # --- ai end

    return res


def fetch_stream(client: 'Client', url: str):
    """Fetch для SSE streaming запросов"""
    base = f'https://xn--d1ah4a.com/api/{url}'
    headers = {
        "Accept": "text/event-stream",
        "Authorization": 'Bearer ' + client.token,
        "Cache-Control": "no-cache",
        'Sec-WebSocket-Extensions': 'permessage-deflate',
        'Sec-WebSocket-Key': '3tMaiXFWtq34tenKN/+T4Q==',
        'Sec-WebSocket-Version': '13'
    }
    return client.session.get(base, headers=headers, stream=True, timeout=None)


@dataclass
class Payload:
    """Тело запроса эндпоинта: параметры и файлы"""

    params: dict = field(default_factory=dict)
    files: dict[str, tuple[str, BufferedReader | bytes]] = field(default_factory=dict)


def _filter_bytes(args: tuple):
    filtered = []
    for arg in args:
        if isinstance(arg, bytes):
            filtered.append('_bytecode_')
        else:
            filtered.append(arg)
    return filtered


def _find_error(res: Response, json: dict, exceptions: tuple[ITDException, ...]) -> ITDException | None:
    """Найти ошибку, под которую подходит ответ

    Args:
        res (Response): Ответ
        json (dict): Тело ответа
        exceptions (tuple[ITDException, ...]): Ошибки эндпоинта (проверяются после общих)

    Returns:
        ITDException | None: Ошибка (None если ответ успешный)
    """
    for declaration in DEFAULT_ERRORS + exceptions:
        if declaration.matches(res, json):
            return declaration.prepare(json)
    return None


# user calls `Me` -> model calls `get_me` -> `api_wrapper` wrapper: (`get_me` -> `client.request` -> `fetch` -> responses 401 -> `refresh_auth` from `api_wrapper` -> `client.resuest` -> `fetch` -> token refreshed -> `api_wrapper` backs to main query -> `get_me` -> `client.request` -> `fetch` -> user fetched) -> model recieves data -> pydantic fills model
def api_wrapper(*exceptions: ITDException):
    """Декоратор для отлавливания ошибок

    Args:
        *exceptions (ITDException): Список ошибок для отлавливания
    """

    def decorator(func):
        @wraps(func)
        def wrapper(client: 'Client', *args, **kwargs) -> Response | None:
            name = func.__name__
            reauthed = False

            def exec():
                nonlocal reauthed
                l.info('exec %s %s %s', name, _filter_bytes(args), kwargs)

                config = get_config()
                is_first = True
                if name in limits and limits[name] in limiters:
                    limiter = limiters[limits[name]]
                    if config.auto_acquire:
                        limiter.acquire()
                    is_first = not limiter.used
                    limiter.request()

                ip_limiter = config.ip_limiter
                if ip_limiter:
                    ip_limiter.acquire()

                res: Response = func(client, *args, **kwargs)

                assert isinstance(res, Response)
                if res.status_code == 204:
                    if client.config.debug_response != DebugResponseMode.NO:
                        l.debug('no response')
                    return res

                remaining = int(res.headers.get('x-ratelimit-remaining', 0))
                limit = int(res.headers.get('x-ratelimit-limit', 0))
                limits[name] = limit

                if limit not in limiters and config.limiter is not None:
                    limiters[limit] = config.limiter(limit)

                if limit in limiters and (config.auto_acquire or is_first):
                    limiters[limit].sync(remaining)

                if client.config.debug_response == DebugResponseMode.BEFORE:
                    l.debug('response (raw): %s', res.text)

                try:
                    json = res.json()
                except JSONDecodeError:
                    json = {}
                    l.warning('failed to parse json: %s', res.text[:1000])

                exception = _find_error(res, json, exceptions)
                if exception is not None:
                    # token is checked before the request, but server still can reject it (clock skew, revoked session,
                    # token expired while request was in flight) - refresh and repeat the request once, before callbacks and before raising
                    if (
                        isinstance(exception, (AccessTokenExpiredError, InvalidAccessTokenError))
                        and not reauthed
                        and name != 'refresh_token'
                        and client.can_refresh_auth
                    ):
                        reauthed = True
                        if not client.is_token_expired(margin=0):
                            l.warning(
                                'server rejected access_token that is not expired by local clock (expires at %s, now is %s): '
                                'check system time (clock skew) or session was revoked',
                                client.access_token_data.expired_at if client.access_token_data else None,
                                datetime.now()
                            )
                        l.warning('%s on %s: refresh access_token and retry', exception.__class__.__name__, name)
                        client.refresh_auth(force=True)
                        return exec()

                    client._process_exc_callbacks(exception)
                    raise exception

                if client.config.debug_response == DebugResponseMode.AFTER:
                    l.debug('response: %s', json)
                if client.config.debug_response == DebugResponseMode.KEYS:
                    if 'data' in json:
                        l.debug('response keys: data - %s', list(json['data'].keys()))
                    else:
                        l.debug('response keys: %s', list(json.keys()))
                res.raise_for_status()
                return res

            if not client.config._retry_enabled:
                return exec()

            while True:
                try:
                    return exec()
                except client.config._retry_exceptions as e:
                    if getattr(e, 'retry_after', 0) > client.config.retry_max_retry_after:
                        l.error('too large rate limit')
                        raise

                    retry_after = getattr(e, 'retry_after', 0) or client.config.retry_delay
                    l.warning('%s on %s: wait %ss', e.__class__.__name__, name, retry_after)
                    sleep(retry_after)
                    if name in limits and limits[name] in limiters:
                        limiters[limits[name]].on_limit()

        return wrapper

    return decorator


catch_errors = api_wrapper


@dataclass
class Endpoint:
    """Описание эндпоинта, доступно как атрибут `.endpoint` у декорированной функции"""

    method: str
    url: str
    level: AuthLevel
    exceptions: tuple[ITDException, ...]


def endpoint(method: str, url: str, *exceptions: ITDException, level: AuthLevel = AuthLevel.ACCESS):
    """Объявить эндпоинт: декорированная функция только собирает тело запроса (dict с параметрами, Payload или ничего),
    а отправку, авторизацию, лимиты и ошибки берет на себя пайплайн

    Args:
        method (str): Метод
        url (str): URL, может содержать имена аргументов функции: 'posts/{post_id}/comments'
        *exceptions (ITDException): Ошибки, специфичные для эндпоинта (общие проверяются всегда)
        level (AuthLevel, optional): Требуемый уровень авторизации. Defaults to AuthLevel.ACCESS.
    """

    def decorator(func: Callable[..., dict | Payload | None]):
        params = signature(func) if '{' in url else None  # аргументы нужно связывать, только если url шаблонный

        @wraps(func)
        def request(client: 'Client', *args, **kwargs) -> Response:
            payload = func(client, *args, **kwargs) or Payload()
            if isinstance(payload, dict):
                payload = Payload(payload)

            if params is None:
                path = url
            else:
                bound = params.bind(client, *args, **kwargs)
                bound.apply_defaults()
                path = url.format(**bound.arguments)

            return client.request(method, path, payload.params, payload.files, level=level)

        wrapper = api_wrapper(*exceptions)(request)
        wrapper.endpoint = Endpoint(method, url, level, exceptions)
        return wrapper

    return decorator


def rate_limit():

    def decorator(func):
        @wraps(func)
        def wrapper(client: 'Client', *args, **kwargs) -> Response | None:
            l.warning('rate_limit is deprecated and will be removed in 2.7.0.')
            return func(client, *args, **kwargs)

        return wrapper

    return decorator
