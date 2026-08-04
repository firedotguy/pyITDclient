from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from itd.core.request import endpoint

if TYPE_CHECKING:
    from itd.core.client import Client


@endpoint('get', 'v1/auth/sessions')
def get_sessions(client: Client): ...


@endpoint('delete', 'v1/auth/sessions/{id}')
def revoke(client: Client, id: UUID): ...


@endpoint('delete', 'v1/auth/sessions')
def revoke_all(client: Client): ...
