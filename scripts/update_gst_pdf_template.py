import re

def update_gst_template():
    path = r"C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\utils\gstInvoiceHtml.ts"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Normalize line endings
    content_norm = content.replace("\r\n", "\n")

    # Replace buyer box
    buyer_pattern = re.compile(
        r'<div class="buyer-box">.*?<div class="company-title"[^>]*>\$\{buyer\.name\}</div>.*?<div>\$\{buyer\.address\}</div>.*?'
        r'<table style="width: 100%; margin-top: 3px;">.*?'
        r'(\$\{buyer\.pan \? `<tr><td style="width: 90px;">Party Pan No\.</td><td>: <b>\$\{buyer\.pan\}</b></td></tr>` : \'\'\}\n)?.*?'
        r'<tr><td style="width: 90px;">GSTIN/UIN</td><td>: <b>\$\{buyer\.gstin \|\| \'Unregistered\'\}</b></td></tr>',
        re.DOTALL
    )

    new_buyer_section = """<div class="buyer-box">
          <div style="font-size: 7.5pt; color: #555;">Buyer (Bill to)</div>
          <div class="company-title" style="font-size: 8.5pt;">${buyer.name}</div>
          <div>${buyer.address}${buyer.pan && !buyer.address?.includes('Party Pan') ? `, Party Pan No. ${buyer.pan}` : ''}</div>
          ${(buyer.address?.includes('India') || buyer.address?.includes('306912, India')) ? '' : `<div>${buyer.state || 'Rajasthan'} - 306912, India</div>`}
          <table style="width: 100%; margin-top: 3px;">
            <tr><td style="width: 90px;">GSTIN/UIN</td><td>: <b>${buyer.gstin || 'Unregistered'}</b></td></tr>"""

    if buyer_pattern.search(content_norm):
        content_norm = buyer_pattern.sub(new_buyer_section, content_norm, count=1)
        print("Successfully updated buyer box in gstInvoiceHtml.ts")
    else:
        print("Buyer pattern did not match directly, trying string replacement")

    # Seller box state/country line
    seller_needle = '<div class="seller-box">\n          <div class="company-title">${seller.name}</div>\n          <div>${seller.address}</div>\n          <table style="width: 100%; margin-top: 3px;">'
    seller_replace = '<div class="seller-box">\n          <div class="company-title">${seller.name}</div>\n          <div>${seller.address}</div>\n          ${(seller.address?.includes(\'India\') || seller.address?.includes(\'342001, India\')) ? \'\' : `<div>${seller.state || \'Rajasthan\'} - 342001, India</div>`}\n          <table style="width: 100%; margin-top: 3px;">'

    if seller_needle in content_norm:
        content_norm = content_norm.replace(seller_needle, seller_replace)
        print("Successfully updated seller box in gstInvoiceHtml.ts")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content_norm.replace("\n", "\r\n"))

def update_invoice_pdf_utils():
    path = r"C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\utils\invoicePdfUtils.ts"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Ensure isSaideepBuyer handles Yash, empty, or saideep
    old_buyer_block = """        buyer: {
          name: data.customer?.name || 'Saideep Jewellers',
          address: data.customer?.address || (data.customer?.name?.toLowerCase().includes('saideep') || !data.customer?.name ? '167, Ward No. 3, Khedawas, Thakhatgarh,Pali (Raj.)-306912' : 'Takhatgarh, Pali (Raj.)'),
          pan: data.customer?.pan || (data.customer?.name?.toLowerCase().includes('saideep') || !data.customer?.name ? 'BNUPK1610E' : ''),
          gstin: data.customer?.gstin || (data.customer?.name?.toLowerCase().includes('saideep') || !data.customer?.name ? '08BNUPK1610E1Z3' : ''),
          state: data.customer?.state || 'Rajasthan',
          state_code: buyerStateCode,
          place_of_supply: data.customer?.state || 'Rajasthan',
          contact_person: data.customer?.contact_person || (data.customer?.name?.toLowerCase().includes('saideep') || !data.customer?.name ? 'Rajesh Kumar' : ''),
          phone: data.customer?.phone || (data.customer?.name?.toLowerCase().includes('saideep') || !data.customer?.name ? '+91-9460820878' : ''),
          email: data.customer?.email || (data.customer?.name?.toLowerCase().includes('saideep') || !data.customer?.name ? 'saideepjewellers78@gmail.com' : '')
        },"""

    new_buyer_block = """        buyer: (() => {
          const cName = (data.customer?.name || '').trim();
          const isSaideep = !cName || cName.toLowerCase().includes('saideep') || cName.toLowerCase().includes('yash') || data.customer?.gstin === '08BNUPK1610E1Z3';
          return {
            name: isSaideep ? 'Saideep Jewellers' : cName,
            address: isSaideep ? '167, Ward No. 3, Khedawas, Thakhatgarh, Pali (Raj.)-306912' : (data.customer?.address || 'Takhatgarh, Pali (Raj.)'),
            pan: isSaideep ? 'BNUPK1610E' : (data.customer?.pan || ''),
            gstin: isSaideep ? '08BNUPK1610E1Z3' : (data.customer?.gstin || ''),
            state: data.customer?.state || 'Rajasthan',
            state_code: buyerStateCode,
            place_of_supply: data.customer?.state || 'Rajasthan',
            contact_person: isSaideep ? 'Rajesh Kumar' : (data.customer?.contact_person || ''),
            phone: isSaideep ? '+91-9460820878' : (data.customer?.phone || ''),
            email: isSaideep ? 'saideepjewellers78@gmail.com' : (data.customer?.email || '')
          };
        })(),"""

    if old_buyer_block in content:
        content = content.replace(old_buyer_block, new_buyer_block)
        print("Successfully updated buyer block in invoicePdfUtils.ts")
    else:
        # Check normalized
        c_norm = content.replace("\r\n", "\n")
        o_norm = old_buyer_block.replace("\r\n", "\n")
        n_norm = new_buyer_block.replace("\r\n", "\n")
        if o_norm in c_norm:
            content = c_norm.replace(o_norm, n_norm).replace("\n", "\r\n")
            print("Successfully updated buyer block in invoicePdfUtils.ts (normalized)")
        else:
            print("Notice: old_buyer_block in invoicePdfUtils.ts not found directly")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def update_backend_invoices():
    path = r"C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\api\v1\invoices.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    old_snippet = """            cust = db.query(Customer).filter(Customer.id == invoice_in.customer_id).first() if invoice_in.customer_id else None
            buyer_data = {
                "name": f"{cust.first_name} {cust.last_name or ''}".strip() if cust else "Saideep Jewellers",
                "address": cust.address if (cust and cust.address) else "167, Ward No. 3, Khedawas, Thakhatgarh,Pali (Raj.)-306912",
                "pan": cust.aadhaar_pan if (cust and cust.aadhaar_pan) else "BNUPK1610E",
                "gstin": cust.gst_number if (cust and cust.gst_number) else "08BNUPK1610E1Z3",
                "state": getattr(cust, 'state', None) or "Rajasthan",
                "state_code": getattr(cust, 'state_code', None) or "08",
                "place_of_supply": getattr(cust, 'place_of_supply', None) or "Rajasthan",
                "contact_person": "Rajesh Kumar",
                "phone": cust.phone_number if cust else "+91-9460820878",
                "email": cust.email if (cust and cust.email) else "saideepjewellers78@gmail.com"
            }"""

    new_snippet = """            cust = db.query(Customer).filter(Customer.id == invoice_in.customer_id).first() if invoice_in.customer_id else None
            c_name = f"{cust.first_name} {cust.last_name or ''}".strip() if cust else ""
            is_saideep = (not cust) or ('saideep' in c_name.lower()) or ('yash' in c_name.lower()) or (getattr(cust, 'id', None) == 1) or (getattr(cust, 'gst_number', '') == '08BNUPK1610E1Z3')
            buyer_data = {
                "name": "Saideep Jewellers" if is_saideep else c_name,
                "address": "167, Ward No. 3, Khedawas, Thakhatgarh, Pali (Raj.)-306912" if is_saideep else (cust.address or ""),
                "pan": "BNUPK1610E" if is_saideep else (cust.aadhaar_pan or ""),
                "gstin": "08BNUPK1610E1Z3" if is_saideep else (cust.gst_number or ""),
                "state": getattr(cust, 'state', None) or "Rajasthan",
                "state_code": getattr(cust, 'state_code', None) or "08",
                "place_of_supply": getattr(cust, 'place_of_supply', None) or "Rajasthan",
                "contact_person": "Rajesh Kumar" if is_saideep else (getattr(cust, 'contact_person', None) or ""),
                "phone": "+91-9460820878" if is_saideep else (cust.phone_number or ""),
                "email": "saideepjewellers78@gmail.com" if is_saideep else (cust.email or "")
            }"""

    c_norm = content.replace("\r\n", "\n")
    o_norm = old_snippet.replace("\r\n", "\n")
    n_norm = new_snippet.replace("\r\n", "\n")
    if o_norm in c_norm:
        content = c_norm.replace(o_norm, n_norm).replace("\n", "\r\n")
        print("Successfully updated buyer_data in invoices.py")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    else:
        print("Notice: old_snippet in invoices.py not found directly")

if __name__ == "__main__":
    update_gst_template()
    update_invoice_pdf_utils()
    update_backend_invoices()
