import contextlib
from typing import Annotated, Self

import ulid
from pydantic import BaseModel, Field, model_validator

__all__ = (
    'OrganizationStockIn',
)


class OrganizationStockIn(BaseModel):
    product_id: Annotated[
        ulid.ULID,
        Field(description='ID продукта.'),
    ]
    in_stock: Annotated[
        float,
        Field(description='Остаток продукта на организации.', ge=0)
    ]
    min_level: Annotated[
        float | None,
        Field(ge=0, description='Минимально допустимый остаток продукта.')
    ] = None
    max_level: Annotated[
        float | None,
        Field(gt=0, description='Максимальное кол-во продукта которе организация готова принять.')
    ]
    necessity: Annotated[
        float | None,
        Field(gt=0, description='Запрос продукта организацией.')
    ]

    @model_validator(mode='after')
    def check_passwords_match(self) -> Self:
        with contextlib.suppress(TypeError):
            if self.max_level <= self.min_level:
                raise ValueError('Max level should be greater then min level.')
        return self
