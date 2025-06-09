import enum

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


# noinspection PyEnum
class Role(CaseInsensitiveMixin, enum.StrEnum):
    """
    Потребитель или производитель или накопитель продукта.
    """
    PRODUCER = enum.auto()
    CONSUMER = enum.auto()

