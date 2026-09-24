"""add is_deleted to suppliers

Revision ID: 35c06be254b1
Revises: 91e5be60854f
Create Date: 2026-07-30 18:34:48.002394

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '35c06be254b1'
down_revision: Union[str, Sequence[str], None] = '91e5be60854f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('suppliers', sa.Column('is_deleted', sa.Boolean(), nullable=True, server_default='0'))
    op.alter_column('suppliers', 'is_deleted', existing_type=sa.Boolean(), nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    pass
