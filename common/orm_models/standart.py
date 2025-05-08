from sqlalchemy.orm import Mapped, mapped_column

from common.orm_models.mixins import ActiveMixin, TimestampMixin
from common.resources.database.postgres import Base

__all__ = (
    'StandardORM',
)


class StandardORM(TimestampMixin, ActiveMixin, Base):
    """
    Стандарт продукта.
    """
    code: Mapped[str] = mapped_column(
        primary_key=True,
        comment='Код стандарта, например ГОСТ ХХ-ХХХ',
    )
    description: Mapped[str] = mapped_column(
        comment='Краткое описание стандарта.',
    )
    oks_code: Mapped[list[str]] = mapped_column(
        comment='Код ОКС.'
    )

    def __repr__(self):
        return self.code
