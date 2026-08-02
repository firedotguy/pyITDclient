"""Склейка моделей SDK с pydantic: моделям не нужен ручной класс-валидатор"""

from __future__ import annotations

from datetime import datetime
from functools import cache
from typing import TYPE_CHECKING, Annotated, Any

from pydantic import BaseModel, BeforeValidator, GetCoreSchemaHandler
from pydantic_core import CoreSchema
from pydantic_core.core_schema import with_info_plain_validator_function

from itd.core.utils import parse_datetime

if TYPE_CHECKING:
    from itd.core.base import ITDBaseModel

ITDDatetime = Annotated[datetime, BeforeValidator(parse_datetime)]  # дата в формате апи


@cache
def validator_for(cls: type) -> type[BaseModel]:
    """Собрать класс-валидатор для модели: один на класс, при первой валидации

    Args:
        cls (type): Модель

    Returns:
        type[BaseModel]: pydantic модель с теми же полями
    """
    # __module__ нужен, чтобы pydantic резолвил forward refs в аннотациях модели
    return type(f'_{cls.__name__}Validate', (BaseModel, cls), {'__module__': cls.__module__})


def model_core_schema(cls: type[ITDBaseModel], source: type, handler: GetCoreSchemaHandler) -> CoreSchema:
    """Схема модели для pydantic

    Как класс-валидатор - обычная pydantic модель, как тип поля - собирается из dict через from_dict
    (с контекстом родителя, поэтому вложенным моделям не нужны свои валидаторы)
    """
    if issubclass(source, BaseModel):
        return handler(source)

    def validate(data: Any, info):
        if isinstance(data, source):
            return data
        return source.from_dict(data, context=dict(info.context or {}))

    return with_info_plain_validator_function(validate)
