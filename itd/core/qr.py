from json import loads
from time import sleep
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, Field
from sseclient import SSEClient

from itd.api.auth import qr_claim, qr_start, qr_stream
from itd.core.logger import RICH_AVAILABLE, get_logger, iprint

if TYPE_CHECKING:
    from itd.core.client import Client

try:
    from qrcode import QRCode

    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False

try:
    from rich.status import Status
except ImportError:
    pass

l = get_logger('qr')


class ITDQRCode(BaseModel):
    id: UUID = Field(alias='qrId')
    payload: str
    claim_token: str = Field(alias='claimToken')
    expires_in: int = Field(90, alias='expiresIn')


def auth_qr(client: 'Client'):
    if not QR_AVAILABLE:
        l.error('qrcode library not installed; install via `uv add itd-sdk[qrcode]`')
        return False

    itd_qr = None

    def generate_qr():
        nonlocal itd_qr
        if status:
            status.update('Generating QR')
        itd_qr = ITDQRCode.model_validate(qr_start(client).json())
        l.debug('qr code: id=%s claim_token=%s', itd_qr.id, itd_qr.claim_token)
        qr = QRCode(border=0)
        qr.add_data(itd_qr.payload)
        iprint(l, 'scan QR code with mobile app:')
        qr.print_ascii(invert=False)
        if status:
            status.update('Waiting for scan')

    if RICH_AVAILABLE:
        status = Status('Waiting for scan')
        status.start()
    else:
        status = None
    stream = None

    try:
        for _ in range(5):
            generate_qr()
            assert itd_qr

            stream = qr_stream(client, qr_id=itd_qr.id, claim_token=itd_qr.claim_token)
            l.info('start stream')
            for event in SSEClient(stream).events():
                res = loads(event.data)
                l.debug('qr code status: %s', res['status'])

                if res['status'] == 'approved':
                    iprint(l, 'qr code approved')
                    claim_res = qr_claim(client, qr_id=itd_qr.id, claim_token=itd_qr.claim_token)
                    client._profile.set_refresh(claim_res.cookies['refresh_token'])
                    client._profile.set_access(claim_res.json()['accessToken'])
                    stream.close()
                    return True

                elif res['status'] == 'rejected':
                    l.error('qr code rejected')
                    generate_qr()
                    stream.close()
                    break

                elif res['status'] == 'scanned':
                    iprint(l, 'qr code scanned')
                    if status:
                        status.update('Waiting for accept')

                elif res['status'] == 'pending':
                    iprint(l, 'qr code pending')

                # elif res['status'] == 'captcha_required':
                #     iprint(l, 'captcha required')
                #     if status:
                #         status.update('Solving captcha')
                #     turnstile = get_turnstile(client)

            l.info('stop stream')
            sleep(5)

        l.error('all retries to auth qr exceeded')
        return False
    finally:
        if status:
            status.stop()
        if stream:
            stream.close()
