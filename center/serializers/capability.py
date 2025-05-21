from typing import Annotated

import ulid
from pydantic import BaseModel, Field, NonNegativeInt

from center.enums import Period

__all__ = (
    'CapabilityIn',
)


class CapabilityIn(BaseModel):
    """
    Модель для сериализации входящих данный от компании по производительности в единицу времени.
    """
    organization_name: Annotated[
        str,
        Field(description='Имя компании передающей производительность.'),
    ]
    product_id: Annotated[
        ulid.ULID,
        Field(description='ID продукта.'),
    ]
    period: Annotated[
        Period,
        Field(description='Период производительности.'),
    ]
    value: Annotated[
        NonNegativeInt | None,
        Field(description='Значение производительности.'),
    ] = None
