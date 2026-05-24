from __future__ import annotations
from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from itd.client import Client
from itd.exceptions import ValidationError
from itd.base import catch_errors, rate_limit

@catch_errors()
@rate_limit()
def get_sessions(client: Client):
    return client.request('get', 'v1/auth/sessions')

@catch_errors()
@rate_limit()
def delete_session(client: Client, id: UUID):
    return client.request('delete', f'v1/auth/sessions/{id}')

@catch_errors()
@rate_limit()
def delete_all_sessions(client: Client):
    return client.request('delete', 'v1/auth/sessions')