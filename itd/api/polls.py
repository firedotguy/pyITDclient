# moved from posts.py due to circular import
from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from itd.exceptions import NotFoundError, NotMultipleChoiceError, OptionsNotBelongError
from itd.request import endpoint

if TYPE_CHECKING:
    from itd.client import Client


@endpoint('post', 'posts/{id}/poll/vote', NotFoundError('Post'), NotFoundError('Poll', 'Опрос не найден'), OptionsNotBelongError(), NotMultipleChoiceError())
def vote(client: Client, id: UUID, options: list[UUID]):
    return {'optionIds': [str(option) for option in options]}
