from polyfactory import Use

from center.orm_models import CapabilityORM, OrganizationORM
from common.testing.factories.sqlalchemy import CustomFactory


class OrganizationFactory(CustomFactory[OrganizationORM]):
    __set_relationships__ = True

    name: str = Use(CustomFactory.__faker__.unique.company)
    is_active: bool = True


class CapabilityFactory(CustomFactory[CapabilityORM]):
    pass
