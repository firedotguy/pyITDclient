from typing import TYPE_CHECKING

# from itd.api.auth import get_captcha_provider
from itd.core.captcha import cloudflare, itd  # required to they fill "providers" value # noqa
from itd.core.captcha.base import providers

if TYPE_CHECKING:
    from itd.core.client import Client


def get_turnstile(client: 'Client') -> tuple[str, str]:
    provider_data = {'provider': 'cloudflare', 'token': 'turnstileToken'}  # get_captcha_provider(client)
    if provider_data['provider'] not in providers:
        raise RuntimeError(f'Unknown provider: {provider_data["provider"]}')

    provider = providers[provider_data['provider']]()
    provider.launch()
    turnstile = provider.solve()
    provider.close()

    return provider_data.get('token', 'token'), turnstile
