from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

from center.orm_models import CapabilityORM, OrganizationORM
from center.repositories.postgres import CommonPostgresRepository

if TYPE_CHECKING:
    from center.serializers import CapabilityIn

__all__ = (
    'CapabilityPostgresRepository',
)


class CapabilityPostgresRepository(CommonPostgresRepository, model=CapabilityORM):
    """
    Репозиторий БД для модели CapabilityORM
    """
    async def insert_or_update_capabilities(self, capabilities: list['CapabilityIn']) -> None:
        """
        :param capabilities: Набор производительностей от компании.
        :return:
        """
        value_expr = sa.values(
            sa.column('organization_name', sa.TEXT),
            sa.column('product_id', self._model.product_id.type),
            sa.column('period', self._model.period.type),
            sa.column('value', self._model.value.type),
            name='capabilities_from_company',
        ).data([
            (c.organization_name, c.product_id, c.period, c.value)
            for c in capabilities
        ])

        sel = sa.select(
            OrganizationORM.id,
            sa.cast(value_expr.c.product_id, self._model.product_id.type),
            sa.cast(value_expr.c.period, self._model.period.type),
            value_expr.c.value,
        ).join(
            OrganizationORM,
            OrganizationORM.name == value_expr.c.organization_name,
        )

        insert_stmt = pg.insert(self._model).from_select(
            ['organization_id', 'product_id', 'period', 'value',],
            sel,
        )

        stmt = insert_stmt.on_conflict_do_update(
            index_elements=('organization_id', 'product_id', 'period'),
            set_={
                self._model.value: insert_stmt.excluded.value,
                self._model.updated_at: sa.func.now(),
            },
            where=self._model.value.is_distinct_from(insert_stmt.excluded.value),
        ).returning(
            self._model.updated_at == sa.func.now(),  # обновленные
        )

        async with self._db.async_session as session:
            await session.execute(stmt)
            await session.commit()
