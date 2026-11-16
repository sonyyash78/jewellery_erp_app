import sqlite3

db_path = r"C:\Users\YASH SONI\JewelleryERP_Data\jewellery_erp.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=== COMPANIES ===")
cursor.execute("SELECT * FROM companies")
for r in cursor.fetchall():
    print(dict(r))

conn.close()
