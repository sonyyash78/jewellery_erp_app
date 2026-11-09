with open('frontend/src/utils/gstInvoiceHtml.ts', 'r', encoding='utf-8') as f:
    text = f.read()

old_stamp = """            <div>★ PRIDE GOLD ★</div>
            <div style="font-size: 4.5pt; margin-top: 1px;">JODHPUR</div>"""

new_stamp = """            <div>★ ${seller.name.toUpperCase()} ★</div>
            <div style="font-size: 4.5pt; margin-top: 1px;">${(seller.city || seller.jurisdiction_city || 'PALI').toUpperCase()}</div>"""

if old_stamp in text:
    text = text.replace(old_stamp, new_stamp, 1)
    print("Updated circular stamp to dynamic seller name and city!")
else:
    # Try with \u2605 or single lines
    text = text.replace("PRIDE GOLD", "${seller.name.toUpperCase()}")
    print("Fallback replace done")

with open('frontend/src/utils/gstInvoiceHtml.ts', 'w', encoding='utf-8') as f:
    f.write(text)
