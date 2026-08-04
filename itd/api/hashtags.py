from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from itd.enums import AuthLevel
from itd.exceptions import NotFoundError, TooLargeError, ValidationError
from itd.core.request import endpoint

if TYPE_CHECKING:
    from itd.core.client import Client


@endpoint('get', 'hashtags', ValidationError(), level=AuthLevel.NO)
def search_hashtags(client: Client, query: str, limit: int = 10):
    return {'q': query, 'limit': limit}


@endpoint('get', 'hashtags/trending', ValidationError(), level=AuthLevel.NO)
def get_hashtags(client: Client, limit: int = 10):
    return {'limit': limit}


@endpoint(
    'get',
    'hashtags/{hashtag}/posts',
    TooLargeError('Hashtag'),
    NotFoundError('Hashtag', json_check=lambda json: json.get('data', {}).get('hashtag', '') is None),
    ValidationError(),
    level=AuthLevel.NO
)
def get_posts_by_hashtag(client: Client, hashtag: str, cursor: UUID | None = None, limit: int = 20):
    return {'limit': limit, 'cursor': cursor}
