from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import Field

from itd.api.pins import remove_pin, set_pin
from itd.base import ITDBaseModel

if TYPE_CHECKING:
    from itd.client import Client
    from itd.user import _UserBase


class Pin(ITDBaseModel):
    _refreshable = False
    _user: '_UserBase'

    slug: str
    name: str
    description: str
    url: str | None = None
    granted_at: datetime | None = Field(None, alias='grantedAt')

    def _post_refresh(self, context: dict = {}):
        if context.get('user'):
            self._user = context['user']

    def __str__(self) -> str:
        return self.name

    def set(self, client: Client | None = None) -> None:
        set_pin(client or self.client, self.slug)
        self._user.pin = self

    def remove(self, client: Client | None = None) -> None:
        remove_pin(client or self.client)
        self._user.pin = None
