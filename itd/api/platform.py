from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from itd.client import Client
from itd.enums import AuthLevel
from itd.base import catch_errors, rate_limit


@catch_errors()
@rate_limit()
def get_apps(client: Client):
    return client.request('get', 'platform/version', level=AuthLevel.NO)


@catch_errors()
@rate_limit()
def get_changelog(client: Client):
    return client.request('get', 'platform/changelog', level=AuthLevel.NO)
