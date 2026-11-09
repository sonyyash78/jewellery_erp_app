import sqlite3
import os

model_path = r'C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\models\exchange.py'
with open(model_path, 'r', encoding='utf-8') as f:
    text = f.read()

if 'exchange_number' not in text:
    target = 'store_id = Column(Integer'
    replacement = 'exchange_number = Column(String(30), nullable=True, unique=True, index=True)\n    store_id = Column(Integer'
    text = text.replace(target, replacement, 1)
    with open(model_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print('Updated backend/app/models/exchange.py')
else:
    print('exchange_number already in exchange.py')

db_path = r'C:\Users\YASH SONI\JewelleryERP_Data\jewellery_erp.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cols = [r[1] for r in cur.execute('PRAGMA table_info(exchanges)').fetchall()]
    if 'exchange_number' not in cols:
        cur.execute('ALTER TABLE exchanges ADD COLUMN exchange_number VARCHAR(30)')
        conn.commit()
        print('Added exchange_number column to exchanges table in DB!')
    else:
        print('exchange_number column already in DB')
    conn.close()
