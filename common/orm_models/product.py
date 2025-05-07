import enum

import sqlalchemy as sa
import ulid
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column

from common.enums.product import ProductUnit
from common.orm_models.mixins import TimestampMixin
from common.resources.database.postgres import Base

__all__ = (
    'ProductORM',
)


class ProductORM(TimestampMixin, Base):
    """
    Продукт.
    """
    __tablename__ = 'product'

    id: Mapped[ulid.ULID] = mapped_column(
        primary_key=True,
        server_default=sa.func.gen_monotonic_ulid(),
    )
    name: Mapped[str]
    # category
    # standart
    unit: Mapped[enum.Enum] = mapped_column(ENUM(ProductUnit, validate_strings=True))

    def __repr__(self):
        return f'1 {self.unit} of {self.name}'
