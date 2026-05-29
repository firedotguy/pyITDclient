from pydantic import BaseModel, Field

from itd.base import ITDBaseModel
from itd.logger import get_logger
from itd.api.etc import get_top_clans


l = get_logger('clan')


class Clan(BaseModel):
    avatar: str
    members_count: int = Field(0, alias='memberCount')

    def __str__(self) -> str:
        return self.avatar


class TopClans(ITDBaseModel, list[Clan]):
    _refreshable = False

    def __init__(self) -> None:
        super().__init__()
        self.load()

    def load(self):
        self.clear()
        self.extend([Clan.model_validate(clan) for clan in get_top_clans(self.client).json()['clans']])
        return self

    def refresh(self, *, client=None):
        l.warning('TopClans.refresh is deprecated and will be removed in 2.6.0. Please use TopClans.load')
        self.load()

    @classmethod
    def empty(cls):
        instance = cls.__new__(cls)
        super(TopClans, instance).__init__()
        return instance
