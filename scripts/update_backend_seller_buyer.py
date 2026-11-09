import os
import re

repo_root = r"C:\Users\YASH SONI\Desktop\jeweller-app"

# 1. Update backend/app/schemas/invoice.py
schema_path = os.path.join(repo_root, "backend", "app", "schemas", "invoice.py")
with open(schema_path, "r", encoding="utf-8") as f:
    schema_code = f.read()

buyer_fields = """    # Editable Buyer details on invoice
    buyer_name: Optional[str] = None
    buyer_phone: Optional[str] = None
    buyer_address: Optional[str] = None
    buyer_city: Optional[str] = None
    buyer_state: Optional[str] = None
    buyer_state_code: Optional[str] = None
    buyer_place_of_supply: Optional[str] = None
    buyer_gstin: Optional[str] = None
    buyer_pan: Optional[str] = None
    buyer_email: Optional[str] = None
"""

if "buyer_address: Optional[str]" not in schema_code:
    target_pos = "silver_balance_metal_weight: float = 0.0\n"
    if target_pos in schema_code:
        schema_code = schema_code.replace(target_pos, target_pos + buyer_fields)
        print("Added buyer fields to InvoiceCreate in schemas/invoice.py")
        with open(schema_path, "w", encoding="utf-8") as f:
            f.write(schema_code)
    else:
        print("Target position in schemas/invoice.py not found!")

# 2. Update backend/app/api/v1/invoices.py
inv_api_path = os.path.join(repo_root, "backend", "app", "api", "v1", "invoices.py")
with open(inv_api_path, "r", encoding="utf-8") as f:
    inv_api_code = f.read()

# Replace seller & buyer snapshot block
old_snap_block_pattern = r"if target_company_id == 2:.*?db_invoice\.buyer_snapshot_json = json\.dumps\(buyer_data\)"

new_snap_block = """if target_company_id == 2:
            from app.models.company import Company
            target_co = db.query(Company).filter(Company.id == target_company_id).first()
            if not target_co:
                target_co = db.query(Company).filter(Company.id == 2).first()
            
            seller_data = {
                "name": target_co.name if (target_co and target_co.name) else "SAIDEEP JEWELLERS",
                "address": target_co.address if (target_co and target_co.address) else "167, Ward No. 3, Khedawas, Takhatgarh, Pali (Raj.)-306912",
                "city": target_co.city if (target_co and target_co.city) else "Takhatgarh",
                "state": target_co.state if (target_co and target_co.state) else "Rajasthan",
                "state_code": target_co.state_code if (target_co and target_co.state_code) else "08",
                "gstin": target_co.gstin if (target_co and target_co.gstin) else "08BNUPK1610E1Z3",
                "pan": target_co.pan if (target_co and target_co.pan) else "BNUPK1610E",
                "phone": target_co.phone if (target_co and target_co.phone) else "+91-9460820878",
                "email": target_co.email if (target_co and target_co.email) else "saideepjewellers78@gmail.com",
                "jurisdiction_city": target_co.jurisdiction_city if (target_co and target_co.jurisdiction_city) else "PALI",
                "declaration": target_co.declaration if (target_co and target_co.declaration) else "We declare that this invoice shows the actual price of the goods described and that all particulars are true and correct."
            }
            db_invoice.seller_snapshot_json = json.dumps(seller_data)

            cust = db.query(Customer).filter(Customer.id == invoice_in.customer_id).first() if invoice_in.customer_id else None
            c_name = f"{cust.first_name} {cust.last_name or ''}".strip() if cust else ""

            # Use incoming buyer details from payload if provided (editable from checkout modal!)
            b_name = (getattr(invoice_in, 'buyer_name', None) or c_name or "Walk-in Customer").strip()
            b_phone = getattr(invoice_in, 'buyer_phone', None) or (cust.phone_number if cust else "")
            b_addr = getattr(invoice_in, 'buyer_address', None) or (cust.address if cust else "")
            b_city = getattr(invoice_in, 'buyer_city', None) or (cust.city if cust else "Takhatgarh")
            b_state = getattr(invoice_in, 'buyer_state', None) or (getattr(cust, 'state', None) or "Rajasthan")
            b_code = getattr(invoice_in, 'buyer_state_code', None) or (getattr(cust, 'state_code', None) or "08")
            b_pos = getattr(invoice_in, 'buyer_place_of_supply', None) or (getattr(cust, 'place_of_supply', None) or b_state)
            b_gstin = getattr(invoice_in, 'buyer_gstin', None) or (getattr(cust, 'gst_number', None) or "")
            b_pan = getattr(invoice_in, 'buyer_pan', None) or (getattr(cust, 'aadhaar_pan', None) or "")
            b_email = getattr(invoice_in, 'buyer_email', None) or (cust.email if cust else "")

            # If customer is in database and address/gstin/pan were edited in checkout, update customer record too
            if cust:
                if b_addr and b_addr != cust.address:
                    cust.address = b_addr
                if b_gstin and b_gstin != cust.gst_number:
                    cust.gst_number = b_gstin
                if b_pan and b_pan != cust.aadhaar_pan:
                    cust.aadhaar_pan = b_pan

            buyer_data = {
                "name": b_name,
                "address": b_addr,
                "city": b_city,
                "state": b_state,
                "state_code": b_code,
                "place_of_supply": b_pos,
                "contact_person": b_name,
                "phone": b_phone,
                "email": b_email,
                "gstin": b_gstin,
                "pan": b_pan
            }
            db_invoice.buyer_snapshot_json = json.dumps(buyer_data)"""

match = re.search(old_snap_block_pattern, inv_api_code, re.DOTALL)
if match:
    inv_api_code = inv_api_code[:match.start()] + new_snap_block + inv_api_code[match.end():]
    print("Replaced seller and buyer snapshot logic in backend invoices.py")
    with open(inv_api_path, "w", encoding="utf-8") as f:
        f.write(inv_api_code)
else:
    print("Old snapshot block not found in invoices.py!")

# 3. Update backend/app/services/invoice_pdf_service.py
pdf_svc_path = os.path.join(repo_root, "backend", "app", "services", "invoice_pdf_service.py")
with open(pdf_svc_path, "r", encoding="utf-8") as f:
    pdf_svc_code = f.read()

# Replace hardcoded PRIDE GOLD in company resolution
old_company_res = """        company_id = getattr(invoice, 'company_id', None) or 1
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
            company['gst_enabled'] = False"""

new_company_res = """        company_id = getattr(invoice, 'company_id', None) or 1
        from app.models.company import Company
        co = db.query(Company).filter(Company.id == company_id).first()
        if not co:
            co = db.query(Company).filter(Company.id == 2).first() if company_id == 2 else db.query(Company).filter(Company.id == 1).first()

        if co:
            company = {
                'name': co.name or "SAIDEEP JEWELLERS",
                'address': co.address or "167, Ward No. 3, Khedawas, Takhatgarh, Pali (Raj.)-306912",
                'city': co.city or "Takhatgarh",
                'state': co.state or "Rajasthan",
                'state_code': co.state_code or "08",
                'gstin': co.gstin or ("08BNUPK1610E1Z3" if co.gst_enabled else ""),
                'pan': co.pan or ("BNUPK1610E" if co.gst_enabled else ""),
                'phone': co.phone or "+91-9460820878",
                'email': co.email or "saideepjewellers78@gmail.com",
                'gst_enabled': bool(co.gst_enabled),
                'jurisdiction_city': co.jurisdiction_city or "PALI",
                'declaration': co.declaration or "We declare that this invoice shows the actual price of the goods described and that all particulars are true and correct.",
                'logo_url': co.logo_url or "",
                'stamp_url': co.stamp_url or "",
                'signature_url': co.signature_url or ""
            }
        else:
            company = InvoicePDFService._get_company_details(db, getattr(invoice, 'store_id', 1) or 1)
            company['gst_enabled'] = (company_id == 2)"""

if old_company_res in pdf_svc_code:
    pdf_svc_code = pdf_svc_code.replace(old_company_res, new_company_res)
    print("Updated company resolution in invoice_pdf_service.py")

# Replace is_saideep_buyer block
old_buyer_res = """        # Customer details
        customer_name = f"{invoice.customer.first_name} {invoice.customer.last_name or ''}".strip() if invoice.customer else ('Saideep Jewellers' if company_id == 2 else 'Walk-in Customer')
        is_saideep_buyer = (company_id == 2) and (
            not invoice.customer or
            'saideep' in customer_name.lower() or
            'yash' in customer_name.lower() or
            getattr(invoice.customer, 'gst_number', '') == '08BNUPK1610E1Z3' or
            getattr(invoice.customer, 'id', None) == 1
        )

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
        }"""

new_buyer_res = """        # Customer details
        customer_name = f"{invoice.customer.first_name} {invoice.customer.last_name or ''}".strip() if invoice.customer else 'Walk-in Customer'

        customer_data = {
            'name': customer_name,
            'phone': invoice.customer.phone_number if (invoice.customer and invoice.customer.phone_number) else '',
            'email': invoice.customer.email if (invoice.customer and invoice.customer.email) else '',
            'address': ', '.join(customer_address_parts) if customer_address_parts else (getattr(invoice.customer, 'address', '') if invoice.customer else ''),
            'gstin': getattr(invoice.customer, 'gst_number', '') if invoice.customer else '',
            'pan': getattr(invoice.customer, 'aadhaar_pan', '') if invoice.customer else '',
            'state': getattr(invoice.customer, 'state', None) or 'Rajasthan',
            'state_code': getattr(invoice.customer, 'state_code', None) or '08',
            'place_of_supply': getattr(invoice.customer, 'place_of_supply', None) or 'Rajasthan',
            'contact_person': customer_name
        }"""

if old_buyer_res in pdf_svc_code:
    pdf_svc_code = pdf_svc_code.replace(old_buyer_res, new_buyer_res)
    print("Removed is_saideep_buyer override in invoice_pdf_service.py")

with open(pdf_svc_path, "w", encoding="utf-8") as f:
    f.write(pdf_svc_code)

# 4. Update backend/app/services/gst_pdf_template.py
tmpl_path = os.path.join(repo_root, "backend", "app", "services", "gst_pdf_template.py")
with open(tmpl_path, "r", encoding="utf-8") as f:
    tmpl_code = f.read()

tmpl_code = tmpl_code.replace('co_name = company.get("name", "PRIDE GOLD")', 'co_name = company.get("name", "SAIDEEP JEWELLERS")')
tmpl_code = tmpl_code.replace('co_email = company.get("email", "info.pridegoldjdr@gmail.com")', 'co_email = company.get("email", "saideepjewellers78@gmail.com")')
tmpl_code = tmpl_code.replace('● PRIDE GOLD ●', '● {co_name} ●')

with open(tmpl_path, "w", encoding="utf-8") as f:
    f.write(tmpl_code)
print("Updated fallback and stamp in gst_pdf_template.py")
