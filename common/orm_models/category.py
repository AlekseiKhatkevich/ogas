from sqlalchemy import Computed, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column

from common.orm_models.mixins import TimestampMixin
from common.resources.database.postgres import Base

__all__ = (
    'CategoryORM',
)


class CategoryORM(TimestampMixin, Base):
    """
    Категория продукта (напитки, одежда, итд)
    """
    code: Mapped[str] = mapped_column(
        VARCHAR(length=12),
        primary_key=True,
        comment='Код категории продукта.'
    )
    name: Mapped[str] = mapped_column(
        comment='Наименование категории продукта.',
    )#№ несколько категорий на 1 продукт
    main_prefix: Mapped[str] = mapped_column(
        VARCHAR(length=2),
        Computed('code::varchar(2)'),
        comment='Главный префикс кода (главная категория).',
    )

    def __repr__(self):
        return f'{self.__class__.__name__}({self.code})'
