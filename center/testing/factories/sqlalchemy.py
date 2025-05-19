from polyfactory import Use

from center.orm_models import OrganizationORM
from common.testing.factories.sqlalchemy import CustomFactory




class OrganizationFactory(CustomFactory[OrganizationORM]):
    name: str = Use(CustomFactory.__faker__.unique.company)
    is_active: bool = True
