from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import Select
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.orm import aliased

from center.orm_models import CapabilityORM, OrganizationORM
from common.repositories.postgres import CommonPostgresRepository, UpsertResult
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

    async def insert_or_update_capabilities(self, capabilities: set['CapabilityIn']) -> UpsertResult:
        """
        Создает или обновляет в БД записи CapabilityORM пришедшими от компании данными.
        :param capabilities: Набор производительностей от компании.
        :return: Кол-во созданных + кол-во обновленных записей.
        """
        updated, created = [], []

        async with self._db.async_session as session:
            for batch in batch_for_asyncpg(capabilities):
                value_expr = sa.values(
                    sa.column('organization_name', sa.TEXT),
                    sa.column('product_id', self._model.product_id.type),
                    sa.column('period', self._model.period.type),
                    sa.column('role', self._model.role.type),
                    sa.column('value', self._model.value.type),
                    name='capabilities_from_company',
                ).data(
                    [(c.organization_name, c.product_id, c.period, c.role, c.value) for c in batch]
                )

                sel = sa.select(
                    OrganizationORM.id,
                    sa.cast(value_expr.c.product_id, self._model.product_id.type),
                    sa.cast(value_expr.c.period, self._model.period.type),
                    sa.cast(value_expr.c.role, self._model.role.type),
                    value_expr.c.value,
                ).join(
                    OrganizationORM,
                    OrganizationORM.name == value_expr.c.organization_name,
                )

                insert_stmt = pg.insert(self._model).from_select(
                    ['organization_id', 'product_id', 'period', 'role', 'value', ],
                    sel,
                )

                stmt = insert_stmt.on_conflict_do_update(
                    index_elements=('organization_id', 'product_id', 'period', 'role',),
                    set_={
                        self._model.value: insert_stmt.excluded.value,
                        self._model.updated_at: sa.func.now(),
                    },
                    where=self._model.value.is_distinct_from(insert_stmt.excluded.value),
                ).returning(
                    self._model.id,
                    self._model.updated_at.is_not_distinct_from(sa.func.now()),
                )

                response = await session.execute(stmt)
                await session.commit()

                for _ulid, is_updated in response.all():
                    if is_updated:
                        updated.append(_ulid)
                    else:
                        created.append(_ulid)

        return UpsertResult(created, updated)

    @property
    def warehouses(self) -> Select[CapabilityORM]:
        from center.enums import Role
        cap2 = aliased(self._model)
        stmt = sa.select(
            self._model,
        ).join(
            cap2,
            sa.and_(
                self._model.organization_id == cap2.organization_id,
                self._model.product_id == cap2.product_id,
                self._model.role == Role.PRODUCER,
                cap2.role == Role.CONSUMER,
            )
        )
        return stmt
