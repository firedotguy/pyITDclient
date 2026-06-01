from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from itd.api.etc import get_who_to_follow
from itd.api.pins import get_pins, remove_pin
from itd.api.subscription import get_payment_methods, get_subscription, pay_subscription, toggle_subscription_auto_renewal
from itd.api.users import (
    block,
    delete_account,
    follow,
    get_blocked,
    get_followers,
    get_following,
    get_privacy,
    get_profile,
    get_user,
    restore_account,
    unblock,
    unfollow,
    update_privacy,
    update_profile
)
from itd.base import ITDBaseModel, ITDList
from itd.enums import AccessType, LoadStatus, ReportReason, ReportTargetType, Role, Unset
from itd.exceptions import AccountDeletedError, PinNotOwnedError
from itd.pin import Pin
from itd.poll import NewPoll
from itd.report import Report
from itd.span import Span
from itd.utils import ATTACHMENTS, parse_datetime, to_uuid

if TYPE_CHECKING:
    from itd.client import Client
    from itd.post import LikedPosts, Post, UserPosts


class ProfileUser(BaseModel):
    id: UUID
    username: str
    display_name: str = Field(alias='displayName')
    avatar: str
    verified: bool = False
    bio: str | None = None
    is_phone_verified: bool = Field(False, alias='isPhoneVerified')
    roles: list[Role] = [Role.USER]

    def __str__(self) -> str:
        return self.display_name


class Profile(ITDBaseModel):
    _validator = lambda _: _ProfileValidate
    _load_with_parent = False

    authenticated: bool = True
    user: ProfileUser | None = None
    banned: bool = False
    deleted: bool = False
    can_restore: bool = Field(True, alias='canRestore')
    message: str | None = None
    profile_required: bool = Field(False, alias='profileRequired')
    user_id: UUID | None = Field(None, alias='userId')
    roles: list[Role] | None = None

    def _refresh(self, *, client: Client):
        return get_profile(client).json()

    def __str__(self) -> str:
        if self.user:
            return str(self.user)
        return super().__str__()


class _ProfileValidate(BaseModel, Profile):
    pass


class Privacy(ITDBaseModel):
    _validator = lambda _: _PrivacyValidate
    _user: 'Me | None' = None
    _load_with_parent = False

    is_private: bool = Field(alias='isPrivate')
    wall_access: AccessType = Field(alias='wallAccess')
    likes_visibility: AccessType = Field(alias='likesVisibility')
    show_last_seen: bool = Field(alias='showLastSeen')

    def _refresh(self, *, client: Client):
        return get_privacy(client).json()

    def update(
        self,
        is_private: bool | None = None,
        wall_access: AccessType | None = None,
        likes_visibility: AccessType | None = None,
        show_last_seen: bool | None = None,
        client: Client | None = None
    ):
        data = update_privacy(client or self.client, is_private, wall_access, likes_visibility, show_last_seen).json()
        if 'isPrivate' in data:
            self.is_private = data['isPrivate']
        if 'wallAccess' in data:
            self.wall_access = AccessType(data['wallAccess'])
        if 'likesVisibility' in data:
            self.likes_visibility = AccessType(data['likesVisibility'])
        if 'showLastSeen' in data:
            self.show_last_seen = data['showLastSeen']

        if self._user:
            for field in ('wall_access', 'likes_visibility', 'is_private'):
                setattr(self._user, field, object.__getattribute__(self, field))

    def update_from_fields(self):  # you can update fields (like privacy.is_private = True), then exec this func to update
        self.update(self.is_private, self.wall_access, self.likes_visibility, self.show_last_seen)

    @classmethod
    def _from_user(cls, user: 'Me', client: Client | None = None):
        instance = cls(client)
        instance._user = user
        return instance

    if not TYPE_CHECKING:

        def __getattribute__(self, name: str):
            if name in ('is_private', 'wall_access', 'likes_visibility') and object.__getattribute__(self, '_user'):
                setattr(self, name, getattr(object.__getattribute__(self, '_user'), name))
            return super().__getattribute__(name)


class _PrivacyValidate(BaseModel, Privacy):
    pass


class Subscription(ITDBaseModel):
    _validator = lambda _: _SubscriptionValidate
    _payment_methods: list
    _refreshable = False

    active: bool = Field(False, alias='isActive')
    expires_at: datetime | None = Field(None, alias='expiresAt')
    auto_renewal: bool = Field(True, alias='autoRenewal')

    def __init__(self, data: dict, client: Client | None = None):
        super().__init__(client)

        validated = _SubscriptionValidate.model_validate(data)
        self._fields_from_data = validated.model_fields_set
        for name, value in validated.__dict__.items():
            setattr(self, name, value)

    def _refresh(self, *, client: Client):  # refreshes only is_active
        return get_subscription(client).json()

    def pay(self):
        return pay_subscription(self.client).json()['confirmationUrl']

    def set_auto_renewal(self, enabled: bool) -> bool:
        self.auto_renewal = toggle_subscription_auto_renewal(self.client, enabled).json()['autoRenewal']
        return self.auto_renewal

    def toggle_auto_renewal(self) -> bool:
        return self.set_auto_renewal(not self.auto_renewal)

    @property
    def payment_methods(self):
        if getattr(self, '_payment_methods', None) is None:
            self._payment_methods = get_payment_methods(self.client).json()['data']
        return self._payment_methods

    def __bool__(self):
        return self.active

    def __str__(self) -> str:
        return str(self.active)


class _SubscriptionValidate(BaseModel, Subscription):
    pass


class _UserBase(ITDBaseModel):
    _identifier: str | UUID

    id: UUID
    username: str
    display_name: str = Field(alias='displayName')
    avatar: str
    verified: bool = False
    pin: Pin | None = None
    banner: str | None = None
    bio: str | None = None

    def __init__(self, username_or_id: str | UUID, client: Client | None = None) -> None:
        self._identifier = username_or_id
        if isinstance(username_or_id, str) and username_or_id != 'me':
            self.username = username_or_id
        elif isinstance(username_or_id, UUID):
            self.id = username_or_id

        super().__init__(client)

    def __str__(self) -> str:
        return self.display_name

    def _refresh(self, *, client: Client):
        return get_user(client, self._identifier).json()

    @property
    def posts(self) -> UserPosts:
        if not hasattr(self, '_posts'):
            from itd.post import UserPosts

            self._posts = UserPosts(self, client=self.client)
        return self._posts

    @property
    def liked_posts(self) -> LikedPosts:
        if not hasattr(self, '_liked_posts'):
            from itd.post import LikedPosts

            self._liked_posts = LikedPosts(self, client=self.client)
        return self._liked_posts

    @property
    def url(self) -> str:
        return f'https://xn--d1ah4a.com/@{self.username}'

    @property
    def link(self) -> str:
        return self.url


class User(_UserBase):
    _validator = lambda _: _UserValidate
    _fields_from_data: set[str] = set()

    _followers: list[User] = []
    _following: list[User] = []

    is_following: bool = Field(False, alias='isFollowing')
    is_followed_by: bool = Field(False, alias='isFollowedBy')

    is_blocked_by: bool = Field(
        False, alias='isBlockedByThem'
    )  # not 100% true, server returns value only if isBlockedByThem is True and isBlockedByMe is False
    is_blocking: bool = Field(False, alias='isBlockedByMe')
    blocked_at: datetime | None = Field(None, alias='blockedAt')

    followers_count: int | None = Field(None, alias='followersCount')
    following_count: int | None = Field(None, alias='followingCount')
    posts_count: int | None = Field(None, alias='postsCount')

    wall_access: AccessType | None = Field(None, alias='wallAccess')  # none if blocked
    likes_visibility: AccessType | None = Field(None, alias='likesVisibility')  # none if blocked
    is_private: bool | None = Field(None, alias='isPrivate')  # none if following or blocked

    is_subscribed: bool = Field(False, alias='hasNuksta')
    last_seen: datetime | dict | None = Field(None, alias='lastSeen')  # none if hidden or blocked
    online: bool = False

    pinned_post_id: UUID | None = Field(None, alias='pinnedPostId')  # none if no or blocked

    created_at: datetime | None = Field(None, alias='createdAt')  # none if blocked

    @classmethod
    def by_id(cls, id: UUID | str) -> 'User':
        return cls(to_uuid(id))

    @classmethod
    def by_username(cls, username: str) -> 'User':
        return cls(username)

    @classmethod
    def by_u(cls, username: str) -> 'User':  # just abbr for username
        return User.by_username(username)

    @classmethod
    def me(cls, client: Client | None = None) -> 'Me':
        return Me(client)

    def for_client(self, client: Client) -> "User":
        return User(self._identifier, client=client)

    def complete_actions_for_wall_access(self, client: Client | None = None) -> bool:
        if client != self.client:
            user = User(self._identifier, client)
        else:
            user = self

        if user.wall_access == AccessType.NOBODY:
            return False
        if user.wall_access == AccessType.MUTUAL:
            if user.is_followed_by:
                if not user.is_following:
                    user.follow(client)
                return True
            return False
        if user.wall_access == AccessType.FOLLOWERS:
            if not user.is_following:
                user.follow(client)
        return True

    def complete_actions_for_likes_visibility(self, client: Client | None = None) -> bool:
        if client != self.client:
            user = User(self._identifier, client)
        else:
            user = self

        if user.likes_visibility == AccessType.NOBODY:
            return False
        if user.likes_visibility == AccessType.MUTUAL:
            if user.is_followed_by:
                if not user.is_following:
                    user.follow(client)
                return True
            return False
        if user.likes_visibility == AccessType.FOLLOWERS:
            if not user.is_following:
                user.follow(client)
        return True

    @property
    def can_post_on_wall(self) -> bool:
        if self.wall_access == AccessType.NOBODY:
            return False
        if self.wall_access == AccessType.MUTUAL:
            return self.is_following and self.is_followed_by
        if self.wall_access == AccessType.FOLLOWERS:
            return self.is_following
        return True

    @property
    def can_see_liked_posts(self) -> bool:
        if self.likes_visibility == AccessType.NOBODY:
            return False
        if self.likes_visibility == AccessType.MUTUAL:
            return self.is_following and self.is_followed_by
        if self.likes_visibility == AccessType.FOLLOWERS:
            return self.is_following
        return True

    def report(self, reason: ReportReason, description: str | None = None, client: Client | None = None) -> Report:
        return Report(self.id, ReportTargetType.USER, reason, description, client or self.client)

    def follow(self, client: Client | None = None) -> int:
        self.followers_count = follow(client or self.client, self._identifier).json()['followersCount']
        if (client or self.client) == self.client:
            self.is_following = True

        assert self.followers_count is not None
        return self.followers_count

    def unfollow(self, client: Client | None = None) -> int:
        self.followers_count = unfollow(client or self.client, self._identifier).json()['followersCount']
        if (client or self.client) == self.client:
            self.is_following = False

        assert self.followers_count is not None
        return self.followers_count

    def block(self, client: Client | None = None) -> None:
        block(client or self.client, self._identifier)
        if (client or self.client) == self.client:
            self.is_blocking = True

    def unblock(self, client: Client | None = None) -> None:
        unblock(client or self.client, self._identifier)
        if (client or self.client) == self.client:
            self.is_blocking = False

    def post(
        self, content: str | None = None, spans: list[Span] = [], attachments: ATTACHMENTS = [], poll: NewPoll | None = None, client: Client | None = None
    ) -> Post:
        from itd.post import Post  # stupid circular import

        return Post.new(content, spans, attachments, poll, self, client or self.client)

    @property
    def following(self) -> list[User]:
        if not self._following:
            self._following = [User.from_dict(user, client=self.client) for user in get_following(self.client, self._identifier).json()['data']['users']]
        return self._following

    @property
    def followers(self) -> list[User]:
        if not self._followers:
            self._followers = [User.from_dict(user, client=self.client) for user in get_followers(self.client, self._identifier).json()['data']['users']]
        return self._followers


class _UserValidate(BaseModel, User):
    @field_validator('pin', mode='plain')
    @classmethod
    def validate_pin(cls, pin: dict | None):
        if pin:
            return Pin(pin)


class Me(_UserBase):
    _validator = lambda _: _MeValidate

    wall_access: AccessType = Field(alias='wallAccess')
    likes_visibility: AccessType = Field(alias='likesVisibility')
    is_private: bool = Field(False, alias='isPrivate')
    is_phone_verified: bool = Field(alias='isPhoneVerified')
    subscription: Subscription

    followers_count: int = Field(alias='followersCount')
    following_count: int = Field(alias='followingCount')
    posts_count: int = Field(alias='postsCount')

    created_at: datetime = Field(alias='createdAt')

    def __init__(self, client: Client | None = None) -> None:
        super().__init__('me', client)

        self._blocked = Blocked()
        self._followers = Followers()
        self._following = Following()
        self._pins: list[Pin] = []
        self.privacy: Privacy = Privacy._from_user(self, self.client)
        self.profile: Profile = Profile(self.client)
        self.client._user = self

    def to_user(self) -> User:
        instance = User.__new__(User)
        ITDBaseModel.__init__(instance, self._client)
        for name in _UserValidate.model_fields:
            if hasattr(self, name):
                setattr(instance, name, getattr(self, name))
        instance._identifier = self.id
        instance.load_status = LoadStatus.PARTIALLY
        return instance

    def delete(self) -> datetime:  # should not use other client, because you can get Me only from current client
        return parse_datetime(delete_account(self.client).json()['restoreDeadline'])

    def restore(self) -> None:
        restore_account(self.client)

    def update_privacy(
        self,
        is_private: bool | None = None,
        wall_access: AccessType | None = None,
        likes_visibility: AccessType | None = None,
        show_last_seen: bool | None = None
    ):
        self.privacy.update(is_private, wall_access, likes_visibility, show_last_seen)

    def update(self, bio: str | None = None, display_name: str | None = None, username: str | None = None, banner_id: UUID | str | Unset | None = None):
        if isinstance(banner_id, str):
            banner_id = to_uuid(banner_id)
        update_profile(self.client, bio, display_name, username, banner_id)
        if bio:
            self.bio = bio
        if display_name:
            self.display_name = display_name
        if username:
            self.username = username

    def update_from_fields(self):
        update_profile(self.client, self.bio, self.display_name, self.username)

    def remove_pin(self) -> None:
        if (
            object.__getattribute__(self, 'pin') and self.pin
        ):  # can be a bit strange for first look, but this prevent loading (itdbasemodel catches) and add rule for type checker
            self.pin.remove()
        else:
            remove_pin(self.client)  # if pins not loaded just use straight call

    def set_pin(self, pin: Pin | str | None = None):
        if pin is None:
            if self.pins:
                self.pins[0].set()
            else:
                raise ValueError('No pins available')
        elif isinstance(pin, str):
            pins = [_pin for _pin in self.pins if _pin.slug == pin]
            if pins:
                pins[0].set()
            else:
                raise PinNotOwnedError(pin)
        else:
            if pin.slug in [p.slug for p in self.pins]:
                pin.set(self.client)  # can be not our pin, so set our client to ensure client is correct
            else:
                raise PinNotOwnedError(pin.slug)

    @property
    def blocked(self) -> 'Blocked':
        if not self._blocked:
            self._blocked._client = self.client
            self._blocked.load()
        return self._blocked

    @property
    def followers(self) -> 'Followers':
        if not self._followers:
            self._followers._user_id = self.id
            self._followers._client = self._client
            self._followers.load()
        return self._followers

    @property
    def following(self) -> 'Following':
        if not self._following:
            self._following._user_id = self.id
            self._following._client = self._client
            self._following.load()
        return self._following

    @property
    def pins(self) -> list[Pin]:
        if not self._pins:
            self._pins = [Pin(pin, self) for pin in get_pins(self.client).json()['data']['pins']]
        return self._pins

    def _refresh(self, *, client: Client):
        user = get_user(client, self._identifier).json()
        if user.get('isDeleted'):
            exc = AccountDeletedError()
            exc.can_restore = user.get('canRestore', True)
            exc.restore_deadline = parse_datetime(user['restoreDeadline']) if 'restoreDeadline' in user else None
            raise exc
        return user

    def _post_refresh(self):
        if self.pin:
            self.pin._user = self


class _MeValidate(BaseModel, Me):
    @field_validator('pin', mode='plain')
    @classmethod
    def validate_pin(cls, pin: dict | None) -> Pin | None:
        if pin:
            return Pin(pin)

    @field_validator('subscription', mode='plain')
    @classmethod
    def validate_subscription(cls, subscription: dict) -> Subscription:
        return Subscription(subscription)


class Followers(ITDList[User]):
    _load_with_parent = False
    _user_id: UUID
    cursor: int = 1

    def _fetch(self, client: Client, limit: int) -> dict:
        return get_followers(client, self._user_id, self.cursor).json()['data']

    @staticmethod
    def _get_has_more(data: dict) -> bool:
        return data['pagination']['hasMore']

    @staticmethod
    def _get_total(data: dict):
        return data['pagination']['total']

    @staticmethod
    def _get_objects(data: dict) -> list[dict]:
        return data['users']

    @staticmethod
    def _get_cursor(data: dict):
        return data['pagination']['page'] + 1

    def _to_models(self, objects: list, client: Client):
        return [User.from_dict(user, client=client) for user in objects]

    def __setattr__(self, name: str, value) -> None:
        if name == '_client':
            for user in self.copy():
                user._client = value
        super().__setattr__(name, value)


class Following(Followers):
    def _fetch(self, client: Client, limit: int) -> dict:
        return get_following(client, self._user_id, self.cursor).json()['data']


class Blocked(Followers):
    limit = 100

    def _fetch(self, client: Client, limit: int) -> dict:
        return get_blocked(client, self.cursor, limit).json()['data']


class WhoToFollow(ITDBaseModel, list[User]):
    _refreshable = False

    def __init__(self, client: Client | None = None) -> None:
        super().__init__(client)
        self.refresh()

    def refresh(self, *, client: Client | None = None):
        self.clear()
        self.extend([User.from_dict(user, client=client or self.client) for user in get_who_to_follow(self.client).json()['users']])
