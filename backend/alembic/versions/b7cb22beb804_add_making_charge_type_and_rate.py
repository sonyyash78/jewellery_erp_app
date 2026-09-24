"""Add making charge type and rate

Revision ID: b7cb22beb804
Revises: c74dc7ba0951
Create Date: 2026-08-02 00:04:18.874330

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'b7cb22beb804'
down_revision: Union[str, Sequence[str], None] = 'c74dc7ba0951'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('gold_calculations', sa.Column('making_charge_type', sa.String(length=20), nullable=False, server_default='flat'))
    op.add_column('gold_calculations', sa.Column('making_charge_rate', sa.DECIMAL(precision=10, scale=2), nullable=False, server_default='0.0'))
    
    op.add_column('silver_calculations', sa.Column('making_charge_type', sa.String(length=20), nullable=False, server_default='flat'))
    op.add_column('silver_calculations', sa.Column('making_charge_rate', sa.DECIMAL(precision=10, scale=2), nullable=False, server_default='0.0'))

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('silver_calculations', 'making_charge_rate')
    op.drop_column('silver_calculations', 'making_charge_type')
    
    op.drop_column('gold_calculations', 'making_charge_rate')
    op.drop_column('gold_calculations', 'making_charge_type')

