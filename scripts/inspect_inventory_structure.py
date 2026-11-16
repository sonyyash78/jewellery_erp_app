import sqlite3

db_path = r"C:\Users\YASH SONI\JewelleryERP_Data\jewellery_erp.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

tables = [
    'inventory', 'inventory_items', 'stock_items', 'products', 
    'product_variants', 'qr_inventory', 'categories'
]

for t in tables:
    cur.execute(f"PRAGMA table_info({t})")
    cols = [r['name'] for r in cur.fetchall()]
    cur.execute(f"SELECT COUNT(*) as cnt FROM {t}")
    cnt = cur.fetchone()['cnt']
    print(f"\nTable: {t} (Count: {cnt})")
    print("  Columns:", cols)
    if cnt > 0:
        cur.execute(f"SELECT * FROM {t} LIMIT 3")
        for row in cur.fetchall():
            print("    Row:", dict(row))

conn.close()
