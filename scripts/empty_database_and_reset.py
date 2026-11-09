import os
import shutil
import sqlite3
from datetime import datetime

def main():
    db_path = r"C:\Users\YASH SONI\JewelleryERP_Data\jewellery_erp.db"
    backup_dir = r"C:\Users\YASH SONI\JewelleryERP_Data\backups"
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(backup_dir, f"pre_empty_backup_{timestamp}.db")
    shutil.copy2(db_path, backup_file)
    print(f"[1/4] Created database backup: {backup_file} ({os.path.getsize(backup_file):,} bytes)")

    con = sqlite3.connect(db_path)
    cur = con.cursor()

    # Tables to completely empty (transactional and test data)
    tables_to_empty = [
        "invoices",
        "invoice_items",
        "gold_calculations",
        "silver_calculations",
        "diamond_calculations",
        "invoice_gst_lines",
        "invoice_einvoice",
        "purchases",
        "purchase_items",
        "exchanges",
        "exchange_items",
        "exchange_new_items",
        "customer_ledgers",
        "supplier_ledgers",
        "payments",
        "bills",
        "bill_items",
        "gold_purchases",
        "silver_purchases",
        "generated_reports",
        "audit_logs",
        "company_number_sequences",
        "stock_items",
        "inventory_transactions",
        "inventory",
        "inventory_items",
        "expenses",
        "sellers",
        "customers",
    ]

    print("[2/4] Truncating transactional & test tables...")
    for t in tables_to_empty:
        try:
            cur.execute(f"DELETE FROM `{t}`")
            print(f"  Emptied `{t}`")
        except Exception as e:
            print(f"  Notice on `{t}`: {e}")

    # Reset sqlite_sequence autoincrement
    try:
        cur.execute("DELETE FROM sqlite_sequence WHERE name IN ({})".format(
            ",".join(f"'{t}'" for t in tables_to_empty)
        ))
        print("  Reset autoincrement counters in sqlite_sequence")
    except Exception as e:
        print(f"  sqlite_sequence notice: {e}")

    print("[3/4] Ensuring clean Companies and Master Customer...")
    # Update Company 1: Saideep Jewellers (Normal Retail, No GST)
    cur.execute("""
        UPDATE companies
        SET name = 'SAIDEEP JEWELLERS',
            code = 'SAIDEEP',
            address = '167, Ward No. 3, Khedawas, Takhatgarh, Pali (Raj.)-306912',
            city = 'Takhatgarh',
            state = 'Rajasthan',
            state_code = '08',
            gstin = '',
            pan = '',
            phone = '9460820878',
            email = 'saideepjewellers78@gmail.com',
            gst_enabled = 0,
            invoice_prefix = 'INV',
            jurisdiction_city = 'PALI',
            is_active = 1
        WHERE id = 1
    """)

    # Update Company 2: PRIDE GOLD (GST Bullion & Wholesale)
    cur.execute("""
        UPDATE companies
        SET name = 'PRIDE GOLD',
            code = 'PRIDE_GOLD',
            address = '1st Floor, Near Koira Ji ka Bera, Ghodo ka Chowk, Sojati Gate, Jodhpur (Raj.)- 342001',
            city = 'Jodhpur',
            state = 'Rajasthan',
            state_code = '08',
            gstin = '08AEZPK5007N1ZS',
            pan = 'AEZPK5007N',
            phone = '0291-2640999, +91-9929562800',
            email = 'info.pridegoldjdr@gmail.com',
            gst_enabled = 1,
            invoice_prefix = 'PG',
            invoice_series = 'S',
            jurisdiction_city = 'JODHPUR',
            is_active = 1
        WHERE id = 2
    """)

    # Seed Master Customer for Company 2 B2B buyer: Saideep Jewellers
    cur.execute("""
        INSERT INTO customers (
            id, store_id, first_name, last_name, phone_number, email, 
            address, city, state, pincode, gst_number, aadhaar_pan, created_at
        ) VALUES (
            1, 1, 'Saideep', 'Jewellers', '+91-9460820878', 'saideepjewellers78@gmail.com',
            '167, Ward No. 3, Khedawas, Thakhatgarh, Pali (Raj.)-306912', 'Takhatgarh', 'Rajasthan', '306912',
            '08BNUPK1610E1Z3', 'BNUPK1610E', datetime('now')
        )
    """)
    print("  Seeded Customer 1 (Saideep Jewellers B2B purchaser)")

    con.commit()
    con.close()

    print("[4/4] Verification of clean state:")
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    for t in ["invoices", "purchases", "exchanges", "customers", "companies", "users"]:
        cnt = cur.execute(f"SELECT COUNT(*) FROM `{t}`").fetchone()[0]
        print(f"  {t}: {cnt} rows")
    con.close()
    print("SUCCESS: Database has been cleanly reset and initialized!")

if __name__ == "__main__":
    main()
