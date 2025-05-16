from common.orm_models import CategoryORM
from common.testing.factories.sqlalchemy import CategoryFactory


async def test_person_factory(category_factory: CategoryFactory, save_in_db, apply_alembic_migrations) -> None:
    person_instance = category_factory.build()
    assert isinstance(person_instance, CategoryORM)
    await save_in_db(category_factory)
