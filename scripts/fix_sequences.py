import sqlite3

for db_path in [
    r'C:\Users\YASH SONI\JewelleryERP_Data\jewellery_erp.db',
    r'C:\Users\YASH SONI\Desktop\jeweller-app\backend\jewellery_erp.db'
]:
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("UPDATE company_number_sequences SET prefix = 'SJ' WHERE company_id = 2")
        conn.commit()
        cur.execute("SELECT * FROM company_number_sequences")
        print(f"Updated {db_path}:", cur.fetchall())
        conn.close()
    except Exception as e:
        print(f"Error on {db_path}: {e}")
