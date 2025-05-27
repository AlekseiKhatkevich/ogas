from center.orm_models import OrganizationORM
from center.repositories.postgres import CommonPostgresRepository


__all__ = (
    'OrganizationPostgresRepository',
)


class OrganizationPostgresRepository(CommonPostgresRepository, model=OrganizationORM):
    pass
