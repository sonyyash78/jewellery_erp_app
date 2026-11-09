p = r'C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\utils\invoicePdfUtils.ts'
with open(p, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    if "const customerFolder = data.customer?.name" in line:
        new_lines.append("        const isPurchase = (data as any).type === 'purchase' || String(data.invoice?.invoice_number || '').startsWith('PUR-') || String(data.invoice?.invoice_number || '').includes('/P/');\n")
        new_lines.append("        const isExchange = (data as any).type === 'exchange' || String(data.invoice?.invoice_number || '').startsWith('EXC-') || String(data.invoice?.invoice_number || '').includes('/E/');\n")
        new_lines.append("        const category = isPurchase ? 'Purchases' : isExchange ? 'Exchanges' : 'Sales';\n")
        new_lines.append("        const partyName = (data.customer?.name || (data as any).seller?.name || (data as any).supplier?.name || (isPurchase ? 'Supplier' : 'Walk-in Customer')).trim();\n")
        new_lines.append("        await electronAPI.saveVaultPdf({\n")
        new_lines.append("          category,\n")
        new_lines.append("          folderName: partyName,\n")
        new_lines.append("          fileName: `${data.invoice?.invoice_number || (isPurchase ? 'PURCHASE' : isExchange ? 'EXCHANGE' : 'INVOICE')}.pdf`,\n")
        new_lines.append("          base64Data: cleanBase64\n")
        new_lines.append("        });\n")
        skip = True
    elif skip:
        if "});" in line:
            skip = False
    else:
        new_lines.append(line)

with open(p, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Successfully replaced vault save block in invoicePdfUtils.ts!")
