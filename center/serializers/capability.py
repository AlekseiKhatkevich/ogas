from typing import Annotated

import ulid
from pydantic import BaseModel, Field, NonNegativeInt

from center.enums import Period, Role
from utils.pydantic_utils import hashable_model

__all__ = (
    'CapabilityIn',
)


@hashable_model(fields=['organization_name', 'product_id', 'period'])
class CapabilityIn(BaseModel):
    """
    Модель для сериализации входящих данный от компании по производительности в единицу времени.
    """
    organization_name: Annotated[
        str | None,
        Field(description='Имя компании передающей производительность.'),
    ] = None
    product_id: Annotated[
        ulid.ULID,
        Field(description='ID продукта.'),
    ]
    period: Annotated[
        Period,
        Field(description='Период производительности.'),
    ]
    role: Annotated[
        Role,
        Field(description='Производитель или потребитель продукта.'),
    ]
    value: Annotated[
        NonNegativeInt | None,
        Field(description='Значение производительности.'),
    ] = None
