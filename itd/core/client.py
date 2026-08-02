from __future__ import annotations

from _io import BufferedReader
from atexit import register
from datetime import datetime, timedelta
from functools import cached_property
from os import getenv
from threading import RLock, Thread
from time import sleep
from typing import TYPE_CHECKING, overload
from uuid import UUID

from pydantic import BaseModel, Field, field_validator
from requests import Session
from requests.adapters import HTTPAdapter

from itd.api.auth import change_password, logout, refresh_token
from itd.api.posts import get_stats
from itd.api.search import search
from itd.core.config import Config
from itd.core.credfile import Credfile
from itd.core.default import _default_client, set_default_client
from itd.core.dwell import DwellTracker
from itd.core.logger import get_logger
from itd.core.request import decode_jwt_payload, fetch, fetch_stream
from itd.core.utils import get_credfile, shorten_token
from itd.enums import AuthLevel, Role, ViewReason
from itd.exceptions import InsufficientAuthLevelError, NotFoundError, SessionExpiredError, SessionNotFoundError, SessionRevokedError

if TYPE_CHECKING:
    from itd.models.hashtag import Hashtag
    from itd.models.post import Post
    from itd.models.user import Me, User

l = get_logger('client')


class AccessToken(BaseModel):
    roles: list[Role] = [Role.USER]
    session_id: UUID = Field(alias='sid')
    is_active: bool = Field(True, alias='isActive')
    subject_id: UUID = Field(alias='sub')
    issued_at: datetime = Field(alias='iat')
    issuer: str | None = Field(None, alias='iss')  # "auth-service"
    expired_at: datetime = Field(alias='exp')
    jwt_id: UUID | None = Field(None, alias='jti')

    @field_validator('issued_at', 'expired_at', mode='plain')
    @classmethod
    def validate_datetimes(cls, v):
        return datetime.fromtimestamp(v)


class Client:
    def __init__(self, refresh: str | None = None, access: str | None = None, config: Config = Config()):
        l.info('init client refresh=%s access=%s', refresh is not None, access is not None)
        self.config = config
        self.last_actions: dict[str, int | float] = {}
        self.auth_level: AuthLevel = AuthLevel.NO
        self.access_token: str | None = None
        self.access_token_data: AccessToken | None = None
        self.refresh_token: str | None = None
        self.visible_posts: list[Post] = []
        self._visible_posts_buffer: list[Post] = []
        self.last_active = datetime.now()
        self._credfile: Credfile | None = None
        self._refresh_lock = RLock()  # so background timers and main thread dont refresh token simultaneously # еба он мой стиль коментов спиздил

        self.session = Session()
        adapter = HTTPAdapter(pool_connections=1, pool_maxsize=10, pool_block=False)  # idk what is this, (claude added) just for better stability
        self.session.mount('https://', adapter)

        if access:
            self.auth_level = AuthLevel.ACCESS
            self.token = access.replace('Bearer ', '')

        if refresh:
            self.session.cookies.set(config.refresh_token_cookie_name, refresh, path='/')
            self.auth_level = AuthLevel.REFRESH
            self.refresh_token = refresh

        if _default_client is None or config.is_default:
            set_default_client(self)

        self.dwell_tracker = DwellTracker(self)
        self.dwell_tracker._start_timer()

        if self.config._post_update_stats:
            self._start_update_timer()
        if self.config._dwell_check_active:
            self._start_check_active_timer()

    @classmethod
    def from_file(cls, name: str, initial_refresh: str | None = None, verify_refresh: bool = False, config: Config = Config()):
        credfile = get_credfile(name)
        l.debug('get credentials file refresh=%s access=%s', shorten_token(credfile.refresh), shorten_token(credfile.access))
        if not credfile.valid:
            l.warning('last refresh token was expired or not found. Please enter a new one:')
            update = True
        else:
            update = credfile.refresh is None

        if update:
            if initial_refresh is not None:
                credfile.refresh = initial_refresh
            elif getenv('ITD_REFRESH_TOKEN') is not None:
                credfile.refresh = getenv('ITD_REFRESH_TOKEN')
            else:
                try:
                    from rich.prompt import Prompt
                except ImportError:
                    credfile.refresh = input('refresh token: ')
                else:
                    credfile.refresh = Prompt.ask('[cyan]refresh token[/]')

        instance = cls(credfile.refresh, credfile.access, config=config)
        if instance.access_token_data and instance.access_token_data.expired_at < datetime.now():
            instance.access_token = instance.access_token_data = None
        instance._credfile = credfile
        if verify_refresh and initial_refresh is not None:
            instance.refresh_auth(force=True)
        elif update:
            instance._update_file()
        return instance

    def _update_file(self, valid: bool = True):
        if self._credfile is None:
            return

        l.debug('update credentials file refresh=%s access=%s', shorten_token(self.refresh_token), shorten_token(self.access_token))
        if not valid:
            l.warning('mark %s as not valid', shorten_token(self.refresh_token))

        self._credfile.access = self.access_token
        self._credfile.refresh = self.refresh_token
        self._credfile.valid = valid
        self._credfile.flush()

    @property
    def is_token_expired(self) -> bool:
        """Истёк ли (или вот-вот истечет) access token"""
        if self.access_token is None:
            return True
        if self.access_token_data is None:  # failed to parse jwt - assume valid, let server decide
            return False

        return self.access_token_data.expired_at - timedelta(seconds=self.config.token_expiry_margin) <= datetime.now()

    @property
    def can_refresh_auth(self) -> bool:
        """Есть ли refresh token, чтобы обновить access token"""
        return self.refresh_token is not None or self.auth_level >= AuthLevel.REFRESH

    def refresh_auth(self, force: bool = False) -> str:
        """Обновить access token

        Args:
            force (bool, optional): Обновить, даже если текущий токен еще валиден. Defaults to False.

        Returns:
            str: Токен
        """

        with self._refresh_lock:
            if not force and not self.is_token_expired:  # refreshed by another thread while we were waiting for the lock
                l.debug('access_token is already fresh')
                return self.token

            l.debug('refresh access_token')
            if not force and self._credfile and self._credfile.update():
                self.token = self._credfile.access
                self.refresh_token = self._credfile.refresh

                if self.access_token:
                    if not self.is_token_expired:
                        l.debug('update access_token from credfile')
                        return self.access_token
                    else:
                        l.info('credfile access_token expired')
                else:
                    l.info('crefile access_token is none')

            try:
                res = refresh_token(self)
            except (SessionExpiredError, SessionNotFoundError, SessionRevokedError):
                if force:
                    raise
                self._update_file(valid=False)
                raise

            self.token = res.json().get('accessToken') or res.json()['token']
            if 'refresh_token' in res.cookies:
                self.refresh_token = res.cookies['refresh_token']
            self._update_file()

            return self.token

    def _start_check_active_timer(self):
        l.debug('start check active timer')
        if not self.config.dwell_check_active_interval:
            return

        def loop():
            while True:
                sleep(self.config.dwell_check_active_interval)
                is_active = self.last_active + timedelta(seconds=self.config.dwell_inactive_timeout) > datetime.now()

                if not self._visible_posts_buffer and not is_active:
                    self._visible_posts_buffer = self.visible_posts.copy()
                    for post in self._visible_posts_buffer:
                        post._entered_at = datetime.now() - timedelta(seconds=self.config.dwell_inactive_timeout)
                        post.set_invisible(reason=ViewReason.INACTIVE)

                elif self._visible_posts_buffer and is_active:
                    for post in self._visible_posts_buffer:
                        post.set_visible()
                    self._visible_posts_buffer.clear()

        self._check_active_thread = Thread(target=loop)
        self._check_active_thread.daemon = True
        self._check_active_thread.start()

        def on_exit():
            if self._check_active_thread:
                self._check_active_thread.join(timeout=0)

        register(on_exit)

    def set_active(self):  # call when user is active (scroll, move etc)
        self.last_active = datetime.now()

    def _start_update_timer(self):
        l.debug('start update timer')
        if not self.config.post_update_stats_interval:
            return

        def loop():
            while True:
                sleep(self.config.post_update_stats_interval)
                self.update_post_stats()

        self._update_thread = Thread(target=loop)
        self._update_thread.daemon = True
        self._update_thread.start()

        def on_exit():
            if self._update_thread:
                self._update_thread.join(timeout=0)

        register(on_exit)

    def request(self, method: str, url: str, params: dict = {}, files: dict[str, tuple[str, BufferedReader | bytes]] = {}, level=AuthLevel.ACCESS):
        """Сделать запрос

        Args:
            method (str): Метод
            url (str): URL
            params (dict, optional): Параметры. Defaults to {}.
            files (dict[str, tuple[str, BufferedReader | bytes]], optional): Файлы. Defaults to {}.
        """
        l.debug('%s %s params=%s authlevel=%s', method.upper(), url, params, level.value)

        if level > self.auth_level and not self.config.bypass_auth_level:
            raise InsufficientAuthLevelError(self.auth_level, level)

        send_token = True
        # access token is attached to every request (including AuthLevel.NO endpoints), so it must be refreshed regardless of level:
        # otherwise such requests fail with AccessTokenExpiredError forever once the token expires
        if url != 'v1/auth/refresh' and self.is_token_expired:
            if level >= AuthLevel.ACCESS or self.can_refresh_auth:
                self.refresh_auth()
            elif self.access_token is not None:
                l.warning('access_token expired and cannot be refreshed, send %s %s without authorization', method.upper(), url)
                send_token = False

        return fetch(self, method, url, params, files, send_token=send_token)

    def request_sse(self, url: str):
        l.debug('sse %s', url)

        if self.is_token_expired:
            self.refresh_auth()

        return fetch_stream(self, url)

    def update_post_stats(self):
        if len(self.visible_posts) == 0:
            return

        l.debug('update post stats count=%s', len(self.visible_posts))
        stats: list[dict] = get_stats(self, [post.id for post in self.visible_posts]).json().get('posts', [])
        if len(stats) != len(self.visible_posts):
            raise NotFoundError('Post(s)')

        for post in self.visible_posts:
            post._set_stats(next((stat for stat in stats if stat['id'] == str(post.id))))

    @property
    def token(self) -> str:
        assert self.access_token, 'Access token not refreshed yet'
        return self.access_token

    @token.setter
    def token(self, token: str | None):
        self.access_token = token
        if token is None:
            self.access_token_data = None
        else:
            self.access_token_data = AccessToken.model_validate(decode_jwt_payload(token))

    @property
    def user_id(self) -> UUID:
        assert self.access_token_data
        return self.access_token_data.subject_id

    @cached_property
    def user(self) -> Me:
        from itd.models.user import Me

        return Me(client=self)

    def _process_exc_callbacks(self, exception: Exception):
        # l.debug([v for k, v in self.config.on_exceptions.items() if k in exception.__class__.mro()])
        for callback in [v for k, v in self.config.on_exceptions.items() if k in exception.__class__.mro()]:
            callback(exception)

    def logout(self):
        """Выход из аккаунта"""
        res = logout(self)
        res.raise_for_status()

    def change_password(self, old: str, new: str) -> None:
        """Смена пароля

        Args:
            old (str): Старый пароль
            new (str): Новый пароль

        Raises:
            NoCookie: Нет cookie
            SamePasswordError: Одинаковые пароли
            InvalidOldPasswordError: Старый пароль неверный

        """
        # if not self.refresh_token:
        # raise InsufficientAuthLevelError()

        change_password(self, old, new)


def init_client(name: str | None = None, initial_refresh: str | None = None, verify_refresh: bool = False, config: Config = Config()) -> Client:
    return Client.from_file(name or 'default', initial_refresh=initial_refresh, verify_refresh=verify_refresh, config=config)
