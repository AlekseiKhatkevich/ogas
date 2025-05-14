from polyfactory import Ignore
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

from common.orm_models import CategoryORM


__all__ = (
    'CategoryFactory',
)


class CategoryFactory(SQLAlchemyFactory[CategoryORM]):
    main_prefix = Ignore()
# CategoryFactory.__async_session__ = db.async_sessionmaker()
# await CategoryFactory.create_async()
