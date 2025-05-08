import enum

from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column

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
    # standart
    unit: Mapped[enum.Enum] = mapped_column(
        ENUM(ProductUnit, validate_strings=True),
        comment='Категория продукта',
    )

    def __repr__(self):
        return f'1 {self.unit} of {self.name}'
