from center.orm_models import PlanORM
from common.repositories.postgres import CommonPostgresRepository

__all__ = (
    'PlanPostgresRepository',
)


class PlanPostgresRepository(CommonPostgresRepository, model=PlanORM):
    pass
