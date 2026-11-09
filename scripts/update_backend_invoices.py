import os
import re

p_inv = r"c:\Users\YASH SONI\Desktop\jeweller-app\backend\app\api\v1\invoices.py"
with open(p_inv, "r", encoding="utf-8") as f:
    c = f.read()

is_crlf = "\r\n" in c
c = c.replace("\r\n", "\n")

# Ensure Header is imported
if "from fastapi import APIRouter, Depends, HTTPException, Query" in c and "Header" not in c:
    c = c.replace(
        "from fastapi import APIRouter, Depends, HTTPException, Query",
        "from fastapi import APIRouter, Depends, HTTPException, Query, Header"
    )

# 1. Update create_invoice signature to include x_company_id
pattern_create = r'@router\.post\("/",\s*response_model=InvoiceResponse\)\s*def create_invoice\(\s*invoice_in:\s*InvoiceCreate,\s*db:\s*Session\s*=\s*Depends\(get_db\),\s*current_user:\s*User\s*=\s*Depends\(get_current_user\)\s*\):'

repl_create = """@router.post("/", response_model=InvoiceResponse)
def create_invoice(
    invoice_in: InvoiceCreate,
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):"""

c, count1 = re.subn(pattern_create, repl_create, c, count=1)
print("Replaced create_invoice signature:", count1)

# 2. Add target_company_id resolution
pattern_store = r'store_id\s*=\s*require_tenant_id\(current_user\)\s*# 1\. Validate customer exists if provided'

repl_store = """store_id = require_tenant_id(current_user)

    # Resolve target company ID from payload, header, or default to 1
    target_company_id = getattr(invoice_in, 'company_id', None)
    if not target_company_id and x_company_id and x_company_id.isdigit():
        target_company_id = int(x_company_id)
    if not target_company_id:
        target_company_id = 1

    # 1. Validate customer exists if provided"""

c, count2 = re.subn(pattern_store, repl_store, c, count=1)
print("Replaced target_company_id resolution:", count2)

# 3. Update Invoice creation with SequenceService and company_id
pattern_db_inv = r'# 3\. Create Invoice\s*db_invoice\s*=\s*Invoice\(\s*store_id=store_id,\s*customer_id=invoice_in\.customer_id,\s*invoice_number=generate_invoice_number\(db,\s*store_id\),'

repl_db_inv = """# 3. Create Invoice using SequenceService for company-specific numbering
        from app.services.sequence_service import SequenceService
        inv_number = SequenceService.generate_document_number(db, company_id=target_company_id, doc_type="INVOICE")

        db_invoice = Invoice(
            store_id=store_id,
            company_id=target_company_id,
            customer_id=invoice_in.customer_id,
            invoice_number=inv_number,"""

c, count3 = re.subn(pattern_db_inv, repl_db_inv, c, count=1)
print("Replaced db_invoice creation:", count3)

# 4. Add snapshots before db.commit()
pattern_commit = r'db\.commit\(\)\s*db\.refresh\(db_invoice\)'

repl_commit = """# If Company 2 (Pride Gold GST), freeze seller & buyer snapshots
        if target_company_id == 2:
            import json
            from app.models.company import Company
            co2 = db.query(Company).filter(Company.id == 2).first()
            seller_data = {
                "name": co2.name if (co2 and co2.name) else "PRIDE GOLD",
                "address": co2.address if (co2 and co2.address) else "1st Floor, Near Koira Ji ka Bera, Ghodo ka Chowk, Sojati Gate, Jodhpur (Raj.)- 342001",
                "city": co2.city if (co2 and co2.city) else "Jodhpur",
                "state": co2.state if (co2 and co2.state) else "Rajasthan",
                "state_code": co2.state_code if (co2 and co2.state_code) else "08",
                "gstin": co2.gstin if (co2 and co2.gstin) else "08AEZPK5007N1ZS",
                "pan": co2.pan if (co2 and co2.pan) else "AEZPK5007N",
                "phone": co2.phone if (co2 and co2.phone) else "0291-2640999,+91-9929562800",
                "email": co2.email if (co2 and co2.email) else "info.pridegoldjdr@gmail.com",
                "jurisdiction_city": co2.jurisdiction_city if (co2 and co2.jurisdiction_city) else "JODHPUR"
            }
            db_invoice.seller_snapshot_json = json.dumps(seller_data)

            cust = db.query(Customer).filter(Customer.id == invoice_in.customer_id).first() if invoice_in.customer_id else None
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
            }
            db_invoice.buyer_snapshot_json = json.dumps(buyer_data)

        db.commit()
        db.refresh(db_invoice)"""

c, count4 = re.subn(pattern_commit, repl_commit, c, count=1)
print("Replaced db.commit with snapshots:", count4)

# 5. Update list_invoices signature
pattern_list = r'@router\.get\("/",\s*response_model=List\[InvoiceResponse\]\)\s*def list_invoices\(\s*skip:\s*int\s*=\s*Query\(0,\s*ge=0\),\s*limit:\s*int\s*=\s*Query\(50,\s*ge=1,\s*le=100\),\s*search:\s*Optional\[str\]\s*=\s*Query\(None\),\s*status:\s*Optional\[str\]\s*=\s*Query\(None\),\s*start_date:\s*Optional\[date\]\s*=\s*Query\(None\),\s*end_date:\s*Optional\[date\]\s*=\s*Query\(None\),\s*customer_id:\s*Optional\[int\]\s*=\s*Query\(None\),\s*db:\s*Session\s*=\s*Depends\(get_db\),\s*current_user:\s*User\s*=\s*Depends\(get_current_user\)\s*\):'

repl_list = """@router.get("/", response_model=List[InvoiceResponse])
def list_invoices(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    customer_id: Optional[int] = Query(None),
    company_id: Optional[int] = Query(None),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):"""

c, count5 = re.subn(pattern_list, repl_list, c, count=1)
print("Replaced list_invoices signature:", count5)

# 6. Update list_invoices query
pattern_list_q = r'store_id\s*=\s*require_tenant_id\(current_user\)\s*query\s*=\s*db\.query\(Invoice\)\.filter\(Invoice\.store_id\s*==\s*store_id\)'

repl_list_q = """store_id = require_tenant_id(current_user)

    # Resolve target operating company for strict data isolation
    active_company = company_id
    if not active_company and x_company_id and x_company_id.isdigit():
        active_company = int(x_company_id)
    if not active_company:
        active_company = 1

    query = db.query(Invoice).filter(Invoice.store_id == store_id)

    # Strict Company Isolation: Company 1 gets (1 or None), Company 2 gets (2)
    if active_company == 1:
        query = query.filter((Invoice.company_id == 1) | (Invoice.company_id.is_(None)))
    else:
        query = query.filter(Invoice.company_id == active_company)"""

c, count6 = re.subn(pattern_list_q, repl_list_q, c, count=1)
print("Replaced list_invoices query filter:", count6)

final_c = c.replace("\n", "\r\n") if is_crlf else c
with open(p_inv, "w", encoding="utf-8") as f:
    f.write(final_c)
print("Done writing invoices.py")
