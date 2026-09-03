from __future__ import annotations

from io import BufferedReader
from typing import TYPE_CHECKING
from uuid import UUID

from itd.core.request import Payload, endpoint
from itd.exceptions import InvalidFileTypeError, ModerationFailedError, TooLargeError, UploadError

if TYPE_CHECKING:
    from itd.core.client import Client


@endpoint('post', 'files/upload', UploadError(), ModerationFailedError(), InvalidFileTypeError(), TooLargeError('File', 413))
def upload_file(client: Client, name: str, data: BufferedReader | bytes):
    return Payload(files={'file': (name, data)})


@endpoint('delete', 'files/{id}')
def delete_file(client: Client, id: UUID): ...
