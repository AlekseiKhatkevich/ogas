import datetime
from typing import Annotated

import ulid
from pydantic import BaseModel, Field, PositiveFloat, NonNegativeFloat

__all__ = (
    'OrganizationCurrentInfoOut',
)

from center.enums import Period


class ProductionUnitCurrentInfo(BaseModel):
    id: Annotated[
        ulid.ULID,
        Field(description='Id продукта.'),
    ]
    plan_value: Annotated[
        NonNegativeFloat,
        Field(description='Производственный план на сегодня.', ),
    ]
    fact_value: Annotated[
        NonNegativeFloat,
        Field(description='Факт на сегодня.'),
    ] = 0
    instant_performance_value: Annotated[
        NonNegativeFloat,
        Field(description='Мгновенная текущая производительность',)
    ]
    instant_performance_period: Annotated[
        Period,
        Field(description='За какой период...', )
    ] = Period.HOUR
    suspended_now: Annotated[
        bool,
        Field('Остановлено ли производство данной продукции сейчас.',)
    ] = False


class OrganizationCurrentInfoOut(BaseModel):
    id: Annotated[
        ulid.ULID,
        Field(description='Id компании.'),
    ]
    dt: Annotated[
        datetime.datetime,
        Field(default_factory=lambda: datetime.datetime.now(tz=datetime.UTC), description='Время состояния.'),
    ]
    current_data: Annotated[
        list[ProductionUnitCurrentInfo],
        Field(description='Производственные данные на конкретные продукты.', default_factory=list)
    ]

