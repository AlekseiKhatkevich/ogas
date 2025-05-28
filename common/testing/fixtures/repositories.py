import pytest

from common.repositories.postgres import ProductPostgresRepository


@pytest.fixture(scope='session')
def product_repo() -> ProductPostgresRepository:
    return ProductPostgresRepository()
