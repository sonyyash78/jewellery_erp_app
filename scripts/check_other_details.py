import sqlite3

db_path = r"C:\Users\YASH SONI\JewelleryERP_Data\jewellery_erp.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

for t in ['invoice_gst_lines', 'invoice_einvoice', 'gold_calculations', 'silver_calculations', 'diamond_calculations']:
    cursor.execute(f"SELECT * FROM {t}")
    rows = cursor.fetchall()
    print(f"=== {t} ({len(rows)} rows) ===")
    for r in rows:
        print(dict(r))

conn.close()
