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
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        nullable=True,
        onupdate=func.Now(),
        server_onupdate=FetchedValue(),
    )
    __mapper_args__ = {'eager_defaults': True}


class ActiveMixin:
    """
    Для добавления поля is_active.
    """

    def __init_subclass__(cls, default_is_active:bool = True, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        cls.default_is_active = default_is_active

    default_is_active: bool
    # is_active: Mapped[bool] = mapped_column(
    #     default=True,
    #     nullable=False,
    # )

    # noinspection PyNestedDecorators
    @declared_attr
    @classmethod
    def is_active(cls):
        return Column(
            Boolean,
            # default=cls.default_is_active,
            nullable=False,
            server_default=true() if cls.default_is_active else false()
        )
