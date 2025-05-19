from sqlalchemy.orm import Mapped, mapped_column

from common.orm_models.mixins import ActiveMixin, TimestampMixin
from common.resources.database.postgres.alchemy_related import Base, ULID_PK

__all__ = (
    'OrganizationORM',
)


class OrganizationORM(TimestampMixin, ActiveMixin,  Base):
    """
    Организация.
    """
    id: Mapped[ULID_PK]
    name: Mapped[str] = mapped_column(
        comment='Название организации.',
        unique=True,
    )

    def __repr__(self):
        return self.name[:50]

