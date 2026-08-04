from __future__ import annotations

from typing import TYPE_CHECKING

from itd.exceptions import PinNotOwnedError
from itd.core.request import endpoint

if TYPE_CHECKING:
    from itd.core.client import Client


@endpoint('get', 'users/me/pins')
def get_pins(client: Client): ...


@endpoint('delete', 'users/me/pin')
def remove_pin(client: Client): ...


@endpoint('put', 'users/me/pin', PinNotOwnedError())
def set_pin(client: Client, slug: str):
    return {'slug': slug}
