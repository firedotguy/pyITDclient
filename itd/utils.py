from uuid import UUID
from html.parser import HTMLParser
from datetime import datetime
import re
from sys import version
from typing import TYPE_CHECKING

from telegramify_markdown import convert, converter
import pyromark
from lxml import html

from itd.span import Span
from itd.file import PostAttach, File
from itd.enums import SpanType, AttachType
if TYPE_CHECKING:
    from itd.client import Config

converter.STANDARD_OPTIONS = pyromark.Options.ENABLE_STRIKETHROUGH

def get_sdk_user_agent():
    from itd import __version__ # i fucking hate circular imports this is sooo stupid
    return f'itd-sdk/{__version__} (Python/{version})'


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
                formatted.append(to_uuid(attachment))
        return formatted
    else:
        if isinstance(attachments, File):
            return [attachments.id]
        return [to_uuid(attachments)]


def calc_view_duration(config: 'Config', text: str, attachments: list[PostAttach] = []):
    text_reading = round(len(text.split()) / config.view_read_speed * 60_000)
    image_reading = sum([config.view_images_speed for attachment in attachments if attachment.type == AttachType.IMAGE])
    # video_watching = sum([attachment.duration for attachment in attachments if attachment.type == AttachType.VIDEO]) # TODO
    return text_reading + image_reading


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
    """
    Парсит HTML-текст, извлекает чистый текст и spans с форматированием.

    Поддерживаемые теги:
    - <b>, <i>, <s>, <u>, <code>, <spoiler>, <q>
    - <a href="url">text</a> или <а>url</а> (ссылки)

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
        spans.append(Span(length=length, offset=offset, type=TAG_MAP[element.tag], url=element.get('href')))
    return root.text_content(), spans


def parse_md(md: str) -> tuple[str, list[Span]]:
    text, spans = convert(md, latex_escape=False)
    return text, [Span.model_validate(span, from_attributes=True) for span in spans]
