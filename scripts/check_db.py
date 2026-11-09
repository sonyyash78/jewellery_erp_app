import sqlite3

conn = sqlite3.connect(r"C:\Users\YASH SONI\JewelleryERP_Data\jewellery_erp.db")
cur = conn.cursor()

print("=== companies ===")
cur.execute("SELECT * FROM companies")
cols = [c[0] for c in cur.description]
for r in cur.fetchall():
    print(dict(zip(cols, r)))

print("\n=== settings ===")
cur.execute("SELECT key, value FROM settings")
for r in cur.fetchall():
    print(r)
