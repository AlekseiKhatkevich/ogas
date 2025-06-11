import datetime

import ulid
from sqlalchemy.orm import Mapped, mapped_column

from common.resources.database.postgres.alchemy_related import Base

__all__ = (
    'OperativeDataORM',
)


class OperativeDataORM(Base):
    # id: Mapped[int] = mapped_column(
    #     Identity(cycle=True, always=True,),
    #     primary_key=True,
    #     comment='ID',
    # )
    product_id: Mapped[ulid.ULID] = mapped_column(
        comment='Продукт.',
    )
    organization_id: Mapped[ulid.ULID] = mapped_column(
        comment='Компания.',
    )
    diff: Mapped[float] = mapped_column(
        comment='Приход или расход продукта в единицах измерения.',
    )
    change_datetime: Mapped[datetime.datetime] = mapped_column(
        comment='Время наступления события.',
    )
    __mapper_args__ = {
        'primary_key': ['product_id', 'organization_id', 'change_datetime', ]
    }
