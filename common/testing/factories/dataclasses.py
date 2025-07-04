from typing import Generic, TypeVar

from faker import Faker
from polyfactory import Use
from polyfactory.factories import DataclassFactory

from common.repositories.postgres import InfoForPlanning

__all__ = (
    'InfoForPlanningDCFactory',
)

T = TypeVar('T')


# noinspection PyUnresolvedReferences
class CustomFactory(Generic[T], DataclassFactory[T]):
    __is_base_factory__ = True
    __faker__ = Faker(locale='ru_RU')
    __randomize_collection_length__ = True
    __min_collection_length__ = 1
    __max_collection_length__ = 2
    __check_model__ = True


class InfoForPlanningDCFactory(CustomFactory[InfoForPlanning]):
    __allow_none_optionals__ = False
    capability: float = Use(CustomFactory.__faker__.pyfloat, positive=True)
    is_warehouse: bool = False
    common_capacity_per_hour: float | None = None
