from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from itd.exceptions import AlreadyDeletedError, BannedWordError, ForbiddenError, NotFoundError, RequiresSubscriptionError, ValidationError
from itd.request import endpoint

if TYPE_CHECKING:
    from itd.client import Client


@endpoint(
    'post',
    'posts/{post_id}/comments',
    ValidationError(),
    NotFoundError('Post'),
    BannedWordError('Comment'),
    ForbiddenError('comment - some files not owned'),
    RequiresSubscriptionError('Video uploading')
)
def add_comment(client: Client, post_id: UUID, content: str | None = None, attachment_ids: list[UUID] = []):
    return {'content': content or '', 'attachmentIds': list(map(str, attachment_ids))}


@endpoint(
    'post',
    'comments/{comment_id}/replies',
    ValidationError(),
    NotFoundError('Comment'),
    NotFoundError('User', res_check=lambda res: res.status_code == 500 and 'Failed query' in res.text),
    BannedWordError('Reply'),
    ForbiddenError('reply - some files not owned'),
    RequiresSubscriptionError('Video uploading')
)
def add_reply_comment(client: Client, comment_id: UUID, author_id: UUID, content: str | None = None, attachment_ids: list[UUID] = []):
    return {'content': content or '', 'replyToUserId': str(author_id), 'attachmentIds': list(map(str, attachment_ids))}


@endpoint('get', 'posts/{post_id}/comments', ValidationError(), NotFoundError('Post'))
def get_comments(client: Client, post_id: UUID, cursor: int = 0, limit: int = 20, sort: str = 'popular'):
    return {'limit': limit, 'sort': sort, 'cursor': cursor}


@endpoint('post', 'comments/{id}/like', NotFoundError('Comment'))
def like_comment(client: Client, id: UUID): ...


@endpoint('delete', 'comments/{id}/like', NotFoundError('Comment'))
def unlike_comment(client: Client, id: UUID): ...


@endpoint('delete', 'comments/{id}', NotFoundError('Comment'), AlreadyDeletedError('Comment'), ForbiddenError('delete comment'))
def delete_comment(client: Client, id: UUID): ...


@endpoint('get', 'comments/{id}/replies', ValidationError(), NotFoundError('Comment'))
def get_replies(client: Client, id: UUID, page: int = 1, limit: int = 50):
    return {'page': page, 'limit': limit}


@endpoint('patch', 'comments/{id}', ValidationError(), NotFoundError('Comment'), ForbiddenError('edit comment'))
def edit_comment(client: Client, id: UUID, content: str):
    return {'content': content}
