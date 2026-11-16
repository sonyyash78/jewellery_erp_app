import sqlite3

db_path = r"C:\Users\YASH SONI\JewelleryERP_Data\jewellery_erp.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=== INVOICES ===")
cursor.execute("SELECT * FROM invoices")
for row in cursor.fetchall():
    print(dict(row))

print("\n=== CUSTOMERS ===")
cursor.execute("SELECT * FROM customers")
for row in cursor.fetchall():
    print(dict(row))

print("\n=== CUSTOMER LEDGERS ===")
cursor.execute("SELECT * FROM customer_ledgers")
for row in cursor.fetchall():
    print(dict(row))

conn.close()
