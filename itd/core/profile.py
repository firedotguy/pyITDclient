from datetime import datetime, timedelta
from json import dumps, loads
from pathlib import Path
from uuid import UUID

from pydantic import AliasChoices, BaseModel, Field, field_validator, model_validator

from itd.core.request import decode_jwt_payload
from itd.enums import Role


class AccessToken(BaseModel):
    roles: list[Role] = [Role.USER]
    session_id: UUID = Field(alias='sid')
    is_active: bool = Field(True, alias='isActive')
    subject_id: UUID = Field(alias='sub')
    issued_at: datetime = Field(alias='iat')
    issuer: str | None = Field(None, alias='iss')  # "auth-service"
    expired_at: datetime = Field(alias='exp')
    jwt_id: UUID | None = Field(None, alias='jti')

    @field_validator('issued_at', 'expired_at', mode='plain')
    @classmethod
    def validate_datetimes(cls, v):
        return datetime.fromtimestamp(v)

    @property
    def is_expired(self) -> bool:
        return datetime.now() > (self.expired_at - timedelta(minutes=1))


class Profile(BaseModel):
    access: str | None = None
    access_data: AccessToken | None = Field(None, exclude=True)
    access_valid: bool = False

    refresh: str | None = None
    refresh_expires_at: datetime | None = None
    refresh_valid: bool = Field(False, validation_alias=AliasChoices('refresh_valid', 'valid'))

    email: str | None = None
    password: str | None = None
    creds_valid: bool = False

    updated_at: datetime = Field(default_factory=datetime.now)
    seen_announcements: list[str] = []

    _file: Path

    def flush(self):
        assert self._file
        self.updated_at = datetime.now()
        self._file.write_text(dumps(self.model_dump(mode='json')))

    def update(self):
        assert self._file
        new = self.model_validate(loads(self._file.read_text()))
        if self.updated_at <= new.updated_at:
            for field in Profile.model_fields:
                setattr(self, field, getattr(new, field))
            return True
        return False

    @property
    def is_refresh_expired(self) -> bool:
        if not self.refresh_expires_at:
            return False
        return datetime.now() > (self.refresh_expires_at - timedelta(minutes=30))

    def set_refresh_expire(self):
        self.refresh_expires_at = datetime.now() + timedelta(days=30)

    def refresh_access_data(self):
        if not self.access:
            return
        return AccessToken.model_validate(decode_jwt_payload(self.access))

    @model_validator(mode='after')
    def validate_model(self):
        self.access_data = self.refresh_access_data()
        return self
