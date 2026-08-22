from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import Field

from itd.api.hashtags import get_hashtags, get_posts_by_hashtag, search_hashtags
from itd.core.base import ITDBaseModel
from itd.exceptions import NotFoundError

if TYPE_CHECKING:
    from itd.core.client import Client
    from itd.models.post import HashtagPosts


class Hashtag(ITDBaseModel):
    id: UUID
    name: str
    posts_count: int = Field(alias='postsCount')

    def __init__(self, name: str, client: Client | None = None) -> None:
        super().__init__(client)
        self.name = name.lstrip('#')
        self._init_refresh()

    def _refresh(self, *, client: Client):
        return get_posts_by_hashtag(client, self.name, limit=1).json()['data']['hashtag']

    def __str__(self) -> str:
        return '#' + self.name

    def __int__(self) -> int:
        return self.posts_count

    def __hash__(self):
        return int(self.id)

    @cached_property
    def posts(self) -> 'HashtagPosts':
        from itd.models.post import HashtagPosts

        return HashtagPosts(self, client=self.client)

    @classmethod
    def search(cls, query: str):
        result = Hashtags.search(query, limit=1)
        if result:
            return result[0]
        raise NotFoundError('Hashtag')


class Hashtags(ITDBaseModel, list[Hashtag]):
    _refreshable = False

    def __init__(self, query: str | None = None, limit: int = 10, client: Client | None = None):
        super().__init__(client)
        self.query = query
        self.load(limit)

    def load(self, limit: int = 10):
        self.clear()
        if self.query:
            self.extend([Hashtag.from_dict(hashtag) for hashtag in search_hashtags(self.client, self.query, limit).json()['data']['hashtags']])
        else:
            self.extend([Hashtag.from_dict(hashtag) for hashtag in get_hashtags(self.client, limit).json()['data']['hashtags']])
        return self

    @classmethod
    def empty(cls):
        instance = cls.__new__(cls)
        super(Hashtags, instance).__init__()
        return instance

    @classmethod
    def search(cls, query: str, limit: int = 10):
        return cls(query, limit)
