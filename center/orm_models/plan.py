import datetime
import sqlalchemy as sa
import ulid
from sqlalchemy import Computed, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from common.resources.database.postgres.alchemy_related import Base, ULID_PK

__all__ = (
    'PlanORM',
)


class PlanORM(Base):
    id: Mapped[ULID_PK]
    organization_id: Mapped[ulid.ULID | None] = mapped_column(
        ForeignKey('organization.id', ondelete='CASCADE', ),
        comment='Компания. None - план на закупку заграницей.',
        index=True,
    )
    product_id: Mapped[ulid.ULID] = mapped_column(
        ForeignKey('product.id', ondelete='CASCADE', ),
        comment='Продукт.',
        index=True,
    )
    value: Mapped[float] = mapped_column(
        comment='Необходимо произвести единиц продукта.'
    )
    fact_time: Mapped[datetime.datetime] = mapped_column(
        comment='Время вычисления необходимости в пр-ве продукта.'
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        Computed(sa.func.ulid_to_timestamp(sa.text("id")), persisted=None),
        comment='Время создания записи.',
    )

    __table_args__ = (
        Index('ix_created_at_desc', created_at.desc()),
    )

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.organization_id})({self.product_id})'
