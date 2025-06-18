import ulid
from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint, text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from center.enums import Period, Role
from common.orm_models.mixins import TimestampMixin
from common.resources.database.postgres.alchemy_related import Base, ULID_PK

__all__ = (
    'CapabilityORM',
)


class CapabilityORM(TimestampMixin, Base):
    """
    Производительность / потребление организацией продукта.
    """
    id: Mapped[ulid.ULID] = mapped_column(
        comment='id',
        nullable=False,
        server_default=func.gen_monotonic_ulid(),
    )
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
    role: Mapped[Role] = mapped_column(
        comment='В качестве производителя или потребителя товара.',
    )
    value: Mapped[int | None] = mapped_column(
        comment='Производительность, единиц товара.',
    )
    organization: Mapped['OrganizationORM'] = relationship(
        back_populates='capabilities',
        passive_deletes=True,
        cascade='save-update',
        innerjoin=True,
        lazy='joined',
    )
    product: Mapped['ProductORM'] = relationship(
        passive_deletes=True,
    )
    __table_args__ = (
        UniqueConstraint('product_id', 'organization_id', 'period', 'role', ),
        CheckConstraint(text('value >= 0'), name='value_gt_0_check', ),
        {'postgresql_partition_by': 'LIST (role)'},
    )
    __mapper_args__ = {
        'primary_key': ['id', ],
    }

    def __repr__(self):
        return f'Product {self.product_id} in {self.organization_id} per {self.period}.'

