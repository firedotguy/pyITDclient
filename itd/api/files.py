from __future__ import annotations

from _io import BufferedReader
from typing import TYPE_CHECKING
from uuid import UUID

from itd.base import api_wrapper, rate_limit
from itd.exceptions import InvalidFileTypeError, ModerationFailedError, TooLargeError, UploadError

if TYPE_CHECKING:
    from itd.client import Client


@rate_limit(None, None, 1)
@api_wrapper(UploadError(), ModerationFailedError(), InvalidFileTypeError(), TooLargeError('File', 413))
def upload_file(client: Client, name: str, data: BufferedReader | bytes):
    return client.request('post', 'files/upload', files={'file': (name, data)})


@rate_limit()
@api_wrapper()
def delete_file(client: Client, id: UUID):
    return client.request('delete', f'files/{id}')
