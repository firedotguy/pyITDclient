from uuid import UUID
from ipaddress import IPv4Address
from datetime import datetime

from pydantic import Field, BaseModel

from itd.base import ITDBaseModel
from itd.client import Client
from itd.enums import DeviceType
from itd.api.sessions import get_sessions, delete_session, delete_all_sessions


class Session(ITDBaseModel):
    _refreshable = False
    _validator = lambda _: _SessionValidate

    id: UUID
    is_current: bool = Field(alias='isCurrent')

    created_at: datetime = Field(alias='createdAt')
    last_used_at: datetime = Field(alias='lastUsedAt')
    expires_at: datetime = Field(alias='expiresAt')

    ip: IPv4Address = Field(alias='ipAddress')
    country: str | None = Field(None, alias='ipCountry') # country code
    city: str | None = Field(None, alias='ipCity')

    device_type: DeviceType = Field(alias='deviceType')
    device_os: str = Field(alias='osName') # TODO use enum
    device_os_version: int = Field(alias='osVersion')
    device_model: str | None = Field(None, alias='deviceModel') # always none

    client_name: str = Field(alias='clientName') # cant use "client"
    client_version: str = Field(alias='clientVersion')

    def delete(self):
        delete_session(self.client, self.id)

    def __init__(self, session: dict, client: Client | None = None) -> None:
        super().__init__(client)

        for name, value in _SessionValidate.model_validate(session).__dict__.items():
            setattr(self, name, value)

    def __str__(self):
        return f'{self.device_os} {self.device_os_version} ({self.device_type.value}) {self.client_name}/{self.client_version}'

    @property
    def location(self) -> str | None:
        if self.country and self.city:
            return f'{self.city}, {self.country}'
        if self.country:
            return self.country
        if self.city:
            return self.city


class _SessionValidate(BaseModel, Session):
    pass



class Sessions(ITDBaseModel, list[Session]):
    _refreshable = False

    def __init__(self, client: Client | None = None):
        super().__init__(client)
        self.load()

    def load(self):
        self.clear()
        self.extend([Session(session) for session in get_sessions(self.client).json()['sessions']])