paths = [
    r'C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\services\calculation_service.py',
    r'C:\Users\YASH SONI\Desktop\Saideep\jewellery-erp\backend\app\services\calculation_service.py'
]

for p in paths:
    with open(p, 'r', encoding='utf-8') as f:
        c = f.read()

    target_def = """    @staticmethod
    def calculate_diamond(
        carat_weight: Decimal,
        rate_per_carat: Decimal,"""

    replacement_def = """    @staticmethod
    def calculate_diamond(
        carat_weight: Decimal = Decimal('0'),
        rate_per_carat: Decimal = Decimal('0'),
        weight_gm: Optional[Decimal] = None,
        rate_per_gm: Optional[Decimal] = None,"""

    if target_def in c:
        c = c.replace(target_def, replacement_def)

    target_body = """        carat = CalculationService._to_decimal(carat_weight)
        rate = CalculationService._to_decimal(rate_per_carat)
        making = CalculationService._to_decimal(making_charges)
        other = CalculationService._to_decimal(other_charges)
        disc = CalculationService._to_decimal(discount)
        gst = CalculationService._to_decimal(gst_rate)

        subtotal = CalculationService._round_final(carat * rate)"""

    replacement_body = """        wt_gm = CalculationService._to_decimal(weight_gm) if weight_gm is not None else None
        rt_gm = CalculationService._to_decimal(rate_per_gm) if rate_per_gm is not None else None
        making = CalculationService._to_decimal(making_charges)
        other = CalculationService._to_decimal(other_charges)
        disc = CalculationService._to_decimal(discount)
        gst = CalculationService._to_decimal(gst_rate)

        if wt_gm is not None and wt_gm > 0:
            carat = CalculationService._round_weight(wt_gm * Decimal('5'))
            rate = rt_gm if rt_gm is not None else CalculationService._to_decimal(rate_per_carat)
            subtotal = CalculationService._round_final(wt_gm * (rt_gm if rt_gm is not None else rate))
        else:
            carat = CalculationService._to_decimal(carat_weight)
            rate = CalculationService._to_decimal(rate_per_carat)
            wt_gm = CalculationService._round_weight(carat / Decimal('5'))
            rt_gm = CalculationService._round_final(rate * Decimal('5'))
            subtotal = CalculationService._round_final(carat * rate)"""

    if target_body in c:
        c = c.replace(target_body, replacement_body)

    # Return weight_gm and rate_per_gm in dict result
    target_dict = """            "subtotal": subtotal,
            "taxable_amount": taxable,"""
    replacement_dict = """            "weight_gm": wt_gm,
            "rate_per_gm": rt_gm,
            "subtotal": subtotal,
            "taxable_amount": taxable,"""
    if target_dict in c and "weight_gm" not in c:
        c = c.replace(target_dict, replacement_dict)

    with open(p, 'w', encoding='utf-8') as f:
        f.write(c)

print('Updated calculation_service.py in both repos')
