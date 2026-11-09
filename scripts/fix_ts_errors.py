# 1. Fix InvoiceHistory.tsx
path1 = r'C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\pages\invoices\InvoiceHistory.tsx'
with open(path1, 'r', encoding='utf-8') as f:
    c1 = f.read()
c1 = c1.replace("tab === 'exchange'", "tab === 'exchanges'")
with open(path1, 'w', encoding='utf-8') as f:
    f.write(c1)
print('Fixed InvoiceHistory.tsx')

# 2. Fix invoicePdfUtils.ts
path2 = r'C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\utils\invoicePdfUtils.ts'
with open(path2, 'r', encoding='utf-8') as f:
    c2 = f.read()
c2 = c2.replace(
    'const resolvedCompanyId = Number(data.company_id || data.company?.id || (data.invoice as any)?.company_id || 1);',
    'const resolvedCompanyId = Number((data as any).company_id || data.company?.id || (data.invoice as any)?.company_id || 1);'
)
with open(path2, 'w', encoding='utf-8') as f:
    f.write(c2)
print('Fixed invoicePdfUtils.ts')
