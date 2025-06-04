from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import selectinload

from common.orm_models import CategoryORM, ProductORM
from common.repositories.postgres import CommonPostgresRepository

if TYPE_CHECKING:
    from common.enums.product import ProductUnit


__all__ = (
    'ProductPostgresRepository',
)


class ProductPostgresRepository(CommonPostgresRepository, model=ProductORM):

    async def create_or_update_product(self,
                                       name: str,
                                       unit: 'ProductUnit',
                                       code: str,
                                       categories: set[str],
                                       ) -> ProductORM:
        select_stmt = self.select.where(
            self._model.name == name,
            self._model.unit == unit,
            self._model.standard_code == code,
        ).options(
            selectinload(self._model.categories),
        )
        async with self._db.async_session as session:
            instance = await session.scalar(select_stmt)

            if instance is None:
                # noinspection PyCallingNonCallable
                instance = self._model(
                    name=name,
                    unit=unit,
                    standard_code=code,
                )

            if not categories:
                instance.categories.clear()
            else:
                categories_stmt = sa.select(CategoryORM).where(CategoryORM.code.in_(categories))
                categories = await session.scalars(categories_stmt)
                instance.categories = list(categories.all())

            session.add(instance)
            await session.commit()

            return instance
