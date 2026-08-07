from __future__ import annotations

from typing import TYPE_CHECKING

from itd.core.request import endpoint
from itd.enums import AuthLevel

if TYPE_CHECKING:
    from itd.core.client import Client


@endpoint('get', 'platform/version', level=AuthLevel.NO)
def get_apps(client: Client): ...


@endpoint('get', 'platform/changelog', level=AuthLevel.NO)
def get_changelog(client: Client): ...


@endpoint('get', 'platform/announcements', level=AuthLevel.NO)
def get_announcements(client: Client): ...
