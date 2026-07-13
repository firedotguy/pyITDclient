from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from itd.base import api_wrapper
from itd.exceptions import NotFoundError

if TYPE_CHECKING:
    from itd.client import Client
    from itd.notification import NotificationsSettings


@api_wrapper()
def get_notifications(client: Client, limit: int = 20, offset: int = 0):
    return client.request('get', 'notifications', {'limit': limit, 'offset': offset})


@api_wrapper(NotFoundError('Notification', json_check=lambda json: json.get('success') is False))
def mark_as_read(client: Client, id: UUID):
    return client.request('post', f'notifications/{id}/read')


@api_wrapper()
def mark_all_as_read(client: Client):
    return client.request('post', 'notifications/read-all')


@api_wrapper()
def get_unread_notifications_count(client: Client):
    return client.request('get', 'notifications/count')


def stream_notifications(client: Client):
    return client.request_sse('notifications/stream')


def get_notifications_settings(client: Client):
    return client.request('get', 'notifications/settings')


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

    return client.request('put', 'notifications/settings', data)
