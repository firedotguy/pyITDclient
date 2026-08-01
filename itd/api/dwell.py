from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from itd.request import endpoint

if TYPE_CHECKING:
    from itd.client import Client


@endpoint('post', 'v1/i')
def send_views(client: Client, objects: list[dict], sid: UUID):
    return {'e': objects, 'sid': str(sid)}


@endpoint('post', 'v1/x')
def send_interactions(client: Client, objects: list[dict], sid: UUID):
    return {'e': objects, 'sid': str(sid)}
