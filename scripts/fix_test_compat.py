path = r'C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\services\report_service.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

old_ret = 'return {\n            "company_id": company_id,\n            "summary": {'
new_ret = '''return {
            "company_id": company_id,
            "gold_wastage_earned_gms": float(round(gold_sold_wastage, 3)),
            "gold_fine_sold_gms": float(round(Decimal(str(g_sold_fine or 0)), 3)),
            "silver_wastage_earned_gms": float(round(silver_sold_wastage, 3)),
            "silver_pure_sold_gms": float(round(Decimal(str(s_sold_pure or 0)), 3)),
            "summary": {'''

text = text.replace(old_ret, new_ret)
with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
print('Added legacy keys for test compatibility!')
