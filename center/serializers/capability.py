from typing import Annotated

import ulid
from pydantic import BaseModel, Field, NonNegativeInt

from center.enums import Period

__all__ = (
    'CapabilityIn',
)


class CapabilityIn(BaseModel):
    organization_id: Annotated[ulid.ULID, Field(description='ID компании передающей производительность.')]
    product_id: Annotated[ulid.ULID, Field(description='ID продукта.')]
    period: Annotated[Period, Field(description='Период производительности.')]
    value: Annotated[NonNegativeInt | None, Field(description='Значение производительности')] = None
