from _io import BufferedReader
from atexit import register
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from functools import cached_property
from os import getenv
from threading import RLock, Thread
from time import sleep
from typing import Callable, Literal, overload
from uuid import UUID

from pydantic import BaseModel, Field, field_validator
from requests import Session
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException
from requests.utils import default_user_agent

from itd._credfile import Credfile
from itd._default import _default_client, set_default_client
from itd.api.auth import change_password, logout, refresh_token
from itd.api.posts import get_stats
from itd.api.search import search
from itd.enums import BATCH, All, AuthLevel, Batch, DebugResponseMode, ParseMode, Role, UserAgent, ViewReason
from itd.exceptions import (
    InsufficientAuthLevelError,
    NotFoundError,
    RateLimitError,
    SessionExpiredError,
    SessionNotFoundError,
    SessionRevokedError
)
from itd.hashtag import Hashtag, Hashtags
from itd.logger import get_logger
from itd.post import DwellTracker, Post
from itd.request import decode_jwt_payload, fetch, fetch_stream
from itd.user import Me, User, Users, get_follow_status
from itd.utils import get_credfile, get_sdk_user_agent, shorten_token

l = get_logger('client')


@dataclass
class BatchSizes:
    preset: Literal['decreased', 'default', 'increased', 'max'] = 'default'
    comments: int | None = None
    replies: int | None = None
    hashtags: int | None = None
    notifications: int | None = None
    posts: int | None = None
    user_posts: int | None = None
    liked_posts: int | None = None
    hashtag_posts: int | None = None
    followers: int | None = None
    following: int | None = None
    blocked: int | None = None

    def __post_init__(self):
        presets = {
            'comments': [50, 100, 200, 500],
            'replies': [20, 100, 100, 100],
            'hashtags': [5, 10, 20, 50],
            'notifications': [10, 20, 50, 1000],
            'posts': [10, 20, 30, 50],
            'user_posts': [10, 20, 30, 50],
            'liked_posts': [10, 20, 30, 50],
            'hashtag_posts': [10, 20, 30, 50],
            'followers': [10, 20, 50, 100],
            'following': [10, 20, 50, 100],
            'blocked': [10, 20, 50, 100]
        }
        presets_map = ['decreased', 'default', 'increased', 'max']
        self._values: dict[str, int] = {}
        for k, v in presets.items():
            if getattr(self, k) is None:
                self._values[k.replace('_', '')] = v[presets_map.index(self.preset)]
            else:
                self._values[k.replace('_', '')] = getattr(self, k)


@dataclass
class Config:
    # для реальных клиентов включен калбэк на ошибки (сами ошибки не выбрасываются) и выключен логгер. Передает ошибки в калбэк, в консоль ничего не пишет, при ошибках сети падает.
    # для ботов включен отлов всех ошибок, а также калбэк при ошибках сети (шоб отправлять в тг например), включен логгер на инфо. Показывает ошибки в консоли, но не завершшает скрипт.
    # для одноразовых скриптов стандартное поведение, отловов ошибок нет, включен логгер на дебаг.
    # ^ это если что просто мысли, не обращайте внимания
    client_type: Literal['client', 'bot', 'onetime'] = 'onetime'

    auto_acquire: bool | None = None

    # enable_logging: bool | None = None
    # logging_level = 'DEBUG'

    is_default: bool = False

    userposts_add_pinned_post: bool = True

    load_on_init: bool = False
    load_on_getattr: bool = True
    auto_load: bool | None = None
    load_on_getitem: int | All | Batch | None = 1
    load_on_iter: int | All | Batch | None = BATCH
    force_load_lists: bool = False  # load lists even if has_more is False

    debug_response: DebugResponseMode = DebugResponseMode.NO

    timeout: float | None = None
    timeout_file: float | None = None
    timeout_file_download: float | None = None

    url: str = 'https://xn--d1ah4a.com/api'
    user_agent: UserAgent | str = UserAgent.BROWSER
    solve_challenge: bool = True

    parse_mode: ParseMode = ParseMode.NO

    retry_enabled: bool | None = None
    retry_delay: float = 10  # delay before next attempt (after rate limit error) if retry_after is not provided in response
    retry_max_retries: int | None = 10  # none for no limit
    retry_exceptions: tuple[type[Exception], ...] | None = None
    retry_max_retry_after: int = 500

    bypass_auth_level: bool = False

    dwell_enabled: bool = True
    dwell_max_buffer: int = 20
    dwell_send_interval: float = 2
    dwell_save_on_quit: bool = True
    dwell_wait_durations: bool = False
    dwell_max_duration: int = 30000
    dwell_min_duration: int = 250
    dwell_check_active: bool | None = None
    dwell_check_active_interval: float = 5
    dwell_inactive_timeout: int = 30
    post_view_increment: bool = False
    post_auto_view: bool = True  # view when called post.set_invisible()

    post_update_stats: bool | None = None
    post_update_stats_interval: int = 3

    view_read_speed: int = 250  # in WPM # https://scholarwithin.com/average-reading-speed
    view_images_speed: int = 130  # https://news.mit.edu/2014/in-the-blink-of-an-eye-0116

    on_exceptions: dict[type[Exception], Callable[[Exception], None]] = field(default_factory=dict)
    batch_sizes: BatchSizes = field(default_factory=BatchSizes)
    refresh_token_cookie_name: str = 'refresh_token'
    token_expiry_margin: float = 60  # how many seconds before expiration access token is considered expired (margin for network and clock skew)

    def __post_init__(self):
        match self.user_agent:
            case UserAgent.DEFAULT:
                self._user_agent = default_user_agent()
            case UserAgent.SDK:
                self._user_agent = get_sdk_user_agent()
            case UserAgent.EMPTY:
                self._user_agent = ''
            case UserAgent.BROWSER:
                self._user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0'
            case _:
                self._user_agent = self.user_agent

        if self.timeout is None:
            match self.client_type:
                case 'onetime':
                    self._timeout = 5
                case 'client':
                    self._timeout = 20
                case 'bot':
                    self._timeout = 60
        else:
            self._timeout = self.timeout

        if self.retry_enabled is None:
            self._retry_enabled = self.client_type == 'bot'
        else:
            self._retry_enabled = self.retry_enabled

        if self.post_update_stats is None:
            self._post_update_stats = self.client_type == 'client'
        else:
            self._post_update_stats = self.post_update_stats

        if self.dwell_check_active is None:
            self._dwell_check_active = self.client_type == 'client'
        else:
            self._dwell_check_active = self.dwell_check_active

        if self.retry_exceptions is None:
            if self.client_type == 'bot':
                self._retry_exceptions = (RateLimitError, RequestException)
            else:
                self._retry_exceptions = ()
        else:
            self._retry_exceptions = self.retry_exceptions

        if self.auto_load is not None:
            l.warning('config.auto_load is deprecated and will be removed in 2.8.0. Please use load_on_getattr.')
            self.load_on_getattr = self.auto_load


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
        self._refresh_lock = RLock()  # so background timers and main thread dont refresh token simultaneously

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
            # if access is None:
            #     self.refresh_auth()

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

    def is_token_expired(self, margin: float | None = None) -> bool:
        """Истёк ли (или вот-вот истечет) access token

        Args:
            margin (float | None, optional): Запас в секундах (None - config.token_expiry_margin). Defaults to None.

        Returns:
            bool: Истёк ли токен (True если токена нет вообще)
        """
        if self.access_token is None:
            return True
        if self.access_token_data is None:  # failed to parse jwt - assume valid, let server decide
            return False

        margin = self.config.token_expiry_margin if margin is None else margin
        return self.access_token_data.expired_at - timedelta(seconds=margin) <= datetime.now()

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
            if not force and not self.is_token_expired():  # refreshed by another thread while we were waiting for the lock
                l.debug('access_token is already fresh')
                return self.token

            l.debug('refresh access_token')
            if not force and self._credfile and self._credfile.update():
                self.token = self._credfile.access
                self.refresh_token = self._credfile.refresh

                if self.access_token:
                    if not self.is_token_expired():
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
        if url != 'v1/auth/refresh' and self.is_token_expired():
            if level >= AuthLevel.ACCESS or self.can_refresh_auth:
                self.refresh_auth()
            elif self.access_token is not None:
                l.warning('access_token expired and cannot be refreshed, send %s %s without authorization', method.upper(), url)
                send_token = False

        return fetch(self, method, url, params, files, send_token=send_token)

    def request_sse(self, url: str):
        l.debug('sse %s', url)

        if self.is_token_expired():
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
        return Me(self)

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

    def search(self, query: str, hashtags_limit: int = 20, users_limit: int = 20) -> tuple[list[User], list[Hashtag]]:
        """Поиск пользователей и хэштэгов

        Args:
            query (str): Запрос
            hashtags_limit (int, optional): Лимит хэштэгов. Defaults to 20.
            users_limit (int, optional): Лимит пользователей. Defaults to 20.

        Returns:
            tuple[list[User], list[Hashtag]]: Результат поиска
        """
        res = search(self, query, users_limit, hashtags_limit).json()['data']
        return [User.from_dict(user, client=self) for user in res['users']], [Hashtag.from_dict(hashtag, client=self) for hashtag in res['hashtags']]

    def search_users(self, query: str, limit: int = 10) -> list[User]:
        """Поиск пользователей

        Args:
            query (str): Запрос
            limit (int, optional): Лимит. Defaults to 10.

        Returns:
            list[User]: Список пользователей
        """
        l.warning('Client.search_users is deprecated. Please use Users.search.')
        return Users.search(query, limit)

    def search_hashtags(self, query: str, limit: int = 10) -> list[Hashtag]:
        """Поиск хэштэгов

        Args:
            query (str): Запрос
            limit (int, optional): Лимит. Defaults to 10.

        Returns:
            list[Hashtag]: Список хэштэгов
        """
        l.warning('Client.search_hashtags is deprecated. Please use Hashtags.search.')
        return Hashtags.search(query, limit)

    def search_user(self, query: str) -> User | None:
        """Поиск пользователя

        Args:
            query (str): Запрос

        Returns:
            User | None: Пользователь
        """
        l.warning('Client.search_user is deprecated. Please use User.search.')
        try:
            return User.search(query)
        except NotFoundError:
            return None

    def search_hashtag(self, query: str) -> Hashtag | None:
        """Поиск хэштэга

        Args:
            query (str): Запрос

        Returns:
            Hashtag | None: Хэштэг
        """
        l.warning('Client.search_hashtag is deprecated. Please use Hashtag.search.')
        try:
            return Hashtag.search(query)
        except NotFoundError:
            return None

    @overload
    def get_follow_status(self, users: list[User | UUID | str]) -> dict[UUID, bool]: ...

    @overload
    def get_follow_status(self, users: User | UUID | str) -> bool: ...

    def get_follow_status(self, users: list[User | UUID | str] | User | UUID | str) -> dict[UUID, bool] | bool:
        """Получить статус подписки

        Args:
            users (list[User | UUID | str] | User | UUID | str): Пользователи для проверки (можно как и списком, так и как одиночным объектом)

        Returns:
            dict[UUID, bool] | bool: Результат
        """
        l.warning('Client.get_follow_status is deprecated. Please use get_follow_status.')
        return get_follow_status(users)


def init_client(name: str | None = None, initial_refresh: str | None = None, verify_refresh: bool = False, config: Config = Config()) -> Client:
    return Client.from_file(name or 'default', initial_refresh=initial_refresh, verify_refresh=verify_refresh, config=config)
