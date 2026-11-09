import sqlite3
conn = sqlite3.connect(r'C:\Users\YASH SONI\JewelleryERP_Data\jewellery_erp.db')
cur = conn.cursor()
cur.execute("DELETE FROM invoices WHERE invoice_number LIKE 'SJ/S/%'")
cur.execute("UPDATE company_number_sequences SET last_sequence = 0 WHERE company_id = 2")
conn.commit()
print("Reset sequence to 0 and cleared test SJ/S/ invoices")
conn.close()
