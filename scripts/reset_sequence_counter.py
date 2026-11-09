import sqlite3

db_path = r'C:\Users\YASH SONI\JewelleryERP_Data\jewellery_erp.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Reset last_sequence to 0 for Company 2 so next is 1 ('01' -> SJ/S/01/26-27)
cur.execute("UPDATE company_number_sequences SET last_sequence = 0 WHERE company_id = 2")
print("Updated company_number_sequences last_sequence to 0 for company_id = 2")

# Clean up test invoices with PG/S/1944, SJ/S/1945, SJ/S/1946
cur.execute("DELETE FROM invoices WHERE invoice_number LIKE 'PG/%' OR invoice_number LIKE 'SJ/S/194%'")
deleted_inv = cur.rowcount
print(f"Deleted {deleted_inv} test invoices with old sequence numbers")

# Check current sequence
cur.execute("SELECT id, company_id, doc_type, prefix, series, last_sequence, financial_year FROM company_number_sequences")
print("Current sequences:", cur.fetchall())

conn.commit()
conn.close()
print("Sequence reset complete!")
