import sqlite3

db_path = r"C:\Users\YASH SONI\JewelleryERP_Data\jewellery_erp.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row['name'] for row in cursor.fetchall()]
print("Tables:", tables)

for t in ['invoice_items', 'payments', 'metal_transactions', 'metal_ledger', 'account_ledgers', 'cash_transactions']:
    if t in tables:
        cursor.execute(f"SELECT COUNT(*) as cnt FROM {t}")
        print(f"{t}: {cursor.fetchone()['cnt']} rows")

conn.close()
