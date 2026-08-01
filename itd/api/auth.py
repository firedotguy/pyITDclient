from __future__ import annotations

from typing import TYPE_CHECKING

from itd.enums import AuthLevel
from itd.exceptions import (
    CaptchaFailedError,
    EmailDomainNotAllowed,
    InvalidCredentials,
    InvalidOldPasswordError,
    InvalidPasswordError,
    SamePasswordError,
    SessionExpiredError,
    SessionNotFoundError,
    SessionRevokedError
)
from itd.request import endpoint

if TYPE_CHECKING:
    from itd.client import Client


@endpoint('post', 'v1/auth/refresh', SessionExpiredError(), SessionNotFoundError(), SessionRevokedError(), level=AuthLevel.REFRESH)
def refresh_token(client: Client): ...


@endpoint('post', 'v1/auth/change-password', InvalidPasswordError(), SamePasswordError(), InvalidOldPasswordError())
def change_password(client: Client, old: str, new: str):
    return {'newPassword': new, 'oldPassword': old}


@endpoint('post', 'v1/auth/logout', level=AuthLevel.REFRESH)
def logout(client: Client): ...


@endpoint('post', 'v1/auth/sign-in', InvalidCredentials(), CaptchaFailedError(), EmailDomainNotAllowed(), level=AuthLevel.NO)
def sign_in(client: Client, email: str, password: str, turnstile: str):
    return {'email': email, 'password': password, 'turnstileToken': turnstile}
