import re

path = r'C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\services\report_service.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Replace gold sold wastage query
content = content.replace(
    'func.coalesce(func.sum(GoldCalculation.net_weight * GoldCalculation.wastage / 100), 0),',
    'func.coalesce(func.sum(GoldCalculation.wastage), 0),'
)

# 2. Replace gold purchased wastage query
content = content.replace(
    'func.coalesce(func.sum(PurchaseItem.net_weight * PurchaseItem.wastage / 100), 0),',
    'func.coalesce(func.sum(PurchaseItem.wastage), 0),'
)

# 3. Replace silver sold wastage query
content = content.replace(
    'func.coalesce(func.sum(SilverCalculation.wastage * (SilverCalculation.gross_weight - SilverCalculation.stone_weight) / 100), 0),',
    'func.coalesce(func.sum(SilverCalculation.wastage), 0),'
)

# 4. Replace silver purchased wastage query
content = content.replace(
    'func.coalesce(func.sum(PurchaseItem.net_weight * PurchaseItem.wastage / 100), 0),',
    'func.coalesce(func.sum(PurchaseItem.wastage), 0),'
)

# 5. In g_lines loop:
old_g_block = """        for row in g_lines.order_by(Invoice.invoice_date.desc()).limit(20).all():
            w_gms = float(Decimal(str(row[3] or 0)) * Decimal(str(row[5] or 0)) / Decimal('100'))
            transactions.append({
                "date": row[0].strftime("%Y-%m-%d") if row[0] else "",
                "type": "Sale",
                "bill_no": row[1],
                "item_name": row[2] or "Gold Item",
                "metal": "Gold",
                "weight_g": float(row[3] or 0),
                "touch_pct": float(row[4] or 0),
                "wastage_pct": float(row[5] or 0),
                "wastage_g": round(w_gms, 3),
                "fine_weight_g": float(row[6] or 0),
                "making_charges": float(row[7] or 0),
                "total_amount": float(row[8] or 0)
            })"""

new_g_block = """        for row in g_lines.order_by(Invoice.invoice_date.desc()).limit(20).all():
            w_gms = float(Decimal(str(row[5] or 0)))
            touch_val = float(Decimal(str(row[4] or 0)))
            transactions.append({
                "date": row[0].strftime("%Y-%m-%d") if row[0] else "",
                "type": "Sale",
                "bill_no": row[1],
                "item_name": row[2] or "Gold Item",
                "metal": "Gold",
                "weight_g": float(row[3] or 0),
                "touch": touch_val,
                "touch_pct": touch_val,
                "wastage_g": round(w_gms, 3),
                "fine_weight_g": float(row[6] or 0),
                "making_charges": float(row[7] or 0),
                "total_amount": float(row[8] or 0)
            })"""

# 6. In g_pur_lines loop:
old_p_block = """        for row in g_pur_lines.order_by(Purchase.created_at.desc()).limit(20).all():
            w_gms = float(Decimal(str(row[3] or 0)) * Decimal(str(row[5] or 0)) / Decimal('100'))
            transactions.append({
                "date": row[0].strftime("%Y-%m-%d") if row[0] else "",
                "type": "Purchase",
                "bill_no": row[1],
                "item_name": row[2] or "Gold Purchase",
                "metal": "Gold",
                "weight_g": float(row[3] or 0),
                "touch_pct": float(row[4] or 0),
                "wastage_pct": float(row[5] or 0),
                "wastage_g": round(w_gms, 3),
                "fine_weight_g": float(row[6] or 0),
                "making_charges": float(row[7] or 0),
                "total_amount": float(row[8] or 0)
            })"""

new_p_block = """        for row in g_pur_lines.order_by(Purchase.created_at.desc()).limit(20).all():
            w_gms = float(Decimal(str(row[5] or 0)))
            touch_val = float(Decimal(str(row[4] or 0)))
            transactions.append({
                "date": row[0].strftime("%Y-%m-%d") if row[0] else "",
                "type": "Purchase",
                "bill_no": row[1],
                "item_name": row[2] or "Gold Purchase",
                "metal": "Gold",
                "weight_g": float(row[3] or 0),
                "touch": touch_val,
                "touch_pct": touch_val,
                "wastage_g": round(w_gms, 3),
                "fine_weight_g": float(row[6] or 0),
                "making_charges": float(row[7] or 0),
                "total_amount": float(row[8] or 0)
            })"""

assert old_g_block in content, "old_g_block not found in report_service.py"
assert old_p_block in content, "old_p_block not found in report_service.py"

content = content.replace(old_g_block, new_g_block)
content = content.replace(old_p_block, new_p_block)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESS: report_service.py updated successfully!")
