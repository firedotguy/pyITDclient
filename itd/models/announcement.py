from pydantic import BaseModel

from itd.api.platform import get_announcements
from itd.core.base import ITDBaseModel
from itd.core.client import Client
from itd.enums import AnnouncementButtonStyle, AnnouncementButtonType


class AnnouncementImage(BaseModel):
    url: str
    width: int | None = None
    height: int | None = None

    def __str__(self):
        return self.url


class AnnouncementButtonAction(BaseModel):
    type: AnnouncementButtonType
    url: str | None = None


class AnnouncementButton(BaseModel):
    title: str
    style: AnnouncementButtonStyle = AnnouncementButtonStyle.PRIMARY
    action: AnnouncementButtonAction

    def __str__(self):
        return self.title


class Announcement(ITDBaseModel):
    id: str
    image: AnnouncementImage | None = None
    title: str
    description: str | None = None
    additional_text: str | None = None

    buttons: list[AnnouncementButton] = []

    def __str__(self):
        return self.title

    def read(self):
        assert self.client._session_file, 'No session file'
        self.client._session_file.seen_announcements.append(self.id)
        self.client._session_file.flush()


class Announcements(ITDBaseModel, list[Announcement]):
    def __init__(self, *, hide_seen: bool = True, client: Client | None = None):
        super().__init__(client=client)
        self.load(hide_seen=hide_seen)

    def load(self, *, hide_seen: bool = True) -> 'Announcements':
        self.clear()
        self.extend([Announcement.from_dict(announcement, client=self.client) for announcement in get_announcements(self.client).json()['announcements']])

        if hide_seen and self.client._session_file:
            for announcement in self.copy():
                if announcement.id in self.client._session_file.seen_announcements:
                    self.remove(announcement)

        return self

    def get(self) -> Announcement | None:
        if self:
            return self[0]

    @classmethod
    def empty(cls):
        instance = cls.__new__(cls)
        super(Announcements, instance).__init__()
        return instance
