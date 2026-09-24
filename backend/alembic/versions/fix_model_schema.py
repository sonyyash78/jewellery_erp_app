"""Fix model schema to match SQLAlchemy definitions

Revision ID: fix_model_schema
Revises: 9e5a866bbd8f
Create Date: 2026-07-31

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'fix_model_schema'
down_revision: Union[str, Sequence[str], None] = '9e5a866bbd8f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema to match current SQLAlchemy models."""
    
    # Create missing customer_addresses table
    op.create_table('customer_addresses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('address_line1', sa.Text(), nullable=False),
        sa.Column('address_line2', sa.Text(), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=False),
        sa.Column('state', sa.String(length=100), nullable=False),
        sa.Column('zip_code', sa.String(length=20), nullable=False),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default='0'),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_customer_addresses_customer_id', 'customer_addresses', ['customer_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema - reverse changes."""
    op.drop_table('customer_addresses')