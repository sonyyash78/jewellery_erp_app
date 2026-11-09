import sqlite3

db_path = r'C:\Users\YASH SONI\JewelleryERP_Data\jewellery_erp.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

def add_col_if_missing(table, col_name, col_type):
    c.execute(f"PRAGMA table_info({table})")
    cols = [r[1] for r in c.fetchall()]
    if col_name not in cols:
        print(f"Adding {col_name} to {table}...")
        c.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type}")

add_col_if_missing("purchases", "idempotency_key", "VARCHAR(100)")
add_col_if_missing("purchases", "verification_token", "VARCHAR(100)")
add_col_if_missing("exchanges", "idempotency_key", "VARCHAR(100)")
add_col_if_missing("exchanges", "verification_token", "VARCHAR(100)")
add_col_if_missing("invoices", "idempotency_key", "VARCHAR(100)")
add_col_if_missing("invoices", "verification_token", "VARCHAR(100)")

conn.commit()
conn.close()
print("All missing columns checked and added!")
