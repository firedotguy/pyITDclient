from __future__ import annotations

from typing import TYPE_CHECKING

from itd._limiter import IPRateLimiter, RateLimiter

if TYPE_CHECKING:
    from itd.client import Client

_default_client: Client | None = None
limiters: dict[int, RateLimiter] = {}
limits: dict[str, int] = {}
ip_limiter = IPRateLimiter()


def get_default_client() -> Client:
    global _default_client
    if _default_client is None:
        raise
    return _default_client


def set_default_client(client: Client):
    global _default_client
    _default_client = client
