with open('backend/app/api/v1/sellers.py', 'r', encoding='utf-8') as f:
    text = f.read()

old_block = """            "gold_change": float((entry.gold_credit or 0.0) - (entry.gold_debit or 0.0)),
            "silver_change": float((entry.silver_credit or 0.0) - (entry.silver_debit or 0.0)),
            "debit": float(entry.debit or 0.0),
            "credit": float(entry.credit or 0.0),
            "balance": float(entry.balance or 0.0)"""

new_block = """            "gold_change": float(Decimal(str(entry.gold_credit or 0)) - Decimal(str(entry.gold_debit or 0))),
            "silver_change": float(Decimal(str(entry.silver_credit or 0)) - Decimal(str(entry.silver_debit or 0))),
            "debit": float(Decimal(str(entry.debit or 0))),
            "credit": float(Decimal(str(entry.credit or 0))),
            "balance": float(Decimal(str(entry.balance or 0)))"""

assert old_block in text, "old_block not found in sellers.py"
text = text.replace(old_block, new_block, 1)

with open('backend/app/api/v1/sellers.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("Updated sellers.py successfully!")
