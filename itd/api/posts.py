from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from itd.base import api_wrapper
from itd.enums import PostsTab, UserPostSorting
from itd.exceptions import (
    AlreadyRepostedError,
    BannedWordError,
    CantRepostYourselfError,
    EditExpiredError,
    ForbiddenError,
    NotFoundError,
    NotPinnedError,
    RequiresSubscriptionError,
    ValidationError
)
from itd.poll import NewPoll

if TYPE_CHECKING:
    from itd.client import Client


@api_wrapper(
    NotFoundError('Wall recipient'),
    ForbiddenError('post - some files not owned'),
    RequiresSubscriptionError('Video uploading'),
    BannedWordError('Post'),
    ValidationError()
)
def create_post(
    client: Client,
    content: str | None = None,
    spans: list[dict] = [],
    wall_recipient_id: UUID | None = None,
    attachment_ids: list[UUID] = [],
    poll: NewPoll | None = None
):
    data: dict = {'content': content or ''}
    if spans:
        data['spans'] = spans
    if wall_recipient_id:
        data['wallRecipientId'] = str(wall_recipient_id)
    if attachment_ids:
        data['attachmentIds'] = list(map(str, attachment_ids))
    if poll:
        data['poll'] = poll.poll.model_dump(mode='json')

    return client.request('post', 'posts', data)


@api_wrapper(ValidationError())
def get_posts(client: Client, cursor: str | datetime | None = None, limit: int = 20, tab: PostsTab = PostsTab.POPULAR):
    data: dict = {'limit': limit, 'tab': tab.value}
    if cursor is not None:
        data['cursor'] = cursor
    return client.request('get', 'posts', data)


@api_wrapper(NotFoundError('Post'))
def get_post(client: Client, id: UUID):
    return client.request('get', f'posts/{id}')


@api_wrapper(NotFoundError('Post'), ForbiddenError('edit post'), EditExpiredError(), BannedWordError('Post'))
def edit_post(client: Client, id: UUID, content: str, spans: list[dict] = []):
    return client.request('put', f'posts/{id}', {'content': content, 'spans': spans})


@api_wrapper(NotFoundError('Post'), ForbiddenError('delete post'))
def delete_post(client: Client, id: UUID):
    return client.request('delete', f'posts/{id}')


@api_wrapper(NotFoundError('Post'), ForbiddenError('restore post'))
def restore_post(client: Client, id: UUID):
    return client.request('post', f'posts/{id}/restore')


@api_wrapper(NotFoundError('Post'), ForbiddenError('pin post'))
def pin_post(client: Client, id: UUID):
    return client.request('post', f'posts/{id}/pin')


@api_wrapper(NotPinnedError())
def unpin_post(client: Client, id: UUID):
    return client.request('delete', f'posts/{id}/pin')


@api_wrapper(NotFoundError('Post'), AlreadyRepostedError(), CantRepostYourselfError(), ValidationError(), BannedWordError('Post'))
def repost(client: Client, id: UUID, content: str | None = None):
    data = {}
    if content:
        data['content'] = content
    return client.request('post', f'posts/{id}/repost', data)


@api_wrapper(NotFoundError('Post'))
def view_post(client: Client, id: UUID):
    return client.request('post', f'posts/{id}/view')


@api_wrapper(ValidationError(), NotFoundError('User'))
def get_liked_posts(client: Client, username_or_id: str | UUID, cursor: datetime | None = None, limit: int = 20):
    return client.request('get', f'posts/user/{username_or_id}/liked', {'limit': limit, 'cursor': cursor})


@api_wrapper(ValidationError(), NotFoundError('User', res_check=lambda res: res.status_code == 404 and res.text == 'NOT_FOUND'))
def get_user_posts(
    client: Client,
    username_or_id: str | UUID,
    cursor: datetime | None = None,
    limit: int = 20,
    pinned_post_id: UUID | None = None,
    sort: UserPostSorting = UserPostSorting.NEW
):
    return client.request('get', f'posts/user/{username_or_id}', {'limit': limit, 'cursor': cursor, 'pinnedPostId': pinned_post_id, 'sort': sort.value})


@api_wrapper(NotFoundError('Post'))
def like_post(client: Client, id: UUID):
    return client.request('post', f'posts/{id}/like')


@api_wrapper(NotFoundError('Post'))
def unlike_post(client: Client, id: UUID):
    return client.request('delete', f'posts/{id}/like')


@api_wrapper(ValidationError())
def get_stats(client: Client, ids: list[UUID]):
    return client.request('post', 'posts/stats', {'ids': [str(id) for id in ids]})  # if not found, will return empty list
