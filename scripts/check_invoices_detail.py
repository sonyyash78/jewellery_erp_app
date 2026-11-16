import sqlite3

db_path = r"C:\Users\YASH SONI\JewelleryERP_Data\jewellery_erp.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("SELECT * FROM invoices WHERE id IN (3, 4)")
for r in cursor.fetchall():
    print("--- INVOICE ---")
    for k in r.keys():
        print(f"  {k}: {r[k]}")

conn.close()
