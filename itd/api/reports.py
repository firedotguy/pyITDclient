from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from itd.base import api_wrapper, rate_limit
from itd.enums import ReportReason, ReportTargetType
from itd.exceptions import AlreadyReportedError, NotFoundError, ValidationError

if TYPE_CHECKING:
    from itd.client import Client


@rate_limit(5, 30, 60)  # это стоило мне одного ака виталия
@api_wrapper(
    AlreadyReportedError(), NotFoundError('Report target', json_check=lambda json: 'не найден' in json.get('error', {}).get('message', '')), ValidationError()
)
def report(client: Client, id: UUID, type: ReportTargetType = ReportTargetType.POST, reason: ReportReason = ReportReason.OTHER, description: str | None = None):
    if description is None:
        description = ''
    return client.request('post', 'reports', {'targetId': str(id), 'targetType': type.value, 'reason': reason.value, 'description': description})
