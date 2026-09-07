from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from itd.core.client import Client
    from itd.core.limiter import IPRateLimiter, RateLimiter

_logging_setupped: bool = False
_default_client: Client | None = None
limiters: dict[int, RateLimiter] = {}
limits: dict[str, int] = {}


@dataclass
class LimiterConfig:
    limiter: type[RateLimiter] | None = None
    ip_limiter: IPRateLimiter | None = None
    auto_acquire: bool = True


_config = LimiterConfig()


def set_config(config: LimiterConfig):
    global _config
    _config = config


def get_config() -> LimiterConfig:
    global _config
    return _config


def get_default_client() -> Client:
    global _default_client
    if _default_client is None:
        raise RuntimeError('No client inited')
    return _default_client


def maybe_get_default_client() -> Client | None:
    global _default_client
    return _default_client


def set_default_client(client: Client):
    global _default_client
    _default_client = client


def mark_logging_setupped():
    global _logging_setupped
    _logging_setupped = True


def is_logging_setupped():
    global _logging_setupped
    return _logging_setupped
