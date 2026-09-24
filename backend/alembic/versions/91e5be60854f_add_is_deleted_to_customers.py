"""add is_deleted to customers

Revision ID: 91e5be60854f
Revises: 0ba5cd488db8
Create Date: 2026-07-30 18:33:27.311254

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '91e5be60854f'
down_revision: Union[str, Sequence[str], None] = '0ba5cd488db8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('customers', sa.Column('is_deleted', sa.Boolean(), nullable=True, server_default='0'))
    op.alter_column('customers', 'is_deleted', existing_type=sa.Boolean(), nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    pass
