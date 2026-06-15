from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from itd.client import Client
from itd.base import api_wrapper
from itd.enums import AuthLevel
from itd.exceptions import ValidationError


@api_wrapper(ValidationError())
def search(client: Client, query: str, user_limit: int = 5, hashtag_limit: int = 5):
    return client.request('get', 'search', {'userLimit': user_limit, 'hashtagLimit': hashtag_limit, 'q': query}, level=AuthLevel.NO)
