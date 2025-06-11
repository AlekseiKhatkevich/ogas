import datetime

import ulid
from sqlalchemy import ForeignKey, Identity
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Column, Integer, DateTime, event, DDL, orm
from common.resources.database.postgres.alchemy_related import Base

__all__ = (
    'OperativeDataORM',
)


class OperativeDataORM(Base):
    id: Mapped[int] = mapped_column(
        Identity(cycle=True, always=True,),
        primary_key=True,
        comment='ID',
    )
    organization_id: Mapped[ulid.ULID] = mapped_column(
        comment='Компания.',
    )
    product_id: Mapped[ulid.ULID] = mapped_column(
        comment='Продукт.',
    )
    diff: Mapped[float] = mapped_column(
        comment='Приход или расход продукта в единицах измерения.',
    )
    change_datetime: Mapped[datetime.datetime] = mapped_column(
        comment='Время наступления события.',
    )


# event.listen(
#     OperativeDataORM.__table__,
#     'after_create',
#     DDL(
#         f"SELECT create_hypertable('{OperativeDataORM.__tablename__}', by_range('time', INTERVAL '1 day')));"
#     )
# )
