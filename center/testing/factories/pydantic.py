import datetime
from typing import Any, Generic, Type, TypeVar

import ulid
from faker import Faker
from polyfactory import Use
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic.types import SecretStr

from center.serializers import CapabilityIn, OperativeDataIn, OrganizationUpdateIn

__all__ = (
    'CapabilityInFactory',
    'OrganizationUpdateInFactory',
    'OperativeDataInFactory',
)


T = TypeVar('T')


class CustomFactory(Generic[T], ModelFactory[T]):
    __is_base_factory__ = True
    __faker__ = Faker(locale='ru_RU')
    __randomize_collection_length__ = True
    __min_collection_length__ = 1
    __max_collection_length__ = 3
    __check_model__ = True

    @classmethod
    def get_provider_map(cls) -> dict[Type, Any]:
        return {
            SecretStr: lambda: cls.__faker__.unique.pystr(min_chars=24, max_chars=72),
            **super().get_provider_map(),
        }


class CapabilityInFactory(CustomFactory[CapabilityIn]):
    __allow_none_optionals__ = False
    organization_name: str = Use(CustomFactory.__faker__.unique.company)


class OrganizationUpdateInFactory(CustomFactory[OrganizationUpdateIn]):
    __allow_none_optionals__ = False
    new_token: str = Use(CustomFactory.__faker__.unique.pystr, min_chars=24, max_chars=72)


class OperativeDataInFactory(CustomFactory[OperativeDataIn]):
    organization_id: ulid.ULID | None = None
    change_datetime: datetime.datetime = Use(
        CustomFactory.__faker__.date_time_between, '-1m', 'now', datetime.UTC,
    )
