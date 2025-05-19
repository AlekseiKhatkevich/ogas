import ulid
from sqlalchemy import ForeignKey, UniqueConstraint, CheckConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from center.enums import Period
from center.orm_models import OrganizationORM
from common.orm_models import ProductORM
from common.orm_models.mixins import TimestampMixin
from common.resources.database.postgres.alchemy_related import Base, ULID_PK

__all__ = (
    'CapabilityORM',
)


class CapabilityORM(TimestampMixin, Base):
    id: Mapped[ULID_PK]
    organization_id: Mapped[ulid.ULID] = mapped_column(
        ForeignKey('organization.id', ondelete='CASCADE', ),
        comment='Компания.',
    )
    product_id: Mapped[ulid.ULID] = mapped_column(
        ForeignKey('product.id', ondelete='CASCADE', ),
        comment='Продукт.',
    )
    period: Mapped[Period] = mapped_column(
        comment='Период за который указана производительность.',
    )
    value: Mapped[int | None] = mapped_column(
        comment='Производительность, единиц товара.',
    )
    organization: Mapped['OrganizationORM'] = relationship(
        back_populates='capabilities',
    )
    product: Mapped['ProductORM'] = relationship(
        back_populates='capabilities',
    )

    __table_args__ = (
        UniqueConstraint('organization_id', 'product_id', 'period', ),
        CheckConstraint(text('value >= 0'), name='value_gt_0_check', ),
    )

    def __repr__(self):
        return f'Product {self.product_id} in {self.organization_id} per {self.period}.'

