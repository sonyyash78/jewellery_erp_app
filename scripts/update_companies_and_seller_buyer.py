import sqlite3
import json

db_path = r"C:\Users\YASH SONI\JewelleryERP_Data\jewellery_erp.db"
con = sqlite3.connect(db_path)
cur = con.cursor()

# 1. Update Company 2 (Saideep Jewellers GST)
cur.execute("""
    UPDATE companies
    SET name = 'SAIDEEP JEWELLERS',
        code = 'SAIDEEP_GST',
        address = '167, Ward No. 3, Khedawas, Takhatgarh, Pali (Raj.)-306912',
        city = 'Takhatgarh',
        state = 'Rajasthan',
        state_code = '08',
        gstin = '08BNUPK1610E1Z3',
        pan = 'BNUPK1610E',
        phone = '+91-9460820878',
        email = 'saideepjewellers78@gmail.com',
        jurisdiction_city = 'PALI',
        invoice_prefix = 'SJ',
        invoice_series = 'S',
        bank_name = 'State Bank of India',
        bank_account_no = '38927492019',
        bank_ifsc = 'SBIN0031245',
        bank_branch = 'Takhatgarh',
        upi_id = 'saideep@upi',
        upi_name = 'Saideep Jewellers',
        declaration = 'We declare that this invoice shows the actual price of the goods described and that all particulars are true and correct.',
        gst_enabled = 1,
        diamond_enabled = 1,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = 2
""")

# 2. Update Company 1 (Saideep Jewellers Normal / Without GST)
cur.execute("""
    UPDATE companies
    SET name = 'SAIDEEP JEWELLERS',
        code = 'SAIDEEP',
        address = '167, Ward No. 3, Khedawas, Takhatgarh, Pali (Raj.)-306912',
        city = 'Takhatgarh',
        state = 'Rajasthan',
        state_code = '08',
        gstin = '',
        pan = '',
        phone = '9460820878',
        email = 'saideepjewellers78@gmail.com',
        jurisdiction_city = 'PALI',
        invoice_prefix = 'INV',
        invoice_series = 'S',
        gst_enabled = 0,
        diamond_enabled = 1
    WHERE id = 1
""")

# 3. Clean up Customer 1 (was seeded as Saideep Jewellers)
cur.execute("DELETE FROM customers WHERE id = 1 AND first_name = 'Saideep'")

# 4. Update Invoice 1 snapshots if exists
new_seller_snap = {
    "name": "SAIDEEP JEWELLERS",
    "address": "167, Ward No. 3, Khedawas, Takhatgarh, Pali (Raj.)-306912",
    "city": "Takhatgarh",
    "state": "Rajasthan",
    "state_code": "08",
    "gstin": "08BNUPK1610E1Z3",
    "pan": "BNUPK1610E",
    "phone": "+91-9460820878",
    "email": "saideepjewellers78@gmail.com",
    "jurisdiction_city": "PALI",
    "declaration": "We declare that this invoice shows the actual price of the goods described and that all particulars are true and correct."
}

new_buyer_snap = {
    "name": "YASH",
    "address": "167, Ward No. 3, Khedawas, Thakhatgarh, Pali (Raj.)-306912",
    "city": "Takhatgarh",
    "state": "Rajasthan",
    "state_code": "08",
    "place_of_supply": "Rajasthan",
    "contact_person": "Rajesh Kumar",
    "phone": "7894563214",
    "email": "saideepjewellers78@gmail.com",
    "gstin": "",
    "pan": ""
}

cur.execute("""
    UPDATE invoices
    SET seller_snapshot_json = ?,
        buyer_snapshot_json = ?
    WHERE id = 1
""", (json.dumps(new_seller_snap), json.dumps(new_buyer_snap)))

con.commit()

# Verify
con.row_factory = sqlite3.Row
cur = con.cursor()
print("Updated Companies:")
for c in cur.execute("SELECT id, code, name, gstin, pan, gst_enabled, invoice_prefix FROM companies").fetchall():
    print(dict(c))

print("\nUpdated Invoices:")
for inv in cur.execute("SELECT id, invoice_number, company_id, customer_id, seller_snapshot_json, buyer_snapshot_json FROM invoices").fetchall():
    print(dict(inv))

con.close()
