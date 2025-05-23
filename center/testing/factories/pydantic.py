from typing import Generic, TypeVar

from faker import Faker
from polyfactory import Use
from polyfactory.factories.pydantic_factory import ModelFactory

from center.serializers import CapabilityIn

__all__ = (
    'CapabilityInFactory',
)


T = TypeVar('T')


class CustomFactory(Generic[T], ModelFactory[T]):
    __is_base_factory__ = True
    __faker__ = Faker(locale='ru_RU')
    __randomize_collection_length__ = True
    __min_collection_length__ = 1
    __max_collection_length__ = 3
    __check_model__ = True


class CapabilityInFactory(CustomFactory[CapabilityIn]):
    __allow_none_optionals__ = False
    organization_name: str = Use(CustomFactory.__faker__.unique.company)
