from decimal import Decimal
import os

path = r'C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\api\v1\sellers.py'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if '"gold_change": float((entry.gold_credit or 0.0) - (entry.gold_debit or 0.0))' in line:
        new_lines.append(line.replace(
            'float((entry.gold_credit or 0.0) - (entry.gold_debit or 0.0))',
            'float(Decimal(str(entry.gold_credit or 0)) - Decimal(str(entry.gold_debit or 0)))'
        ))
    elif '"silver_change": float((entry.silver_credit or 0.0) - (entry.silver_debit or 0.0))' in line:
        new_lines.append(line.replace(
            'float((entry.silver_credit or 0.0) - (entry.silver_debit or 0.0))',
            'float(Decimal(str(entry.silver_credit or 0)) - Decimal(str(entry.silver_debit or 0)))'
        ))
    elif '"debit": float(entry.debit or 0.0)' in line:
        new_lines.append(line.replace(
            'float(entry.debit or 0.0)',
            'float(Decimal(str(entry.debit or 0)))'
        ))
    elif '"credit": float(entry.credit or 0.0)' in line:
        new_lines.append(line.replace(
            'float(entry.credit or 0.0)',
            'float(Decimal(str(entry.credit or 0)))'
        ))
    elif '"balance": float(entry.balance or 0.0)' in line:
        new_lines.append(line.replace(
            'float(entry.balance or 0.0)',
            'float(Decimal(str(entry.balance or 0)))'
        ))
    else:
        new_lines.append(line)

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print('Updated sellers.py successfully!')
