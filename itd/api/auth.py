from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from itd.core.request import endpoint
from itd.enums import AuthLevel
from itd.exceptions import (
    CaptchaFailedError,
    EmailDomainNotAllowedError,
    InvalidCredentialsError,
    InvalidEmailError,
    InvalidOldPasswordError,
    InvalidPasswordError,
    SamePasswordError,
    SessionExpiredError,
    SessionNotFoundError,
    SessionRevokedError
)

if TYPE_CHECKING:
    from itd.core.client import Client


@endpoint('post', 'v1/auth/refresh', SessionExpiredError(), SessionNotFoundError(), SessionRevokedError(), level=AuthLevel.REFRESH)
def refresh_token(client: Client): ...


@endpoint('post', 'v1/auth/change-password', InvalidPasswordError(), SamePasswordError(), InvalidOldPasswordError())
def change_password(client: Client, old: str, new: str):
    return {'newPassword': new, 'oldPassword': old}


@endpoint('post', 'v1/auth/logout', level=AuthLevel.REFRESH)
def logout(client: Client): ...


@endpoint('get', 'v1/auth/captcha/provider', level=AuthLevel.NO)
def get_captcha_provider(client: Client): ...


@endpoint('post', 'v1/auth/sign-in', InvalidCredentialsError(), CaptchaFailedError(), EmailDomainNotAllowedError(), InvalidEmailError(), level=AuthLevel.NO)
def sign_in(client: Client, email: str, password: str, token_field: str, token: str):  # token field: turnstileToken for клодфлер token for итд
    return {'email': email, 'password': password, token_field: token}


@endpoint('post', 'v1/auth/qr/start', level=AuthLevel.NO)
def qr_start(cleint: Client): ...


@endpoint('post', 'v1/auth/qr/claim', level=AuthLevel.NO)
def qr_claim(client: Client, qr_id: UUID, claim_token: str):
    return {'qrId': str(qr_id), 'claimToken': claim_token}
