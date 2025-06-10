"""Create extension timescale

Revision ID: 9dcd0336d4d2
Revises: 4329c53fa210
Create Date: 2025-06-10 16:29:55.794407

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import common.orm_models.custom_types


# revision identifiers, used by Alembic.
revision: str = '9dcd0336d4d2'
down_revision: Union[str, None] = '4329c53fa210'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        'CREATE EXTENSION IF NOT EXISTS timescaledb;'
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        'DROP EXTENSION IF EXISTS timescaledb;'
    )
