from center.orm_models import OrganizationStockORM
from common.repositories.postgres import CommonPostgresRepository

__all__ = (
    'OrganizationStockPostgresRepository',
)


class OrganizationStockPostgresRepository(CommonPostgresRepository, model=OrganizationStockORM):
    pass
