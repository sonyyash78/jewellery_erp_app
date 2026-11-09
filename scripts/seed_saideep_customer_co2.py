import sqlite3

def seed_customer():
    conn = sqlite3.connect(r'C:\Users\YASH SONI\JewelleryERP_Data\jewellery_erp.db')
    c = conn.cursor()
    c.execute("SELECT id FROM customers WHERE phone_number = '9460820878' AND company_id = 2")
    row = c.fetchone()
    if not row:
        c.execute("""
            INSERT INTO customers (
                store_id, company_id, first_name, last_name, phone_number,
                address, city, state, pincode, aadhaar_pan, gst_number,
                is_active, is_deleted, created_at, updated_at
            ) VALUES (
                1, 2, 'Saideep', 'Jewellers', '9460820878',
                '167, Ward No. 3, Khedawas, Takhatgarh, Pali (Raj.)-306912', 'Takhatgarh', 'Rajasthan', '306912',
                'BNUPK1610E', '08BNUPK1610E1Z3',
                1, 0, datetime('now'), datetime('now')
            )
        """)
        conn.commit()
        print('Inserted Saideep Jewellers as Customer in Company 2')
    else:
        print('Saideep Jewellers customer already exists in Company 2 with ID:', row[0])
    conn.close()

if __name__ == '__main__':
    seed_customer()
