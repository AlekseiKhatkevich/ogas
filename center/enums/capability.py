import enum
from functools import cached_property

from utils.enums import CaseInsensitiveMixin


# noinspection PyEnum
class Period(CaseInsensitiveMixin, enum.StrEnum):
    """
    Период времени.
    """
    HOUR = enum.auto()
    DAY = enum.auto()
    WEEK = enum.auto()
    MONTH = enum.auto()
    QUARTER = enum.auto()
    YEAR = enum.auto()

    @cached_property
    def to_hours(self) -> int:
        match self:
            case self.HOUR:
                return 1
            case self.DAY:
                return self.HOUR.to_hours * 24
            case self.WEEK:
                return self.DAY.to_hours * 7
            case self.MONTH:
                return self.DAY.to_hours * 30
            case self.QUARTER:
                return self.MONTH.to_hours * 3
            case self.YEAR:
                return self.DAY.to_hours * 364
        raise NotImplemented()


# noinspection PyEnum
class Role(CaseInsensitiveMixin, enum.StrEnum):
    """
    Потребитель или производитель или накопитель продукта.
    """
    PRODUCER = enum.auto()
    CONSUMER = enum.auto()

