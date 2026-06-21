from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from itd.base import api_wrapper
from itd.exceptions import AlreadyDeletedError, BannedWordError, ForbiddenError, NotFoundError, RequiresSubscriptionError, ValidationError

if TYPE_CHECKING:
    from itd.client import Client


@api_wrapper(
    ValidationError(),
    NotFoundError('Post'),
    BannedWordError('Comment'),
    ForbiddenError('comment - some files not owned'),
    RequiresSubscriptionError('Video uploading')
)
def add_comment(client: Client, post_id: UUID, content: str | None = None, attachment_ids: list[UUID] = []):
    return client.request('post', f'posts/{post_id}/comments', {'content': content or '', "attachmentIds": list(map(str, attachment_ids))})


@api_wrapper(
    ValidationError(),
    NotFoundError('Comment'),
    NotFoundError('User', res_check=lambda res: res.status_code == 500 and 'Failed query' in res.text),
    BannedWordError('Reply'),
    ForbiddenError('reply - some files not owned'),
    RequiresSubscriptionError('Video uploading')
)
def add_reply_comment(client: Client, comment_id: UUID, author_id: UUID, content: str | None = None, attachment_ids: list[UUID] = []):
    return client.request(
        'post', f'comments/{comment_id}/replies', {'content': content or '', 'replyToUserId': str(author_id), "attachmentIds": list(map(str, attachment_ids))}
    )


@api_wrapper(ValidationError(), NotFoundError('Post'))
def get_comments(client: Client, post_id: UUID, cursor: int = 0, limit: int = 20, sort: str = 'popular'):
    return client.request('get', f'posts/{post_id}/comments', {'limit': limit, 'sort': sort, 'cursor': cursor})


@api_wrapper(NotFoundError('Comment'))
def like_comment(client: Client, id: UUID):
    return client.request('post', f'comments/{id}/like')


@api_wrapper(NotFoundError('Comment'))
def unlike_comment(client: Client, id: UUID):
    return client.request('delete', f'comments/{id}/like')


@api_wrapper(NotFoundError('Comment'), AlreadyDeletedError('Comment'))
def delete_comment(client: Client, id: UUID):
    return client.request('delete', f'comments/{id}')


@api_wrapper(ValidationError(), NotFoundError('Comment'))
def get_replies(client: Client, id: UUID, page: int = 1, limit: int = 50):
    return client.request('get', f'comments/{id}/replies', {'page': page, 'limit': limit})


@api_wrapper(ValidationError(), NotFoundError('Comment'), ForbiddenError('edit comment'))
def edit_comment(client: Client, id: UUID, content: str):
    return client.request('patch', f'comments/{id}', {'content': content})
