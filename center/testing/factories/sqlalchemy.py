from polyfactory import Use

from center.orm_models import CapabilityORM, OrganizationORM
from common.testing.factories.sqlalchemy import CustomFactory

__all__ = (
    'OrganizationFactory',
    'CapabilityFactory',
)


class OrganizationFactory(CustomFactory[OrganizationORM]):
    __set_relationships__ = True

    name: str = Use(CustomFactory.__faker__.unique.company)
    is_active: bool = True


class CapabilityFactory(CustomFactory[CapabilityORM]):
    __set_relationships__ = True
    value: int = Use(CustomFactory.__faker__.random_int, min=0)
