from decimal import Decimal, ROUND_HALF_UP

class PurchaseService:
    @staticmethod
    def calculate_silver_purchase(weight: Decimal, tanch: Decimal, wastage: Decimal, todays_rate: Decimal) -> dict:
        """
        Calculate Silver Purchase values.
        Formula:
        Final Tanch = Tanch + Wastage
        Recovered Silver = Weight * (Final Tanch / 100)
        Silver Value = Recovered Silver * (Today's Rate / 1000) (Assuming rate is per kg, wait. Usually Silver rate is per Kg or per gram)
        Wait, if rate is per gram, then Value = Recovered * Rate.
        Let's assume rate is per gram or per 10 grams. Let's use per gram for consistency.
        """
        final_tanch = tanch + wastage
        recovered_silver = weight * (final_tanch / Decimal('100.0'))
        
        # If todays rate is per kg, then divide by 1000. 
        # Typically in ERPs rate per gram is used.
        silver_value = recovered_silver * todays_rate
        
        return {
            "final_tanch": final_tanch.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP),
            "recovered_silver": recovered_silver.quantize(Decimal('0.000'), rounding=ROUND_HALF_UP),
            "silver_value": silver_value.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
        }
