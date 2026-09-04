from getpass import getpass
from typing import TYPE_CHECKING

from itd.core.captcha import get_turnstile
from itd.core.default import is_logging_setupped
from itd.core.logger import get_logger
from itd.core.profile import Profile
from itd.core.utils import shorten_token
from itd.enums import AuthLevel
from itd.exceptions import (
    AccessTokenExpiredError,
    CaptchaFailedError,
    EmailDomainNotAllowed,
    InvalidAccessTokenError,
    InvalidCredentials,
    JWTAlgorithmUnsupportedError,
    SessionExpiredError,
    SessionNotFoundError,
    SessionRevokedError
)

if TYPE_CHECKING:
    from itd.core.client import Client

try:
    from rich.prompt import Prompt
    from rich.status import Status

    RICH_SUPPORTED = True
except ImportError:
    RICH_SUPPORTED = False

l = get_logger('auth')


def _input(prompt: str, color: str, password: bool = False):
    if RICH_SUPPORTED:
        return Prompt.ask(f'[{color}]{prompt}[/]', password=password)
    else:
        return (getpass if password else input)(f'{prompt}: ')


def _cred_login(client: 'Client', profile: Profile):
    eprint = l.error if is_logging_setupped() else print

    def _sign_in(field: str, turnstile: str):
        try:
            client.login(turnstile)
        except CaptchaFailedError:
            eprint('Captcha verify failed. Please fill issue at https://github.com/itd-sdk/itd-sdk/issues/new')
        except InvalidCredentials:
            eprint('Invalid email or password')
        except EmailDomainNotAllowed:
            eprint('Email domain not allowed')
        else:
            return True

    if RICH_SUPPORTED:
        with Status('Solving captcha..') as status:
            field, turnstile = get_turnstile(client)
            status.update('Verifying..')
            if _sign_in(field, turnstile):
                return profile
    else:
        if _sign_in(*get_turnstile(client)):
            return profile


def auth(client: 'Client') -> Profile:
    profile: Profile = client._profile

    if profile.creds_valid or profile.refresh_valid or profile.access_valid:
        # if not profile.access_valid:
        #     profile.access = None
        # if not profile.refresh_valid:
        #     profile.refresh = None
        # if not profile.creds_valid:
        #     profile.email = None
        #     profile.password = None

        return profile

    iprint = l.info if is_logging_setupped() else print
    wprint = l.warning if is_logging_setupped() else print
    eprint = l.error if is_logging_setupped() else print

    if not profile.refresh_valid and profile.refresh:
        wprint('Session file refresh token is not valid')

    if not profile.creds_valid and profile.access:
        wprint('Session file credentials is not valid')

    iprint(f'Session file data: access={shorten_token(profile.access)} refresh={shorten_token(profile.refresh)} email={profile.email}')
    iprint('Select auth option:')
    iprint('[1] Login using credentials')
    iprint('[2] Login via QR code')
    iprint('[3] Manually auth using refresh token')
    iprint('[4] Manually auth using access token')
    iprint('[5] Quit')

    while True:
        option = _input('option', 'magenta')

        if option == '1':
            profile.email = _input('email', 'green')
            profile.password = _input('password', 'green', password=True)
            if _profile := _cred_login(client, profile):
                iprint('accepted')
                return _profile

        elif option == '2':
            wprint('QRcode currently is not supported')

        elif option == '3':
            profile.refresh = _input('refresh token', 'cyan', password=True)
            client._profile = profile

            def _verify():
                client.auth_level = AuthLevel.REFRESH
                try:
                    profile.access = client.refresh_auth()
                except SessionExpiredError:
                    eprint('refresh token expired')
                except SessionNotFoundError:
                    eprint('invalid refresh token')
                except SessionRevokedError:
                    eprint('refresh token revoked')
                else:
                    profile.refresh_valid = True
                    profile.set_refresh_expire()
                    profile.access_valid = True
                    return True

            if RICH_SUPPORTED:
                with Status('Verifying..'):
                    if _verify():
                        iprint('accepted')
                        return profile
            else:
                if _verify():
                    iprint('accepted')
                    return profile

        elif option == '4':
            wprint('note: authorization will work only for ~15min')
            profile.access = _input('access token', 'yellow')

            def _verify():
                client.auth_level = AuthLevel.ACCESS
                try:
                    client.user.refresh()
                except AccessTokenExpiredError:
                    eprint('access token expired')
                except InvalidAccessTokenError:
                    eprint('invalid access token')
                except JWTAlgorithmUnsupportedError:
                    eprint('jwt algorithm unsupported')
                else:
                    profile.access_valid = True
                    return True

            if RICH_SUPPORTED:
                with Status('Verifying..'):
                    if _verify():
                        iprint('accepted')
                        return profile
            else:
                if _verify():
                    iprint('accepted')
                    return profile

        elif option in ('5', 'q', 'quit'):
            quit()

        else:
            eprint('unknown option')
