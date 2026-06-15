from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from itd.base import api_wrapper
from itd.enums import AuthLevel
from itd.exceptions import NotFoundError, TooLargeError, ValidationError

if TYPE_CHECKING:
    from itd.client import Client


@api_wrapper(ValidationError())
def search_hashtags(client: Client, query: str, limit: int = 10):
    return client.request('get', 'hashtags', {'q': query, 'limit': limit}, level=AuthLevel.NO)


@api_wrapper(ValidationError())
def get_hashtags(client: Client, limit: int = 10):
    return client.request('get', 'hashtags/trending', {'limit': limit}, level=AuthLevel.NO)


@api_wrapper(TooLargeError('Hashtag'), NotFoundError('Hashtag', json_check=lambda json: json.get('data', {}).get('hashtag', '') is None), ValidationError())
def get_posts_by_hashtag(client: Client, hashtag: str, cursor: UUID | None = None, limit: int = 20):
    return client.request('get', f'hashtags/{hashtag}/posts', {'limit': limit, 'cursor': cursor}, level=AuthLevel.NO)
