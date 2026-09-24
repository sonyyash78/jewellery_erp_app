# GST Calculation Formulas - Single Source of Truth

## Core Principle
**Use one taxable_amount for all GST calculations. Never recalculate GST from different bases.**

## Invoice/Sales GST

### Taxable Amount
```
Taxable Amount = 
    Metal Value
    + Making Charge
    + Hallmark Charge
    + Other Charges
    - Discount
```

### GST Calculation (Same State)
```
CGST = Taxable Amount × GST Rate / 2
SGST = Taxable Amount × GST Rate / 2  
IGST = 0
Total GST = CGST + SGST + IGST
```

### GST Calculation (Different State)
```
CGST = 0
SGST = 0
IGST = Taxable Amount × GST Rate
Total GST = IGST
```

### Grand Total
```
Grand Total = Taxable Amount + Total GST
```

### Validation
```
✓ Grand Total = Taxable + CGST + SGST + IGST
✓ Total GST = CGST + SGST + IGST
✓ Use invoice.tax_amount from database (do NOT recalculate)
```

## Purchase GST

### Taxable Amount
```
Taxable Amount = 
    Metal Value (Fine Weight × Rate)
    + Labour Charge
    + Making Charge
    + Hallmark Charge
    + Testing Charge
    + Other Charges
    - Discount
```

### GST Calculation (Same State)
```
CGST = Taxable Amount × GST Rate / 2
SGST = Taxable Amount × GST Rate / 2
IGST = 0
Total GST = CGST + SGST
```

### GST Calculation (Different State)
```
CGST = 0
SGST = 0
IGST = Taxable Amount × GST Rate
Total GST = IGST
```

### Grand Total
```
Grand Total = Taxable Amount + Total GST
```

### Validation
```
✓ Grand Total = Taxable + CGST + SGST + IGST
✓ Total GST = CGST + SGST + IGST
✓ Use purchase.cgst, purchase.sgst, purchase.igst from database
```

## GST Report (Input Tax Credit)

### Output GST (Sales)
```
Output GST = SUM(invoice.tax_amount)
            WHERE invoice_date BETWEEN start_date AND end_date
```

### Input GST (Purchases)
```
Input GST = SUM(purchase.cgst + purchase.sgst + purchase.igst)
           WHERE purchase_date BETWEEN start_date AND end_date
```

### Net GST Payable (ITC Applied)
```
Net GST Payable = Output GST - Input GST
```

### Validation
```
✓ Output GST = SUM(Sales GST) from database
✓ Input GST = SUM(Purchase GST) from database
✓ No recalculation - use stored values
✓ Net GST = Output - Input (Input Tax Credit)
```

## Database Schema

### Invoice Table (Sales)
```sql
invoices
├── subtotal         -- Taxable Amount (before GST)
├── tax_amount       -- Total GST (CGST + SGST + IGST)
├── discount_amount  -- Total Discount
└── grand_total      -- Subtotal + Tax
```

**Note**: Currently CGST/SGST/IGST not stored separately in invoices. Consider adding these columns for precise tracking.

### Purchase Table
```sql
purchases
├── total_taxable    -- Taxable Amount (before GST)
├── cgst             -- Central GST
├── sgst             -- State GST
├── igst             -- Integrated GST
└── grand_total      -- Taxable + CGST + SGST + IGST
```

## Common Mistakes to Avoid

❌ **Wrong**: Recalculating GST from grand total
```python
gst = grand_total - subtotal  # WRONG - ignores discount
```

❌ **Wrong**: Using different taxable amounts
```python
gst1 = metal_value * 0.03
gst2 = (metal_value + making) * 0.03  # INCONSISTENT
```

❌ **Wrong**: Mixing float and Decimal
```python
taxable = float(metal_value)  # WRONG - precision loss
gst = taxable * 0.03
```

✅ **Correct**: Use database values
```python
# Sales
output_gst = Decimal(str(invoice.tax_amount))

# Purchase
input_gst = (
    Decimal(str(purchase.cgst)) +
    Decimal(str(purchase.sgst)) +
    Decimal(str(purchase.igst))
)

# Net GST
net_gst = output_gst - input_gst
```

✅ **Correct**: Calculate GST from one taxable amount
```python
taxable_amount = Decimal(str(metal_value + making + charges - discount))
cgst = taxable_amount * Decimal('0.03') / Decimal('2')
sgst = taxable_amount * Decimal('0.03') / Decimal('2')
total_gst = cgst + sgst
grand_total = taxable_amount + total_gst
```

✅ **Correct**: Use Decimal everywhere
```python
from decimal import Decimal, ROUND_HALF_UP

taxable = Decimal('1000.00')
gst = taxable * Decimal('0.03')
total = taxable + gst
# Round only final output
final = total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
```

## Testing Checklist

When implementing GST calculations:

1. ✅ Use one taxable_amount as base for all GST
2. ✅ Validate: GST = CGST + SGST + IGST
3. ✅ Validate: Grand Total = Taxable + GST
4. ✅ Use Decimal (not float) for all amounts
5. ✅ Round only final values to 2 decimal places
6. ✅ Store GST components separately (CGST/SGST/IGST)
7. ✅ Use database values in reports (no recalculation)
8. ✅ Apply Input Tax Credit correctly: Net = Output - Input
9. ✅ Handle same-state vs different-state GST rules
10. ✅ Add validation warnings for mismatches

## GST Rates (India - Jewellery)

| Item | GST Rate |
|------|----------|
| Gold Jewellery | 3% |
| Silver Jewellery | 3% |
| Gold Bars/Coins | 3% |
| Making Charges | 5% (if separate) |
| Stones/Diamonds | 3% |

**Implementation**: Currently using 3% for all items. GST rate should be configurable per item category.
