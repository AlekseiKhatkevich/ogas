from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

from center.orm_models import OrganizationORM, OrganizationStockORM
from common.repositories.postgres import CommonPostgresRepository

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
                *update_where_elements)
        ).returning(
            self._model,
        )
        async with self._db.async_session as session:
            instance = await session.scalar(stmt)
            await session.commit()

        return instance
