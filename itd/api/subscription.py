from __future__ import annotations

from typing import TYPE_CHECKING

from itd.exceptions import NotFoundError
from itd.request import endpoint

if TYPE_CHECKING:
    from itd.client import Client


@endpoint('get', 'v1/subscription')
def get_subscription(client: Client): ...


@endpoint('post', 'v1/subscription/pay')
def pay_subscription(client: Client): ...


@endpoint('post', 'v1/subscription/auto-renewal', NotFoundError('Subsciption', json_check=lambda json: json.get('error') == 'Активная подписка не найдена'))
def toggle_subscription_auto_renewal(client: Client, enabled: bool):
    return {'enabled': enabled}


@endpoint('post', 'v1/subscription/bind-card')
def bind_card(client: Client): ...


@endpoint('get', 'v1/subscription/methods')
def get_payment_methods(client: Client): ...


@endpoint('post', '/v1/subscription/methods/{method}/default')
def set_default_payment_method(client: Client, method: str): ...


@endpoint('delete', '/v1/subscription/methods/{method}')
def delete_payment_method(client: Client, method: str): ...
