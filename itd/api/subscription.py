from __future__ import annotations

from typing import TYPE_CHECKING

from itd.base import api_wrapper
from itd.exceptions import NotFoundError

if TYPE_CHECKING:
    from itd.client import Client


@api_wrapper()
def get_subscription(client: Client):
    return client.request('get', 'v1/subscription')


@api_wrapper()
def pay_subscription(client: Client):
    return client.request('post', 'v1/subscription/pay')


@api_wrapper(NotFoundError('Subsciption', json_check=lambda json: json.get('error') == 'Активная подписка не найдена'))
def toggle_subscription_auto_renewal(client: Client, enabled: bool):
    return client.request('post', 'v1/subscription/auto-renewal', {'enabled': enabled})


@api_wrapper()
def bind_card(client: Client):
    return client.request('post', 'v1/subscription/bind-card')


@api_wrapper()
def get_payment_methods(client: Client):
    return client.request('get', 'v1/subscription/methods')


@api_wrapper()
def set_default_payment_method(client: Client, method: str):
    return client.request('post', f'/v1/subscription/methods/{method}/default')


@api_wrapper()
def delete_payment_method(client: Client, method: str):
    return client.request('delete', f'/v1/subscription/methods/{method}')
