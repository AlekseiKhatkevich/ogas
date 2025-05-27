import enum

import pytest

from utils.enums import CaseInsensitiveMixin


@pytest.fixture
def enum_for_test() -> 'TestEnum':
    class TestEnum(CaseInsensitiveMixin, enum.StrEnum):
        GREEN = enum.auto()
        RED = enum.auto()
    return TestEnum


def test_case_insensitive_mixin_positive(enum_for_test):
    assert enum_for_test('grEen') == enum_for_test.GREEN
