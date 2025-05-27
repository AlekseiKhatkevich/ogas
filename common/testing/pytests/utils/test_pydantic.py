import pytest
from pydantic import BaseModel

from utils.pydantic_utils import hashable_model


@pytest.fixture
def pydantic_model_for_test() -> 'TestModel':
    @hashable_model(fields=['field_1', 'field_2', ])
    class TestModel(BaseModel):
        field_1: int
        field_2: str
        field_3: float
    return TestModel


def test_hashable_model_positive(pydantic_model_for_test):
    isinstance_1 = pydantic_model_for_test(field_1=1, field_2='test', field_3=333)
    instance_2 = pydantic_model_for_test(field_1=1, field_2='test', field_3=444)
    instance_3 = pydantic_model_for_test(field_1=1, field_2='new', field_3=333)

    container = {isinstance_1, instance_2, instance_3}

    assert hash(isinstance_1) == hash(instance_2)
    assert isinstance_1 == instance_2
    assert hash(isinstance_1) != hash(instance_3)
    assert isinstance_1 != instance_3
    assert isinstance_1 in container
    assert instance_3 in container
    assert len(container) == 2
