

import sqlalchemy as sa
from sqlalchemy import TEXT
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.mutable import MutableList

from sqlalchemy.orm import Mapped, mapped_column

from common.orm_models.mixins import ActiveMixin, TimestampMixin
from common.resources.database.postgres import Base


# __all__ = (
#     'StandardORM',
# )
#
#
# class StandardORM(TimestampMixin, ActiveMixin, Base):
#     """
#     Стандарт продукта
#     """
#     designation: Mapped[str] = mapped_column(
#         primary_key=True,
#         comment='Код стандарта, например ГОСТ ХХ-ХХХ',
#     )
#     description: Mapped[str] = mapped_column(
#         comment='Краткое описание стандарта.',
#     )
#     OKS_CODE: Mapped[list[str]] = mapped_column(
#         MutableList.as_mutable(ARRAY(TEXT)),
#         comment='Код ОКС.'
#     )
#