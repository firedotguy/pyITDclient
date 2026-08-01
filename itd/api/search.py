from __future__ import annotations

from typing import TYPE_CHECKING

from itd.enums import AuthLevel
from itd.exceptions import ValidationError
from itd.request import endpoint

if TYPE_CHECKING:
    from itd.client import Client


@endpoint('get', 'search', ValidationError(), level=AuthLevel.NO)
def search(client: Client, query: str, user_limit: int = 5, hashtag_limit: int = 5):
    return {'userLimit': user_limit, 'hashtagLimit': hashtag_limit, 'q': query}
