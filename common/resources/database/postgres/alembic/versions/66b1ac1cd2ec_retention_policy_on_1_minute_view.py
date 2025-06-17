"""Retention policy on 1 minute view

Revision ID: 66b1ac1cd2ec
Revises: 4cf33b7e94ff
Create Date: 2025-06-17 15:35:19.370153

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import common.orm_models.custom_types
from center.orm_models import OperativeDataORM1MinuteView

# revision identifiers, used by Alembic.
revision: str = '66b1ac1cd2ec'
down_revision: Union[str, None] = '4cf33b7e94ff'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    OperativeDataORM1MinuteView.add_retention_policy(op)


def downgrade() -> None:
    """Downgrade schema."""
    OperativeDataORM1MinuteView.remove_retention_policy(op)
