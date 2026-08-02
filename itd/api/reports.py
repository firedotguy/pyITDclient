from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from itd.enums import ReportReason, ReportTargetType
from itd.exceptions import AlreadyReportedError, NotFoundError, ValidationError
from itd.core.request import endpoint

if TYPE_CHECKING:
    from itd.core.client import Client


@endpoint(
    'post',
    'reports',
    AlreadyReportedError(),
    NotFoundError('Report target', json_check=lambda json: 'не найден' in json.get('error', {}).get('message', '')),
    ValidationError()
)
def report(client: Client, id: UUID, type: ReportTargetType = ReportTargetType.POST, reason: ReportReason = ReportReason.OTHER, description: str | None = None):
    return {'targetId': str(id), 'targetType': type.value, 'reason': reason.value, 'description': description or ''}
