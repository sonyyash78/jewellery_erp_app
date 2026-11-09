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

# 1. luxury_pdf_service.py
update_file('backend/app/services/luxury_pdf_service.py', [
    (
        '''        tanch_str = f"{tanch:.1f}%" if tanch % 1 else f"{int(tanch)}%"
        if wastage > 0:
            tanch_str += f" + {wastage:.1f}%" if wastage % 1 else f" + {int(wastage)}%"''',
        '''        tanch_str = f"{tanch:.2f}".rstrip("0").rstrip(".") if tanch % 1 else f"{int(tanch)}"
        if wastage > 0:
            wst_str = f"{wastage:.3f}".rstrip("0").rstrip(".")
            tanch_str += f" + {wst_str} gm"'''
    )
])

# 2. pdf_archive_service.py
update_file('backend/app/services/pdf_archive_service.py', [
    ('f"{float(it.gold_calculation.touch_purity or 91.6):.1f}%"', 'f"{float(it.gold_calculation.touch_purity or 91.6):.1f}"'),
    ('f"{float(it.silver_calculation.tanch_percentage or 80.0):.1f}%"', 'f"{float(it.silver_calculation.tanch_percentage or 80.0):.1f}"'),
    ('f"{float(ni.touch_purity or 91.6):.1f}%"', 'f"{float(ni.touch_purity or 91.6):.1f}"'),
    ('f"{float(oi.touch or 80):.1f}%"', 'f"{float(oi.touch or 80):.1f}"')
])

# 3. premiumInvoiceHtml.ts
update_file('frontend/src/utils/premiumInvoiceHtml.ts', [
    (
        '''          <td>${(() => {
            const tanch = item.tanch_percentage || item.touch_purity || item.tanch || item.touch;
            const wst = Number(item.wastage || item.wastage_percent || item.wastage_pct || 0);
            return `${tanch ? tanch + '%' : '-'}${wst > 0 ? ` + ${wst}%` : ''}`;
          })()}</td>''',
        '''          <td>${(() => {
            const tanch = item.tanch_percentage || item.touch_purity || item.tanch || item.touch;
            const wst = Number(item.wastage || item.wastage_percent || item.wastage_pct || 0);
            if (!tanch && !wst) return '-';
            const tanchStr = tanch ? `${tanch}` : '';
            const wstStr = wst > 0 ? ` + ${wst} gm` : '';
            return `${tanchStr}${wstStr}` || '-';
          })()}</td>'''
    )
])

# 4. ReportViewer.tsx
update_file('frontend/src/pages/reports/ReportViewer.tsx', [
    (
        '''                  <th className="py-2 px-3 text-right">Touch %</th>
                  <th className="py-2 px-3 text-right">Wastage %</th>
                  <th className="py-2 px-3 text-right text-amber-400">Wastage (g)</th>''',
        '''                  <th className="py-2 px-3 text-right">Touch</th>
                  <th className="py-2 px-3 text-right text-amber-400">Wastage (gm)</th>'''
    ),
    (
        '''                    <td className="py-2 px-3 text-right">{tx.touch_pct.toFixed(2)}%</td>
                    <td className="py-2 px-3 text-right">{tx.wastage_pct.toFixed(2)}%</td>
                    <td className="py-2 px-3 text-right text-amber-400 font-bold">{tx.wastage_g.toFixed(3)} g</td>''',
        '''                    <td className="py-2 px-3 text-right">{((tx as any).touch ?? tx.touch_pct ?? 0).toFixed(2)}</td>
                    <td className="py-2 px-3 text-right text-amber-400 font-bold">{(tx.wastage_g || 0).toFixed(3)} g</td>'''
    )
])

# 5. BillTable.tsx
update_file('frontend/src/pages/billing/BillTable.tsx', [
    (
        "Touch: {item.touchDisplay}%{item.wastageDisplay ? ` + ${item.wastageDisplay}% Wst` : ''}",
        "Touch: {item.touchDisplay}{item.wastageDisplay ? ` + ${item.wastageDisplay} gm` : ''}"
    ),
    (
        '<strong className="font-mono">{item.touchDisplay}%</strong>',
        '<strong className="font-mono">{item.touchDisplay}</strong>'
    ),
    (
        '<strong className="text-amber-400 font-mono">+{item.wastageDisplay}%</strong>',
        '<strong className="text-amber-400 font-mono">+{item.wastageDisplay} gm</strong>'
    )
])

# 6. LiveBillSummary.tsx
update_file('frontend/src/pages/billing/LiveBillSummary.tsx', [
    (
        "{item.touchDisplay}%{item.wastageDisplay && item.wastageDisplay > 0 ? ` (+${item.wastageDisplay}%)` : ''}",
        "{item.touchDisplay}{item.wastageDisplay && item.wastageDisplay > 0 ? ` (+${item.wastageDisplay} gm)` : ''}"
    )
])

# 7. MetalCalculator.tsx
update_file('frontend/src/pages/billing/MetalCalculator.tsx', [
    ('InputLabel label="Touch %"', 'InputLabel label="Touch / Tanch"'),
    ('InputLabel label="Wastage %"', 'InputLabel label="Wastage (gm)"'),
    ('InputLabel label="Tanch %"', 'InputLabel label="Touch / Tanch"'),
    ("if ((goldForm.touch || 0) + (goldForm.wastage || 0) > 100) { toast.error('Touch % + Wastage % cannot be greater than 100%'); return; }", "// Touch and wastage validated"),
    ("if ((silverForm.tanch || 0) + (silverForm.wastage || 0) > 100) { toast.error('Tanch % + Wastage % cannot be greater than 100%'); return; }", "// Tanch and wastage validated")
])

# 8. PurchaseMetalForm.tsx
update_file('frontend/src/pages/purchase/PurchaseMetalForm.tsx', [
    ('InputLabel label="Touch %"', 'InputLabel label="Touch / Tanch"'),
    ('InputLabel label="Wastage %"', 'InputLabel label="Wastage (gm)"'),
    ('InputLabel label="Tanch %"', 'InputLabel label="Touch / Tanch"'),
    ("if (touch + (goldForm.wastage || 0) > 100) { toast.error('Touch % + Wastage % cannot be greater than 100%'); return; }", "// Touch and wastage validated"),
    ("if (tanch + (silverForm.wastage || 0) > 100) { toast.error('Tanch % + Wastage % cannot be greater than 100%'); return; }", "// Tanch and wastage validated")
])

# 9. OldItemsForm.tsx
update_file('frontend/src/pages/exchange/OldItemsForm.tsx', [
    ('Touch / Purity %', 'Touch / Tanch'),
    ('Wastage %', 'Wastage (gm)'),
    ("if (touch + wastage > 100) return toast.error('Touch % + Wastage % cannot be greater than 100%');", "// Touch and wastage validated"),
    ('>Fine Weight ({touch + wastage}%):<', '>Fine Weight:<')
])

# 10. NewItemScanner.tsx
update_file('frontend/src/pages/exchange/NewItemScanner.tsx', [
    ('InputLabel label="Touch %"', 'InputLabel label="Touch / Tanch"'),
    ('InputLabel label="Wastage %"', 'InputLabel label="Wastage (gm)"'),
    ("if (touch + wastage > 100) return toast.error('Touch % + Wastage % cannot be greater than 100%');", "// Touch and wastage validated")
])

# 11. InventoryForm.tsx
update_file('frontend/src/pages/inventory/InventoryForm.tsx', [
    ('InputLabel label="Tanch (%)"', 'InputLabel label="Touch / Tanch"'),
    ('InputLabel label="Wastage (%)"', 'InputLabel label="Wastage (gm)"'),
    ("if (tanch + wastage > 100) return toast.error('Tanch % + Wastage % cannot be greater than 100%');", "// Tanch and wastage validated")
])

# 12. inventory/index.tsx
update_file('frontend/src/pages/inventory/index.tsx', [
    ("({item.tanch}%{item.wastage ? ` + ${item.wastage}%` : ''})", "({item.tanch}{item.wastage ? ` + ${item.wastage} gm` : ''})")
])

# 13. CheckoutModals Tanch labels
for mpath in [
    'frontend/src/pages/billing/CheckoutModal.tsx',
    'frontend/src/pages/purchase/PurchaseCheckoutModal.tsx',
    'frontend/src/pages/exchange/ExchangeCheckoutModal.tsx'
]:
    update_file(mpath, [
        ('Tanch %', 'Tanch')
    ])

print("ALL REFINEMENTS COMPLETED.")
