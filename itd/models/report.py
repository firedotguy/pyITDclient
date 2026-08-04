from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import Field

from itd.api.reports import report
from itd.core.base import ITDBaseModel
from itd.enums import ReportReason, ReportTargetType

if TYPE_CHECKING:
    from itd.core.client import Client


class Report(ITDBaseModel):
    _refreshable = False

    id: UUID
    created_at: datetime = Field(alias='createdAt')

    def __init__(self, target_id: UUID, target_type: ReportTargetType, reason: ReportReason, description: str | None = None, client: Client | None = None):
        super().__init__(client)

        self.target_id = target_id
        self.target_type = target_type
        self.reason = reason
        self.description = description

        self._fill_from_data(report(client or self.client, self.target_id, self.target_type, self.reason, self.description).json()['data'])

    def __hash__(self):
        return int(self.id)
