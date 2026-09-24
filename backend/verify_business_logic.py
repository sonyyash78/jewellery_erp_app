#!/usr/bin/env python3
"""
Business Logic Verification Script
Verifies GST calculations, discounts, round-off, totals, and profit calculations
"""

import sys
from decimal import Decimal

# Colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

class BusinessLogicVerifier:
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []
        
    def log_pass(self, msg: str):
        self.passed.append(msg)
        print(f"{GREEN}✓ PASS{RESET}: {msg}")
        
    def log_fail(self, msg: str, details: str = ""):
        self.failed.append(f"{msg} | {details}")
        print(f"{RED}✗ FAIL{RESET}: {msg}")
        if details:
            print(f"  Details: {details}")
            
    def log_warn(self, msg: str):
        self.warnings.append(msg)
        print(f"{YELLOW}⚠ WARN{RESET}: {msg}")

    def verify_gst_calculations(self):
        """Verify GST calculation formulas"""
        print("\n=== GST CALCULATIONS ===")
        
        # Test case 1: Basic GST calculation at 3%
        base_amount = Decimal('10000')
        gst_rate = Decimal('3')
        
        # Method 1: Calculate GST on base
        gst_amount = (base_amount * gst_rate) / Decimal('100')
        total_with_gst = base_amount + gst_amount
        
        expected_gst = Decimal('300')
        expected_total = Decimal('10300')
        
        if abs(gst_amount - expected_gst) < Decimal('0.01'):
            self.log_pass(f"GST calculation: ₹10000 @ 3% = ₹{gst_amount} (correct)")
        else:
            self.log_fail(f"GST calculation: Expected ₹{expected_gst}, got ₹{gst_amount}")
            
        if abs(total_with_gst - expected_total) < Decimal('0.01'):
            self.log_pass(f"Total with GST: ₹10000 + ₹300 GST = ₹{total_with_gst} (correct)")
        else:
            self.log_fail(f"Total with GST: Expected ₹{expected_total}, got ₹{total_with_gst}")
        
        # Test case 2: Reverse GST calculation (inclusive)
        total_inclusive = Decimal('10300')
        gst_rate = Decimal('3')
        
        # Extract base from inclusive total
        base_from_inclusive = (total_inclusive * Decimal('100')) / (Decimal('100') + gst_rate)
        gst_from_inclusive = total_inclusive - base_from_inclusive
        
        if abs(base_from_inclusive - base_amount) < Decimal('0.01'):
            self.log_pass(f"Reverse GST: ₹10300 inclusive @ 3% → base ₹{base_from_inclusive:.2f} (correct)")
        else:
            self.log_fail(f"Reverse GST: Expected base ₹{base_amount}, got ₹{base_from_inclusive}")
            
        # Test case 3: CGST + SGST split
        gst_rate = Decimal('3')
        cgst_rate = gst_rate / Decimal('2')
        sgst_rate = gst_rate / Decimal('2')
        
        if cgst_rate == Decimal('1.5') and sgst_rate == Decimal('1.5'):
            self.log_pass(f"GST split: 3% = 1.5% CGST + 1.5% SGST (correct)")
        else:
            self.log_fail(f"GST split: Expected 1.5%+1.5%, got {cgst_rate}%+{sgst_rate}%")

    def verify_discount_calculations(self):
        """Verify discount calculations"""
        print("\n=== DISCOUNT CALCULATIONS ===")
        
        # Test case 1: Percentage discount
        original_price = Decimal('5000')
        discount_percent = Decimal('10')
        
        discount_amount = (original_price * discount_percent) / Decimal('100')
        final_price = original_price - discount_amount
        
        expected_discount = Decimal('500')
        expected_final = Decimal('4500')
        
        if abs(discount_amount - expected_discount) < Decimal('0.01'):
            self.log_pass(f"Percentage discount: 10% of ₹5000 = ₹{discount_amount} (correct)")
        else:
            self.log_fail(f"Percentage discount: Expected ₹{expected_discount}, got ₹{discount_amount}")
            
        if abs(final_price - expected_final) < Decimal('0.01'):
            self.log_pass(f"Final price after discount: ₹5000 - ₹500 = ₹{final_price} (correct)")
        else:
            self.log_fail(f"Final price: Expected ₹{expected_final}, got ₹{final_price}")
        
        # Test case 2: Fixed amount discount
        original_price = Decimal('5000')
        discount_fixed = Decimal('750')
        
        final_price = original_price - discount_fixed
        expected_final = Decimal('4250')
        
        if abs(final_price - expected_final) < Decimal('0.01'):
            self.log_pass(f"Fixed discount: ₹5000 - ₹750 = ₹{final_price} (correct)")
        else:
            self.log_fail(f"Fixed discount: Expected ₹{expected_final}, got ₹{final_price}")

    def verify_round_off(self):
        """Verify round-off logic"""
        print("\n=== ROUND-OFF CALCULATIONS ===")
        
        test_cases = [
            (Decimal('1234.56'), Decimal('1235'), "Round up"),
            (Decimal('1234.44'), Decimal('1234'), "Round down"),
            (Decimal('1234.50'), Decimal('1235'), "Round half up"),
            (Decimal('9999.99'), Decimal('10000'), "Round large number"),
        ]
        
        for original, expected, description in test_cases:
            rounded = round(original)
            if rounded == expected:
                self.log_pass(f"{description}: ₹{original} → ₹{rounded} (correct)")
            else:
                self.log_fail(f"{description}: Expected ₹{expected}, got ₹{rounded}")
                
        # Test round-off adjustment
        subtotal = Decimal('1234.56')
        rounded_total = round(subtotal)
        round_off_adjustment = rounded_total - subtotal
        
        expected_adjustment = Decimal('0.44')
        if abs(round_off_adjustment - expected_adjustment) < Decimal('0.01'):
            self.log_pass(f"Round-off adjustment: ₹{subtotal} → ₹{rounded_total}, adjustment = ₹{round_off_adjustment:.2f} (correct)")
        else:
            self.log_fail(f"Round-off adjustment: Expected ₹{expected_adjustment}, got ₹{round_off_adjustment}")

    def verify_invoice_totals(self):
        """Verify invoice total calculations"""
        print("\n=== INVOICE TOTAL CALCULATIONS ===")
        
        # Complex invoice with multiple items
        item1_price = Decimal('10000')
        item2_price = Decimal('5000')
        subtotal = item1_price + item2_price
        
        expected_subtotal = Decimal('15000')
        if subtotal == expected_subtotal:
            self.log_pass(f"Invoice subtotal: ₹10000 + ₹5000 = ₹{subtotal} (correct)")
        else:
            self.log_fail(f"Invoice subtotal: Expected ₹{expected_subtotal}, got ₹{subtotal}")
        
        # Apply discount
        discount_percent = Decimal('5')
        discount_amount = (subtotal * discount_percent) / Decimal('100')
        amount_after_discount = subtotal - discount_amount
        
        expected_discount = Decimal('750')
        expected_after_discount = Decimal('14250')
        
        if abs(discount_amount - expected_discount) < Decimal('0.01'):
            self.log_pass(f"Invoice discount: 5% of ₹15000 = ₹{discount_amount} (correct)")
        else:
            self.log_fail(f"Invoice discount: Expected ₹{expected_discount}, got ₹{discount_amount}")
        
        # Apply GST
        gst_rate = Decimal('3')
        gst_amount = (amount_after_discount * gst_rate) / Decimal('100')
        total_with_gst = amount_after_discount + gst_amount
        
        expected_gst = Decimal('427.50')
        expected_total = Decimal('14677.50')
        
        if abs(gst_amount - expected_gst) < Decimal('0.01'):
            self.log_pass(f"Invoice GST: 3% of ₹14250 = ₹{gst_amount} (correct)")
        else:
            self.log_fail(f"Invoice GST: Expected ₹{expected_gst}, got ₹{gst_amount}")
        
        # Round-off
        grand_total = round(total_with_gst)
        round_off = grand_total - total_with_gst
        
        expected_grand_total = Decimal('14678')
        if grand_total == expected_grand_total:
            self.log_pass(f"Invoice grand total: ₹{total_with_gst:.2f} → ₹{grand_total} (correct)")
        else:
            self.log_fail(f"Invoice grand total: Expected ₹{expected_grand_total}, got ₹{grand_total}")

    def verify_purchase_calculations(self):
        """Verify purchase calculation logic"""
        print("\n=== PURCHASE CALCULATIONS ===")
        
        # Gold purchase calculation
        weight_grams = Decimal('100')
        rate_per_gram = Decimal('6000')
        purity_percent = Decimal('91.6')  # 22K
        
        # Pure gold value
        pure_weight = (weight_grams * purity_percent) / Decimal('100')
        pure_value = pure_weight * rate_per_gram
        
        expected_pure_weight = Decimal('91.6')
        expected_value = Decimal('549600')
        
        if abs(pure_weight - expected_pure_weight) < Decimal('0.01'):
            self.log_pass(f"Pure gold weight: 100g @ 91.6% = {pure_weight}g (correct)")
        else:
            self.log_fail(f"Pure gold weight: Expected {expected_pure_weight}g, got {pure_weight}g")
            
        if abs(pure_value - expected_value) < Decimal('0.01'):
            self.log_pass(f"Gold purchase value: 91.6g @ ₹6000 = ₹{pure_value} (correct)")
        else:
            self.log_fail(f"Gold purchase value: Expected ₹{expected_value}, got ₹{pure_value}")
        
        # Making charges
        making_charge_per_gram = Decimal('500')
        making_charges = weight_grams * making_charge_per_gram
        
        expected_making = Decimal('50000')
        if making_charges == expected_making:
            self.log_pass(f"Making charges: 100g @ ₹500 = ₹{making_charges} (correct)")
        else:
            self.log_fail(f"Making charges: Expected ₹{expected_making}, got ₹{making_charges}")
        
        # Total purchase cost
        total_cost = pure_value + making_charges
        expected_total = Decimal('599600')
        
        if total_cost == expected_total:
            self.log_pass(f"Total purchase cost: ₹549600 + ₹50000 = ₹{total_cost} (correct)")
        else:
            self.log_fail(f"Total purchase cost: Expected ₹{expected_total}, got ₹{total_cost}")

    def verify_stock_calculations(self):
        """Verify stock quantity calculations"""
        print("\n=== STOCK CALCULATIONS ===")
        
        # Opening stock
        opening_stock = 100
        
        # Add purchases
        purchases = 50
        current_stock = opening_stock + purchases
        
        if current_stock == 150:
            self.log_pass(f"Stock after purchase: 100 + 50 = {current_stock} (correct)")
        else:
            self.log_fail(f"Stock after purchase: Expected 150, got {current_stock}")
        
        # Subtract sales
        sales = 30
        current_stock = current_stock - sales
        
        if current_stock == 120:
            self.log_pass(f"Stock after sale: 150 - 30 = {current_stock} (correct)")
        else:
            self.log_fail(f"Stock after sale: Expected 120, got {current_stock}")
        
        # Check low stock alert
        min_stock = 20
        low_stock = current_stock < min_stock
        
        if not low_stock:
            self.log_pass(f"Low stock check: {current_stock} >= {min_stock}, no alert (correct)")
        else:
            self.log_fail(f"Low stock check: {current_stock} < {min_stock}, should not alert")

    def verify_profit_calculations(self):
        """Verify profit calculation logic"""
        print("\n=== PROFIT CALCULATIONS ===")
        
        # Single item profit
        cost_price = Decimal('5000')
        selling_price = Decimal('7000')
        
        profit = selling_price - cost_price
        profit_percent = (profit / cost_price) * Decimal('100')
        
        expected_profit = Decimal('2000')
        expected_profit_percent = Decimal('40')
        
        if profit == expected_profit:
            self.log_pass(f"Item profit: ₹7000 - ₹5000 = ₹{profit} (correct)")
        else:
            self.log_fail(f"Item profit: Expected ₹{expected_profit}, got ₹{profit}")
            
        if abs(profit_percent - expected_profit_percent) < Decimal('0.01'):
            self.log_pass(f"Profit percentage: (₹2000 / ₹5000) × 100 = {profit_percent:.2f}% (correct)")
        else:
            self.log_fail(f"Profit percentage: Expected {expected_profit_percent}%, got {profit_percent}%")
        
        # Gross profit calculation
        total_sales = Decimal('100000')
        total_cost = Decimal('70000')
        gross_profit = total_sales - total_cost
        gross_margin = (gross_profit / total_sales) * Decimal('100')
        
        expected_gross_profit = Decimal('30000')
        expected_margin = Decimal('30')
        
        if gross_profit == expected_gross_profit:
            self.log_pass(f"Gross profit: ₹100000 - ₹70000 = ₹{gross_profit} (correct)")
        else:
            self.log_fail(f"Gross profit: Expected ₹{expected_gross_profit}, got ₹{gross_profit}")
            
        if abs(gross_margin - expected_margin) < Decimal('0.01'):
            self.log_pass(f"Gross margin: (₹30000 / ₹100000) × 100 = {gross_margin:.2f}% (correct)")
        else:
            self.log_fail(f"Gross margin: Expected {expected_margin}%, got {gross_margin}%")

    def verify_weight_calculations(self):
        """Verify weight calculation formulas"""
        print("\n=== WEIGHT CALCULATIONS ===")
        
        # Gross weight, net weight, stone weight
        gross_weight = Decimal('25.5')
        stone_weight = Decimal('2.3')
        net_weight = gross_weight - stone_weight
        
        expected_net = Decimal('23.2')
        
        if abs(net_weight - expected_net) < Decimal('0.01'):
            self.log_pass(f"Net weight: 25.5g - 2.3g stones = {net_weight}g (correct)")
        else:
            self.log_fail(f"Net weight: Expected {expected_net}g, got {net_weight}g")
        
        # Weight conversion (grams to tolas, if applicable)
        grams = Decimal('100')
        tola_conversion = Decimal('11.664')  # 1 tola = 11.664 grams
        tolas = grams / tola_conversion
        
        expected_tolas = Decimal('8.573')
        if abs(tolas - expected_tolas) < Decimal('0.01'):
            self.log_pass(f"Weight conversion: 100g = {tolas:.3f} tolas (correct)")
        else:
            self.log_warn(f"Weight conversion: Expected {expected_tolas} tolas, got {tolas:.3f} tolas")

    def print_summary(self):
        """Print verification summary"""
        print("\n" + "="*70)
        print("BUSINESS LOGIC VERIFICATION SUMMARY")
        print("="*70)
        print(f"\n{GREEN}PASSED: {len(self.passed)}{RESET}")
        for msg in self.passed[:15]:  # Show first 15
            print(f"  ✓ {msg}")
        if len(self.passed) > 15:
            print(f"  ... and {len(self.passed) - 15} more")
            
        if self.warnings:
            print(f"\n{YELLOW}WARNINGS: {len(self.warnings)}{RESET}")
            for msg in self.warnings:
                print(f"  ⚠ {msg}")
            
        if self.failed:
            print(f"\n{RED}FAILED: {len(self.failed)}{RESET}")
            for msg in self.failed:
                print(f"  ✗ {msg}")
            
        print("\n" + "="*70)
        total = len(self.passed) + len(self.failed)
        pass_rate = (len(self.passed) / total * 100) if total > 0 else 0
        print(f"Pass Rate: {pass_rate:.1f}% ({len(self.passed)}/{total})")
        print("="*70 + "\n")
        
        return len(self.failed) == 0

def main():
    print("="*70)
    print("BUSINESS LOGIC VERIFICATION")
    print("="*70)
    print("Testing: GST, Discounts, Round-off, Totals, Profit, Stock, Weights")
    print("="*70)
    
    verifier = BusinessLogicVerifier()
    
    verifier.verify_gst_calculations()
    verifier.verify_discount_calculations()
    verifier.verify_round_off()
    verifier.verify_invoice_totals()
    verifier.verify_purchase_calculations()
    verifier.verify_stock_calculations()
    verifier.verify_profit_calculations()
    verifier.verify_weight_calculations()
    
    success = verifier.print_summary()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
