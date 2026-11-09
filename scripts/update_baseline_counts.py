import sqlite3
import json

db_path = r"C:\Users\YASH SONI\JewelleryERP_Data\jewellery_erp.db"
con = sqlite3.connect(db_path)
cur = con.cursor()
tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
counts = {}
for t in sorted(tables):
    counts[t] = cur.execute(f"SELECT count(*) FROM `{t}`").fetchone()[0]

con.close()

with open(r"C:\Users\YASH SONI\Desktop\jeweller-app\tests\baselines\table_counts_baseline.json", "w", encoding="utf-8") as f:
    json.dump(counts, f, indent=2)

print("Updated table_counts_baseline.json successfully")
