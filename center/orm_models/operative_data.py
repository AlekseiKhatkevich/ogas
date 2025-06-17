import datetime
from typing import TYPE_CHECKING
import sqlalchemy_utils as sa_utils
import ulid
import sqlalchemy  as sa
from alembic.operations import Operations
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils.view import CreateView, DropView

from common.resources.database.postgres.alchemy_related import Base

if TYPE_CHECKING:
    from center.orm_models import OrganizationORM
    from common.orm_models import ProductORM

__all__ = (
    'OperativeDataORM',
    'OperativeDataORM1MinuteView',
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


class BaseMatViewORMMixin:
    selectable: sa.Select = None
    __table__: sa.Table = None

    @classmethod
    def create(cls, op: Operations):
        """Используется только в миграциях alembic"""
        cls.drop(op)
        create_sql = CreateView(cls.__table__.fullname, cls.selectable, materialized=True)
        op.execute(create_sql)
        for idx in cls.__table__.indexes:
            idx.create(op.get_bind())

    @classmethod
    def drop(cls, op: Operations):
        """Используется только в миграциях alembic"""
        drop_sql = DropView(cls.__table__.fullname, materialized=True, cascade=True)
        op.execute(drop_sql)

    @classmethod
    def update(cls, op: Operations):
        """Используется только в миграциях alembic

        Основано на:
        https://stackoverflow.com/questions/64653231/add-a-new-column-to-a-postgres-materialized-view
        """
        create_sql = CreateView(f"{cls.__table__.fullname}temp", cls.selectable, materialized=True)
        op.execute(create_sql)

        cls.drop(op)

        op.rename_table(f"{cls.__table__.fullname}temp", cls.__table__.fullname)

        for idx in cls.__table__.indexes:
            idx.create(op.get_bind())


class OperativeDataORM1MinuteView(BaseMatViewORMMixin, Base):
    is_view = True
    selectable = sa.select(
                sa.func.time_bucket('1 minute', OperativeDataORM.change_datetime).label('bucket'),
                OperativeDataORM.product_id,
                OperativeDataORM.organization_id,
                sa.func.sum(OperativeDataORM.diff).filter(OperativeDataORM.diff > 0).label('positive_diff'),
                sa.func.sum(OperativeDataORM.diff).filter(OperativeDataORM.diff < 0).label('negative_diff'),
        ).group_by(
            sa.text('bucket'),
            OperativeDataORM.product_id,
            OperativeDataORM.organization_id,
        )

    __table__ = sa_utils.create_materialized_view(
        name='operative_data_by_minute',
        # cascade_on_drop=True,
        metadata=Base.metadata,
        selectable=selectable,
    )