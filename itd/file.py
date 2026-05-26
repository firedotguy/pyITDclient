from __future__ import annotations
from typing import TYPE_CHECKING
from uuid import UUID
from os.path import basename
from _io import BufferedReader
from pathlib import Path

from pydantic import BaseModel, Field
from requests import get

from itd.base import ITDBaseModel
from itd.enums import AttachType
from itd.api.files import upload_file, delete_file
if TYPE_CHECKING:
    from itd.client import Client
    from itd.post import Post

class File(ITDBaseModel):
    _refreshable = False
    _validator = lambda _: _FileValidate

    id: UUID
    url: str
    filename: str
    mime_type: str = Field(alias='mimeType')
    size: int
    # created_at: datetime | None = Field(None, alias='createdAt')

    def __init__(self, name: str, data: bytes | BufferedReader, client: Client | None = None):
        super().__init__(client)
        self.filename = name
        self.data = data
        self.refresh()

    @classmethod
    def from_path(cls, path: Path | str, *, client: Client | None = None):
        if isinstance(path, str):
            path = Path(path)
        return cls(path.name, path.read_bytes(), client)

    @classmethod
    def from_bytes(cls, data: bytes | BufferedReader, name: str | None = None, *, client: Client | None = None):
        if not name:
            try:
                from filetype import guess
            except ModuleNotFoundError:
                raise ImportError('filetype is required for File.from_bytes. Install by running "uv add itd-sdk[filetype]" (or "pip install itd-sdk[filetype]" if you are using pip)')

            kind = guess(data)
            name = f'file.{kind.extension}' if kind else 'file.0'

        return cls(name, data, client)

    def _refresh(self, *, client: Client):
        return upload_file(client, self.filename, self.data).json()

    def delete(self, *, client: Client | None = None) -> None:
        delete_file(client or self.client, self.id)

    def download(self, name: str | None = None) -> None:
        with open(name or self.filename, 'wb') as fl:
            fl.write(get(self.url, timeout=self.client.config.timeout_file).content)

    def __str__(self) -> str:
        return self.filename


class _FileValidate(BaseModel, File):
    pass



class PostAttach(ITDBaseModel):
    _validator = lambda _: _PostAttachValidate
    _post: Post

    id: UUID
    type: AttachType = AttachType.IMAGE
    url: str
    thumbnail_url: str | None = Field(None, alias='thumbnailUrl')
    width: int | None = None
    height: int | None = None

    def __init__(self, attach: dict, client: Client | None = None) -> None:
        super().__init__(client)

        for name, value in _PostAttachValidate.model_validate(attach).__dict__.items():
            setattr(self, name, value)

    def download(self, name: str) -> None:
        """Скачать вложение

        Args:
            name (str): Имя файла.
        """
        with open(name, 'wb') as fl:
            fl.write(get(self.url, timeout=self.client.config.timeout_file).content)

    def record_open(self, client: Client | None = None):
        """Записать событие открытия фото

        Args:
            client (Client | None, optional): Клиент. Defaults to None.
        """
        c = (client or self.client)
        assert c.dwell_tracker is not None, 'Enable dwell to record photo opens'
        assert self.type == AttachType.IMAGE, 'Recording photo open allowed only for images'
        c.dwell_tracker.record_photo_open(self._post.vs, self._post.source, self.id, self._post.attachments.index(self))

    def record_progress(self, duration: int, played: int | None = None, client: Client | None = None):
        """Записать событие просмотра видео

        Args:
            duration (int): Общая длина видео (в сожалению итд не отдает, пишите сами)
            played (int | None, optional): Сколько было просмотренно (мс). None - берется из duration. Defaults to None.
            client (Client | None, optional): Клиент. Defaults to None.
        """
        c = (client or self.client)
        assert c.dwell_tracker is not None, 'Enable dwell to record photo opens'
        assert self.type == AttachType.VIDEO, 'Recording video progress allowed only for videos'
        c.dwell_tracker.record_video_progress(self._post.vs, self._post.source, self.id, played or duration, duration)

    @property
    def extension(self):
        match self.type:
            case AttachType.IMAGE:
                return 'jpg'
            case AttachType.VIDEO:
                return 'mp4'
            case AttachType.AUDIO:
                return 'mp3'


class _PostAttachValidate(BaseModel, PostAttach):
    pass



class CommentAttach(PostAttach):
    _validator = lambda _: _CommentAttachValidate
    filename: str
    mime_type: str = Field(alias='mimeType')
    size: int
    duration: int | None = None
    order: int = 0

    def __init__(self, attach: dict, client: Client | None = None) -> None:
        super(PostAttach, self).__init__(client)

        for name, value in _CommentAttachValidate.model_validate(attach).__dict__.items():
            setattr(self, name, value)

    def record_open(self, client: Client | None = None):
        raise AttributeError

    def record_progress(self, duration: int, played: int | None = None, client: Client | None = None):
        raise AttributeError

    def download(self, name: str | None = None) -> None:
        """Скачать вложение

        Args:
            name (str | None, optional): Имя файла. None - имя, под которым был загружен этот файл. Defaults to None.
        """
        with open(name or self.filename, 'wb') as fl:
            fl.write(get(self.url, timeout=self.client.config.timeout_file).content)


class _CommentAttachValidate(BaseModel, CommentAttach):
    pass
