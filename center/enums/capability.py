import enum


class Period(str, enum.Enum):
    """
    Период времени.
    """
    HOUR = 'hour'
    DAY = 'day'
    WEEK = 'week'
    MONTH = 'month'
    QUARTER = 'quarter'
    YEAR = 'year'

