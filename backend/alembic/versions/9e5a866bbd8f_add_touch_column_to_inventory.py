"""Add touch column to inventory

Revision ID: 9e5a866bbd8f
Revises: 35c06be254b1
Create Date: 2026-07-30 19:24:22.420018

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9e5a866bbd8f'
down_revision: Union[str, Sequence[str], None] = '35c06be254b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('inventory', sa.Column('touch', sa.Numeric(precision=5, scale=2), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('inventory', 'touch')
