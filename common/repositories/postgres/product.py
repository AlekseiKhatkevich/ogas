from common.orm_models import ProductORM
from common.repositories.postgres import CommonPostgresRepository


__all__ = (
    'ProductPostgresRepository',
)


class ProductPostgresRepository(CommonPostgresRepository, model=ProductORM):
    pass
