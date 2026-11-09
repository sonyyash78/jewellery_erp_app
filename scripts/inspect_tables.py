import sqlite3

con = sqlite3.connect(r"C:\Users\YASH SONI\JewelleryERP_Data\jewellery_erp.db")
cur = con.cursor()
tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print("Tables in DB:")
for t in tables:
    count = cur.execute(f"SELECT COUNT(*) FROM `{t}`").fetchone()[0]
    print(f"  {t}: {count} rows")
