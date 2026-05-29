from __future__ import annotations
from typing import Any, Callable, TYPE_CHECKING, Iterator, TypeVar, overload
from functools import wraps
from time import sleep
from datetime import datetime, timedelta

from requests import Response
from requests.exceptions import JSONDecodeError
from pydantic import BaseModel
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefinedType

from itd._default import get_default_client
from itd.logger import get_logger
from itd.exceptions import ITDException, ValidationError, RateLimitError, UnauthorizedError, AccessTokenExpiredError, DEFAULT_ERRORS, AccountDeletedError
from itd.enums import All, ALL, DebugResponseMode, RateLimitMode, BATCH, Batch, LoadStatus

if TYPE_CHECKING:
    from itd.client import Client


l = get_logger('base')


def _is_comments_on_post(value: Any, self: Any) -> bool:
    from itd.comment import Comments
    from itd.post import Post

    return isinstance(value, Comments) and isinstance(self, Post)


def _getattr(self: object, name: str, default: Any | None = None) -> Any:
    try:
        return object.__getattribute__(self, name)
    except AttributeError:
        return default


def _field_has_default(cls: type, name: str) -> bool:
    """Returns True if the field is declared as Field(...) with a default value."""
    for klass in cls.__mro__:
        val = klass.__dict__.get(name)
        if isinstance(val, FieldInfo):
            return not isinstance(val.default, PydanticUndefinedType) or val.default_factory is not None
    return False


class ITDBaseModel:
    """Базовый класс модельки"""

    _refreshable: bool = True
    load_status: LoadStatus = LoadStatus.NO
    _load_with_parent: bool = True  # load parent model if model called
    _validator: Callable[[Any], type[BaseModel]] | None = (
        None  # callable (pls use lambda), becuase we havent validator at that moment (it depends on this class)
    )

    def __init__(self, client: Client | None = None) -> None:
        self._client = client or get_default_client()
        self._loaded_attrs: set[str] = set()

    def __setattr__(self, name: str, value: Any) -> None:
        if isinstance(value, ITDBaseModel) and (client := _getattr(self, '_client')):  # ai
            value._client = client

        object.__setattr__(self, name, value)

    def _post_refresh(self): ...

    @property
    def client(self) -> Client:
        return self._client

    def _refresh(self, *, client: Client) -> dict:
        raise NotImplementedError()

    def refresh(self, *, client: Client | None = None) -> Any:
        if not self._refreshable:
            l.warning(f'{self.__class__.__name__} is not refreshable but refresh is called')
        self.load_status = LoadStatus.LOADING
        self._fill_from_data(self._refresh(client=client or self.client))
        self.load_status = LoadStatus.FULL
        return self

    def _fill_from_data(self, data: dict):
        assert self._validator, 'Unable to use fill_from_data without a validator'
        validated = self._validator().model_validate(data)  # pyright: ignore[reportCallIssue]
        # self._loaded_attrs = validated.model_fields_set # значения автоматически добавляются через __setattr__
        for name, value in validated.__dict__.items():
            setattr(self, name, value)

        self._post_refresh()

    @classmethod
    def from_dict(cls, data: dict, *, client: Client | None = None):
        instance = cls.__new__(cls)
        ITDBaseModel.__init__(instance, client)

        instance._fill_from_data(data)
        instance.load_status = LoadStatus.PARTIALLY
        return instance

    if not TYPE_CHECKING:

        def __getattribute__(self, name: str) -> Any:
            try:
                value = object.__getattribute__(self, name)
                exists = True
            except AttributeError:
                value = None
                exists = False

            if (
                name.startswith('_')  # приватный аттрибут
                or name in ('client', 'model_fields_set', 'load_status')  # спец. имя
                or not _getattr(self, '_refreshable')  # не рефрешабельная модель
                or not _getattr(self, 'client').config.auto_load  # отключено в конфиге
                or callable(value)  # функция
                or isinstance(_getattr(type(self), name), property)
                or self.load_status == LoadStatus.LOADING  # сейчас загружается (уже вроде как не надо, но пусть будет на всяк)
                or (not _getattr(self, 'client').config.load_comments_from_post and _is_comments_on_post(value, self))  # коменты
                or name in self._loaded_attrs
                or name in self.__dict__  # было загружено или добавлено через setattr
                or (isinstance(value, ITDBaseModel) and not value._load_with_parent)
            ):
                # l.debug('return %s as is', name)
                if not exists:
                    raise AttributeError
                return value

            # if isinstance(value, FieldInfo) or self.load_status != LoadStatus.FULL:
            l.info('refresh %s field=%s load_status=%s', self.__class__.__name__, name, self.load_status.value)
            self.refresh()
            return object.__getattribute__(self, name)


T = TypeVar('T', bound=ITDBaseModel)


class ITDList[T](ITDBaseModel, list[T]):
    """Базовый класс списка"""

    _limit: int = 20
    _get_total = None
    _refreshable = False
    has_more = True
    idx = 0

    def _fetch(self, client: Client, limit: int) -> dict:
        return {}

    # edited by calude, thats so fucking crazy pagination
    # ai begin ---
    def load(self, count: int | All | Batch = BATCH, limit: int | Batch = BATCH, client: Client | None = None) -> list[T]:
        """Загрузить объекты

        Args:
            count (int | All | Batch, optional): Количество объектов. Defaults to BATCH.
            limit (int | Batch, optional): Лимит. Defaults to BATCH.
            client (Client | None, optional): Клиент. Defaults to None.

        Returns:
            list[T]: Новые объекты
        """
        if not (self.has_more or (client or self.client).config.force_load_lists):
            l.warning('skip load because has_more=False')
            return []

        limit = limit or self._limit
        if isinstance(count, int) and count < limit:
            limit = count
        l.debug('load %s count=%s limit=%s', self.__class__.__name__.lower(), count, limit)

        # Batch = load one batch (limit), All = load everything, int = load exactly N
        left = None if isinstance(count, All) else (count or limit)
        added = []

        while left is None or left > 0:
            batch = limit if left is None else min(limit, left)
            data = self._fetch(client or self.client, batch)
            objects = self._get_objects(data)
            self.has_more = self._get_has_more(data)
            if self._get_cursor(data) is not None:
                self.cursor = self._get_cursor(data)

            if self._get_total:
                self.total = self._get_total(data)
                if getattr(self, '_min_total', None) and self._min_total > self.total:
                    raise IndexError(f'Given index ({self._min_total - 1}) is too high. Total items is {self.total}')

            length = len(objects)
            if objects and (client or self.client).config.userposts_add_pinned_post and length == batch + 1:  # skip pinned post
                length -= 1

            if left is not None:
                left -= length

            l.info('fetched %s %s (was %s) cursor=%s has_more=%s', length, self.__class__.__name__.lower(), len(self), self.cursor, self.has_more)
            models = self._to_models(objects, client or self.client)
            self.extend(models)
            added.extend(models)

            if not self.has_more or not objects:
                break

        return added

    # --- ai end

    def _to_models(self, objects: list, client: Client) -> list[T]: ...

    @staticmethod
    def _get_has_more(data: dict) -> bool:
        return True

    @staticmethod
    def _get_cursor(data: dict):
        return 0

    @staticmethod
    def _get_objects(data: dict) -> list[dict]:
        return []

    def refresh(self, count: int | All | Batch | None = None, limit: int | Batch = BATCH, *, client: Client | None = None) -> list[T]:
        """Обновить список (удалить все элементы и загрузить заново)

        Args:
            count (int | All | Batch, optional): Количество объектов (None - количество на данный момент). Defaults to None.
            limit (int | Batch, optional): Лимит. Defaults to BATCH.
            client (Client | None, optional): Клиент. Defaults to None.

        Returns:
            list[T]: Обновленный список
        """
        if count is None:
            count = len(self)
            if self and getattr(self[0], 'is_pinned', False):  # skip pinned post
                count -= 1
        self.clear()
        self.cursor = None
        self.has_more = True  # also refresh has_more
        l.debug('refresh %s count=%s limit=%s', self.__class__.__name__.lower(), str(count), limit)
        return self.load(count, limit, client)

    def load_all(self, limit: int | Batch = BATCH, client: Client | None = None) -> list[T]:
        """Загрузить все объекты (эквивалент self.load(ALL))

        Args:
            limit (int | Batch, optional): Лимит. Defaults to BATCH.
            client (Client | None, optional): Клиент. Defaults to None.

        Returns:
            list[T]: Список
        """
        return self.load(ALL, limit, client)

    @overload
    def __getitem__(self, index: int) -> T: ...

    @overload
    def __getitem__(self, index: slice) -> list[T]: ...

    def __getitem__(self, index: int | slice) -> T | list[T]:  # pyright: ignore[reportIncompatibleMethodOverride]
        if isinstance(index, slice):
            value: int | None = index.stop
        else:
            value = index

        if ((value is not None and value > len(self) - 1) or value is None) and self.client.config.load_on_getitem is not None:
            if value:
                self._min_total = value + 1

            if value is None or isinstance(self.client.config.load_on_getitem, All):
                l.debug('getitem load all')
                self.load_all()
            elif isinstance(self.client.config.load_on_getitem, Batch):
                l.debug('getitem load batch')
                self.load(BATCH)
            else:
                l.debug('getitem load %s', value - len(self) + self.client.config.load_on_getitem)
                self.load(value - len(self) + self.client.config.load_on_getitem)

        return super().__getitem__(index)

    def __next__(self) -> T:
        assert self.client.config.load_on_iter is not None
        if getattr(self, 'total', None) and self.idx >= self.total:
            raise StopIteration()
        if self.idx >= len(self) and (self.has_more or self.client.config.force_load_lists):
            l.debug('not enough items to call next - load')
            self.load(self.client.config.load_on_iter)
        if self.idx >= len(self):
            raise StopIteration()
        item = self[self.idx]
        self.idx += 1
        return item

    def __iter__(self) -> Iterator[T]:
        if self.client.config.load_on_iter is None:
            return super().__iter__()
        self.idx = 0
        return self

    @property
    def all(self) -> list[T]:
        return self.load_all()


def _filter_bytes(args: tuple):
    filtered = []
    for arg in args:
        if isinstance(arg, bytes):
            filtered.append('_bytecode_')
        else:
            filtered.append(arg)
    return filtered


# user calls `Me` -> model calls `get_me` -> `catch_errors` wrapper: (`get_me` -> `client.request` -> `fetch` -> responses 401 -> `refresh_auth` from `catch_errors` -> `client.resuest` -> `fetch` -> token refreshed -> `catch_errors` backs to main query -> `get_me` -> `client.request` -> `fetch` -> user fetched) -> model recieves data -> pydantic fills model # hell what the monster i did
def catch_errors(*exceptions: ITDException):
    """Декоратор для отлавливания ошибок

    Args:
        *exceptions (ITDException): Список ошибок для отлавливания
    """

    def decorator(func):
        @wraps(func)
        def wrapper(client: Client, *args, **kwargs) -> Response | None:
            l.info('exec %s %s %s', func.__name__, _filter_bytes(args), kwargs)
            res: Response = func(client, *args, **kwargs)

            assert isinstance(res, Response)
            if res.status_code == 204:
                if client.config.debug_response != DebugResponseMode.NO:
                    l.debug('no response')
                return res

            if client.config.debug_response == DebugResponseMode.BEFORE:
                l.debug('response (raw): %s', res.text)

            try:
                json = res.json()
            except JSONDecodeError:
                json = {}
                l.warning('failed to parse json: %s', res.text[:1000])

            for exception in DEFAULT_ERRORS + exceptions:
                if (
                    (exception.res_check and exception.res_check(res))
                    or (exception.text_check and exception.text_check(res.text))
                    or (exception.json_check and exception.json_check(json))
                    or exception.status_code is not None
                    and res.status_code == exception.status_code
                    or isinstance(json.get('error'), dict)
                    and (
                        exception.code is not None
                        and json['error'].get('code') == exception.code
                        or exception.message is not None
                        and json['error'].get('message') == exception.message
                    )
                ):
                    if isinstance(exception, ValidationError):
                        exception.text = json.get('error', {}).get('message', 'Failed validation')

                    if isinstance(exception, RateLimitError) and isinstance(json.get('error'), dict):
                        exception.retry_after = json.get('error', {}).get('retryAfter', 0)

                    if isinstance(exception, (UnauthorizedError, AccessTokenExpiredError)) and client.refresh_token:
                        client.refresh_auth()
                        return wrapper(client, *args, **kwargs)

                    if isinstance(exception, AccountDeletedError):
                        exception.can_restore = json.get('error', {}).get('canRestore', True)

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

        return wrapper

    return decorator


def rate_limit(delay_min: float | None = None, delay_mid: float | None = None, delay_max: float | None = None):
    """Декоратор для рейт лимита

    Args:
        delay_min (float | None, optional): Задержка для RateLimitMode.MIN. Defaults to None.
        delay_mid (float | None, optional): Задержка для RateLimitMode.MID. Defaults to None.
        delay_max (float | None, optional): Задержка для RateLimitMode.MAX. Defaults to None.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(client: Client, *args, **kwargs) -> Response | None:
            if func.__name__ in client.config.rate_limit_actions:
                delay = client.config.rate_limit_actions[func.__name__]
            elif client.config.rate_limit == RateLimitMode.NO:
                delay = 0
            elif any((delay_min, delay_mid, delay_max)):
                delay = eval(f'delay_{client.config.rate_limit.value}') or next((i for i in (delay_min, delay_mid, delay_max) if i is not None))
            else:
                delay = client.config._rate_limit_default

            if datetime.now() - timedelta(seconds=delay) < client.last_actions.get(func.__name__, datetime(1990, 1, 1)):
                delay -= (datetime.now() - client.last_actions[func.__name__]).seconds
                l.debug('anti rate limit on %s; wait %ss', func.__name__, delay)
                sleep(max(delay, 0))
            client.last_actions[func.__name__] = datetime.now()

            if not client.config.retry_enabled:
                return func(client, *args, **kwargs)

            while True:
                try:
                    return func(client, *args, **kwargs)
                except client.config._retry_exceptions as e:
                    if getattr(e, 'retry_after', 0) > client.config.retry_max_retry_after:
                        l.error('too large rate limit')
                        raise

                    retry_after = getattr(e, 'retry_after', client.config.retry_delay) or 10
                    l.warning('%s on %s: wait %ss', e.__class__.__name__, func.__name__, retry_after)
                    sleep(retry_after)

        return wrapper

    return decorator
