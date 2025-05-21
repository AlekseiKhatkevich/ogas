from center.enums import Period
from center.orm_models import CapabilityORM, OrganizationORM
from center.repositories.postgres import CommonPostgresRepository
from typing import TYPE_CHECKING
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from common.orm_models import custom_types

if TYPE_CHECKING:
    from center.serializers import CapabilityIn

__all__ = (
    'CapabilityPostgresRepository',
)


# stmt.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True})

class CapabilityPostgresRepository(CommonPostgresRepository, model=CapabilityORM):
    """

    """

    async def insert_or_update_capabilities(self, capabilities: list['CapabilityIn']) -> None:
        value_expr = sa.values(
            sa.column('organization_name', sa.TEXT),
            sa.column('product_id', sa.TEXT), # ULID
            sa.column('period', sa.TEXT), # ENUM
            sa.column('value', sa.INTEGER),
            name='capabilities_from_company',
        ).data([
            (c.organization_name, str(c.product_id), str(c.period), c.value)
            for c in capabilities
        ])

        sel = sa.select(
            OrganizationORM.id,
            value_expr.c.product_id,
            value_expr.c.period,
            value_expr.c.value,

        ).join(OrganizationORM, OrganizationORM.name == value_expr.c.organization_name)

        stmt = sa.insert(self._model).from_select(
            ['organization.id', 'product_id', 'period', 'value'],
            sel,
        )
        async with self._db.async_session as session:
            await session.execute(stmt)
            await session.commit()











#
# insert into capability(organization_id, product_id, period, value)
# select organization.id, product_id, period, value
# from (
#     VALUES ('ТМК Чермет'::text, '01JVMDB7W5C3CH4WP052BHBJN4'::ulid, 'QUARTER'::period, 99::int),
#            ('ТМК Чермет'::text, '01JVMDB7W5C3CH4WP052BHBJN4'::ulid, 'MONTH'::period, 99::int)
#      ) x (organization_name, product_id, period, value)
# JOIN organization on organization.name = x.organization_name
# -- on conflict ...
