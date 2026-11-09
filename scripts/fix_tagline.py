with open('backend/app/services/invoice_pdf_service.py', 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace("co.tagline", "getattr(co, 'tagline', '')")
with open('backend/app/services/invoice_pdf_service.py', 'w', encoding='utf-8') as f:
    f.write(c)
print('Replaced co.tagline successfully')
