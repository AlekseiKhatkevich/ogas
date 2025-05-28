import pytest

import constants
from utils.common import batch_for_asyncpg


@pytest.fixture(scope='module')
def elements() -> list[tuple[int, ...]]:
    return [(1, 2, 3, 4,) for _ in range(10_000)]


def test_batch_for_asyncpg_positive_no_args(elements):
    first_batch = next(batch_for_asyncpg(elements))
    assert (len(first_batch) * 4 < constants.SMALLINT_MAX)


def test_batch_for_asyncpg_positive_batch_size(elements):
    first_batch = next(batch_for_asyncpg(elements, batch_size=100))
    assert len(first_batch) == 100
