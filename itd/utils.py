from datetime import datetime
from json import dumps, loads
from sys import version
from typing import TYPE_CHECKING
from uuid import UUID

import pyromark
from lxml import html
from platformdirs import user_data_path
from telegramify_markdown import convert, converter

from itd._credfile import Credfile
from itd.enums import AttachType, SpanType
from itd.file import File, PostAttach
from itd.span import Span

if TYPE_CHECKING:
    from itd.client import Config

converter.STANDARD_OPTIONS = pyromark.Options.ENABLE_STRIKETHROUGH  # ty: ignore[invalid-assignment]


def get_sdk_user_agent():
    from itd import __version__  # i fucking hate circular imports this is sooo stupid

    return f'itd-sdk/{__version__} (Python/{version})'


def get_credfile(name: str) -> Credfile:
    file = user_data_path('itd_sdk', False, ensure_exists=True) / f'{name}.json'
    if not file.exists():
        model = Credfile(_file=file)
        file.write_text(dumps(model.model_dump(mode='json')))
    else:
        model = Credfile.model_validate(loads(file.read_text()))
        model._file = file
    return model


def shorten_token(value: str | None, max_len: int = 20):
    if value is None:
        return None

    if len(value) < max_len + 10:
        return value
    return value[: max_len // 2] + '...' + value[-(max_len // 2) :]


def to_uuid(value: str | UUID) -> UUID:
    if isinstance(value, str):
        return UUID(value)
    return value


def to_nullable_uuid(value: str | UUID | None) -> UUID | None:
    if value is None:
        return None

    return to_uuid(value)


def parse_datetime(value: str) -> datetime:
    v = value.replace('Z', '+00:00')
    try:
        return datetime.strptime(v + '00', '%Y-%m-%d %H:%M:%S.%f%z')
    except ValueError:
        return datetime.fromisoformat(v)


ATTACHMENTS = File | UUID | str | list[File | UUID | str]


def format_attachments(attachments: ATTACHMENTS = []) -> list[UUID]:
    if isinstance(attachments, list):
        formatted = []
        for attachment in attachments:
            if isinstance(attachment, File):
                formatted.append(attachment.id)
            else:
                formatted.append(to_uuid(attachment))  # ty: ignore[invalid-argument-type]
        return formatted
    else:
        if isinstance(attachments, File):
            return [attachments.id]
        return [to_uuid(attachments)]


def calc_view_duration(config: 'Config', text: str, attachments: list[PostAttach] = []):
    text_reading = round(len(text.split()) / config.view_read_speed * 60_000)
    image_reading = sum([config.view_images_speed for attachment in attachments if attachment.type == AttachType.IMAGE])
    # video_watching = sum([attachment.duration for attachment in attachments if attachment.type == AttachType.VIDEO]) # TODO
    return max(config.dwell_min_duration, min(config.dwell_max_duration, text_reading + image_reading))


TAG_MAP = {
    'b': SpanType.BOLD,
    'i': SpanType.ITALIC,
    's': SpanType.STRIKE,
    'u': SpanType.UNDERLINE,
    'code': SpanType.MONOSPACE,
    'spoiler': SpanType.SPOILER,
    'q': SpanType.QUOTE,
    'a': SpanType.LINK
}


def parse_html(text: str) -> tuple[str, list[Span]]:
    """Спарсить HTML

    Поддерживаемые теги:
    - <b>, <i>, <s>, <u>, <code>, <spoiler>, <q>, <a href="url">text</a>, <a>url</a>

    Args:
        text: HTML-строка для парсинга

    Returns:
        str: чистая строка
        list[Span]: список спанов
    """
    if not text:
        return text, []

    root = html.document_fromstring(text)

    # https://stackoverflow.com/questions/67434754/extract-inline-nodes-from-html-string-with-offset-and-length
    spans = []
    for element in root.xpath('.//*'):
        if element.tag not in TAG_MAP:
            continue

        length = len(element.text_content())
        offset = len(''.join(element.xpath('./preceding::text()')))
        spans.append(Span(length=length, offset=offset, type=TAG_MAP[element.tag], url=None if element.tag != 'a' else element.get('href', element.text)))
    return root.text_content(), spans


def parse_md(md: str) -> tuple[str, list[Span]]:
    """Спарсить markdown

    Поддерживаемые теги:
    - *, _, **, __, ~, ~~, `, ||, \\[text](url)

    Args:
        text: строка для парсинга

    Returns:
        str: чистая строка
        list[Span]: список спанов
    """
    text, spans = convert(md, latex_escape=False)
    return text, [Span.model_validate(span, from_attributes=True) for span in spans]
