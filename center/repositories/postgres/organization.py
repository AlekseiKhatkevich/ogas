from center.orm_models import OrganizationORM
from common.repositories.postgres import CommonPostgresRepository

__all__ = (
    'OrganizationPostgresRepository',
)


class OrganizationPostgresRepository(CommonPostgresRepository, model=OrganizationORM):
    pass
