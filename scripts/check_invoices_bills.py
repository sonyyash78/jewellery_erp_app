import sqlite3

db_path = r"C:\Users\YASH SONI\JewelleryERP_Data\jewellery_erp.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=== INVOICE ITEMS ===")
cursor.execute("SELECT * FROM invoice_items")
for r in cursor.fetchall():
    print(dict(r))

print("\n=== BILLS ===")
cursor.execute("SELECT * FROM bills")
for r in cursor.fetchall():
    print(dict(r))

print("\n=== EXCHANGES ===")
cursor.execute("SELECT * FROM exchanges")
for r in cursor.fetchall():
    print(dict(r))

conn.close()
