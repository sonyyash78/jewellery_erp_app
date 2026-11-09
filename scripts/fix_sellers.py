paths = [
    r'C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\api\v1\sellers.py',
    r'C:\Users\YASH SONI\Desktop\Saideep\jewellery-erp\backend\app\api\v1\sellers.py'
]
for p in paths:
    with open(p, 'r', encoding='utf-8') as f:
        c = f.read()
    c = c.replace('float(entry.gold_credit - entry.gold_debit)', 'float((entry.gold_credit or 0.0) - (entry.gold_debit or 0.0))')
    c = c.replace('float(entry.silver_credit - entry.silver_debit)', 'float((entry.silver_credit or 0.0) - (entry.silver_debit or 0.0))')
    c = c.replace('"debit": float(entry.debit)', '"debit": float(entry.debit or 0.0)')
    c = c.replace('"credit": float(entry.credit)', '"credit": float(entry.credit or 0.0)')
    c = c.replace('"balance": float(entry.balance)', '"balance": float(entry.balance or 0.0)')
    with open(p, 'w', encoding='utf-8') as f:
        f.write(c)
print('Successfully updated sellers.py')
