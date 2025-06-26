import datetime

import ulid
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from common.resources.database.postgres.alchemy_related import Base, ULID_PK

__all__ = (
    'NecessityORM',
)

from common.resources.database.postgres.timescaledb.common_utils import BaseTimescaleORMMixin


class NecessityORM(BaseTimescaleORMMixin, Base):
    include_updated_at = False
    timescale_options = {
           'timescaledb.enable_columnstore': True,
           'timescaledb.orderby': 'created_at DESC',
           'timescaledb.segmentby': 'product_id',
           'timescaledb.chunk_interval': '7 DAYS',
    }
    # retention_policy: datetime.timedelta
    # retention_interval: datetime.timedelta
    # columnstore_policy_interval: datetime.timedelta
    partition_by = 'created_at'
    partition_interval = datetime.timedelta(days=7)

    # id: Mapped[ULID_PK]
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
    created_at: Mapped[datetime.datetime] = mapped_column(
        server_default=func.Now(),
        nullable=False,
        comment='Время создания.',
    )
    product: Mapped['ProductORM'] = relationship(
        passive_deletes=True,
    )

    __mapper_args__ = {
        'primary_key': ['product_id', 'created_at', ],
    }

    def __repr__(self) -> str:
        return f'Necessity for {self.product_id}'
