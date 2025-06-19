import ulid
from sqlalchemy import CheckConstraint, ForeignKey, literal, text
from sqlalchemy.orm import Mapped, mapped_column

from common.orm_models.mixins import ActiveMixin, TimestampMixin
from common.resources.database.postgres.alchemy_related import Base

__all__ = (
    'OrganizationStockORM',
)


class OrganizationStockORM(TimestampMixin, ActiveMixin, Base):
    organization_id: Mapped[ulid.ULID] = mapped_column(
        ForeignKey('organization.id', ondelete='CASCADE', ),
        comment='Компания.',
        primary_key=True,
    )
    product_id: Mapped[ulid.ULID] = mapped_column(
        ForeignKey('product.id', ondelete='CASCADE', ),
        comment='Продукт.',
        primary_key=True,
    )
    in_stock: Mapped[float] = mapped_column(
        comment='Остаток продукта на складе.',
    )
    min_level: Mapped[float] = mapped_column(
        server_default=literal("0"),
        comment='Уровень, ниже которого остаток опускаться не должен.',
    )
    max_level: Mapped[float] = mapped_column(
        comment='Максимальная вместимость склада по данному продукту.',
        server_default=literal("Infinity"),
    )
    necessity: Mapped[float | None] = mapped_column(
        comment='Нужна в продукте переданная от организации',
    )
    __table_args__ = (
        CheckConstraint('in_stock > 0', name='in_stock_positive'),
        CheckConstraint('min_level > 0', name='min_level_positive'),
        CheckConstraint('max_level > 0', name='max_level_positive'),
        CheckConstraint('necessity > 0', name='necessity_level_positive'),
    )

    def __repr__(self) -> str:
        return f'Stock, org:{self.organization_id}/prod:{self.product_id}'
