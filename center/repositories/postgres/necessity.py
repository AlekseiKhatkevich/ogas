from center.orm_models import NecessityORM
from common.repositories.postgres import CommonPostgresRepository


__all__ = (
    'NecessityPostgresRepository',
)


class NecessityPostgresRepository(CommonPostgresRepository, model=NecessityORM):
    pass
