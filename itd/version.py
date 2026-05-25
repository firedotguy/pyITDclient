from typing import TYPE_CHECKING
from pydantic import BaseModel, Field

from itd.client import Client
try:
    from dateparser import parse
except ImportError:
    parse = None

from itd.base import ITDBaseModel
from itd.api.platform import get_changelog, get_apps


class Version(BaseModel):
    version: str
    date_str: str = Field(alias='date')
    changes: list[str]

    @property
    def date(self):
        assert parse, 'Install dateparser using `uv add itd-sdk[date]`'

        date = parse(self.date_str, languages=['ru'])
        assert date, 'Failed to parse date'
        return date.date()

    @property
    def version_tuple(self):
        return tuple(map(int, self.version.split('.')))



class Changelog(ITDBaseModel, list[Version]):
    def __init__(self, client: Client | None = None) -> None:
        super().__init__(client)
        self.load()

    def load(self):
        self.clear()
        self.extend([Version.model_validate(version) for version in get_changelog(self.client).json()['data']])


class App(BaseModel):
    name: str
    min_version: str = Field(alias='minVersion')
    version: str = Field(alias='latestVersion')
    update_url: str = Field(alias='updateUrl')

    @property
    def min_version_tuple(self):
        return tuple(map(int, self.min_version.split('.')))

    @property
    def version_tuple(self):
        return tuple(map(int, self.version.split('.')))


class Apps(ITDBaseModel, dict[str, App]):
    def __init__(self, client: Client | None = None) -> None:
        super().__init__(client)
        self.load()

    def load(self):
        self.clear()

        for name, app in get_apps(self.client).json().items():
            app['name'] = name
            self[name] = App.model_validate(app)
            setattr(self, name, self[name])

    if TYPE_CHECKING: # for type checkers that not allow Apps().android
        def __getattribute__(self, name: str):
            return super().__getattribute__(name)