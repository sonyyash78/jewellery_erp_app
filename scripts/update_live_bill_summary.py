import os
import re

p = r"c:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\pages\billing\LiveBillSummary.tsx"
with open(p, "r", encoding="utf-8") as f:
    c = f.read()

is_crlf = "\r\n" in c
c = c.replace("\r\n", "\n")

# Import useCompanyStore
if "import { useCompanyStore } from '../../store/companyStore';" not in c:
    c = c.replace(
        "import { useBillingStore } from '../../store/billingStore';",
        "import { useBillingStore } from '../../store/billingStore';\nimport { useCompanyStore } from '../../store/companyStore';"
    )

# Extract currentCompanyId
pattern_top = r'export default function LiveBillSummary\(\) \{\s*const \{\s*cart,'
repl_top = """export default function LiveBillSummary() {
  const { currentCompanyId, currentCompany } = useCompanyStore();
  const {
    cart,"""
c, count_top = re.subn(pattern_top, repl_top, c, count=1)
print("Replaced top:", count_top)

# Add company_id and diamond_calculation to payload
pattern_payload = r'const payload = \{\s*subtotal: baseTaxableAmount,\s*tax_amount: gstAmount,\s*discount_amount: globalDiscount,\s*grand_total: grandTotal,'
repl_payload = """const payload = {
      company_id: currentCompanyId || 1,
      subtotal: baseTaxableAmount,
      tax_amount: gstAmount,
      discount_amount: globalDiscount,
      grand_total: grandTotal,"""
c, count_pl = re.subn(pattern_payload, repl_payload, c, count=1)
print("Replaced payload:", count_pl)

# Add diamond_calculation in cart.map
pattern_cart_map = r'total_silver_value: item\.metalValue\s*\} : null\s*\}\)\)'
repl_cart_map = """total_silver_value: item.metalValue
        } : null,
        diamond_calculation: item.itemType === 'Diamond' ? {
          weight_gm: item.grossWeight || (item.rawDiamond as any)?.weightGm || 0,
          weight_carats: item.grossWeight || (item.rawDiamond as any)?.caratWeight || 0,
          pieces: (item.rawDiamond as any)?.pieces || 1,
          rate_per_gm: item.rateDisplay || (item.rawDiamond as any)?.ratePerGm || 0,
          rate_per_carat: item.rateDisplay || (item.rawDiamond as any)?.ratePerCarat || 0,
          diamond_type: (item.rawDiamond as any)?.diamondType || 'NATURAL',
          diamond_form: (item.rawDiamond as any)?.diamondForm || 'CUT_AND_POLISHED',
          shape: (item.rawDiamond as any)?.shape || 'Round',
          clarity: (item.rawDiamond as any)?.clarity || '',
          colour: (item.rawDiamond as any)?.colour || '',
          certificate_no: (item.rawDiamond as any)?.certificateNo || '',
          discount: (item.rawDiamond as any)?.discount || 0,
          making_charges: item.makingAmount || 0,
          other_charges: item.otherCharges || 0,
          total_diamond_value: item.taxableAmount
        } : null
      }))"""

c, count_cm = re.subn(pattern_cart_map, repl_cart_map, c, count=1)
print("Replaced cart map with diamond calculation:", count_cm)

final_c = c.replace("\n", "\r\n") if is_crlf else c
with open(p, "w", encoding="utf-8") as f:
    f.write(final_c)

print("Saved LiveBillSummary.tsx successfully")
