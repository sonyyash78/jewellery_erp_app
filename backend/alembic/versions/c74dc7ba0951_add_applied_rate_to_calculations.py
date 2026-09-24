"""add applied_rate to calculations

Revision ID: c74dc7ba0951
Revises: 9b6b04422a8e
Create Date: 2026-08-01 12:45:04.177390

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'c74dc7ba0951'
down_revision: Union[str, Sequence[str], None] = '9b6b04422a8e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('gold_calculations', sa.Column('applied_rate', sa.DECIMAL(precision=10, scale=2), nullable=False, server_default='0.00'))
    op.alter_column('gold_calculations', 'metal_rate_id',
               existing_type=mysql.INTEGER(),
               nullable=True)
    
    op.add_column('silver_calculations', sa.Column('applied_rate', sa.DECIMAL(precision=10, scale=2), nullable=False, server_default='0.00'))
    op.alter_column('silver_calculations', 'metal_rate_id',
               existing_type=mysql.INTEGER(),
               nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('silver_calculations', 'metal_rate_id',
               existing_type=mysql.INTEGER(),
               nullable=False)
    op.drop_column('silver_calculations', 'applied_rate')
    
    op.alter_column('gold_calculations', 'metal_rate_id',
               existing_type=mysql.INTEGER(),
               nullable=False)
    op.drop_column('gold_calculations', 'applied_rate')
    # ### end Alembic commands ###
