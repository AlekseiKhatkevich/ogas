import datetime

from polyfactory import Use

from center.orm_models import (
    CapabilityORM,
    NecessityORM,
    OperativeDataORM,
    OrganizationORM,
    OrganizationStockORM,
)
from common.testing.factories.sqlalchemy import CustomFactory

__all__ = (
    'OrganizationFactory',
    'CapabilityFactory',
    'OperativeDataFactory',
    'OrganizationStockFactory',
    'NecessityFactory',
)


class OrganizationFactory(CustomFactory[OrganizationORM]):
    name: str = Use(CustomFactory.__faker__.unique.company)
    is_active: bool = True
    token: str = '$2a$06$QaK1P3svJ/ZjSO2WdaebhuHk8/0K2B2A42svHnn/y7hdzGDUbrv9K'  # token = test_token


class CapabilityFactory(CustomFactory[CapabilityORM]):
    __set_relationships__ = True
    __allow_none_optionals__ = False
    value: int = Use(CustomFactory.__faker__.random_int, min=0)


class OperativeDataFactory(CustomFactory[OperativeDataORM]):
    __set_relationships__ = True
    diff: float = Use(CustomFactory.__faker__.pyfloat, min_value=-100, max_value=1000)
    change_datetime: datetime.datetime = Use(
        CustomFactory.__faker__.date_time_between, '-1m', 'now', datetime.UTC,
    )


class OrganizationStockFactory(CustomFactory[OrganizationStockORM]):
    __set_relationships__ = True
    in_stock: float = Use(CustomFactory.__faker__.pyfloat, positive=True)
    min_level: float = 0
    max_level: float = float('Infinity')
    necessity: float | None = None
    organization = Use(OrganizationFactory.build)
    is_active: bool = True


class NecessityFactory(CustomFactory[NecessityORM]):
    __set_relationships__ = True
    to_produce: float = Use(CustomFactory.__faker__.pyfloat, positive=True)
    in_stock_at_consumer: float = Use(CustomFactory.__faker__.pyfloat, positive=True)
    in_stock_at_producer: float = Use(CustomFactory.__faker__.pyfloat, positive=True)
