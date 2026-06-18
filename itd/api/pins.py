from __future__ import annotations

from typing import TYPE_CHECKING

from itd.base import api_wrapper
from itd.exceptions import PinNotOwnedError

if TYPE_CHECKING:
    from itd.client import Client


@api_wrapper()
def get_pins(client: Client):
    return client.request('get', 'users/me/pins')


@api_wrapper()
def remove_pin(client: Client):
    return client.request('delete', 'users/me/pin')


@api_wrapper(PinNotOwnedError())
def set_pin(client: Client, slug: str):
    return client.request('put', 'users/me/pin', {'slug': slug})
