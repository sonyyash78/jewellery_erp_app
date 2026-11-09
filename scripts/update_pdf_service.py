import os
import re

p = r"c:\Users\YASH SONI\Desktop\jeweller-app\backend\app\services\invoice_pdf_service.py"
with open(p, "r", encoding="utf-8") as f:
    c = f.read()

is_crlf = "\r\n" in c
c = c.replace("\r\n", "\n")

target = """        # Company details
        company = InvoicePDFService._get_company_details(db, getattr(invoice, 'store_id', 1) or 1)"""

replacement = """        # Company details resolution based on invoice.company_id
        company_id = getattr(invoice, 'company_id', None) or 1
        if company_id == 2:
            from app.models.company import Company
            co = db.query(Company).filter(Company.id == 2).first()
            if co:
                company = {
                    'name': co.name or "PRIDE GOLD",
                    'address': co.address or "1st Floor, Near Koira Ji ka Bera, Ghodo ka Chowk, Sojati Gate, Jodhpur (Raj.)- 342001",
                    'city': co.city or "Jodhpur",
                    'state': co.state or "Rajasthan",
                    'state_code': co.state_code or "08",
                    'gstin': co.gstin or "08AEZPK5007N1ZS",
                    'pan': co.pan or "AEZPK5007N",
                    'phone': co.phone or "0291-2640999,+91-9929562800",
                    'email': co.email or "info.pridegoldjdr@gmail.com",
                    'gst_enabled': True,
                    'jurisdiction_city': co.jurisdiction_city or "JODHPUR",
                    'declaration': co.declaration or "We declare that this invoice shows the actual price of the goods described and that all particulars are true and correct.",
                    'logo_url': co.logo_url or "",
                    'stamp_url': co.stamp_url or "",
                    'signature_url': co.signature_url or ""
                }
            else:
                company = InvoicePDFService._get_company_details(db, getattr(invoice, 'store_id', 1) or 1)
                company['gst_enabled'] = True
        else:
            company = InvoicePDFService._get_company_details(db, getattr(invoice, 'store_id', 1) or 1)
            company['gst_enabled'] = False

        if getattr(invoice, 'seller_snapshot_json', None):
            import json
            try:
                snap_s = json.loads(invoice.seller_snapshot_json)
                if snap_s and isinstance(snap_s, dict):
                    company.update(snap_s)
                    company['gst_enabled'] = True
            except Exception:
                pass"""

assert target in c, "target company details not found"
c = c.replace(target, replacement, 1)

target_cust = """        # Customer details
        customer_data = {
            'name': f"{invoice.customer.first_name} {invoice.customer.last_name or ''}".strip() if invoice.customer else 'Walk-in Customer',
            'phone': invoice.customer.phone_number if invoice.customer else '',
            'email': invoice.customer.email if invoice.customer else '',
            'address': ', '.join(customer_address_parts),
            'gstin': invoice.customer.gst_number if invoice.customer else '',
            'pan': invoice.customer.aadhaar_pan if invoice.customer else ''
        }"""

repl_cust = """        # Customer details
        customer_name = f"{invoice.customer.first_name} {invoice.customer.last_name or ''}".strip() if invoice.customer else ('Saideep Jewellers' if company_id == 2 else 'Walk-in Customer')
        is_saideep_buyer = 'saideep' in customer_name.lower() or (company_id == 2 and not invoice.customer)

        customer_data = {
            'name': 'Saideep Jewellers' if is_saideep_buyer else customer_name,
            'phone': invoice.customer.phone_number if (invoice.customer and invoice.customer.phone_number) else ('+91-9460820878' if is_saideep_buyer else ''),
            'email': invoice.customer.email if (invoice.customer and invoice.customer.email) else ('saideepjewellers78@gmail.com' if is_saideep_buyer else ''),
            'address': ', '.join(customer_address_parts) if customer_address_parts else ('167, Ward No. 3, Khedawas, Thakhatgarh,Pali (Raj.)-306912' if is_saideep_buyer else ''),
            'gstin': invoice.customer.gst_number if (invoice.customer and invoice.customer.gst_number) else ('08BNUPK1610E1Z3' if is_saideep_buyer else ''),
            'pan': invoice.customer.aadhaar_pan if (invoice.customer and invoice.customer.aadhaar_pan) else ('BNUPK1610E' if is_saideep_buyer else ''),
            'state': getattr(invoice.customer, 'state', None) or 'Rajasthan',
            'state_code': getattr(invoice.customer, 'state_code', None) or '08',
            'place_of_supply': getattr(invoice.customer, 'place_of_supply', None) or 'Rajasthan',
            'contact_person': 'Rajesh Kumar' if is_saideep_buyer else ''
        }

        if getattr(invoice, 'buyer_snapshot_json', None):
            import json
            try:
                snap_b = json.loads(invoice.buyer_snapshot_json)
                if snap_b and isinstance(snap_b, dict):
                    customer_data.update(snap_b)
            except Exception:
                pass"""

assert target_cust in c, "target_cust not found"
c = c.replace(target_cust, repl_cust, 1)

final_c = c.replace("\n", "\r\n") if is_crlf else c
with open(p, "w", encoding="utf-8") as f:
    f.write(final_c)

print("Updated backend/app/services/invoice_pdf_service.py successfully")
