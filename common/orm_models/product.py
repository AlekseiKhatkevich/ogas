import enum

import ulid
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column

from common.enums.product import ProductUnit
from common.resources.database.postgres import Base

__all__ = (
    'ProductORM',
)

from sqlalchemy import Column
from sqlalchemy.types import UserDefinedType


class ULID(UserDefinedType):
    cache_ok = True

    # def __init__(self, precision=8):
    #     self.precision = precision

    def get_col_spec(self, **kw):
        return 'ULID'

    def bind_processor(self, dialect):
        def process(value):
            return str(value)

        return process

    def result_processor(self, dialect, coltype):
        def process(value):
            return ulid.ULID.from_str(value) if value is not None else value

        return process


class ProductORM(Base):
    """
    Продукт.
    """
    __tablename__ = 'product'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    # category
    # standart
    unit: Mapped[enum.Enum] = mapped_column(ENUM(ProductUnit, validate_strings=True))
    ident = Column(ULID)

    def __repr__(self):
        return f'1 {self.unit} of {self.name}'
