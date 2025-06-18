"""Add columnstore policy on 1m matview

Revision ID: 70f6f87931a1
Revises: beb6a004c944
Create Date: 2025-06-18 13:32:36.645931

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import common.orm_models.custom_types
from center.orm_models import OperativeDataORM1MinuteView

# revision identifiers, used by Alembic.
revision: str = '70f6f87931a1'
down_revision: Union[str, None] = 'beb6a004c944'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    OperativeDataORM1MinuteView.add_columnstore_policy(op)


def downgrade() -> None:
    """Downgrade schema."""
    OperativeDataORM1MinuteView.remove_columnstore_policy(op)
