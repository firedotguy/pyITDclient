from _io import BufferedReader
from atexit import register
from dataclasses import dataclass, field
from datetime import datetime
from threading import Thread
from time import sleep
from typing import Callable, Literal, overload
from uuid import UUID

from pydantic import BaseModel, Field, field_validator
from requests import Session
from requests.adapters import HTTPAdapter
from requests.utils import default_user_agent

from itd._default import _default_client, set_default_client
from itd.api.auth import change_password, logout, refresh_token
from itd.api.posts import get_stats
from itd.api.search import search
from itd.enums import BATCH, All, AuthLevel, Batch, DebugResponseMode, ParseMode, RateLimitMode, Role, UserAgent
from itd.exceptions import InsufficientAuthLevelError, NotFoundError, RateLimitError
from itd.hashtag import Hashtag, Hashtags
from itd.logger import get_logger
from itd.post import DwellTracker, Post
from itd.request import decode_jwt_payload, fetch, fetch_stream
from itd.user import Me, User, Users, get_follow_status
from itd.utils import get_sdk_user_agent

l = get_logger('client')  # noqa: E741


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
    client_type: Literal['client', 'bot', 'onetime'] = 'onetime'

    rate_limit: RateLimitMode | None = None  # deprecated
    rate_limit_default: int | None = None  # deprecated
    rate_limit_actions: dict[str, float | int] | None = None  # deprecated
    anti_rate_limit: bool | None = None
    burst_requests: bool | None = None
    anti_ip_ban: bool = True
    limit_coefficient: float | None = None

    # enable_logging: bool | None = None
    # logging_level = 'DEBUG'

    is_default: bool = False

    userposts_add_pinned_post: bool = True

    # load_on_init: bool = True
    # load_on_getattr: bool = False
    auto_load: bool | None = None
    load_on_getitem: int | All | Batch | None = 1
    load_on_iter: int | All | Batch | None = BATCH
    force_load_lists: bool = False  # load lists even if has_more is False

    debug_response: DebugResponseMode = DebugResponseMode.NO

    timeout: float | None = None
    timeout_file: float | None = None
    timeout_file_download: float | None = None

    url: str = 'https://xn--d1ah4a.com/api'
    url_api: str | None = None  # deprecated
    user_agent: UserAgent | str = UserAgent.BROWSER
    solve_challenge: bool = True

    load_comments_from_post: bool | None = None

    parse_mode: ParseMode = ParseMode.NO

    retry_enabled: bool | None = None
    retry_delay: float = 10  # delay before next attempt (after rate limit error) if retry_after is not provided in response
    retry_max_retries: int | None = 10  # none for no limit
    retry_exceptions: tuple[type[Exception]] = field(default_factory=lambda: (RateLimitError,))
    retry_max_retry_after: int = 500

    bypass_auth_level: bool = False

    dwell_enabled: bool = True
    dwell_max_buffer: int = 20
    dwell_send_interval: float = 2
    dwell_save_on_quit: bool = True
    dwell_wait_durations: bool = False
    post_view_increment: bool = False
    post_auto_view: bool = True  # view when called post.set_invisible()

    post_update_stats: bool | None = None
    post_update_stats_interval: int = 3

    view_read_speed: int = 250  # in WPM # https://scholarwithin.com/average-reading-speed
    view_images_speed: int = 130  # https://news.mit.edu/2014/in-the-blink-of-an-eye-0116

    on_exceptions: dict[type[Exception], Callable[[Exception], None]] = field(default_factory=dict)
    batch_sizes: BatchSizes = field(default_factory=BatchSizes)
    refresh_token_cookie_name: str = 'refresh_token'

    def __post_init__(self):
        if self.url_api is not None:
            l.warning('config.url_api is deprecated and will be removed in 2.7.0. Please use config.url.')
            self.url = self.url_api

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

        if self.dwell_wait_durations:
            l.warning('config.dwell_wait_durations is deprecated and will be removed in 2.6.0.')

        if self.rate_limit is not None:
            l.warning('config.rate_limit is deprecated and will be removed in 2.7.0.')
        if self.rate_limit_default is not None:
            l.warning('config.rate_limit_default is deprecated and will be removed in 2.7.0.')
        if self.rate_limit_actions is not None:
            l.warning('config.rate_limit_actions is deprecated and will be removed in 2.7.0.')

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

        if self.anti_rate_limit is None:
            self._anti_rate_limit = self.client_type == 'bot'
        else:
            self._anti_rate_limit = self.anti_rate_limit
        if self.load_comments_from_post is not None:
            l.warning('load_comments_from_post is deprecated and will be removed in 2.7.0.')

        if self.burst_requests is None:
            self._burst_requests = self.client_type != 'bot'
        else:
            self._burst_requests = self.burst_requests

        if self.limit_coefficient is None:
            if self.client_type == 'bot':
                self._limit_coefficient = 0.75
            elif self.client_type == 'client':
                self._limit_coefficient = 0.9
            else:
                self._limit_coefficient = 1
        else:
            self._limit_coefficient = self.limit_coefficient


class AccessToken(BaseModel):
    roles: list[Role]
    session_id: UUID = Field(alias='sid')
    is_active: bool = Field(alias='isActive')
    subject_id: UUID = Field(alias='sub')
    issued_at: datetime = Field(alias='iat')
    issuer: str = Field(alias='iss')  # "auth-service"
    expired_at: datetime = Field(alias='exp')
    jwt_id: UUID = Field(alias='jti')

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
        self._user: Me | None = None
        self.visible_posts: list[Post] = []

        self.session = Session()
        adapter = HTTPAdapter(pool_connections=1, pool_maxsize=10, pool_block=False)  # idk what is this, (claude added) just for better stability
        self.session.mount('https://', adapter)

        if access:
            self.auth_level = AuthLevel.ACCESS
            self.access_token = access.replace('Bearer ', '')

        if refresh:
            self.session.cookies.set(config.refresh_token_cookie_name, refresh, path='/')
            self.auth_level = AuthLevel.REFRESH
            self.refresh_token = refresh
            # if access is None:
            #     self.refresh_auth()

        if _default_client is None or config.is_default:
            set_default_client(self)

        if self.auth_level > AuthLevel.NO and self.config.dwell_enabled:
            self.dwell_tracker = DwellTracker(self)
            self.dwell_tracker._start_timer()
        else:
            self.dwell_tracker = None

        if self.config.post_update_stats:
            self._start_update_timer()

    def _start_update_timer(self):
        l.debug('start update timer')
        if not self.config.post_update_stats_interval:
            return

        def loop():
            while True:
                sleep(self.config.post_update_stats_interval)
                self.update_post_stats()

        self._thread = Thread(target=loop)
        self._thread.daemon = True
        self._thread.start()

        def on_exit():
            l.debug('stop update timer')
            if self._thread:
                self._thread.join(timeout=0)

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

        if level >= AuthLevel.ACCESS and self.access_token is None and url != 'v1/auth/refresh':
            self.refresh_auth()

        return fetch(self, method, url, params, files)

    def request_sse(self, url: str):
        l.debug('sse %s', url)

        if self.access_token is None and url != 'v1/auth/refresh':
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

    @property
    def user_id(self) -> UUID:
        assert self.access_token_data
        return self.access_token_data.subject_id

    @property
    def user(self) -> Me:
        if not self._user:
            self._user = Me(self)
        return self._user

    def _process_exc_callbacks(self, exception: Exception):
        # l.debug([v for k, v in self.config.on_exceptions.items() if k in exception.__class__.mro()])
        for callback in [v for k, v in self.config.on_exceptions.items() if k in exception.__class__.mro()]:
            callback(exception)

    def refresh_auth(self) -> str:
        """Обновить access token

        Returns:
            str: Токен
        """
        l.debug('refresh token')

        res = refresh_token(self)
        res.raise_for_status()

        self.access_token = res.json()['accessToken']
        self.access_token_data = AccessToken.model_validate(decode_jwt_payload(self.access_token))

        assert self.access_token
        return self.access_token

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


def init_client(refresh: str | None = None, access: str | None = None, config: Config = Config()):
    return Client(refresh, access, config)
