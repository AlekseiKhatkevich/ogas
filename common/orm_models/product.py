import enum

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from common.enums.product import ProductUnit
from common.orm_models.mixins import TimestampMixin
from common.resources.database.postgres import Base
from common.resources.database.postgres.alchemy_related import ULID_PK

__all__ = (
    'ProductORM',
)


class ProductORM(TimestampMixin, Base):
    """
    Продукт.
    """
    __tablename__ = 'product'

    id: Mapped[ULID_PK]
    name: Mapped[str] = mapped_column(
        comment='Наименование продукта.',
    )
    # category
    unit: Mapped[enum.Enum] = mapped_column(
        ENUM(ProductUnit, validate_strings=True),
        comment='Категория продукта',
    )
    standard_code: Mapped[str] = mapped_column(
        ForeignKey('standard.code'),
        comment='Код стандарта, например ГОСТ ХХ-ХХХ',
    )
    standard: Mapped['StandardORM'] = relationship(back_populates='products')

    def __repr__(self):
        return f'1 {self.unit} of {self.name} acc. {self.standard_code}.'
