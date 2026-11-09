paths = [
    r'C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\services\calculation_service.py',
    r'C:\Users\YASH SONI\Desktop\Saideep\jewellery-erp\backend\app\services\calculation_service.py'
]

for p in paths:
    with open(p, 'r', encoding='utf-8') as f:
        c = f.read()

    c = c.replace(
        "CalculationService._round_weight(wt_gm * Decimal('5'))",
        "CalculationService._round_final(wt_gm * Decimal('5'), Decimal('0.0001'))"
    )
    c = c.replace(
        "CalculationService._round_weight(carat / Decimal('5'))",
        "CalculationService._round_final(carat / Decimal('5'), Decimal('0.001'))"
    )

    # In return dict, return carat_weight
    if '"carat_weight": carat,' not in c:
        c = c.replace(
            '"weight_gm": wt_gm,',
            '"carat_weight": carat,\n            "weight_gm": wt_gm,'
        )

    with open(p, 'w', encoding='utf-8') as f:
        f.write(c)

print('Fixed calculation_service.py rounding')
