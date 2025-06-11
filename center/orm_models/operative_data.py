import datetime
from typing import TYPE_CHECKING

import ulid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from common.resources.database.postgres.alchemy_related import Base

if TYPE_CHECKING:
    from center.orm_models import OrganizationORM
    from common.orm_models import ProductORM

__all__ = (
    'OperativeDataORM',
)


class OperativeDataORM(Base):
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
    organization: Mapped['OrganizationORM'] = relationship(
        'OrganizationORM',
        backref='operative_data',
        primaryjoin='OperativeDataORM.organization_id == OrganizationORM.id',
        foreign_keys=organization_id,
    )
    product: Mapped['ProductORM'] = relationship(
        'ProductORM',
        backref='operative_data',
        primaryjoin='OperativeDataORM.product_id == ProductORM.id',
        foreign_keys=product_id,
    )

    __mapper_args__ = {
        'primary_key': ['product_id', 'organization_id', 'change_datetime', ],
    }

    def __repr__(self) -> str:
        return f'Product {self.product_id}, organization {self.organization_id}.'
