from sqlalchemy import Computed, VARCHAR, Table, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from common.orm_models.mixins import TimestampMixin
from common.resources.database.postgres.alchemy_related import Base

__all__ = (
    'CategoryORM',
    'category_association_table',
    'ProductCategoryM2MIntermediate',
)


class CategoryORM(TimestampMixin, Base):
    """
    Категория продукта (напитки, одежда, итд).
    """
    code: Mapped[str] = mapped_column(
        VARCHAR(length=12),
        primary_key=True,
        comment='Код категории продукта.'
    )
    name: Mapped[str] = mapped_column(
        comment='Наименование категории продукта.',
    )
    main_prefix: Mapped[str] = mapped_column(
        VARCHAR(length=2),
        Computed('code::varchar(2)'),
        comment='Главный префикс кода (главная категория).',
    )
    products: Mapped[list['ProductORM']] = relationship(
        secondary='category_association_table',
        back_populates='categories',
        passive_deletes=True,
    )

    def __repr__(self):
        return f'{self.__class__.__name__}({self.code})'


category_association_table = Table(
    'category_association_table',
    Base.metadata,
    Column(
        'product_id',
        ForeignKey('product.id', ondelete='CASCADE', ),
        primary_key=True,
    ),
    Column(
        "category_code",
        ForeignKey('category.code', ondelete='CASCADE',),
        primary_key=True,
    ),
)


class ProductCategoryM2MIntermediate(Base):
    __table__ = category_association_table
