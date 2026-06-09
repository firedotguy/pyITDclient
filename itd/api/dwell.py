from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from itd.base import api_wrapper, rate_limit

if TYPE_CHECKING:
    from itd.client import Client


@rate_limit()
@api_wrapper()
def send_views(client: Client, objects: list[dict], sid: UUID):
    return client.request('post', 'v1/i', {'e': objects, 'sid': str(sid)})


@rate_limit()
@api_wrapper()
def send_interactions(client: Client, objects: list[dict], sid: UUID):
    return client.request('post', 'v1/x', {'e': objects, 'sid': str(sid)})
