from __future__ import annotations

from typing import TYPE_CHECKING

from itd.base import api_wrapper, rate_limit

if TYPE_CHECKING:
    from itd.client import Client


@rate_limit()
@api_wrapper()
def get_top_clans(client: Client):
    return client.request('get', 'users/stats/top-clans')


@rate_limit()
@api_wrapper()
def get_who_to_follow(client: Client):
    return client.request('get', 'users/suggestions/who-to-follow')
