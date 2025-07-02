from typing import AsyncGenerator

from sqlalchemy import outerjoin
from sqlalchemy.orm import aliased

from center.enums import Role
from center.orm_models import CapabilityORM, NecessityORM
from common.orm_models import ProductORM
from common.repositories.postgres import CommonPostgresRepository, InfoForPlanning
import sqlalchemy as sa


__all__ = (
    'NecessityPostgresRepository',
)


class NecessityPostgresRepository(CommonPostgresRepository, model=NecessityORM):

    async def get_necessities_for_planing(self) -> AsyncGenerator[InfoForPlanning]:
        from center.repositories.postgres import CapabilityPostgresRepository
        warehouses_cte = CapabilityPostgresRepository().warehouses.cte()
        warehouses = aliased(CapabilityORM, warehouses_cte, name='warehouses')

        from center.enums import Period
        stmt = sa.select(
            self._model.product_id,
            self._model.to_produce,
            self._model.created_at.label('fact_time'),
            CapabilityORM.organization_id.label('producer_id'),
            CapabilityORM.value.label('capability'),
            CapabilityORM.period,
            sa.case(
                (warehouses.organization_id.is_not(None), sa.true()),
                else_=sa.false(),
            ).label('is_warehouse'),
            ProductORM.unit.label('product_unit'),
        ).join(
            self._model.product,
        ).outerjoin(
            self._model.capabilities.and_(
                CapabilityORM.role == Role.PRODUCER,
            ),
        ).outerjoin(
            warehouses,
            sa.and_(
                CapabilityORM.organization_id == warehouses.organization_id,
                CapabilityORM.product_id == warehouses.product_id,
            )
        ).distinct(
            self._model.product_id,
            CapabilityORM.organization_id,
        ).where(
            self._model.to_produce > 0,
        ).order_by(
            self._model.product_id,
            CapabilityORM.organization_id,
            sa.case(
                (CapabilityORM.period == Period.DAY, 2),
                (CapabilityORM.period == Period.WEEK, 3),
                (CapabilityORM.period == Period.MONTH, 4),
                (CapabilityORM.period == Period.QUARTER, 5),
                (CapabilityORM.period == Period.YEAR, 6),
                else_=7,
            ),
            self._model.created_at.desc(),
        )

        stmt = stmt.execution_options(stream_results=True, yield_per=1000)
        async with self._db.async_session as session:
            res = await session.stream(stmt)
            async for partition in res.partitions():
                for element in partition:
                    # noinspection PyTypeChecker
                    yield InfoForPlanning(*element)
