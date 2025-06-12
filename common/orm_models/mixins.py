import datetime

from sqlalchemy import Boolean, Column, FetchedValue, false, func, true
from sqlalchemy.orm import Mapped, declared_attr, mapped_column


class TimestampMixin:
    """
    Для добавления полей created_at, updated_at к конкретный класс."
    """
    created_at: Mapped[datetime.datetime] = mapped_column(
        server_default=func.Now(),
        nullable=False,
        comment='Время создания.',
    )
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        onupdate=func.Now(),
        comment='Время обновления.',
        server_onupdate=FetchedValue(for_update=True),
    )
    __mapper_args__ = {'eager_defaults': True}


class ActiveMixin:
    """
    Для добавления поля is_active.
    """
    default_is_active: bool = True

    # noinspection PyNestedDecorators
    @declared_attr
    @classmethod
    def is_active(cls):
        return Column(
            Boolean,
            nullable=False,
            server_default=true() if cls.default_is_active else false(),
            comment='Признак активности.'
        )
