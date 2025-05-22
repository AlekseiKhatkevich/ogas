from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

from center.orm_models import CapabilityORM, OrganizationORM
from center.repositories.postgres import CommonPostgresRepository
from utils.common import batch_for_asyncpg

if TYPE_CHECKING:
    from center.serializers import CapabilityIn

__all__ = (
    'CapabilityPostgresRepository',
)


class CapabilityPostgresRepository(CommonPostgresRepository, model=CapabilityORM):
    """
    Репозиторий БД для модели CapabilityORM.
    """
    async def insert_or_update_capabilities(self, capabilities: list['CapabilityIn']) -> tuple[int, int]:
        """
        Создает или обновляет в БД записи CapabilityORM пришедшими от компании данными.
        :param capabilities: Набор производительностей от компании.
        :return: Кол-во созданных + кол-во обновленных записей.
        """
        cnt_updated, cnt_created = 0, 0

        async with self._db.async_session as session:
            for batch in batch_for_asyncpg(capabilities):
                value_expr = sa.values(
                    sa.column('organization_name', sa.TEXT),
                    sa.column('product_id', self._model.product_id.type),
                    sa.column('period', self._model.period.type),
                    sa.column('value', self._model.value.type),
                    name='capabilities_from_company',
                ).data([
                    (c.organization_name, c.product_id, c.period, c.value)
                    for c in batch
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
                    self._model.updated_at.is_not_distinct_from(sa.func.now()),
                )

                response = await session.scalars(stmt)
                await session.commit()

                work_done_info = response.all()
                cnt_updated += (updated_this_batch := work_done_info.count(True))
                cnt_created += len(work_done_info) - updated_this_batch

        return cnt_created, cnt_updated
