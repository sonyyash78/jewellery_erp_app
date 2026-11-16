import re

invoices_path = r'c:\Users\YASH SONI\Desktop\jeweller-app\backend\app\api\v1\invoices.py'
with open(invoices_path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update customer validation / lookup block (around line 424)
old_block1_pattern = r'# 1\. Validate customer exists if provided\s+if invoice_in\.customer_id is not None:[\s\S]*?detail=f"Customer with id \{invoice_in\.customer_id\} not found"\s+\)'

new_block1 = '''    # 1. Validate customer exists if provided, or lookup by phone / auto-create
    customer = None
    if invoice_in.customer_id is not None:
        customer = db.query(Customer).filter(Customer.id == invoice_in.customer_id, Customer.store_id == store_id).first()

    b_phone = getattr(invoice_in, 'buyer_phone', None)
    b_name = getattr(invoice_in, 'buyer_name', None)
    b_addr = getattr(invoice_in, 'buyer_address', None)
    b_city = getattr(invoice_in, 'buyer_city', None)
    b_state = getattr(invoice_in, 'buyer_state', None)
    b_gstin = getattr(invoice_in, 'buyer_gstin', None)
    b_pan = getattr(invoice_in, 'buyer_pan', None)

    clean_b_phone = re.sub(r'[^0-9]', '', str(b_phone or ''))
    if len(clean_b_phone) == 12 and clean_b_phone.startswith('91'):
        clean_b_phone = clean_b_phone[2:]

    if not customer and len(clean_b_phone) == 10:
        customer = db.query(Customer).filter(Customer.phone_number == clean_b_phone, Customer.store_id == store_id).first()

    if not customer and b_name and b_name.strip() and b_name.strip() != 'Walk-in Customer':
        if len(clean_b_phone) == 10:
            name_parts = b_name.strip().split(' ', 1)
            fname = name_parts[0]
            lname = name_parts[1] if len(name_parts) > 1 else ''
            try:
                customer = Customer(
                    store_id=store_id,
                    first_name=fname,
                    last_name=lname,
                    phone_number=clean_b_phone,
                    address=b_addr or '',
                    city=b_city or 'Takhatgarh',
                    state=b_state or 'Rajasthan',
                    gst_number=b_gstin or None,
                    aadhaar_pan=b_pan or None,
                    is_active=True
                )
                db.add(customer)
                db.flush()
            except Exception as e:
                print(f"[Auto-create customer error] {e}")

    if invoice_in.customer_id is not None and not customer:
        raise HTTPException(
            status_code=404,
            detail=f"Customer with id {invoice_in.customer_id} not found"
        )'''

code, count1 = re.subn(old_block1_pattern, new_block1, code)
print(f"Customer validation block replaced: {count1}")

# 2. Update line 838 where customer_id is assigned on Invoice
old_assign = "customer_id=invoice_in.customer_id,"
new_assign = "customer_id=customer.id if customer else invoice_in.customer_id,"
if old_assign in code:
    code = code.replace(old_assign, new_assign, 1)
    print("customer_id assignment on db_invoice updated")

# 3. Update snapshots & customer update (around line 2630)
old_block3_pattern = r'# If Company 2 \(Saideep Jewellers GST\), freeze seller & buyer snapshots\s+if target_company_id == 2:[\s\S]*?db_invoice\.buyer_snapshot_json = json\.dumps\(buyer_data\)'

new_block3 = '''        # Freeze seller & buyer snapshots (available for both Company 1 and Company 2)
        from app.models.company import Company
        target_co = db.query(Company).filter(Company.id == target_company_id).first()
        if not target_co:
            target_co = db.query(Company).filter(Company.id == (2 if target_company_id == 2 else 1)).first()
        
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

        # Lookup customer to update attributes
        cust_id = db_invoice.customer_id or invoice_in.customer_id
        cust = db.query(Customer).filter(Customer.id == cust_id).first() if cust_id else customer
        if not cust and clean_b_phone and len(clean_b_phone) == 10:
            cust = db.query(Customer).filter(Customer.phone_number == clean_b_phone, Customer.store_id == store_id).first()

        c_name = f"{cust.first_name} {cust.last_name or ''}".strip() if cust else ""
        b_name_final = (getattr(invoice_in, 'buyer_name', None) or c_name or "Walk-in Customer").strip()
        b_phone_final = clean_b_phone or (cust.phone_number if cust else "")
        b_addr_final = getattr(invoice_in, 'buyer_address', None) or (cust.address if cust else "")
        b_city_final = getattr(invoice_in, 'buyer_city', None) or (cust.city if cust else "Takhatgarh")
        b_state_final = getattr(invoice_in, 'buyer_state', None) or (getattr(cust, 'state', None) or "Rajasthan")
        b_code_final = getattr(invoice_in, 'buyer_state_code', None) or (getattr(cust, 'state_code', None) or "08")
        b_pos_final = getattr(invoice_in, 'buyer_place_of_supply', None) or (getattr(cust, 'place_of_supply', None) or b_state_final)
        b_gstin_final = getattr(invoice_in, 'buyer_gstin', None) or (getattr(cust, 'gst_number', None) or "")
        b_pan_final = getattr(invoice_in, 'buyer_pan', None) or (getattr(cust, 'aadhaar_pan', None) or "")
        b_email_final = getattr(invoice_in, 'buyer_email', None) or (cust.email if cust else "")

        # Always update Customer table with the latest info entered on the bill!
        if cust:
            if b_name_final and b_name_final != "Walk-in Customer":
                name_pts = b_name_final.split(" ", 1)
                cust.first_name = name_pts[0]
                if len(name_pts) > 1:
                    cust.last_name = name_pts[1]
            if len(clean_b_phone) == 10:
                cust.phone_number = clean_b_phone
            if b_addr_final:
                cust.address = b_addr_final
            if b_city_final:
                cust.city = b_city_final
            if b_state_final:
                cust.state = b_state_final
            if b_gstin_final:
                cust.gst_number = b_gstin_final
            if b_pan_final:
                cust.aadhaar_pan = b_pan_final
            db_invoice.customer_id = cust.id

        buyer_data = {
            "name": b_name_final,
            "address": b_addr_final,
            "city": b_city_final,
            "state": b_state_final,
            "state_code": b_code_final,
            "place_of_supply": b_pos_final,
            "contact_person": b_name_final,
            "phone": b_phone_final,
            "email": b_email_final,
            "gstin": b_gstin_final,
            "pan": b_pan_final
        }
        db_invoice.buyer_snapshot_json = json.dumps(buyer_data)'''

code, count3 = re.subn(old_block3_pattern, new_block3, code)
print(f"Snapshots block replaced: {count3}")

with open(invoices_path, 'w', encoding='utf-8') as f:
    f.write(code)
print("Finished patching invoices.py")
