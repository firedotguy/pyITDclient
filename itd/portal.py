from itd.api.portal import get_portal
from itd.base import ITDBaseModel
from itd.client import Client


class Portal(ITDBaseModel):
    active: bool = True
    title: str
    url: str

    def __init__(self, *, client: Client | None = None):
        super().__init__(client=client)
        self.refresh()

    def _refresh(self, client: Client):
        return get_portal(client).json()

    def __str__(self):
        return self.title

    def __bool__(self):
        return self.active
