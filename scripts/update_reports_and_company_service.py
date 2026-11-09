import os
import re

def update_companies_api():
    p = r"C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\api\v1\companies.py"
    with open(p, "r", encoding="utf-8") as f:
        c = f.read()

    # Make permission check tolerant for any admin user
    old_perm = 'if not (getattr(current_user, "is_owner", False) or getattr(current_user, "role_name", "") == "Admin"):'
    new_perm = """    is_admin = (
        current_user.username == "admin"
        or getattr(current_user, "is_owner", False)
        or getattr(current_user, "is_admin", False)
        or (current_user.role and current_user.role.name.lower() in ["admin", "owner"])
        or getattr(current_user, "role_id", None) == 1
    )
    if not is_admin:"""
    if old_perm in c:
        c = c.replace(old_perm, new_perm)
        print("Updated companies.py permission check")

    # Sync company 1 changes to Setting table
    target_commit = """    db.commit()
    db.refresh(company)
    return company"""
    sync_code = """    # If company 1, sync core details to Setting table
    if company_id == 1:
        from app.models.setting import Setting
        key_map = {
            "name": ["business_name", "store_name"],
            "address": ["address"],
            "phone": ["phone"],
            "email": ["email"],
            "gstin": ["gstin"],
            "pan": ["pan"],
            "upi_id": ["upi_id"],
            "upi_name": ["upi_name"]
        }
        for f_name, s_keys in key_map.items():
            if f_name in update_data and update_data[f_name] is not None:
                for k in s_keys:
                    s_row = db.query(Setting).filter(Setting.key == k).first()
                    if s_row:
                        s_row.value = str(update_data[f_name])
                    else:
                        db.add(Setting(key=k, value=str(update_data[f_name])))

    db.commit()
    db.refresh(company)
    return company"""
    if "key_map" not in c:
        c = c.replace(target_commit, sync_code)
        print("Added settings synchronization to update_company")

    with open(p, "w", encoding="utf-8") as f:
        f.write(c)

def update_invoice_pdf_service():
    p = r"C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\services\invoice_pdf_service.py"
    with open(p, "r", encoding="utf-8") as f:
        c = f.read()

    # Ensure dynamic company resolution for all companies
    old_co_block = """        # Company details resolution based on invoice.company_id
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
                    'signature_url': co.signature_url or ""
                }
            else:
                company = InvoicePDFService._get_company_details(db, getattr(invoice, 'store_id', 1) or 1)
                company['gst_enabled'] = True
        else:
            company = InvoicePDFService._get_company_details(db, getattr(invoice, 'store_id', 1) or 1)
            company['gst_enabled'] = False"""

    new_co_block = """        # Company details resolution dynamically from Company master
        company_id = getattr(invoice, 'company_id', None) or 1
        from app.models.company import Company
        co = db.query(Company).filter(Company.id == company_id).first()
        if co:
            company = {
                'name': co.name,
                'address': co.address or '',
                'city': co.city or '',
                'state': co.state or 'Rajasthan',
                'state_code': co.state_code or '08',
                'gstin': co.gstin or '',
                'pan': co.pan or '',
                'phone': co.phone or '',
                'email': co.email or '',
                'gst_enabled': bool(co.gst_enabled),
                'jurisdiction_city': co.jurisdiction_city or ('JODHPUR' if company_id == 2 else 'TAKHATGARH'),
                'declaration': co.declaration or '',
                'signature_url': co.signature_url or '',
                'stamp_url': co.stamp_url or '',
                'logo_url': co.logo_url or ''
            }
        else:
            company = InvoicePDFService._get_company_details(db, getattr(invoice, 'store_id', 1) or 1)
            company['gst_enabled'] = (company_id == 2)"""

    if old_co_block in c:
        c = c.replace(old_co_block, new_co_block)
        print("Updated invoice_pdf_service company resolution")

    # Ensure Saideep Jewellers buyer name for Pride Gold bills
    old_buyer_block = """        customer_name = f"{invoice.customer.first_name} {invoice.customer.last_name or ''}".strip() if invoice.customer else ('Saideep Jewellers' if company_id == 2 else 'Walk-in Customer')
        is_saideep_buyer = 'saideep' in customer_name.lower() or (company_id == 2 and not invoice.customer)

        customer_data = {
            'name': 'Saideep Jewellers' if is_saideep_buyer else customer_name,"""

    new_buyer_block = """        customer_name = f"{invoice.customer.first_name} {invoice.customer.last_name or ''}".strip() if invoice.customer else ('Saideep Jewellers' if company_id == 2 else 'Walk-in Customer')
        is_saideep_buyer = (company_id == 2) and (
            not invoice.customer or
            'saideep' in customer_name.lower() or
            'yash' in customer_name.lower() or
            getattr(invoice.customer, 'gst_number', '') == '08BNUPK1610E1Z3' or
            getattr(invoice.customer, 'id', None) == 1
        )

        customer_data = {
            'name': 'Saideep Jewellers' if is_saideep_buyer else customer_name,"""

    if old_buyer_block in c:
        c = c.replace(old_buyer_block, new_buyer_block)
        print("Updated buyer resolution for Pride Gold invoices")

    with open(p, "w", encoding="utf-8") as f:
        f.write(c)

if __name__ == "__main__":
    update_companies_api()
    update_invoice_pdf_service()
