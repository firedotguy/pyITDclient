from __future__ import annotations

from typing import TYPE_CHECKING

# moved from posts.py due to circular import
from uuid import UUID

from itd.base import api_wrapper, rate_limit
from itd.exceptions import NotFoundError, NotMultipleChoiceError, OptionsNotBelongError

if TYPE_CHECKING:
    from itd.client import Client


@rate_limit()
@api_wrapper(NotFoundError('Post'), NotFoundError('Poll', 'Опрос не найден'), OptionsNotBelongError(), NotMultipleChoiceError())
def vote(client: Client, id: UUID, options: list[UUID]):
    return client.request('post', f'posts/{id}/poll/vote', {'optionIds': [str(option) for option in options]})
