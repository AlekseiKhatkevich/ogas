import datetime
from typing import Any, Callable, Generic, TypeVar

import ulid
from faker import Faker
from polyfactory import Ignore
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

from common.orm_models import CategoryORM, ProductORM, StandardORM
from common.orm_models.custom_types import ULID as ULID_TYPE_FIELD

__all__ = (
    'CategoryFactory',
    'StandardFactory',
    'ProductFactory',
    'CustomFactory',
)

T = TypeVar("T")


# noinspection PyUnresolvedReferences
class CustomFactory(Generic[T], SQLAlchemyFactory[T]):
    __is_base_factory__ = True
    __faker__ = Faker(locale='ru_RU')
    __randomize_collection_length__ = True
    __min_collection_length__ = 1
    __max_collection_length__ = 3
    __check_model__ = True

    created_at: datetime.datetime = Ignore()
    updated_at: datetime.datetime = Ignore()
    main_prefix: str = Ignore()

    @classmethod
    def get_sqlalchemy_types(cls) -> dict[Any, Callable[[], Any]]:
        return super().get_sqlalchemy_types() | {ULID_TYPE_FIELD: ulid.ULID}


class CategoryFactory(CustomFactory[CategoryORM]):
    pass


class StandardFactory(CustomFactory[StandardORM]):
    is_active: bool = True


class ProductFactory(CustomFactory[ProductORM]):
    __set_relationships__ = True
