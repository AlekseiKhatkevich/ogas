import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
import sqlalchemy_utils as sa_utils
import ulid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from common.resources.database.postgres.alchemy_related import Base
from common.resources.database.postgres.timescaledb.view_utils import BaseMatViewORMMixin

if TYPE_CHECKING:
    from center.orm_models import OrganizationORM
    from common.orm_models import ProductORM

__all__ = (
    'OperativeDataORM',
    'OperativeDataORM1MinuteView',
    'OperativeDataORM1HourView',
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
        # backref='operative_data',
        primaryjoin='OperativeDataORM.organization_id == OrganizationORM.id',
        foreign_keys=organization_id,
    )
    product: Mapped['ProductORM'] = relationship(
        'ProductORM',
        # backref='operative_data',
        primaryjoin='OperativeDataORM.product_id == ProductORM.id',
        foreign_keys=product_id,
    )

    __mapper_args__ = {
        'primary_key': ['product_id', 'organization_id', 'change_datetime', ],
    }

    def __repr__(self) -> str:
        return f'Product {self.product_id}, organization {self.organization_id}.'


class OperativeDataORM1MinuteView(BaseMatViewORMMixin, Base):
    selectable = sa.select(
                sa.func.time_bucket('1 minute', OperativeDataORM.change_datetime).label('bucket'),
                OperativeDataORM.product_id,
                OperativeDataORM.organization_id,
                sa.func.sum(OperativeDataORM.diff).filter(OperativeDataORM.diff > 0).label('positive_diff'),
                sa.func.abs(sa.func.sum(OperativeDataORM.diff).filter(OperativeDataORM.diff < 0)).label('negative_diff'),
        ).group_by(
            sa.text('bucket'),
            OperativeDataORM.product_id,
            OperativeDataORM.organization_id,
        )

    __table__ = sa_utils.create_materialized_view(
        name='operative_data_by_minute',
        metadata=Base.metadata,
        selectable=selectable,
    )
    timescale_options = {
        'timescaledb.continuous': True,
        'timescaledb.materialized_only': False,
    }
    retention_policy = datetime.timedelta(days=7)
    retention_interval = datetime.timedelta(hours=1)
    continuous_aggregate_start_offset = datetime.timedelta(hours=1)
    continuous_aggregate_end_offset = datetime.timedelta(minutes=1)
    continuous_aggregate_schedule_interval = datetime.timedelta(minutes=1)
    columnstore_policy_interval = datetime.timedelta(hours=1, minutes=5)

    # noinspection PyUnresolvedReferences
    def __repr__(self) -> str:
        return f'{self.product_id} // {self.organization_id} :: {self.bucket}'


class OperativeDataORM1HourView(BaseMatViewORMMixin, Base):
    selectable = sa.select(
                sa.func.time_bucket('1 hour', OperativeDataORM1MinuteView.bucket).label('hour_bucket'),
                OperativeDataORM1MinuteView.product_id,
                OperativeDataORM1MinuteView.organization_id,
                sa.func.sum(OperativeDataORM1MinuteView.positive_diff).label('positive_diff'),
                sa.func.sum(OperativeDataORM1MinuteView.negative_diff).label('negative_diff'),
        ).group_by(
            sa.text('hour_bucket'),
            OperativeDataORM1MinuteView.product_id,
            OperativeDataORM1MinuteView.organization_id,
        )

    __table__ = sa_utils.create_materialized_view(
        name='operative_data_by_hour',
        metadata=Base.metadata,
        selectable=selectable,
    )
    timescale_options = {
        'timescaledb.continuous': True,
        # 'timescaledb.materialized_only': False,
    }
    retention_policy = datetime.timedelta(days=365)
    retention_interval = datetime.timedelta(days=1)
    continuous_aggregate_start_offset = datetime.timedelta(days=7)
    continuous_aggregate_end_offset = datetime.timedelta(hours=1)
    continuous_aggregate_schedule_interval = datetime.timedelta(hours=1)
    columnstore_policy_interval = datetime.timedelta(days=1, hours=1)

    # noinspection PyUnresolvedReferences
    def __repr__(self) -> str:
        return f'{self.product_id} // {self.organization_id} :: {self.bucket}'
