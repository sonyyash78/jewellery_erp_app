"""
Unified ERP Financial Calculation Service
All calculations use Decimal with 2 decimal precision.
Rounding only on final values.
"""
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Optional
from fastapi import HTTPException

class CalculationService:
    """Single calculation service for all ERP financial operations."""
    
    # Constants
    DECIMAL_PLACES = Decimal('0.01')
    WEIGHT_PLACES = Decimal('0.001')
    PERCENTAGE_PLACES = Decimal('0.01')
    
    @staticmethod
    def _to_decimal(value: any) -> Decimal:
        """Convert any numeric type to Decimal."""
        if isinstance(value, Decimal):
            return value
        return Decimal(str(value))
    
    @staticmethod
    def _round_final(value: Decimal, places: Decimal = None) -> Decimal:
        """Round final values only."""
        if places is None:
            places = CalculationService.DECIMAL_PLACES
        return value.quantize(places, rounding=ROUND_HALF_UP)
    
    # ========== PURCHASE CALCULATIONS ==========
    
    @staticmethod
    def calculate_purchase(
        gross_weight: Decimal,
        stone_weight: Decimal,
        purity: Decimal,
        metal_rate: Decimal,
        labour: Decimal = Decimal('0'),
        making: Decimal = Decimal('0'),
        hallmark: Decimal = Decimal('0'),
        testing: Decimal = Decimal('0'),
        other: Decimal = Decimal('0'),
        discount: Decimal = Decimal('0'),
        gst_rate: Decimal = Decimal('3'),
        is_same_state: bool = True
    ) -> Dict[str, Decimal]:
        """
        Calculate purchase totals.
        
        Net Weight = Gross Weight - Stone Weight
        Fine Weight = Net Weight × Purity / 100
        Metal Value = Fine Weight × Metal Rate
        Taxable = Metal Value + Labour + Making + Hallmark + Testing + Other - Discount
        """
        # Validate inputs
        if gross_weight < stone_weight:
            raise HTTPException(400, "Gross weight must be >= stone weight")
        if not (Decimal('0') <= purity <= Decimal('100')):
            raise HTTPException(400, "Purity must be between 0-100")
        if metal_rate < Decimal('0'):
            raise HTTPException(400, "Rate must be >= 0")
        if gst_rate not in [Decimal('0'), Decimal('3'), Decimal('5')]:
            raise HTTPException(400, "GST must be 0, 3, or 5")
        
        # Convert to Decimal
        gross_weight = CalculationService._to_decimal(gross_weight)
        stone_weight = CalculationService._to_decimal(stone_weight)
        purity = CalculationService._to_decimal(purity)
        metal_rate = CalculationService._to_decimal(metal_rate)
        labour = CalculationService._to_decimal(labour)
        making = CalculationService._to_decimal(making)
        hallmark = CalculationService._to_decimal(hallmark)
        testing = CalculationService._to_decimal(testing)
        other = CalculationService._to_decimal(other)
        discount = CalculationService._to_decimal(discount)
        gst_rate = CalculationService._to_decimal(gst_rate)
        
        # Calculate
        net_weight = gross_weight - stone_weight
        fine_weight = net_weight * purity / Decimal('100')
        metal_value = fine_weight * metal_rate
        
        taxable = metal_value + labour + making + hallmark + testing + other - discount
        
        # GST
        if is_same_state:
            cgst = taxable * gst_rate / Decimal('2') / Decimal('100')
            sgst = taxable * gst_rate / Decimal('2') / Decimal('100')
            igst = Decimal('0')
        else:
            cgst = Decimal('0')
            sgst = Decimal('0')
            igst = taxable * gst_rate / Decimal('100')
        
        grand_total = taxable + cgst + sgst + igst
        
        return {
            'net_weight': CalculationService._round_final(net_weight, CalculationService.WEIGHT_PLACES),
            'fine_weight': CalculationService._round_final(fine_weight, CalculationService.WEIGHT_PLACES),
            'metal_value': CalculationService._round_final(metal_value),
            'taxable': CalculationService._round_final(taxable),
            'cgst': CalculationService._round_final(cgst),
            'sgst': CalculationService._round_final(sgst),
            'igst': CalculationService._round_final(igst),
            'grand_total': CalculationService._round_final(grand_total)
        }
    
    # ========== SELLING CALCULATIONS ==========
    
    @staticmethod
    def calculate_selling(
        net_weight: Decimal,
        metal_rate: Decimal,
        touch_purity: Decimal = Decimal('100'),
        wastage: Decimal = Decimal('0'),
        making_rate: Decimal = Decimal('0'),
        making_type: str = 'FIXED',  # 'FIXED' or 'PER_GRAM'
        hallmark: Decimal = Decimal('0'),
        other: Decimal = Decimal('0'),
        discount: Decimal = Decimal('0'),
        gst_rate: Decimal = Decimal('3')
    ) -> Dict[str, Decimal]:
        """
        Calculate selling totals.
        
        Fine Weight = Net Weight × (Touch + Wastage) / 100
        Metal Value = Fine Weight × Rate (or Net Weight × Rate if no purity specified)
        Making Charge = Net Weight × Making Rate (if PER_GRAM) or Making Rate (if FIXED)
        Taxable = Metal Value + Making + Hallmark + Other - Discount
        Grand Total = Taxable + GST
        """
        # Validate inputs
        if net_weight < Decimal('0'):
            raise HTTPException(400, "Net weight must be >= 0")
        if metal_rate < Decimal('0'):
            raise HTTPException(400, "Rate must be >= 0")
        if gst_rate not in [Decimal('0'), Decimal('3'), Decimal('5')]:
            raise HTTPException(400, "GST must be 0, 3, or 5")
        
        # Convert to Decimal
        net_weight = CalculationService._to_decimal(net_weight)
        metal_rate = CalculationService._to_decimal(metal_rate)
        touch_purity = CalculationService._to_decimal(touch_purity)
        wastage = CalculationService._to_decimal(wastage)
        making_rate = CalculationService._to_decimal(making_rate)
        hallmark = CalculationService._to_decimal(hallmark)
        other = CalculationService._to_decimal(other)
        discount = CalculationService._to_decimal(discount)
        gst_rate = CalculationService._to_decimal(gst_rate)
        
        # Calculate
        fine_weight = net_weight * (touch_purity + wastage) / Decimal('100')
        
        # If touch_purity is 100 and wastage is 0, we can just use net_weight (standard case). 
        # But mathematically, fine_weight == net_weight in that case anyway.
        # In typical retail, metal rate is sometimes quoted for the item's purity (e.g. 22K rate),
        # so if touch_purity is not 100, we apply it. If it is 100, fine_weight equals net_weight.
        metal_value = fine_weight * metal_rate
        
        if making_type == 'PER_GRAM':
            making_charge = net_weight * making_rate
        else:  # FIXED
            making_charge = making_rate
        
        taxable = metal_value + making_charge + hallmark + other - discount
        gst = taxable * gst_rate / Decimal('100')
        grand_total = taxable + gst
        
        return {
            'fine_weight': CalculationService._round_final(fine_weight, CalculationService.WEIGHT_PLACES),
            'metal_value': CalculationService._round_final(metal_value),
            'making_charge': CalculationService._round_final(making_charge),
            'taxable': CalculationService._round_final(taxable),
            'gst': CalculationService._round_final(gst),
            'grand_total': CalculationService._round_final(grand_total)
        }
    
    # ========== INVENTORY CALCULATIONS ==========
    
    @staticmethod
    def calculate_stock_weight(
        opening: Decimal,
        purchase: Decimal,
        exchange_in: Decimal,
        sale: Decimal,
        exchange_out: Decimal
    ) -> Dict[str, Decimal]:
        """
        Calculate stock weight.
        
        Stock Weight = Opening + Purchase + Exchange In - Sale - Exchange Out
        """
        # Convert to Decimal
        opening = CalculationService._to_decimal(opening)
        purchase = CalculationService._to_decimal(purchase)
        exchange_in = CalculationService._to_decimal(exchange_in)
        sale = CalculationService._to_decimal(sale)
        exchange_out = CalculationService._to_decimal(exchange_out)
        
        stock_weight = opening + purchase + exchange_in - sale - exchange_out
        
        return {
            'stock_weight': CalculationService._round_final(stock_weight, CalculationService.WEIGHT_PLACES)
        }
    
    @staticmethod
    def calculate_fine_weight(
        net_weight: Decimal,
        purity: Decimal
    ) -> Dict[str, Decimal]:
        """
        Calculate fine weight.
        
        Fine Weight = Net Weight × Purity / 100
        """
        # Validate
        if not (Decimal('0') <= purity <= Decimal('100')):
            raise HTTPException(400, "Purity must be between 0-100")
        
        # Convert to Decimal
        net_weight = CalculationService._to_decimal(net_weight)
        purity = CalculationService._to_decimal(purity)
        
        fine_weight = net_weight * purity / Decimal('100')
        
        return {
            'fine_weight': CalculationService._round_final(fine_weight, CalculationService.WEIGHT_PLACES)
        }
    
    @staticmethod
    def calculate_inventory_value(
        net_weight: Decimal,
        latest_metal_rate: Decimal
    ) -> Dict[str, Decimal]:
        """
        Calculate inventory value.
        
        Inventory Value = Net Weight × Latest Metal Rate
        """
        # Convert to Decimal
        net_weight = CalculationService._to_decimal(net_weight)
        latest_metal_rate = CalculationService._to_decimal(latest_metal_rate)
        
        inventory_value = net_weight * latest_metal_rate
        
        return {
            'inventory_value': CalculationService._round_final(inventory_value)
        }
    
    # ========== REPORT CALCULATIONS ==========
    
    @staticmethod
    def calculate_cogs(
        purchase_cost: Decimal,
        making: Decimal = Decimal('0'),
        labour: Decimal = Decimal('0'),
        hallmark: Decimal = Decimal('0'),
        stone: Decimal = Decimal('0'),
        other_charges: Decimal = Decimal('0')
    ) -> Dict[str, Decimal]:
        """
        Calculate Cost of Goods Sold.
        
        COGS = Purchase Cost + Making + Labour + Hallmark + Stone + Other Charges
        Note: GST is NOT included in COGS
        """
        # Convert to Decimal
        purchase_cost = CalculationService._to_decimal(purchase_cost)
        making = CalculationService._to_decimal(making)
        labour = CalculationService._to_decimal(labour)
        hallmark = CalculationService._to_decimal(hallmark)
        stone = CalculationService._to_decimal(stone)
        other_charges = CalculationService._to_decimal(other_charges)
        
        cogs = purchase_cost + making + labour + hallmark + stone + other_charges
        
        return {
            'cogs': CalculationService._round_final(cogs)
        }
    
    @staticmethod
    def calculate_gross_profit(
        sales: Decimal,
        cogs: Decimal
    ) -> Dict[str, Decimal]:
        """
        Calculate Gross Profit.
        
        Gross Profit = Sales - COGS
        """
        # Convert to Decimal
        sales = CalculationService._to_decimal(sales)
        cogs = CalculationService._to_decimal(cogs)
        
        gross_profit = sales - cogs
        
        return {
            'gross_profit': CalculationService._round_final(gross_profit)
        }
    
    @staticmethod
    def calculate_net_profit(
        gross_profit: Decimal,
        expenses: Decimal = Decimal('0')
    ) -> Dict[str, Decimal]:
        """
        Calculate Net Profit.
        
        Net Profit = Gross Profit - Expenses
        Note: GST is NOT an expense
        """
        # Convert to Decimal
        gross_profit = CalculationService._to_decimal(gross_profit)
        expenses = CalculationService._to_decimal(expenses)
        
        net_profit = gross_profit - expenses
        
        return {
            'net_profit': CalculationService._round_final(net_profit)
        }
    
    @staticmethod
    def calculate_gst_liability(
        output_gst: Decimal,
        input_gst: Decimal
    ) -> Dict[str, Decimal]:
        """
        Calculate Net GST Liability (Input Tax Credit).
        
        Output GST = Sum(Sales GST)
        Input GST = Sum(Purchase GST)
        Net GST = Output GST - Input GST (ITC)
        """
        # Convert to Decimal
        output_gst = CalculationService._to_decimal(output_gst)
        input_gst = CalculationService._to_decimal(input_gst)
        
        net_gst = output_gst - input_gst
        
        return {
            'output_gst': CalculationService._round_final(output_gst),
            'input_gst': CalculationService._round_final(input_gst),
            'net_gst': CalculationService._round_final(net_gst)
        }
    
    @staticmethod
    def calculate_profit(
        sales_total: Decimal,
        purchases_total: Decimal,
        expenses: Decimal = Decimal('0')
    ) -> Dict[str, Decimal]:
        """
        DEPRECATED: Use calculate_gross_profit and calculate_net_profit instead.
        
        This simplified version is kept for backward compatibility.
        Correct formula: Net Profit = Sales - COGS - Expenses
        """
        # Convert to Decimal
        sales_total = CalculationService._to_decimal(sales_total)
        purchases_total = CalculationService._to_decimal(purchases_total)
        expenses = CalculationService._to_decimal(expenses)
        
        profit = sales_total - purchases_total - expenses
        
        return {
            'profit': CalculationService._round_final(profit)
        }
    
    # ========== VALIDATION ==========
    
    @staticmethod
    def validate_weights(
        gross_weight: Decimal,
        stone_weight: Decimal = Decimal('0')
    ) -> bool:
        """Validate: Gross >= Stone, Net >= 0"""
        gross_weight = CalculationService._to_decimal(gross_weight)
        stone_weight = CalculationService._to_decimal(stone_weight)
        
        if gross_weight < stone_weight:
            raise HTTPException(400, "Gross weight must be >= stone weight")
        if (gross_weight - stone_weight) < Decimal('0'):
            raise HTTPException(400, "Net weight must be >= 0")
        return True
    
    @staticmethod
    def validate_percentage(
        value: Decimal,
        field_name: str
    ) -> bool:
        """Validate: Value between 0-100"""
        value = CalculationService._to_decimal(value)
        
        if not (Decimal('0') <= value <= Decimal('100')):
            raise HTTPException(400, f"{field_name} must be between 0-100")
        return True
    
    @staticmethod
    def validate_positive(
        value: Decimal,
        field_name: str
    ) -> bool:
        """Validate: Value >= 0"""
        value = CalculationService._to_decimal(value)
        
        if value < Decimal('0'):
            raise HTTPException(400, f"{field_name} must be >= 0")
        return True
    
    @staticmethod
    def validate_gst_rate(gst_rate: Decimal) -> bool:
        """Validate: GST only 0, 3, 5"""
        gst_rate = CalculationService._to_decimal(gst_rate)
        
        if gst_rate not in [Decimal('0'), Decimal('3'), Decimal('5')]:
            raise HTTPException(400, "GST must be 0, 3, or 5")
        return True
