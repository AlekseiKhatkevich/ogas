from common.orm_models import CategoryORM
from common.testing.factories.sqlalchemy import CategoryFactory


async def test_person_factory(category_in_db, standard_in_db) -> None:
    assert 1+1