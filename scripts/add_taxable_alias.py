paths = [
    r'C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\services\calculation_service.py',
    r'C:\Users\YASH SONI\Desktop\Saideep\jewellery-erp\backend\app\services\calculation_service.py'
]

for p in paths:
    with open(p, 'r', encoding='utf-8') as f:
        c = f.read()

    if '"taxable_amount": taxable' not in c:
        c = c.replace(
            '"taxable": taxable,',
            '"taxable": taxable,\n            "taxable_amount": taxable,'
        )

    with open(p, 'w', encoding='utf-8') as f:
        f.write(c)

print('Updated taxable_amount alias in calculate_diamond')
