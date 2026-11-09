with open('frontend/src/utils/gstInvoiceHtml.ts', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace(
    '<div style="font-size: 4.5pt; margin-top: 1px;">JODHPUR</div>',
    '<div style="font-size: 4.5pt; margin-top: 1px;">${(seller.city || seller.jurisdiction_city || "RAJASTHAN").toUpperCase()}</div>'
)

with open('frontend/src/utils/gstInvoiceHtml.ts', 'w', encoding='utf-8') as f:
    f.write(text)
print("Updated stamp city!")
