from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import selectinload
from sqlalchemy.orm import noload
from common.orm_models import CategoryORM, ProductORM, category_association_table
from common.repositories.postgres import CommonPostgresRepository
from common.enums.product import ProductUnit
from sqlalchemy.dialects import postgresql



__all__ = (
    'ProductPostgresRepository',
)


class ProductPostgresRepository(CommonPostgresRepository, model=ProductORM):

    async def create_or_update_product(self,
                                       name: str,
                                       unit: ProductUnit,
                                       code: str,
                                       categories: set[str],
                                       ) -> ProductORM:
        """
        https://stackoverflow.com/questions/34708509/how-to-use-returning-with-on-conflict-in-postgresql
        Идея в целом:

        SET lock_timeout = '5s';
        WITH
          extant AS (
            SELECT * FROM product WHERE name = 'sdfsdf115' and  unit = 'BOX' and  standard_code = 'ГОСТ Р 1.12-2020' FOR UPDATE
          ),
          inserted AS (
            INSERT INTO product (name, unit, standard_code)
            SELECT 'sdfsdf115', 'BOX', 'ГОСТ Р 1.12-2020'
            WHERE NOT EXISTS (SELECT FROM extant)
            RETURNING *
          )
        SELECT *  FROM inserted
        UNION ALL
        SELECT * FROM extant;
        """
        timeout_stmt = sa.text("SET lock_timeout = '5s'")

        # noinspection PyTypeChecker
        extant_stmt = self.select.options(
            noload(self._model.standard),
            # selectinload(self._model.categories),
        ).where(
            self._model.name == name,
            self._model.unit == unit,
            self._model.standard_code == code,
        ).with_for_update().cte()

        exists_sq = sa.select(extant_stmt).exists()

        inserted_stmt = self.insert.from_select(
            ['name', 'unit', 'standard_code', ],
            sa.select(
                sa.text(f"'{name}'"),
                sa.cast(sa.text(f"'{unit.name}'"), sa.Enum(ProductUnit)),
                sa.text(f"'{code}'")
            ).where(
                ~ exists_sq,
            )
        ).returning(
            self._model,
        ).cte()

        union_stmt = sa.select(inserted_stmt).union_all(sa.select(extant_stmt))

        final_stmt = self.select.from_statement(union_stmt).options(
            selectinload(self._model.categories),
        )

        async with self._db.async_session as session:
            await session.execute(timeout_stmt)
            instance = await session.scalar(final_stmt)
            await session.execute(sa.delete(category_association_table).where(category_association_table.c.product_id == instance.id))

            await session.commit()


            return instance
