"""make_customer_id_optional_in_invoice

Revision ID: 9b6b04422a8e
Revises: fix_model_schema
Create Date: 2026-08-01 12:31:33.920121

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9b6b04422a8e'
down_revision: Union[str, Sequence[str], None] = 'fix_model_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('invoices', 'customer_id',
               existing_type=sa.Integer(),
               nullable=True)
    op.drop_constraint('invoices_ibfk_1', 'invoices', type_='foreignkey')
    op.create_foreign_key('invoices_ibfk_1', 'invoices', 'customers', ['customer_id'], ['id'], ondelete='SET NULL')

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('invoices_ibfk_1', 'invoices', type_='foreignkey')
    op.alter_column('invoices', 'customer_id',
               existing_type=sa.Integer(),
               nullable=False)
    op.create_foreign_key('invoices_ibfk_1', 'invoices', 'customers', ['customer_id'], ['id'], ondelete='RESTRICT')
