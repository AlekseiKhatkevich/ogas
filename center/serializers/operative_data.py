import datetime
from typing import Annotated

import ulid
from pydantic import BaseModel, Field, field_serializer

__all__ = (
    'OperativeDataIn',
)

from pydantic_core.core_schema import SerializationInfo


class OperativeDataIn(BaseModel):
    product_id: Annotated[
        ulid.ULID,
        Field(description='ID продукта.'),
    ]
    diff: Annotated[
        float,
        Field(description='Изменение кол-ва продукта.'),
    ]
    change_datetime: Annotated[
        datetime.datetime,
        Field(description='Время наступления события.'),
    ]
    organization_id: Annotated[
        ulid.ULID | None,
        Field(description='ID организации.'),
    ] = None

    @field_serializer('organization_id')
    def add_organization_id(self, v: ulid.ULID | None, info: SerializationInfo) -> ulid.ULID | None:
        return context.get('organization_id') if (context := info.context) else v
