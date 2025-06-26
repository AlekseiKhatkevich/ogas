import datetime

import ulid
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from common.resources.database.postgres.alchemy_related import Base, ULID_PK

__all__ = (
    'NecessityORM',
)


class NecessityORM(Base):
    include_updated_at = False

    id: Mapped[ULID_PK]
    product_id: Mapped[ulid.ULID] = mapped_column(
        ForeignKey('product.id', ondelete='CASCADE', ),
        comment='Продукт.',
    )
    to_produce: Mapped[float] = mapped_column(
        comment='Необходимое кол-во продукта для заказа.'
    )
    in_stock_at_consumer: Mapped[float] = mapped_column(
        comment='Кол-во на складах потребителей.',
    )
    in_stock_at_producer: Mapped[float] = mapped_column(
        comment='Кол-во на складах производителей.',
    )
    product: Mapped['ProductORM'] = relationship(
        passive_deletes=True,
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        server_default=func.Now(),
        nullable=False,
        comment='Время создания.',
    )

    def __repr__(self) -> str:
        return f'Necessity for {self.product_id}'
