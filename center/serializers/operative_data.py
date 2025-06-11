import datetime
from typing import Annotated

import ulid
from pydantic import BaseModel, Field

__all__ = (
    'OperativeDataIn',
)


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
