from polyfactory import Ignore
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from faker import Faker
from common.orm_models import CategoryORM, StandardORM

__all__ = (
    'CategoryFactory',
    'StandardFactory',
)


class FactoryMixin:
    __faker__ = Faker(locale='ru_RU')
    __randomize_collection_length__ = True
    __min_collection_length__ = 1
    __max_collection_length__ = 3
    __check_model__ = True


class CategoryFactory(FactoryMixin, SQLAlchemyFactory[CategoryORM]):
    main_prefix = Ignore()


class StandardFactory(FactoryMixin, SQLAlchemyFactory[StandardORM]):
    is_active: bool = True
