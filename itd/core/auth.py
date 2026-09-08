from os import getenv
from typing import TYPE_CHECKING

from itd.api.auth import sign_in
from itd.core.captcha import get_turnstile
from itd.core.logger import RICH_AVAILABLE, get_logger, iprint, rich_input
from itd.core.qr import auth_qr
from itd.core.utils import shorten_token
from itd.exceptions import (
    AccessTokenExpiredError,
    CaptchaFailedError,
    EmailDomainNotAllowedError,
    InvalidAccessTokenError,
    InvalidCredentialsError,
    InvalidEmailError,
    JWTAlgorithmUnsupportedError,
    SessionExpiredError,
    SessionNotFoundError,
    SessionRevokedError
)

if TYPE_CHECKING:
    from itd.core.client import Client

if RICH_AVAILABLE:
    from rich.status import Status

l = get_logger('auth')


def _auth_login(client: 'Client', email: str, password: str):
    client._profile.email = email
    client._profile.password = password
    client._profile.creds_valid = True
    client._set_from_profile()

    def _sign_in(turnstile):
        try:
            res = sign_in(client, client._profile.email, client._profile.password, 'turnstileToken', turnstile)
        except CaptchaFailedError:
            l.error('captcha verify failed. Please fill issue at https://github.com/itd-sdk/itd-sdk/issues/new')
        except InvalidCredentialsError:
            l.error('invalid email or password')
        except EmailDomainNotAllowedError:
            l.error('email domain not allowed')
        except InvalidEmailError:
            l.error('invalid email format')
        else:
            client._profile.set_refresh(res.cookies['refresh_token'], set_expire=True)
            client._profile.set_access(res.json()['accessToken'])
            client._profile.creds_valid = True
            return True

    if RICH_AVAILABLE:
        with Status('Solving captcha..') as status:
            turnstile = get_turnstile(client, status=status)
            status.update('Verifying..')
            if _sign_in(turnstile):
                iprint(l, 'accepted')
                return True
    else:
        iprint(l, 'solving captcha..')
        if _sign_in(get_turnstile(client)):
            iprint(l, 'accepted')
            return True

    client._profile.creds_valid = False


def _auth_refresh(client: 'Client', refresh: str):
    client._profile.set_refresh(refresh, set_expire=True)
    client._set_from_profile()

    def _verify():
        try:
            client.refresh_auth()
        except SessionExpiredError:
            l.error('refresh token expired')
        except SessionNotFoundError:
            l.error('invalid refresh token')
        except SessionRevokedError:
            l.error('refresh token revoked')
        else:
            return True

    if RICH_AVAILABLE:
        with Status('Verifying..'):
            if _verify():
                iprint(l, 'accepted')
                return True
    else:
        if _verify():
            iprint(l, 'accepted')
            return True

    client._profile.refresh_valid = False


def _auth_access(client: 'Client', access: str):
    client._profile.set_access(access)
    client._set_from_profile()

    def _verify():
        try:
            client.user.refresh()
        except AccessTokenExpiredError:
            l.error('access token expired')
        except InvalidAccessTokenError:
            l.error('invalid access token')
        except JWTAlgorithmUnsupportedError:
            l.error('jwt algorithm unsupported')
        else:
            return True

    if RICH_AVAILABLE:
        with Status('Verifying..'):
            if _verify():
                iprint(l, 'accepted')
                return True
    else:
        if _verify():
            iprint(l, 'accepted')
            return True

    client._profile.access_valid = False


def interactive_auth(client: 'Client') -> bool:
    if client._profile._file is None:
        l.debug('create new profile')

    if client._profile.creds_valid or client._profile.refresh_valid or client._profile.access_valid:
        # if not client._profile.access_valid:
        #     client._profile.access = None
        # if not client._profile.refresh_valid:
        #     client._profile.refresh = None
        # if not client._profile.creds_valid:
        #     client._profile.email = None
        #     client._profile.password = None

        return True
    client._credtest = True

    if getenv('ITD_AUTH_METHOD'):
        match getenv('ITD_AUTH_METHOD'):
            case 'login':
                if _auth_login(client, getenv('ITD_LOGIN', ''), getenv('ITD_PASSWORD', '')):
                    return True
            case 'refresh':
                if _auth_refresh(client, getenv('ITD_REFRESH', '')):
                    return True
            case 'access':
                if _auth_access(client, getenv('ITD_ACCESS', '')):
                    return True
            case _:
                l.error('unknown option')
                quit()

        l.error('auth failed')
        quit()

    if not client._profile.refresh_valid and client._profile.refresh:
        l.warning('session file refresh token is not valid')

    if not client._profile.creds_valid and client._profile.email:
        l.warning('session file credentials is not valid')

    iprint(
        l, f'session file data: access={shorten_token(client._profile.access)} refresh={shorten_token(client._profile.refresh)} email={client._profile.email}'
    )
    iprint(l, 'select auth option:')
    iprint(l, '[1] Login using credentials')
    iprint(l, '[2] Login via QR code')
    iprint(l, '[3] Manually auth using refresh token')
    iprint(l, '[4] Manually auth using access token')
    iprint(l, '[5] Quit')

    while True:
        option = rich_input('option', 'magenta')

        match option:
            case '1':
                if _auth_login(client, rich_input('email', 'green'), rich_input('password', 'green', password=True)):
                    return True
            case '2':
                if auth_qr(client):
                    return True
            case '3':
                if _auth_refresh(client, rich_input('refresh token', 'cyan', password=True)):
                    return True
            case '4':
                l.info('note: authorization will work only for ~15min')
                if _auth_access(client, rich_input('access token', 'cyan')):
                    return True
            case '5' | 'q' | 'quit':
                quit()
            case _:
                l.error('unknown option')
