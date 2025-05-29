"""Pgcrypto

Revision ID: 43716b86bda1
Revises: 683d2cff1768
Create Date: 2025-05-29 15:18:53.921574

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import common.orm_models.custom_types


# revision identifiers, used by Alembic.
revision: str = '43716b86bda1'
down_revision: Union[str, None] = '683d2cff1768'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP EXTENSION IF EXISTS pgcrypto;")
