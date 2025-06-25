import datetime
from typing import AsyncGenerator, TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

from center.enums import Period
from center.orm_models import CapabilityORM, OperativeDataORM, OperativeDataORM1HourView, OrganizationORM, \
    OrganizationStockORM
from common.repositories.postgres import CommonPostgresRepository, InfoForSchedule

if TYPE_CHECKING:
    from center.serializers import OrganizationStockIn

__all__ = (
    'OrganizationStockPostgresRepository',
)


class OrganizationStockPostgresRepository(CommonPostgresRepository, model=OrganizationStockORM):

    async def insert_stock(self, stock: 'OrganizationStockIn', organization: OrganizationORM) -> OrganizationStockORM:
        insert_stmt = pg.insert(
            self._model,
        ).values(
            **stock.model_dump(exclude_none=True),
            organization_id=organization.id
        )
        update_where_elements = []
        extra_set_values = {}
        for attr in ('min_level', 'max_level', 'necessity', 'is_active', ):
            if getattr(stock, attr) is not None:
                model_attr = getattr(self._model, attr)
                excluded_attr = getattr(insert_stmt.excluded, attr)
                extra_set_values.update({model_attr: excluded_attr})
                update_where_elements.append(model_attr.is_distinct_from(excluded_attr))

        stmt = insert_stmt.on_conflict_do_update(
            index_elements=('organization_id', 'product_id', ),
            set_={
                self._model.in_stock: insert_stmt.excluded.in_stock,
                self._model.updated_at: sa.func.now(),
                **extra_set_values,
            },
            where=sa.or_(
                self._model.in_stock.is_distinct_from(insert_stmt.excluded.in_stock),
                *update_where_elements,
            )
        ).returning(
            self._model,
        )
        async with self._db.async_session as session:
            instance = await session.scalar(stmt)
            await session.commit()

        return instance

    async def get_info_for_schedule(
            self,
            od_avg_interval: datetime.timedelta = datetime.timedelta(seconds=60 * 60 * 24 * 21),
            cap_period: Period = Period.DAY,
    ) -> AsyncGenerator[InfoForSchedule]:
        # noinspection PyTypeChecker,PyUnresolvedReferences
        oper_data = sa.select(
           sa.func.avg(sa.func.coalesce(OperativeDataORM1HourView.negative_diff, 0)).label('cons_per_hour'),
        ).where(
            self._model.product_id == OperativeDataORM1HourView.product_id,
            self._model.organization_id == OperativeDataORM1HourView.organization_id,
            OperativeDataORM1HourView.hour_bucket >= sa.func.now() - od_avg_interval,
        ).lateral()

        stmt = sa.select(
            self._model.product_id,
            CapabilityORM.role,
            sa.func.sum(self._model.in_stock).label('in_stock'),
            sa.func.sum(oper_data.c.cons_per_hour).label('cons_per_hour'),
            sa.func.sum(self._model.necessity).label('necessity'),
            sa.func.sum(CapabilityORM.value).label('capability_per_interval'),
        ).outerjoin(
            CapabilityORM,
            sa.and_(
                self._model.product_id == CapabilityORM.product_id,
                self._model.organization_id == CapabilityORM.organization_id,
                self._model.is_active == sa.true(),
                CapabilityORM.period == cap_period,
            ),
        ).join(
            oper_data,
            sa.true(),
        ).group_by(
            self._model.product_id,
            CapabilityORM.role,
        ).order_by(
            self._model.product_id,
        )

        async with self._db.async_session as session:
            #  https://docs.sqlalchemy.org/en/20/orm/queryguide/api.html#fetching-large-result-sets-with-yield-per
            res = await session.stream(stmt.execution_options(stream_results=True, yield_per=100))
            async for partition in res.partitions():
                for element in partition:
                    # noinspection PyTypeChecker
                    yield InfoForSchedule(*element, cap_period, od_avg_interval)
