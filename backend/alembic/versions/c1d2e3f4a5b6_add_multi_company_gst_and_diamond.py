"""Add multi-company, GST engine tables, diamond calculations, and invoice snapshots

Revision ID: c1d2e3f4a5b6
Revises: f2c3d4e5f6a7
Create Date: 2026-11-07 22:45:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision: str = 'c1d2e3f4a5b6'
down_revision: Union[str, Sequence[str], None] = 'f2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    tables = insp.get_table_names()

    # 1. Create `companies` table
    if 'companies' not in tables:
        op.create_table(
            'companies',
            sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('code', sa.String(length=20), nullable=False),
            sa.Column('name', sa.String(length=150), nullable=False),
            sa.Column('address', sa.Text(), nullable=True),
            sa.Column('city', sa.String(length=100), nullable=True),
            sa.Column('state', sa.String(length=100), nullable=True),
            sa.Column('state_code', sa.String(length=10), nullable=True),
            sa.Column('gstin', sa.String(length=20), nullable=True),
            sa.Column('pan', sa.String(length=20), nullable=True),
            sa.Column('phone', sa.String(length=50), nullable=True),
            sa.Column('email', sa.String(length=100), nullable=True),
            sa.Column('gst_enabled', sa.Boolean(), nullable=False, server_default=sa.text('0')),
            sa.Column('diamond_enabled', sa.Boolean(), nullable=False, server_default=sa.text('1')),
            sa.Column('invoice_prefix', sa.String(length=20), nullable=False, server_default='INV'),
            sa.Column('invoice_series', sa.String(length=20), nullable=False, server_default='S'),
            sa.Column('bank_name', sa.String(length=100), nullable=True),
            sa.Column('bank_account_no', sa.String(length=50), nullable=True),
            sa.Column('bank_ifsc', sa.String(length=20), nullable=True),
            sa.Column('bank_branch', sa.String(length=100), nullable=True),
            sa.Column('upi_id', sa.String(length=50), nullable=True),
            sa.Column('upi_name', sa.String(length=100), nullable=True),
            sa.Column('logo_url', sa.String(length=255), nullable=True),
            sa.Column('signature_url', sa.String(length=255), nullable=True),
            sa.Column('stamp_url', sa.String(length=255), nullable=True),
            sa.Column('declaration', sa.Text(), nullable=True),
            sa.Column('jurisdiction_city', sa.String(length=100), nullable=True),
            sa.Column('tax_label_style', sa.String(length=50), nullable=False, server_default='STANDARD'),
            sa.Column('computer_generated_note', sa.String(length=255), nullable=False, server_default='This is a computer generated invoice.'),
            sa.Column('financial_year_start', sa.Integer(), nullable=False, server_default='4'),
            sa.Column('rounding_mode', sa.String(length=20), nullable=False, server_default='HALF_UP'),
            sa.Column('storage_root', sa.String(length=255), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('1')),
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('code', name='uq_companies_code')
        )

    # 2. Seed initial companies: Company 1 (Saideep, non-GST), Company 2 (Pride Gold, GST), Company 3 (Inactive)
    existing_companies = bind.execute(sa.text("SELECT COUNT(*) FROM companies")).scalar()
    if existing_companies == 0:
        bind.execute(sa.text("""
            INSERT INTO companies (
                id, code, name, address, city, state, state_code, gstin, pan, phone, email,
                gst_enabled, diamond_enabled, invoice_prefix, invoice_series,
                declaration, jurisdiction_city, tax_label_style, is_active
            ) VALUES
            (1, 'SAIDEEP', 'SAIDEEP JEWELLERS', 'Takhatgarh khedawas, 167, Ward No. 3, Khedawas, Takhatgarh, Pali (Raj.)-306912', 'Takhatgarh', 'Rajasthan', '08', '', '', '8504837854', 'saideepjewellers78@gmail.com',
             0, 1, 'INV', 'S',
             'Goods once sold will not be taken back or exchanged.', 'Takhatgarh', 'STANDARD', 1),
            (2, 'PRIDE_GOLD', 'PRIDE GOLD', '1st Floor, Near Koira Ji ka Bera, Ghodo ka Chowk, Sojati Gate, Jodhpur (Raj.)- 342001', 'Jodhpur', 'Rajasthan', '08', '08AEZPK5007N1ZS', 'AEZPK5007N', '0291-2640999,+91-9929562800', 'info.pridegoldjdr@gmail.com',
             1, 1, 'PG', 'S',
             'We declare that this invoice shows the actual price of the goods described and that all particulars are true and correct.', 'JODHPUR', 'GST', 1),
            (3, 'CO3', 'Company 3 Placeholder', 'Takhatgarh', 'Takhatgarh', 'Rajasthan', '08', '', '', '', '',
             0, 1, 'CO3', 'S',
             '', 'Takhatgarh', 'STANDARD', 0)
        """))

    # 3. Create `company_number_sequences` table
    if 'company_number_sequences' not in tables:
        op.create_table(
            'company_number_sequences',
            sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('company_id', sa.Integer(), nullable=False),
            sa.Column('financial_year', sa.String(length=10), nullable=False),
            sa.Column('doc_type', sa.String(length=20), nullable=False),
            sa.Column('last_sequence', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('prefix', sa.String(length=20), nullable=True),
            sa.Column('series', sa.String(length=20), nullable=True),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
            sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('company_id', 'financial_year', 'doc_type', name='uq_company_fy_doctype')
        )
        op.create_index('ix_cns_company_id', 'company_number_sequences', ['company_id'])

    # 4. Create `hsn_master` table
    if 'hsn_master' not in tables:
        op.create_table(
            'hsn_master',
            sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('hsn_code', sa.String(length=20), nullable=False),
            sa.Column('description', sa.String(length=255), nullable=False),
            sa.Column('category', sa.String(length=50), nullable=False),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('1')),
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('hsn_code', name='uq_hsn_master_code')
        )
        op.create_index('ix_hsn_category', 'hsn_master', ['category'])

        # Seed initial HSNs
        bind.execute(sa.text("""
            INSERT INTO hsn_master (hsn_code, description, category, is_active) VALUES
            ('71081200', 'Gold Bar / Bullion', 'GOLD', 1),
            ('711319', 'Gold Jewellery / Ornaments', 'GOLD', 1),
            ('71069120', 'Silver Bar / Bullion', 'SILVER', 1),
            ('711311', 'Silver Jewellery / Articles', 'SILVER', 1),
            ('71042120', 'Synthetic Diamond (Unworked)', 'DIAMOND', 1),
            ('71049120', 'Synthetic Diamond (Cut & Polished)', 'DIAMOND', 1),
            ('71023910', 'Natural Diamond (Cut & Polished)', 'DIAMOND', 1)
        """))

    # 5. Create `gst_rate_master` table
    if 'gst_rate_master' not in tables:
        op.create_table(
            'gst_rate_master',
            sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('hsn_code', sa.String(length=20), nullable=False),
            sa.Column('total_rate', sa.DECIMAL(precision=6, scale=4), nullable=False),
            sa.Column('cgst_rate', sa.DECIMAL(precision=6, scale=4), nullable=False),
            sa.Column('sgst_rate', sa.DECIMAL(precision=6, scale=4), nullable=False),
            sa.Column('igst_rate', sa.DECIMAL(precision=6, scale=4), nullable=False),
            sa.Column('description', sa.String(length=255), nullable=True),
            sa.Column('effective_from', sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.Column('effective_to', sa.DateTime(), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('1')),
            sa.Column('updated_by', sa.Integer(), nullable=True),
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['hsn_code'], ['hsn_master.hsn_code'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ondelete='SET NULL'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('ix_gst_rate_hsn', 'gst_rate_master', ['hsn_code'])

        # Seed GST Rates
        bind.execute(sa.text("""
            INSERT INTO gst_rate_master (hsn_code, total_rate, cgst_rate, sgst_rate, igst_rate, description) VALUES
            ('71081200', 3.0000, 1.5000, 1.5000, 3.0000, 'Gold Bullion 3% GST'),
            ('711319', 3.0000, 1.5000, 1.5000, 3.0000, 'Gold Ornaments 3% GST'),
            ('71069120', 3.0000, 1.5000, 1.5000, 3.0000, 'Silver Bar 3% GST (Pride Reference 71069120)'),
            ('711311', 3.0000, 1.5000, 1.5000, 3.0000, 'Silver Ornaments 3% GST'),
            ('71042120', 0.2500, 0.1250, 0.1250, 0.2500, 'Synthetic Diamond Unworked 0.25% GST'),
            ('71049120', 1.5000, 0.7500, 0.7500, 1.5000, 'Synthetic Diamond Cut & Polished 1.5% GST'),
            ('71023910', 1.5000, 0.7500, 0.7500, 1.5000, 'Natural Diamond Cut & Polished 1.5% GST')
        """))

    # 6. Create `state_codes` table
    if 'state_codes' not in tables:
        op.create_table(
            'state_codes',
            sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('code', sa.String(length=10), nullable=False),
            sa.Column('state_name', sa.String(length=100), nullable=False),
            sa.Column('state_type', sa.String(length=20), nullable=False, server_default='STATE'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('code', name='uq_state_code')
        )
        op.create_index('ix_state_code_name', 'state_codes', ['state_name'])

        # Seed all 37 Indian States and Union Territories
        bind.execute(sa.text("""
            INSERT INTO state_codes (code, state_name, state_type) VALUES
            ('01', 'Jammu & Kashmir', 'UT'),
            ('02', 'Himachal Pradesh', 'STATE'),
            ('03', 'Punjab', 'STATE'),
            ('04', 'Chandigarh', 'UT'),
            ('05', 'Uttarakhand', 'STATE'),
            ('06', 'Haryana', 'STATE'),
            ('07', 'Delhi', 'UT'),
            ('08', 'Rajasthan', 'STATE'),
            ('09', 'Uttar Pradesh', 'STATE'),
            ('10', 'Bihar', 'STATE'),
            ('11', 'Sikkim', 'STATE'),
            ('12', 'Arunachal Pradesh', 'STATE'),
            ('13', 'Nagaland', 'STATE'),
            ('14', 'Manipur', 'STATE'),
            ('15', 'Mizoram', 'STATE'),
            ('16', 'Tripura', 'STATE'),
            ('17', 'Meghalaya', 'STATE'),
            ('18', 'Assam', 'STATE'),
            ('19', 'West Bengal', 'STATE'),
            ('20', 'Jharkhand', 'STATE'),
            ('21', 'Odisha', 'STATE'),
            ('22', 'Chhattisgarh', 'STATE'),
            ('23', 'Madhya Pradesh', 'STATE'),
            ('24', 'Gujarat', 'STATE'),
            ('25', 'Daman & Diu', 'UT'),
            ('26', 'Dadra & Nagar Haveli', 'UT'),
            ('27', 'Maharashtra', 'STATE'),
            ('28', 'Andhra Pradesh (Old)', 'STATE'),
            ('29', 'Karnataka', 'STATE'),
            ('30', 'Goa', 'STATE'),
            ('31', 'Lakshadweep', 'UT'),
            ('32', 'Kerala', 'STATE'),
            ('33', 'Tamil Nadu', 'STATE'),
            ('34', 'Puducherry', 'UT'),
            ('35', 'Andaman & Nicobar Islands', 'UT'),
            ('36', 'Telangana', 'STATE'),
            ('37', 'Andhra Pradesh', 'STATE'),
            ('38', 'Ladakh', 'UT')
        """))

    # 7. Add `company_id` to business tables & backfill
    business_tables = [
        'invoices',
        'purchases',
        'exchanges',
        'stock_items',
        'customers',
        'sellers',
        'customer_ledgers',
        'supplier_ledgers',
        'metal_rates',
        'audit_logs'
    ]

    for tbl in business_tables:
        if tbl in tables:
            cols = {c['name'] for c in insp.get_columns(tbl)}
            if 'company_id' not in cols:
                op.add_column(tbl, sa.Column('company_id', sa.Integer(), nullable=True))
                # Backfill existing rows with company_id = 1
                bind.execute(sa.text(f"UPDATE `{tbl}` SET company_id = 1 WHERE company_id IS NULL"))
                # Add index
                op.create_index(f'ix_{tbl}_company_id', tbl, ['company_id'])
                # Add FK constraint
                op.create_foreign_key(f'fk_{tbl}_company_id', tbl, 'companies', ['company_id'], ['id'], ondelete='CASCADE')

    # 8. Add invoice snapshot & hash columns to `invoices`
    if 'invoices' in tables:
        inv_cols = {c['name'] for c in insp.get_columns('invoices')}
        if 'seller_snapshot_json' not in inv_cols:
            op.add_column('invoices', sa.Column('seller_snapshot_json', sa.Text(), nullable=True))
        if 'buyer_snapshot_json' not in inv_cols:
            op.add_column('invoices', sa.Column('buyer_snapshot_json', sa.Text(), nullable=True))
        if 'tax_summary_json' not in inv_cols:
            op.add_column('invoices', sa.Column('tax_summary_json', sa.Text(), nullable=True))
        if 'pdf_path' not in inv_cols:
            op.add_column('invoices', sa.Column('pdf_path', sa.String(length=500), nullable=True))
        if 'sha256_hash' not in inv_cols:
            op.add_column('invoices', sa.Column('sha256_hash', sa.String(length=64), nullable=True))

    # 9. Create `invoice_gst_lines` table
    if 'invoice_gst_lines' not in tables:
        op.create_table(
            'invoice_gst_lines',
            sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('invoice_id', sa.Integer(), nullable=False),
            sa.Column('invoice_item_id', sa.Integer(), nullable=True),
            sa.Column('hsn_code', sa.String(length=20), nullable=False),
            sa.Column('taxable_amount', sa.DECIMAL(precision=12, scale=2), nullable=False),
            sa.Column('gst_rate', sa.DECIMAL(precision=6, scale=4), nullable=False),
            sa.Column('cgst_rate', sa.DECIMAL(precision=6, scale=4), nullable=False, server_default='0'),
            sa.Column('cgst_amount', sa.DECIMAL(precision=12, scale=2), nullable=False, server_default='0'),
            sa.Column('sgst_rate', sa.DECIMAL(precision=6, scale=4), nullable=False, server_default='0'),
            sa.Column('sgst_amount', sa.DECIMAL(precision=12, scale=2), nullable=False, server_default='0'),
            sa.Column('igst_rate', sa.DECIMAL(precision=6, scale=4), nullable=False, server_default='0'),
            sa.Column('igst_amount', sa.DECIMAL(precision=12, scale=2), nullable=False, server_default='0'),
            sa.Column('total_tax_amount', sa.DECIMAL(precision=12, scale=2), nullable=False),
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
            sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['invoice_item_id'], ['invoice_items.id'], ondelete='SET NULL'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('ix_igl_invoice_id', 'invoice_gst_lines', ['invoice_id'])
        op.create_index('ix_igl_hsn_code', 'invoice_gst_lines', ['hsn_code'])

    # 10. Create `invoice_einvoice` table
    if 'invoice_einvoice' not in tables:
        op.create_table(
            'invoice_einvoice',
            sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('invoice_id', sa.Integer(), nullable=False),
            sa.Column('irn', sa.String(length=100), nullable=True),
            sa.Column('ack_no', sa.String(length=50), nullable=True),
            sa.Column('ack_date', sa.String(length=50), nullable=True),
            sa.Column('qr_data', sa.Text(), nullable=True),
            sa.Column('qr_image_url', sa.String(length=255), nullable=True),
            sa.Column('entered_by', sa.Integer(), nullable=True),
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['entered_by'], ['users.id'], ondelete='SET NULL'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('invoice_id', name='uq_einvoice_invoice_id')
        )
        op.create_index('ix_einvoice_irn', 'invoice_einvoice', ['irn'])

    # 11. Create `diamond_calculations` table
    if 'diamond_calculations' not in tables:
        op.create_table(
            'diamond_calculations',
            sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('invoice_item_id', sa.Integer(), nullable=True),
            sa.Column('purchase_item_id', sa.Integer(), nullable=True),
            sa.Column('exchange_item_id', sa.Integer(), nullable=True),
            sa.Column('diamond_type', sa.String(length=50), nullable=False, server_default='NATURAL'),
            sa.Column('diamond_form', sa.String(length=50), nullable=False, server_default='CUT_AND_POLISHED'),
            sa.Column('shape', sa.String(length=50), nullable=True),
            sa.Column('carat_weight', sa.DECIMAL(precision=10, scale=4), nullable=False, server_default='0.0000'),
            sa.Column('pieces', sa.Integer(), nullable=False, server_default='1'),
            sa.Column('colour', sa.String(length=20), nullable=True),
            sa.Column('clarity', sa.String(length=20), nullable=True),
            sa.Column('cut', sa.String(length=20), nullable=True),
            sa.Column('certificate_no', sa.String(length=100), nullable=True),
            sa.Column('certifying_lab', sa.String(length=50), nullable=True),
            sa.Column('rate_per_carat', sa.DECIMAL(precision=12, scale=2), nullable=False, server_default='0.00'),
            sa.Column('subtotal_diamond_value', sa.DECIMAL(precision=12, scale=2), nullable=False, server_default='0.00'),
            sa.Column('discount', sa.DECIMAL(precision=12, scale=2), nullable=False, server_default='0.00'),
            sa.Column('making_charges', sa.DECIMAL(precision=12, scale=2), nullable=False, server_default='0.00'),
            sa.Column('other_charges', sa.DECIMAL(precision=12, scale=2), nullable=False, server_default='0.00'),
            sa.Column('total_diamond_value', sa.DECIMAL(precision=12, scale=2), nullable=False, server_default='0.00'),
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['invoice_item_id'], ['invoice_items.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['purchase_item_id'], ['purchase_items.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['exchange_item_id'], ['exchange_items.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('ix_dc_invoice_item_id', 'diamond_calculations', ['invoice_item_id'])
        op.create_index('ix_dc_purchase_item_id', 'diamond_calculations', ['purchase_item_id'])
        op.create_index('ix_dc_exchange_item_id', 'diamond_calculations', ['exchange_item_id'])


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    tables = insp.get_table_names()

    # Drop child tables first
    if 'diamond_calculations' in tables:
        op.drop_table('diamond_calculations')
    if 'invoice_einvoice' in tables:
        op.drop_table('invoice_einvoice')
    if 'invoice_gst_lines' in tables:
        op.drop_table('invoice_gst_lines')

    # Remove snapshot columns from invoices
    if 'invoices' in tables:
        inv_cols = {c['name'] for c in insp.get_columns('invoices')}
        for col in ['sha256_hash', 'pdf_path', 'tax_summary_json', 'buyer_snapshot_json', 'seller_snapshot_json']:
            if col in inv_cols:
                op.drop_column('invoices', col)

    # Drop FK and company_id columns from business tables
    business_tables = [
        'audit_logs', 'metal_rates', 'supplier_ledgers', 'customer_ledgers',
        'sellers', 'customers', 'stock_items', 'exchanges', 'purchases', 'invoices'
    ]
    for tbl in business_tables:
        if tbl in tables:
            fks = {fk['name'] for fk in insp.get_foreign_keys(tbl)}
            if f'fk_{tbl}_company_id' in fks:
                op.drop_constraint(f'fk_{tbl}_company_id', tbl, type_='foreignkey')
            indexes = {idx['name'] for idx in insp.get_indexes(tbl)}
            if f'ix_{tbl}_company_id' in indexes:
                op.drop_index(f'ix_{tbl}_company_id', tbl)
            cols = {c['name'] for c in insp.get_columns(tbl)}
            if 'company_id' in cols:
                op.drop_column(tbl, 'company_id')

    if 'state_codes' in tables:
        op.drop_table('state_codes')
    if 'gst_rate_master' in tables:
        op.drop_table('gst_rate_master')
    if 'hsn_master' in tables:
        op.drop_table('hsn_master')
    if 'company_number_sequences' in tables:
        op.drop_table('company_number_sequences')
    if 'companies' in tables:
        op.drop_table('companies')
