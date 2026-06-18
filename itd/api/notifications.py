from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from itd.base import api_wrapper
from itd.exceptions import NotFoundError

if TYPE_CHECKING:
    from itd.client import Client


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
    """Получить SSE поток уведомлений

    Returns:
        Response: Streaming response для SSE
    """
    return client.request_sse('notifications/stream')
