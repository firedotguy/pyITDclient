from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from itd.enums import UNSET, AccessType, AuthLevel, Unset
from itd.exceptions import (
    AlreadyBlockedError,
    AlreadyDeletedError,
    AlreadyFollowingError,
    CantBlockYourselfError,
    CantFollowYourselfError,
    NotBlockedError,
    NotDeletedError,
    NotFoundError,
    RequiresVerificationError,
    TargetUserBannedError,
    TooLargeError,
    UserBlockedError,
    UsernameTakenError,
    ValidationError
)
from itd.core.request import endpoint

if TYPE_CHECKING:
    from itd.core.client import Client


@endpoint('get', 'users/{username_or_id}', NotFoundError('User'), TooLargeError('User'), NotFoundError('Profile'), TargetUserBannedError())
def get_user(client: Client, username_or_id: str | UUID): ...


@endpoint('put', 'users/me', ValidationError(), RequiresVerificationError('GIF banner uploading'), UsernameTakenError())
def update_profile(client: Client, bio: str | None = None, display_name: str | None = None, username: str | None = None, banner_id: UUID | Unset | None = None):
    data = {}
    if bio is not None:
        data['bio'] = bio
    if display_name:
        data['displayName'] = display_name
    if username:
        data['username'] = username
    if banner_id is not None:
        data['bannerId'] = str(banner_id) if banner_id != UNSET else None
    return data


@endpoint('get', 'profile', level=AuthLevel.NO)
def get_profile(client: Client): ...


@endpoint('get', 'users/me/privacy')
def get_privacy(client: Client): ...


@endpoint('put', 'users/me/privacy', ValidationError())
def update_privacy(
    client: Client,
    is_private: bool | None = None,
    wall_access: AccessType | None = None,
    likes_visibility: AccessType | None = None,
    show_last_seen: bool | None = None
):
    data = {}
    if is_private is not None:
        data['isPrivate'] = is_private
    if wall_access:
        data['wallAccess'] = wall_access.value
    if likes_visibility:
        data['likesVisibility'] = likes_visibility.value
    if show_last_seen is not None:
        data['showLastSeen'] = show_last_seen
    return data


@endpoint(
    'post',
    'users/{username_or_id}/follow',
    NotFoundError('User'),
    AlreadyFollowingError(),
    TooLargeError('Username'),
    CantFollowYourselfError(),
    UserBlockedError(),
    TargetUserBannedError()
)
def follow(client: Client, username_or_id: str | UUID): ...


@endpoint('delete', 'users/{username_or_id}/follow', NotFoundError('User'), TooLargeError('Username'), TargetUserBannedError())
def unfollow(client: Client, username_or_id: str | UUID): ...


@endpoint('get', 'users/{username_or_id}/followers', NotFoundError('User'), ValidationError(), TooLargeError('Username'), TargetUserBannedError())
def get_followers(client: Client, username_or_id: str | UUID, page: int = 1, limit: int = 20):  # !! page not works if not me
    return {'page': page, 'limit': limit}


@endpoint('get', 'users/{username_or_id}/following', NotFoundError('User'), ValidationError(), TooLargeError('Username'), TargetUserBannedError())
def get_following(client: Client, username_or_id: str | UUID, page: int = 1, limit: int = 20):  # !! page not works if not me
    return {'page': page, 'limit': limit}


@endpoint('delete', 'users/me', AlreadyDeletedError('Account'))
def delete_account(client: Client): ...


@endpoint('post', 'users/me/restore', NotDeletedError('Account'))
def restore_account(client: Client): ...


@endpoint(
    'post',
    'users/{username_or_id}/block',
    NotFoundError('User'),
    TooLargeError('Username'),
    AlreadyBlockedError(),
    CantBlockYourselfError(),
    TargetUserBannedError()
)
def block(client: Client, username_or_id: str | UUID): ...


@endpoint('delete', 'users/{username_or_id}/block', NotFoundError('User'), TooLargeError('Username'), NotBlockedError(), TargetUserBannedError())
def unblock(client: Client, username_or_id: str | UUID): ...


@endpoint('get', 'users/me/blocked')
def get_blocked(client: Client, page: int = 1, limit: int = 20):
    return {'limit': limit, 'page': page}


@endpoint('post', 'users/follow-status')
def get_follow_status(client: Client, user_ids: list[UUID]):
    return {'userIds': list(map(str, user_ids))}


@endpoint('get', 'users/search')
def search_users(client: Client, query: str, limit: int = 10):
    return {'q': query, 'limit': limit}
