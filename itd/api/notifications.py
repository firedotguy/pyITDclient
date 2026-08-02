from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from itd.exceptions import NotFoundError
from itd.request import endpoint

if TYPE_CHECKING:
    from itd.client import Client
    from itd.notification import NotificationsSettings


@endpoint('get', 'notifications')
def get_notifications(client: Client, limit: int = 20, offset: int = 0):
    return {'limit': limit, 'offset': offset}


@endpoint('post', 'notifications/{id}/read', NotFoundError('Notification', json_check=lambda json: json.get('success') is False))
def mark_as_read(client: Client, id: UUID): ...


@endpoint('post', 'notifications/read-all')
def mark_all_as_read(client: Client): ...


@endpoint('get', 'notifications/count')
def get_unread_notifications_count(client: Client): ...


@endpoint('get', 'notifications/settings')
def get_notifications_settings(client: Client): ...


@endpoint('put', 'notifications/settings')
def update_notifications_settings(client: Client, settings: NotificationsSettings, *, old: bool = True, new: bool = True):
    from itd.notification import _NotificationsSettingsNew, _NotificationsSettingsNewPreferences, _NotificationsSettingsOld  # жду фикс circular import день 67

    data = {}
    if old:
        data.update(_NotificationsSettingsOld.model_validate(settings, from_attributes=True).model_dump(mode='json', by_alias=True))

    if new:
        data.update(
            _NotificationsSettingsNew(
                web_enabled=settings.web_enabled,
                sound_enabled=settings.sound,
                preferences=_NotificationsSettingsNewPreferences.model_validate(settings, from_attributes=True),
                enabled=settings.enabled
            ).model_dump(mode='json', by_alias=True)
        )

    return data


def stream_notifications(client: Client):
    return client.request_sse('notifications/stream')
