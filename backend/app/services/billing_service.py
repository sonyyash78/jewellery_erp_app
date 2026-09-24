from decimal import Decimal, ROUND_HALF_UP
from typing import List

class BillingService:
    @staticmethod
    def calculate_item_total(
        net_weight: Decimal, 
        rate: Decimal, 
        making_charge: Decimal, 
        making_charge_type: str,
        hallmark_charge: Decimal,
        other_charges: Decimal
    ) -> Decimal:
        """Calculate total for a single bill item."""
        gold_value = net_weight * rate
        
        mc = Decimal('0.00')
        if making_charge_type == "PERCENTAGE":
            mc = gold_value * (making_charge / Decimal('100.0'))
        elif making_charge_type == "PER_GRAM":
            mc = net_weight * making_charge
        elif making_charge_type == "FLAT":
            mc = making_charge
            
        total = gold_value + mc + hallmark_charge + other_charges
        return total.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)

    @staticmethod
    def calculate_bill_totals(
        item_totals: List[Decimal], 
        discount: Decimal,
        cgst_rate: Decimal = Decimal('1.5'),
        sgst_rate: Decimal = Decimal('1.5'),
        igst_rate: Decimal = Decimal('0.0')
    ) -> dict:
        """Calculate the overall bill grand total, GST, and round off."""
        subtotal = sum(item_totals) - discount
        
        if subtotal < 0:
            subtotal = Decimal('0.00')
            
        cgst = subtotal * (cgst_rate / Decimal('100.0'))
        sgst = subtotal * (sgst_rate / Decimal('100.0'))
        igst = subtotal * (igst_rate / Decimal('100.0'))
        
        total_with_tax = subtotal + cgst + sgst + igst
        grand_total = total_with_tax.quantize(Decimal('1.'), rounding=ROUND_HALF_UP)
        round_off = grand_total - total_with_tax
        
        return {
            "total_amount": sum(item_totals).quantize(Decimal('0.00')),
            "cgst": cgst.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP),
            "sgst": sgst.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP),
            "igst": igst.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP),
            "grand_total": grand_total,
            "round_off": round_off.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
        }
