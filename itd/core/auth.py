from typing import TYPE_CHECKING

from itd.api.auth import sign_in
from itd.core.captcha import get_turnstile
from itd.core.logger import RICH_AVAILABLE, get_logger, iprint, rich_input
from itd.core.profile import Profile
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


def interactive_auth(client: 'Client') -> Profile:
    profile: Profile = client._profile or Profile()
    if profile._file is None:
        l.debug('create new profile')

    if profile.creds_valid or profile.refresh_valid or profile.access_valid:
        # if not profile.access_valid:
        #     profile.access = None
        # if not profile.refresh_valid:
        #     profile.refresh = None
        # if not profile.creds_valid:
        #     profile.email = None
        #     profile.password = None

        return profile
    client._credtest = True

    if not profile.refresh_valid and profile.refresh:
        l.warning('session file refresh token is not valid')

    if not profile.creds_valid and profile.access:
        l.warning('session file credentials is not valid')

    iprint(l, f'session file data: access={shorten_token(profile.access)} refresh={shorten_token(profile.refresh)} email={profile.email}')
    iprint(l, 'select auth option:')
    iprint(l, '[1] Login using credentials')
    iprint(l, '[2] Login via QR code')
    iprint(l, '[3] Manually auth using refresh token')
    iprint(l, '[4] Manually auth using access token')
    iprint(l, '[5] Quit')

    while True:
        option = rich_input('option', 'magenta')

        if option == '1':
            profile.email = rich_input('email', 'green')
            profile.password = rich_input('password', 'green', password=True)
            profile.creds_valid = True
            client._profile = profile
            client._set_from_profile()

            def _sign_in(turnstile):
                try:
                    res = sign_in(client, profile.email, profile.password, 'turnstileToken', turnstile)
                except CaptchaFailedError:
                    l.error('captcha verify failed. Please fill issue at https://github.com/itd-sdk/itd-sdk/issues/new')
                except InvalidCredentialsError:
                    l.error('invalid email or password')
                except EmailDomainNotAllowedError:
                    l.error('email domain not allowed')
                except InvalidEmailError:
                    l.error('invalid email format')
                else:
                    profile.set_refresh(res.cookies['refresh_token'], set_expire=True)
                    profile.set_access(res.json()['accessToken'])
                    profile.creds_valid = True
                    return True

            if RICH_AVAILABLE:
                with Status('Solving captcha..') as status:
                    turnstile = get_turnstile(client, status=status)
                    status.update('Verifying..')
                    if _sign_in(turnstile):
                        iprint(l, 'accepted')
                        return profile
            else:
                iprint(l, 'solving captcha..')
                if _sign_in(get_turnstile(client)):
                    iprint(l, 'accepted')
                    return profile

        elif option == '2':
            if auth_qr(client):
                return client._profile

        elif option == '3':
            profile.set_refresh(rich_input('refresh token', 'cyan', password=True))
            client._profile = profile
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
                        return profile
            else:
                if _verify():
                    iprint(l, 'accepted')
                    return profile

        elif option == '4':
            l.info('note: authorization will work only for ~15min')
            profile.set_access(rich_input('access token', 'cyan'))
            client._profile = profile
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
                        return profile
            else:
                if _verify():
                    iprint(l, 'accepted')
                    return profile

        elif option in ('5', 'q', 'quit'):
            quit()

        else:
            l.error('unknown option')
