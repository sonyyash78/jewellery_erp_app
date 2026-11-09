import sys
sys.path.insert(0, r'C:\Users\YASH SONI\Desktop\jeweller-app\backend')
from app.db.database import SessionLocal
from app.models.user import User
from app.schemas.invoice import InvoiceCreate, InvoiceItemCreate, GoldCalcCreate
from app.api.v1.invoices import create_invoice, delete_invoice

db = SessionLocal()
u = db.query(User).filter(User.username == 'admin').first()

item = InvoiceItemCreate(
    item_name='Gold Ring',
    item_type='Gold',
    final_price=10000.0,
    gold_calculation=GoldCalcCreate(
        applied_rate=7250.0,
        gross_weight=1.379,
        net_weight=1.379,
        stone_weight=0.0,
        touch_purity=91.6,
        wastage=0.0,
        fine_weight=1.263,
        making_charge_type='flat',
        making_charge_rate=0.0,
        making_charges_amount=0.0,
        hallmark_charges=0.0,
        other_charges=0.0,
        discount=0.0,
        total_gold_value=10000.0
    )
)

inv_in = InvoiceCreate(
    customer_id=2,
    subtotal=10000.0,
    tax_amount=300.0,
    discount_amount=0.0,
    grand_total=10300.0,
    items=[item],
    bill_type='Cash',
    settlement_type='Cash',
    metal_received_value=0.0,
    cash_received=10300.0,
    balance_amount=0.0,
    balance_metal_weight=0.0,
    company_id=2
)

# 1. Create first invoice
inv1 = create_invoice(invoice_in=inv_in, x_company_id='2', db=db, current_user=u)
print(f"Step 1: Created invoice {inv1.invoice_number} (ID {inv1.id})")
assert inv1.invoice_number == "SJ/S/01/26-27"

# 2. Delete / cancel it
del_res = delete_invoice(id=inv1.id, db=db, current_user=u)
print(f"Step 2: Deleted/cancelled invoice -> {del_res}")

# 3. Create next invoice -> should cleanly reuse SJ/S/01/26-27 with NO UNIQUE error!
inv2 = create_invoice(invoice_in=inv_in, x_company_id='2', db=db, current_user=u)
print(f"Step 3: Created next invoice {inv2.invoice_number} (ID {inv2.id})")
assert inv2.invoice_number == "SJ/S/01/26-27"

# 4. Clean up test invoice
delete_invoice(id=inv2.id, db=db, current_user=u)
print("SUCCESS: 01 numbering, gapless rollback, and UNIQUE reuse all work perfectly!")

# Reset sequence to 0 for production use
from app.models.company import CompanyNumberSequence
seq = db.query(CompanyNumberSequence).filter(CompanyNumberSequence.company_id == 2, CompanyNumberSequence.doc_type == "INVOICE").first()
if seq:
    seq.last_sequence = 0
    db.commit()

db.close()
