from __future__ import annotations

from typing import TYPE_CHECKING

from itd.request import endpoint

if TYPE_CHECKING:
    from itd.client import Client


# {"success":true,"request":{"id":"fc54e54f-8586-4d8c-809e-df93161f99da","userId":"9096a85b-c319-483e-8940-6921be427ad0","videoUrl":"https://943701f000610900cbe86b72234e451d.bckt.ru/videos/354f28a6-9ac7-48a6-879a-a454062b1d6b.mp4","status":"pending","rejectionReason":null,"reviewedBy":null,"reviewedAt":null,"createdAt":"2026-01-30T12:58:14.228Z","updatedAt":"2026-01-30T12:58:14.228Z"}}
@endpoint('post', 'verification/submit')
def verify(client: Client, file_url: str):
    return {'videoUrl': file_url}


@endpoint('get', 'verification/status')
def get_verification_status(client: Client): ...
