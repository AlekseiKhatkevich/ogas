import pytest

from common.repositories.postgres import ProductCategoryM2MIntermediateRepository, ProductPostgresRepository


@pytest.fixture(scope='session')
def product_repo() -> ProductPostgresRepository:
    return ProductPostgresRepository()


@pytest.fixture(scope='session')
def product_category_m2m_repo() -> ProductCategoryM2MIntermediateRepository:
    return ProductCategoryM2MIntermediateRepository()
