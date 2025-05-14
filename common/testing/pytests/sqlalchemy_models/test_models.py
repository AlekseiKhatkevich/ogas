from common.orm_models import CategoryORM
from common.testing.factories.sqlalchemy import CategoryFactory


def test_person_factory(category_factory: CategoryFactory) -> None:
    person_instance = category_factory.build()
    assert isinstance(person_instance, CategoryORM)