from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ENUM

from common.enums.product import ProductUnit
from common.resources.database.postgres import Base


class ProductORM(Base):
    """
    Продукт.
    """
    __tablename__ = 'product'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    # category
    # standart
    unit: Mapped[ENUM] = mapped_column(ENUM(ProductUnit, validate_strings=True))

    def __repr__(self):
        return f'1 {self.unit} of {self.name}'
