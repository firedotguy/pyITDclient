from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from itd.api.comments import add_comment, add_reply_comment, delete_comment, get_comments, get_replies, like_comment, unlike_comment
from itd.base import ITDBaseModel, ITDList
from itd.enums import CommentSorting, ReportReason, ReportTargetType
from itd.file import CommentAttach
from itd.report import Report
from itd.user import User
from itd.utils import ATTACHMENTS, format_attachments, parse_datetime, to_nullable_uuid

if TYPE_CHECKING:
    from itd.client import Client
    from itd.post import Post


class Comment(ITDBaseModel):
    _refreshable = False
    _validator = lambda _: _CommentValidate

    id: UUID
    content: str

    created_at: datetime = Field(alias='createdAt')
    author: User

    likes_count: int = Field(0, alias='likesCount')
    replies_count: int = Field(0, alias='repliesCount')
    is_liked: bool = Field(False, alias='isLiked')

    attachments: list[CommentAttach]
    replies: Replies = Field(default_factory=lambda: Replies())
    reply_to: User | None = None  # author of replied comment, if this comment is reply

    _post: Post
    _base_comment: Comment | None = None

    @classmethod
    def from_dict(cls, data: dict, post: Post | None = None, base_comment: Comment | None = None, *, client: Client | None = None) -> Comment:  # ty: ignore[invalid-method-override]
        instance = super().from_dict(data, client=client)
        if post:
            instance._post = post
        instance._base_comment = base_comment
        instance.replies._post = post
        instance.replies._post_refresh()
        return instance

    def _post_refresh(self):
        self.replies._base_comment = self
        # self.replies._post = self._post
        # self.replies._post_refresh()

    def __str__(self) -> str:
        return self.content

    def report(self, reason: ReportReason, description: str | None = None, client: Client | None = None) -> Report:
        return Report(self.id, ReportTargetType.COMMENT, reason, description, client or self.client)

    def reply(self, content: str | None = None, attachments: ATTACHMENTS = [], user_id: UUID | None = None, client: Client | None = None) -> 'Comment':
        """Ответить на комментарий

        Args:
            content (str | None, optional): Содержимое. Defaults to None.
            attachments (ATTACHMENTS, optional): Вложения. Defaults to [].
            user_id (UUID | None, optional): Автор комментария, на который отвечать. Если None, берется автор текущего комментария. Defaults to None.
            client (Client | None, optional): Клиент. Defaults to None.

        Returns:
            Comment: Комментарий
        """
        return Comment.from_dict(
            add_reply_comment(client or self._client, self.id, user_id or self.author.id, content, format_attachments(attachments)).json(),
            post=self._post,
            base_comment=self,
            client=client or self.client
        )

    def like(self, client: Client | None = None) -> int:
        """Лайкнуть комментарий

        Args:
            client (Client | None, optional): Клиент. Defaults to None.

        Returns:
            int: Количество лайков после лайка
        """
        likes = like_comment(client or self._client, self.id).json()['likesCount']
        self.likes_count = likes
        return likes

    def unlike(self, client: Client | None = None) -> int:
        """Убрать лайк с комментария

        Args:
            client (Client | None, optional): Клиент. Defaults to None.

        Returns:
            int: Количество лайков после убирания лайка
        """
        likes = unlike_comment(client or self._client, self.id).json()['likesCount']
        self.likes_count = likes
        return likes

    def delete(self, client: Client | None = None) -> None:
        """Удалить комментарий

        Args:
            client (Client | None, optional): Клиент. Defaults to None.
        """
        delete_comment(client or self._client, self.id)

    @classmethod
    def new(cls, post: Post, content: str | None = None, attachments: ATTACHMENTS = [], client: Client | None = None):
        instance = cls.__new__(cls)
        super(Comment, instance).__init__(client)
        return cls.from_dict(
            add_comment(client or instance.client, post.id, content, format_attachments(attachments)).json(), post, client=client or instance.client
        )

    @property
    def url(self):
        return f'https://xn--d1ah4a.com/@{self._post.author.username}/post/{self._post.id}?comment={self.id}'

    @property
    def link(self):
        return self.url


class _CommentValidate(BaseModel, Comment):
    @field_validator('attachments', mode='plain')
    @classmethod
    def validate_attachments(cls, attachments: list[dict]):
        return [CommentAttach(attach) for attach in attachments]

    @field_validator('replies', mode='plain')
    @classmethod
    def validate_replies(cls, replies: list[dict]):
        return Replies()._init_raw(replies)

    @field_validator('created_at', mode='plain')
    @classmethod
    def validate_created_at(cls, v: str):
        return parse_datetime(v)

    @field_validator('reply_to', mode='plain')
    @classmethod
    def validate_reply_to(cls, reply_to: dict | None):
        if reply_to is not None:
            return User.from_dict(reply_to)

    @field_validator('author', mode='plain')
    @classmethod
    def validate_author(cls, author: dict):
        return User.from_dict(author)


class Comments(ITDList[Comment]):
    """Список комментариев с функцией дозагрузки"""

    _post: Post
    total: int
    cursor: int = 0
    _sorting: CommentSorting = CommentSorting.POPULAR
    _raw: list[dict] = []

    def _init_raw(self, data: list[dict] = []):
        self._raw = data
        if data:
            self.cursor = len(data) + 1
        return self

    def _post_refresh(self):
        self.extend(self._to_models(self._raw, self.client))
        # self._raw.clear()

    def _fetch(self, client: Client, limit: int):
        return get_comments(client, self._post.id, self.cursor, limit).json()['data']

    def _to_models(self, objects: list, client: Client):
        return [Comment.from_dict(comment, self._post, client=client) for comment in objects]

    @staticmethod
    def _get_objects(data: dict) -> list[dict]:
        return data['comments']

    @staticmethod
    def _get_has_more(data: dict) -> bool:
        return data['hasMore']

    @staticmethod
    def _get_total(data: dict) -> int:
        return data['total']

    @staticmethod
    def _get_cursor(data: dict):
        return data['nextCursor']

    def new(self, content: str | None = None, attachments: ATTACHMENTS = [], client: Client | None = None) -> Comment:
        comment = Comment.new(self._post, content, attachments, client=client or self.client)
        self.insert(0, comment)
        return comment

    @property
    def sorting(self) -> CommentSorting:
        return self._sorting

    @sorting.setter
    def sorting(self, value: CommentSorting):
        self._sorting = value
        self.refresh()

    def __str__(self):
        return str([str(c) for c in self.copy()])


class Replies(ITDList[Comment]):
    _base_comment: 'Comment'

    _post: Post
    total: int
    cursor: int = 1
    _raw: list[dict] = []

    def _init_raw(self, data: list[dict] = []):
        self._raw = data
        return self

    def _fetch(self, client: Client, limit: int):
        if self._raw:
            self.clear()
        return get_replies(client or self._client, self._base_comment.id, self.cursor, limit).json()['data']

    @staticmethod
    def _get_has_more(data: dict) -> bool:
        return data['pagination']['hasMore']

    @staticmethod
    def _get_objects(data: dict) -> list[dict]:
        return data['replies']

    @staticmethod
    def _get_cursor(data: dict):
        return data['pagination']['page'] + 1

    @staticmethod
    def _get_total(data: dict) -> int:
        return data['pagination']['total']

    def _to_models(self, objects: list, client: Client):
        return [Comment.from_dict(comment, self._post, self._base_comment, client=client) for comment in objects]

    def new(self, content: str | None = None, attachments: ATTACHMENTS = [], client: Client | None = None, *, author_id: str | UUID | None = None) -> 'Comment':
        assert self._base_comment is not None
        reply = self._base_comment.reply(content, attachments, to_nullable_uuid(author_id), client)
        self.insert(0, reply)
        return reply
