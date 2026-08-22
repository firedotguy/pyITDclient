from datetime import datetime
from json import dumps, loads
from pathlib import Path

from pydantic import BaseModel, Field


class SessionFile(BaseModel):
    access: str | None = None
    refresh: str | None = None
    valid: bool = True
    updated_at: datetime = Field(default_factory=datetime.now)
    seen_announcements: list[str] = []

    _file: Path

    def flush(self):
        self.updated_at = datetime.now()
        self._file.write_text(dumps(self.model_dump(mode='json')))

    def update(self):
        new = self.model_validate(loads(self._file.read_text()))
        if self.updated_at <= new.updated_at:
            for field in SessionFile.model_fields:
                setattr(self, field, getattr(new, field))
            return True
        return False
