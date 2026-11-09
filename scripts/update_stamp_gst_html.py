paths = [
    r'C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\utils\gstInvoiceHtml.ts',
    r'C:\Users\YASH SONI\Desktop\Saideep\jewellery-erp\frontend\src\utils\gstInvoiceHtml.ts'
]

for p in paths:
    with open(p, 'r', encoding='utf-8') as f:
        c = f.read()

    target = """        <div style="height: 45px; display: flex; align-items: center; justify-content: flex-end;">
          ${seller.stamp_url ? `<img src="${seller.stamp_url}" alt="Stamp" style="max-height: 40px; margin-right: 10px;" />` : ''}
          ${seller.signature_url ? `<img src="${seller.signature_url}" alt="Sign" style="max-height: 40px;" />` : ''}
        </div>"""

    replacement = """        <div style="height: 52px; display: flex; align-items: center; justify-content: flex-end;">
          ${seller.stamp_url ? `<img src="${seller.stamp_url}" alt="Stamp" style="max-height: 45px; margin-right: 10px;" />` : `
          <div style="width: 52px; height: 52px; border-radius: 50%; border: 1.5px solid #2563eb; color: #2563eb; font-size: 5pt; font-weight: bold; display: flex; flex-direction: column; align-items: center; justify-content: center; margin-right: 15px; transform: rotate(-5deg); opacity: 0.85; line-height: 1.1; text-align: center;">
            <div>★ PRIDE GOLD ★</div>
            <div style="font-size: 4.5pt; margin-top: 1px;">JODHPUR</div>
          </div>
          `}
          ${seller.signature_url ? `<img src="${seller.signature_url}" alt="Sign" style="max-height: 40px;" />` : ''}
        </div>"""

    if target in c:
        c = c.replace(target, replacement)
        with open(p, 'w', encoding='utf-8') as f:
            f.write(c)

print('Updated stamp in gstInvoiceHtml.ts')
