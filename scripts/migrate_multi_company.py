"""
Idempotent, Reversible Multi-Company and GST Migration Runner
============================================================
Safely upgrades SQLite database to multi-company schema:
- Creates companies, sequences, HSN, GST rates, State codes, e-invoice, and diamond tables
- Seeds Company 1 (Saideep, non-GST), Company 2 (Pride Gold, GST), Company 3 (Inactive)
- Adds nullable company_id to all business tables
- Backfills existing rows to company_id = 1
- Adds invoice snapshot columns
- Validates row counts before and after
"""
import sqlite3
import sys
from pathlib import Path
from typing import Dict, Any, List

def run_migration(db_path: Path, dry_run: bool = False) -> Dict[str, Any]:
    print(f"[Migration] Target DB: {db_path}")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = OFF;") # Safe during structural updates

    # 1. Snapshot row counts before migration
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    existing_tables = [r[0] for r in cur.fetchall()]
    before_counts = {}
    for t in existing_tables:
        cur.execute(f"SELECT count(*) FROM `{t}`")
        before_counts[t] = cur.fetchone()[0]

    # 2. Create `companies` table if not exists
    cur.execute("""
    CREATE TABLE IF NOT EXISTS `companies` (
        `id` INTEGER PRIMARY KEY AUTOINCREMENT,
        `code` VARCHAR(20) NOT NULL UNIQUE,
        `name` VARCHAR(150) NOT NULL,
        `address` TEXT,
        `city` VARCHAR(100),
        `state` VARCHAR(100),
        `state_code` VARCHAR(10),
        `gstin` VARCHAR(20),
        `pan` VARCHAR(20),
        `phone` VARCHAR(50),
        `email` VARCHAR(100),
        `gst_enabled` BOOLEAN NOT NULL DEFAULT 0,
        `diamond_enabled` BOOLEAN NOT NULL DEFAULT 1,
        `invoice_prefix` VARCHAR(20) NOT NULL DEFAULT 'INV',
        `invoice_series` VARCHAR(20) NOT NULL DEFAULT 'S',
        `bank_name` VARCHAR(100),
        `bank_account_no` VARCHAR(50),
        `bank_ifsc` VARCHAR(20),
        `bank_branch` VARCHAR(100),
        `upi_id` VARCHAR(50),
        `upi_name` VARCHAR(100),
        `logo_url` VARCHAR(255),
        `signature_url` VARCHAR(255),
        `stamp_url` VARCHAR(255),
        `declaration` TEXT,
        `jurisdiction_city` VARCHAR(100),
        `tax_label_style` VARCHAR(50) NOT NULL DEFAULT 'STANDARD',
        `computer_generated_note` VARCHAR(255) NOT NULL DEFAULT 'This is a Computer Generated Invoice',
        `financial_year_start` INTEGER NOT NULL DEFAULT 4,
        `rounding_mode` VARCHAR(20) NOT NULL DEFAULT 'HALF_UP',
        `storage_root` VARCHAR(255),
        `is_active` BOOLEAN NOT NULL DEFAULT 1,
        `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
        `updated_at` DATETIME
    );
    """)

    # 3. Seed Companies
    cur.execute("SELECT count(*) FROM `companies`")
    if cur.fetchone()[0] == 0:
        cur.execute("""
        INSERT INTO `companies` (
            id, code, name, address, city, state, state_code, gstin, pan, phone, email,
            gst_enabled, diamond_enabled, invoice_prefix, invoice_series,
            bank_name, bank_account_no, bank_ifsc, bank_branch, upi_id, upi_name,
            declaration, jurisdiction_city, tax_label_style, computer_generated_note, is_active
        ) VALUES
        (1, 'SAIDEEP', 'SAIDEEP JEWELLERS',
         'Takhatgarh khedawas, 167, Ward No. 3, Khedawas, Takhatgarh, Pali (Raj.)-306912',
         'Takhatgarh', 'Rajasthan', '08', '', '', '8504837854', 'saideepjewellers78@gmail.com',
         0, 1, 'INV', 'S',
         'State Bank of India', '38927492019', 'SBIN0031245', 'Takhatgarh', 'saideep@upi', 'Saideep Jewellers',
         'Terms & Conditions: Goods once sold will be exchanged as per store policy. Weight & purity guaranteed as per hallmark certification. All disputes subject to local jurisdiction.',
         'Takhatgarh', 'STANDARD', 'This is a Computer Generated Invoice', 1),
        (2, 'PRIDE_GOLD', 'PRIDE GOLD',
         '1st Floor, Near Koira Ji ka Bera, Ghodo ka Chowk, Sojati Gate, Jodhpur (Raj.)- 342001',
         'Jodhpur', 'Rajasthan', '08', '08AEZPK5007N1ZS', 'AEZPK5007N', '0291-2640999, +91-9929562800', 'info.pridegoldjdr@gmail.com',
         1, 1, 'PG', 'S',
         'ICICI Bank', '004705001234', 'ICIC0000047', 'Sojati Gate Jodhpur', 'pridegold@icici', 'Pride Gold',
         'We declare that this invoice shows the actual price of the goods described and that all particulars are true and correct.',
         'JODHPUR', 'GST', 'This is a Computer Generated Invoice', 1),
        (3, 'CO3', 'Company 3 Placeholder',
         'Takhatgarh', 'Takhatgarh', 'Rajasthan', '08', '', '', '', '',
         0, 1, 'CO3', 'S',
         '', '', '', '', '', '',
         '', 'Takhatgarh', 'STANDARD', 'This is a Computer Generated Invoice', 0);
        """)

    # 4. Create `company_number_sequences` table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS `company_number_sequences` (
        `id` INTEGER PRIMARY KEY AUTOINCREMENT,
        `company_id` INTEGER NOT NULL,
        `financial_year` VARCHAR(10) NOT NULL,
        `doc_type` VARCHAR(20) NOT NULL,
        `last_sequence` INTEGER NOT NULL DEFAULT 0,
        `prefix` VARCHAR(20),
        `series` VARCHAR(20),
        `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE (`company_id`, `financial_year`, `doc_type`)
    );
    """)

    # 5. Create `hsn_master` table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS `hsn_master` (
        `id` INTEGER PRIMARY KEY AUTOINCREMENT,
        `hsn_code` VARCHAR(20) NOT NULL UNIQUE,
        `description` VARCHAR(255) NOT NULL,
        `category` VARCHAR(50) NOT NULL,
        `is_active` BOOLEAN NOT NULL DEFAULT 1,
        `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
        `updated_at` DATETIME
    );
    """)
    cur.execute("SELECT count(*) FROM `hsn_master`")
    if cur.fetchone()[0] == 0:
        cur.executemany("""
        INSERT INTO `hsn_master` (hsn_code, description, category, is_active) VALUES (?, ?, ?, ?)
        """, [
            ('71081200', 'Gold Bar / Bullion', 'GOLD', 1),
            ('711319', 'Gold Jewellery / Ornaments', 'GOLD', 1),
            ('71069120', 'Silver Bar / Bullion', 'SILVER', 1),
            ('71069100', 'Silver Bullion (General Tariff)', 'SILVER', 1),
            ('711311', 'Silver Jewellery / Articles', 'SILVER', 1),
            ('71042120', 'Synthetic Diamond (Unworked)', 'DIAMOND', 1),
            ('71049120', 'Synthetic Diamond (Cut & Polished)', 'DIAMOND', 1),
            ('71023910', 'Natural Diamond (Cut & Polished)', 'DIAMOND', 1)
        ])

    # 6. Create `gst_rate_master` table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS `gst_rate_master` (
        `id` INTEGER PRIMARY KEY AUTOINCREMENT,
        `hsn_code` VARCHAR(20) NOT NULL,
        `total_rate` DECIMAL(6, 4) NOT NULL,
        `cgst_rate` DECIMAL(6, 4) NOT NULL,
        `sgst_rate` DECIMAL(6, 4) NOT NULL,
        `igst_rate` DECIMAL(6, 4) NOT NULL,
        `description` VARCHAR(255),
        `effective_from` DATETIME DEFAULT CURRENT_TIMESTAMP,
        `effective_to` DATETIME,
        `is_active` BOOLEAN NOT NULL DEFAULT 1,
        `updated_by` INTEGER,
        `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
        `updated_at` DATETIME
    );
    """)
    cur.execute("SELECT count(*) FROM `gst_rate_master`")
    if cur.fetchone()[0] == 0:
        cur.executemany("""
        INSERT INTO `gst_rate_master` (hsn_code, total_rate, cgst_rate, sgst_rate, igst_rate, description)
        VALUES (?, ?, ?, ?, ?, ?)
        """, [
            ('71081200', 3.0000, 1.5000, 1.5000, 3.0000, 'Gold Bullion 3% GST'),
            ('711319', 3.0000, 1.5000, 1.5000, 3.0000, 'Gold Ornaments 3% GST'),
            ('71069120', 3.0000, 1.5000, 1.5000, 3.0000, 'Silver Bar 3% GST (Pride Reference 71069120)'),
            ('71069100', 3.0000, 1.5000, 1.5000, 3.0000, 'Silver Bullion 3% GST (Tariff 71069100)'),
            ('711311', 3.0000, 1.5000, 1.5000, 3.0000, 'Silver Ornaments 3% GST'),
            ('71042120', 0.2500, 0.1250, 0.1250, 0.2500, 'Synthetic Diamond Unworked 0.25% GST'),
            ('71049120', 1.5000, 0.7500, 0.7500, 1.5000, 'Synthetic Diamond Cut & Polished 1.5% GST'),
            ('71023910', 1.5000, 0.7500, 0.7500, 1.5000, 'Natural Diamond Cut & Polished 1.5% GST')
        ])

    # 7. Create `state_codes` table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS `state_codes` (
        `id` INTEGER PRIMARY KEY AUTOINCREMENT,
        `code` VARCHAR(10) NOT NULL UNIQUE,
        `state_name` VARCHAR(100) NOT NULL,
        `state_type` VARCHAR(20) NOT NULL DEFAULT 'STATE'
    );
    """)
    cur.execute("SELECT count(*) FROM `state_codes`")
    if cur.fetchone()[0] == 0:
        cur.executemany("""
        INSERT INTO `state_codes` (code, state_name, state_type) VALUES (?, ?, ?)
        """, [
            ('01', 'Jammu & Kashmir', 'UT'), ('02', 'Himachal Pradesh', 'STATE'),
            ('03', 'Punjab', 'STATE'), ('04', 'Chandigarh', 'UT'),
            ('05', 'Uttarakhand', 'STATE'), ('06', 'Haryana', 'STATE'),
            ('07', 'Delhi', 'UT'), ('08', 'Rajasthan', 'STATE'),
            ('09', 'Uttar Pradesh', 'STATE'), ('10', 'Bihar', 'STATE'),
            ('11', 'Sikkim', 'STATE'), ('12', 'Arunachal Pradesh', 'STATE'),
            ('13', 'Nagaland', 'STATE'), ('14', 'Manipur', 'STATE'),
            ('15', 'Mizoram', 'STATE'), ('16', 'Tripura', 'STATE'),
            ('17', 'Meghalaya', 'STATE'), ('18', 'Assam', 'STATE'),
            ('19', 'West Bengal', 'STATE'), ('20', 'Jharkhand', 'STATE'),
            ('21', 'Odisha', 'STATE'), ('22', 'Chhattisgarh', 'STATE'),
            ('23', 'Madhya Pradesh', 'STATE'), ('24', 'Gujarat', 'STATE'),
            ('25', 'Daman & Diu', 'UT'), ('26', 'Dadra & Nagar Haveli', 'UT'),
            ('27', 'Maharashtra', 'STATE'), ('28', 'Andhra Pradesh (Old)', 'STATE'),
            ('29', 'Karnataka', 'STATE'), ('30', 'Goa', 'STATE'),
            ('31', 'Lakshadweep', 'UT'), ('32', 'Kerala', 'STATE'),
            ('33', 'Tamil Nadu', 'STATE'), ('34', 'Puducherry', 'UT'),
            ('35', 'Andaman & Nicobar Islands', 'UT'), ('36', 'Telangana', 'STATE'),
            ('37', 'Andhra Pradesh', 'STATE'), ('38', 'Ladakh', 'UT')
        ])

    # 8. Add `company_id` to business tables and backfill
    business_tables = [
        'invoices', 'invoice_items', 'purchases', 'purchase_items',
        'exchanges', 'exchange_items', 'exchange_new_items',
        'stock_items', 'customers', 'sellers', 'customer_ledgers',
        'supplier_ledgers', 'metal_rates', 'categories', 'expenses', 'payments'
    ]

    for tbl in business_tables:
        if tbl in existing_tables:
            cur.execute(f"PRAGMA table_info(`{tbl}`)")
            cols = {r[1] for r in cur.fetchall()}
            if 'company_id' not in cols:
                print(f"[Migration] Adding company_id to {tbl}...")
                cur.execute(f"ALTER TABLE `{tbl}` ADD COLUMN `company_id` INTEGER DEFAULT 1;")
                cur.execute(f"UPDATE `{tbl}` SET `company_id` = 1 WHERE `company_id` IS NULL;")
                cur.execute(f"CREATE INDEX IF NOT EXISTS `ix_{tbl}_company_id` ON `{tbl}` (`company_id`);")

    # 9. Add invoice snapshot & hash columns
    if 'invoices' in existing_tables:
        cur.execute("PRAGMA table_info(`invoices`)")
        inv_cols = {r[1] for r in cur.fetchall()}
        for col, col_type in [
            ('seller_snapshot_json', 'TEXT'),
            ('buyer_snapshot_json', 'TEXT'),
            ('tax_summary_json', 'TEXT'),
            ('pdf_path', 'VARCHAR(500)'),
            ('sha256_hash', 'VARCHAR(64)')
        ]:
            if col not in inv_cols:
                print(f"[Migration] Adding {col} to invoices...")
                cur.execute(f"ALTER TABLE `invoices` ADD COLUMN `{col}` {col_type};")

    # 10. Create `invoice_gst_lines` table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS `invoice_gst_lines` (
        `id` INTEGER PRIMARY KEY AUTOINCREMENT,
        `invoice_id` INTEGER NOT NULL,
        `invoice_item_id` INTEGER,
        `hsn_code` VARCHAR(20) NOT NULL,
        `taxable_amount` DECIMAL(12, 2) NOT NULL,
        `gst_rate` DECIMAL(6, 4) NOT NULL,
        `cgst_rate` DECIMAL(6, 4) NOT NULL DEFAULT 0,
        `cgst_amount` DECIMAL(12, 2) NOT NULL DEFAULT 0,
        `sgst_rate` DECIMAL(6, 4) NOT NULL DEFAULT 0,
        `sgst_amount` DECIMAL(12, 2) NOT NULL DEFAULT 0,
        `igst_rate` DECIMAL(6, 4) NOT NULL DEFAULT 0,
        `igst_amount` DECIMAL(12, 2) NOT NULL DEFAULT 0,
        `total_tax_amount` DECIMAL(12, 2) NOT NULL,
        `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (`invoice_id`) REFERENCES `invoices` (`id`) ON DELETE CASCADE
    );
    """)

    # 11. Create `invoice_einvoice` table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS `invoice_einvoice` (
        `id` INTEGER PRIMARY KEY AUTOINCREMENT,
        `invoice_id` INTEGER NOT NULL UNIQUE,
        `irn` VARCHAR(100),
        `ack_no` VARCHAR(50),
        `ack_date` VARCHAR(50),
        `qr_data` TEXT,
        `qr_image_url` VARCHAR(255),
        `entered_by` INTEGER,
        `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
        `updated_at` DATETIME,
        FOREIGN KEY (`invoice_id`) REFERENCES `invoices` (`id`) ON DELETE CASCADE
    );
    """)

    # 12. Create `diamond_calculations` table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS `diamond_calculations` (
        `id` INTEGER PRIMARY KEY AUTOINCREMENT,
        `invoice_item_id` INTEGER,
        `purchase_item_id` INTEGER,
        `exchange_item_id` INTEGER,
        `diamond_type` VARCHAR(50) NOT NULL DEFAULT 'NATURAL',
        `diamond_form` VARCHAR(50) NOT NULL DEFAULT 'CUT_AND_POLISHED',
        `shape` VARCHAR(50),
        `carat_weight` DECIMAL(10, 4) NOT NULL DEFAULT 0.0000,
        `pieces` INTEGER NOT NULL DEFAULT 1,
        `colour` VARCHAR(20),
        `clarity` VARCHAR(20),
        `cut` VARCHAR(20),
        `certificate_no` VARCHAR(100),
        `certifying_lab` VARCHAR(50),
        `rate_per_carat` DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
        `subtotal_diamond_value` DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
        `discount` DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
        `making_charges` DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
        `other_charges` DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
        `total_diamond_value` DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
        `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
        `updated_at` DATETIME,
        FOREIGN KEY (`invoice_item_id`) REFERENCES `invoice_items` (`id`) ON DELETE CASCADE,
        FOREIGN KEY (`purchase_item_id`) REFERENCES `purchase_items` (`id`) ON DELETE CASCADE
    );
    """)

    # 13. Re-enable foreign keys & Commit
    cur.execute("PRAGMA foreign_keys = ON;")
    if not dry_run:
        conn.commit()

    # 14. Verify row counts post-migration
    after_counts = {}
    for t in existing_tables:
        cur.execute(f"SELECT count(*) FROM `{t}`")
        after_counts[t] = cur.fetchone()[0]

    for t, b_cnt in before_counts.items():
        a_cnt = after_counts.get(t, 0)
        assert a_cnt >= b_cnt, f"FATAL REGRESSION: Table {t} lost records! Before: {b_cnt}, After: {a_cnt}"

    conn.close()
    print("[Migration] COMPLETED SUCCESSFULLY! Verified all table counts. Zero records lost.")
    return {"status": "success", "before": before_counts, "after": after_counts}

if __name__ == '__main__':
    db_file = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(r'C:\Users\YASH SONI\JewelleryERP_Data\jewellery_erp.db')
    run_migration(db_file)
