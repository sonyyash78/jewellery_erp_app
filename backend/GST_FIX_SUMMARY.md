# GST Calculation Fix Summary

## Problem
Purchase taxable amount and GST values were inconsistent. GST was being recalculated differently in reports vs stored in database, causing mismatches.

## Root Cause
1. **Sales Report**: Was recalculating GST from `invoice.grand_total - invoice.subtotal + invoice.discount_amount` instead of using `invoice.tax_amount`
2. **Purchase Report**: Was using stored values correctly (cgst, sgst, igst)
3. **GST Report**: Was recalculating values unnecessarily instead of validating database values
4. **Decimal Conversion Error**: `total_expenses` was returning int(0) causing AttributeError in profit calculations

## Fix Applied

### 1. Sales Report (`get_sales_report`)
**BEFORE**: Recalculated GST from totals
```python
gst = Decimal(str(invoice.grand_total)) - Decimal(str(invoice.subtotal)) + Decimal(str(invoice.discount_amount))
```

**AFTER**: Uses stored `tax_amount` directly
```python
tax_amount = Decimal(str(invoice.tax_amount))
total_gst += tax_amount
```

### 2. Purchase Report (`get_purchase_report`)
**Status**: ✅ Already correct - uses stored CGST/SGST/IGST values

**Added**: Validation warning
```python
if abs(calculated_grand_total - total_purchases) > Decimal('1.00'):
    print(f"WARNING: Purchase total mismatch...")
```

### 3. GST Report (`get_gst_report`)
**BEFORE**: Used CalculationService to recalculate
```python
gst_result = CalculationService.calculate_gst_liability(output_gst, input_gst)
```

**AFTER**: Uses database values directly with validation
```python
output_gst = Decimal(str(sales_report['output_gst']))
input_gst = Decimal(str(purchase_report['input_gst']))
net_gst = output_gst - input_gst

# Validate GST = CGST + SGST + IGST
if abs(output_gst - output_gst_calculated) > Decimal('0.01'):
    print(f"WARNING: Output GST mismatch...")
```

### 4. Profit Report (`get_profit_report`)
**Fixed**: Decimal conversion error
```python
# BEFORE
total_expenses = sum([Decimal(str(e.amount)) for e in expenses])

# AFTER
total_expenses = sum([Decimal(str(e.amount)) for e in expenses], Decimal('0'))
```

## Formulas Validated

### Sales
- **Grand Total** = Taxable + GST
- **Output GST** = invoice.tax_amount (stored in DB)
- **GST Split** = CGST + SGST + IGST (approximated as 50/50 for same state)

### Purchases
- **Grand Total** = Taxable + CGST + SGST + IGST
- **Input GST** = CGST + SGST + IGST
- **Validation**: Grand Total = Taxable + Input GST

### GST Report
- **Output GST** = Sum(Sales tax_amount) from database
- **Input GST** = Sum(Purchase CGST + SGST + IGST) from database
- **Net GST Payable** = Output GST - Input GST (ITC)
- **Validation**: GST components sum to total GST

### Profit
- **COGS** = Purchase Taxable (includes all charges)
- **Gross Profit** = Sales Taxable - COGS
- **Net Profit** = Gross Profit - Expenses
- **Note**: GST excluded from profit calculations ✅

## Test Results

All 8 report tests passing:
- ✅ test_sales_report
- ✅ test_purchases_report
- ✅ test_inventory_report
- ✅ test_profit_report
- ✅ test_expenses_report
- ✅ test_gst_report (validates Net GST = Output - Input)
- ✅ test_customers_report
- ✅ test_suppliers_report

## Files Changed

1. **app/services/report_service.py**
   - Fixed `get_sales_report()` to use `invoice.tax_amount`
   - Added validation warnings in `get_purchase_report()`
   - Simplified `get_gst_report()` to use database values with validation
   - Fixed `get_profit_report()` Decimal conversion

2. **test_reports.py**
   - Updated test expectations to match correct response structure
   - Added GST formula validation in test_gst_report

## Verification Checklist

✅ One taxable_amount used for all calculations
✅ GST calculated only from taxable_amount
✅ GST = CGST + SGST + IGST (validated)
✅ Invoice Total = Taxable + GST (validated)
✅ Net GST = Output GST - Input GST (ITC)
✅ No duplicate GST calculations
✅ Decimal used everywhere
✅ Database values used instead of recalculation
✅ Validation warnings for mismatches
✅ All tests passing

## Usage

### API Endpoints
```bash
# Sales Report
GET /api/v1/reports/sales?start_date=2024-01-01&end_date=2024-12-31

# Purchase Report
GET /api/v1/reports/purchases?start_date=2024-01-01&end_date=2024-12-31

# GST Report (with ITC)
GET /api/v1/reports/gst?start_date=2024-01-01&end_date=2024-12-31

# Profit Report
GET /api/v1/reports/profit?start_date=2024-01-01&end_date=2024-12-31
```

### Response Structure

**GST Report Response**:
```json
{
  "output_gst": 221489.75,
  "output_cgst": 110744.88,
  "output_sgst": 110744.88,
  "output_igst": 0.0,
  "input_gst": 25842.24,
  "input_cgst": 12921.12,
  "input_sgst": 12921.12,
  "input_igst": 0.0,
  "net_gst_payable": 195647.51
}
```

**Validation**: net_gst_payable = output_gst - input_gst ✅

## Notes

1. **Invoice GST Storage**: Currently invoices store `tax_amount` (total GST). CGST/SGST split is approximated. Consider adding cgst/sgst/igst columns to invoices table for precise tracking.

2. **Purchase GST Storage**: ✅ Already stores cgst, sgst, igst separately - correct approach.

3. **Consistency**: All reports now use the same calculation logic from database values, ensuring consistency across dashboard, reports, and billing.

4. **Decimal Precision**: All calculations use Decimal with 2 decimal places, rounded only for final output.
