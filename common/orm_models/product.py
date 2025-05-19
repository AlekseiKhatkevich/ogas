from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from center.orm_models import CapabilityORM
from common.enums.product import ProductUnit
from common.orm_models.mixins import TimestampMixin
from common.resources.database.postgres.alchemy_related import Base, ULID_PK

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
    unit: Mapped[ProductUnit] = mapped_column(
        comment='Фасовка продукта.',
    )
    standard_code: Mapped[str] = mapped_column(
        ForeignKey('standard.code', ondelete='RESTRICT', ),
        comment='Код стандарта, например ГОСТ ХХ-ХХХ',
    )
    standard: Mapped['StandardORM'] = relationship(
        back_populates='products',
        innerjoin=True,
        passive_deletes=True,
    )
    categories: Mapped[list['CategoryORM']] = relationship(
        secondary='category_association_table',
        back_populates='products',
        cascade='all, delete',
    )
    capabilities: Mapped[list['CapabilityORM']] = relationship(
        back_populates='product',
    )

    __table_args__ = (
        UniqueConstraint('name', 'unit', 'standard_code',),
    )

    def __repr__(self):
        return f'1 {self.unit} of {self.name} acc. {self.standard_code}.'
