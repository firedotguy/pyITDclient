from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from itd.client import Client
from itd.base import api_wrapper, rate_limit
from itd.exceptions import ValidationError


@api_wrapper()
@rate_limit()
def get_sessions(client: Client):
    return client.request('get', 'v1/auth/sessions')


@api_wrapper()
@rate_limit()
def revoke(client: Client, id: UUID):
    return client.request('delete', f'v1/auth/sessions/{id}')


@api_wrapper()
@rate_limit()
def revoke_all(client: Client):
    return client.request('delete', 'v1/auth/sessions')
