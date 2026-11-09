import re
from pathlib import Path

BASE = Path(r'C:\Users\YASH SONI\Desktop\jeweller-app')

def update_file(rel_path, replacements):
    fpath = BASE / rel_path
    if not fpath.exists():
        print(f"Skipping {rel_path} (does not exist)")
        return
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    orig = content
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
        else:
            print(f"Warning: target not found in {rel_path}:\n{old[:80]}...")
    if content != orig:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Successfully updated {rel_path}")
    else:
        print(f"No changes made to {rel_path}")

# 1. MetalCalculator.tsx
update_file('frontend/src/pages/billing/MetalCalculator.tsx', [
    (
        "// Touch and wastage validated\n    const item: BillItem = {",
        "if (((goldForm.touch || 0) + (goldForm.wastage || 0)) >= 100 && (goldForm.wastage || 0) > 0) { toast.error('Touch + Wastage must be less than 100 (Touch + Wastage < 100)'); return; }\n    if (((goldForm.touch || 0) + (goldForm.wastage || 0)) > 100) { toast.error('Touch + Wastage must be <= 100'); return; }\n    const item: BillItem = {"
    ),
    (
        "// Tanch and wastage validated\n    const item: BillItem = {",
        "if (((silverForm.tanch || 0) + (silverForm.wastage || 0)) >= 100 && (silverForm.wastage || 0) > 0) { toast.error('Touch + Wastage must be less than 100 (Touch + Wastage < 100)'); return; }\n    if (((silverForm.tanch || 0) + (silverForm.wastage || 0)) > 100) { toast.error('Touch + Wastage must be <= 100'); return; }\n    const item: BillItem = {"
    )
])

# 2. PurchaseMetalForm.tsx
update_file('frontend/src/pages/purchase/PurchaseMetalForm.tsx', [
    (
        "// Touch and wastage validated\n    const item: PurchaseItem = {",
        "if ((touch + (goldForm.wastage || 0)) >= 100 && (goldForm.wastage || 0) > 0) { toast.error('Touch + Wastage must be less than 100 (Touch + Wastage < 100)'); return; }\n    if ((touch + (goldForm.wastage || 0)) > 100) { toast.error('Touch + Wastage must be <= 100'); return; }\n    const item: PurchaseItem = {"
    ),
    (
        "// Tanch and wastage validated\n    const item: PurchaseItem = {",
        "if ((tanch + (silverForm.wastage || 0)) >= 100 && (silverForm.wastage || 0) > 0) { toast.error('Touch + Wastage must be less than 100 (Touch + Wastage < 100)'); return; }\n    if ((tanch + (silverForm.wastage || 0)) > 100) { toast.error('Touch + Wastage must be <= 100'); return; }\n    const item: PurchaseItem = {"
    )
])

# 3. OldItemsForm.tsx
update_file('frontend/src/pages/exchange/OldItemsForm.tsx', [
    (
        "// Validated touch and wastage\n    const finalItemName",
        "if (!isDiamond && ((touch || 0) + (wastage || 0) >= 100) && (wastage || 0) > 0) { toast.error('Touch + Wastage must be less than 100 (Touch + Wastage < 100)'); return; }\n    if (!isDiamond && ((touch || 0) + (wastage || 0) > 100)) { toast.error('Touch + Wastage must be <= 100'); return; }\n    const finalItemName"
    )
])

# 4. NewItemScanner.tsx
update_file('frontend/src/pages/exchange/NewItemScanner.tsx', [
    (
        "// Validated touch and wastage\n    const finalItemName",
        "if (((touch || 0) + (wastage || 0) >= 100) && (wastage || 0) > 0) { toast.error('Touch + Wastage must be less than 100 (Touch + Wastage < 100)'); return; }\n    if (((touch || 0) + (wastage || 0) > 100)) { toast.error('Touch + Wastage must be <= 100'); return; }\n    const finalItemName"
    )
])

# 5. InventoryForm.tsx
update_file('frontend/src/pages/inventory/InventoryForm.tsx', [
    (
        "// Validated tanch and wastage\n      setLoading(true);",
        "const tanchVal = Number(form.tanch) || 0;\n      const wstVal = Number(form.wastage) || 0;\n      if (wstVal > 0 && (tanchVal + wstVal >= 100)) { toast.error('Touch + Wastage must be less than 100 (Touch + Wastage < 100)'); return; }\n      if (tanchVal + wstVal > 100) { toast.error('Touch + Wastage must be <= 100'); return; }\n      setLoading(true);"
    )
])

# 6. calculation_service.py
calc_path = BASE / 'backend/app/services/calculation_service.py'
with open(calc_path, 'r', encoding='utf-8') as f:
    calc_code = f.read()

target = "fine_weight = net_weight * (touch_purity + wastage) / Decimal('100')"
replacement = """if wastage > Decimal('0') and (touch_purity + wastage) >= Decimal('100'):
            raise HTTPException(400, "Touch + Wastage must be less than 100 (Touch + Wastage < 100)")
        if (touch_purity + wastage) > Decimal('100'):
            raise HTTPException(400, "Touch + Wastage cannot exceed 100")
        fine_weight = net_weight * (touch_purity + wastage) / Decimal('100')"""

if target in calc_code:
    calc_code = calc_code.replace(target, replacement, 1)
    with open(calc_path, 'w', encoding='utf-8') as f:
        f.write(calc_code)
    print("Successfully updated calculation_service.py with Touch + Wastage < 100 validation")
else:
    print("Warning: target not found in calculation_service.py")

print("Validation Touch + Wastage < 100 successfully applied!")
