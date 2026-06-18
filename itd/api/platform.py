from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from itd.client import Client
from itd.base import api_wrapper
from itd.enums import AuthLevel


@api_wrapper()
def get_apps(client: Client):
    return client.request('get', 'platform/version', level=AuthLevel.NO)


@api_wrapper()
def get_changelog(client: Client):
    return client.request('get', 'platform/changelog', level=AuthLevel.NO)
