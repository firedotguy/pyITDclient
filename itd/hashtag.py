from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, Field

from itd.api.hashtags import get_hashtags, get_posts_by_hashtag, search_hashtags
from itd.base import ITDBaseModel
from itd.exceptions import NotFoundError

if TYPE_CHECKING:
    from itd.client import Client
    from itd.post import HashtagPosts


class Hashtag(ITDBaseModel):
    _validator = lambda _: _HashtagValidate

    id: UUID
    name: str
    posts_count: int = Field(alias='postsCount')

    def __init__(self, name: str, client: Client | None = None) -> None:
        super().__init__(client)
        self.name = name.lstrip('#')

    def _refresh(self, *, client: Client):
        return get_posts_by_hashtag(client, self.name, limit=1).json()['data']['hashtag']

    def __str__(self) -> str:
        return '#' + self.name

    def __int__(self) -> int:
        return self.posts_count

    @property
    def posts(self) -> 'HashtagPosts':
        if not hasattr(self, '_posts'):
            from itd.post import HashtagPosts

            self._posts = HashtagPosts(self, client=self.client)
        return self._posts

    @classmethod
    def search(cls, query: str):
        result = Hashtags.search(query, limit=1)
        if result:
            return result[0]
        raise NotFoundError('Hashtag')


class _HashtagValidate(BaseModel, Hashtag):
    pass


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
