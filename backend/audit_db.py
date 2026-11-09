import sqlite3
import os

p = r'C:\Users\YASH SONI\JewelleryERP_Data\jewellery_erp.db'
conn = sqlite3.connect(p)
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
tables = [r[0] for r in cur.fetchall()]
print(f"Total tables in live DB: {len(tables)}")
for t in sorted(tables):
    try:
        cur.execute(f'SELECT COUNT(*) FROM "{t}"')
        cnt = cur.fetchone()[0]
        cur.execute(f'PRAGMA table_info("{t}")')
        cols = [c[1] for c in cur.fetchall()]
        has_store = "store_id" in cols
        has_comp = "company_id" in cols
        print(f"  {t:25} | rows: {cnt:5} | store_id: {str(has_store):5} | company_id: {str(has_comp):5}")
    except Exception as e:
        print(f"  {t:25} | Error: {e}")
conn.close()
