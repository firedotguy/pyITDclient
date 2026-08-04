from datetime import datetime
from json import dumps, loads
from pathlib import Path

from pydantic import BaseModel, Field

# class CredfileSession(BaseModel):
#     id: int
#     last_active: datetime
#     main: bool

#     @classmethod
#     def current(cls, main: bool = False):
#         return cls(id=getpid(), last_active=datetime.now(), main=main)


class Credfile(BaseModel):
    access: str | None = None
    refresh: str | None = None
    valid: bool = True
    updated_at: datetime = Field(default_factory=datetime.now)
    # sessions: list[CredfileSession] = Field(default_factory=lambda: [])
    _file: Path

    def flush(self):
        self.updated_at = datetime.now()
        self._file.write_text(dumps(self.model_dump(mode='json')))

    def update(self):
        new = self.model_validate(loads(self._file.read_text()))
        if self.updated_at <= new.updated_at:
            for field in Credfile.model_fields:
                setattr(self, field, getattr(new, field))
            return True
        return False

    # @field_validator('sessions', mode='after')
    # def validate_sessions(self, sessions: list[CredfileSession]):
    #     for session in sessions.copy():
    #         if session.last_active < datetime.now() - timedelta(minutes=30):
    #             sessions.remove(session)

    #     sessions.append(CredfileSession.current(main=not any(session.main for session in sessions)))
