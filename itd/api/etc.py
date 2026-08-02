from __future__ import annotations

from typing import TYPE_CHECKING

from itd.core.request import endpoint

if TYPE_CHECKING:
    from itd.core.client import Client


@endpoint('get', 'users/stats/top-clans')
def get_top_clans(client: Client): ...


@endpoint('get', 'users/suggestions/who-to-follow')
def get_who_to_follow(client: Client): ...
