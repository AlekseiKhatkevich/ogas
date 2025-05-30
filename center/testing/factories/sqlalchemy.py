from polyfactory import Use

from center.orm_models import CapabilityORM, OrganizationORM
from common.testing.factories.sqlalchemy import CustomFactory

__all__ = (
    'OrganizationFactory',
    'CapabilityFactory',
)


class OrganizationFactory(CustomFactory[OrganizationORM]):
    name: str = Use(CustomFactory.__faker__.unique.company)
    is_active: bool = True
    token: str = '$2a$06$QaK1P3svJ/ZjSO2WdaebhuHk8/0K2B2A42svHnn/y7hdzGDUbrv9K'  # token = test_token


class CapabilityFactory(CustomFactory[CapabilityORM]):
    __set_relationships__ = True
    __allow_none_optionals__ = False
    value: int = Use(CustomFactory.__faker__.random_int, min=0)
