"""Continuouse policy on 1 minute view

Revision ID: beb6a004c944
Revises: 66b1ac1cd2ec
Create Date: 2025-06-17 16:35:25.883408

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import common.orm_models.custom_types
from center.orm_models import OperativeDataORM1MinuteView

# revision identifiers, used by Alembic.
revision: str = 'beb6a004c944'
down_revision: Union[str, None] = '66b1ac1cd2ec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    OperativeDataORM1MinuteView.add_continuous_aggregate_policy(op)


def downgrade() -> None:
    """Downgrade schema."""
    OperativeDataORM1MinuteView.remove_continuous_aggregate_policy(op)
