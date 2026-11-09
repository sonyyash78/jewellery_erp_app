"""
Multi-Company Rollback Script
=============================
Reverses the additive schema changes safely if ever needed.
Drops only the new multi-company tables and keeps original tables intact.
"""
import sqlite3
import sys
from pathlib import Path

def rollback(db_path: Path):
    print(f"[Rollback] Connecting to {db_path}...")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = OFF;")

    new_tables = [
        "diamond_calculations",
        "invoice_einvoice",
        "invoice_gst_lines",
        "gst_rate_master",
        "hsn_master",
        "state_codes",
        "company_number_sequences",
        "companies"
    ]

    for tbl in new_tables:
        print(f"[Rollback] Dropping table if exists: {tbl}")
        cur.execute(f"DROP TABLE IF EXISTS `{tbl}`;")

    cur.execute("PRAGMA foreign_keys = ON;")
    conn.commit()
    conn.close()
    print("[Rollback] Rollback completed safely.")

if __name__ == '__main__':
    db_file = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(r'C:\Users\YASH SONI\JewelleryERP_Data\jewellery_erp.db')
    rollback(db_file)
