import sys
sys.path.append(r"C:\Users\YASH SONI\Desktop\jeweller-app\backend")

from app.db.database import SessionLocal
from app.models.customer import Customer
from app.models.customer_ledger import CustomerLedger
from app.services.pdf_archive_service import _get_store_header, _sanitize_name
from app.services.luxury_pdf_service import generate_luxury_statement_html

db = SessionLocal()
c = db.query(Customer).filter(Customer.id == 2).first()
store_info = _get_store_header(db, 1)

all_ledgers = db.query(CustomerLedger).filter(CustomerLedger.customer_id == c.id).order_by(CustomerLedger.date.asc()).all()

print(f"Customer: {c.first_name}, Outstanding: {c.outstanding_balance}, Fine Gold: {c.fine_gold_balance}")
print(f"Total ledgers: {len(all_ledgers)}")

for l in all_ledgers:
    print(f"  Voucher: {l.voucher_number}, Type: {l.voucher_type}, Debit: {l.debit}, Credit: {l.credit}, Balance: {l.balance}, Gold: {l.gold_balance}")

# Test statement HTML for Without_GST
entries = []
running_cash = 0.0
running_gold = 0.0
running_silver = 0.0
for l in all_ledgers:
    deb = float(l.debit or 0.0)
    crd = float(l.credit or 0.0)
    running_cash += (deb - crd)
    g_deb = float(getattr(l, "gold_debit", 0.0) or 0.0)
    g_crd = float(getattr(l, "gold_credit", 0.0) or 0.0)
    running_gold += (g_deb - g_crd)
    s_deb = float(getattr(l, "silver_debit", 0.0) or 0.0)
    s_crd = float(getattr(l, "silver_credit", 0.0) or 0.0)
    running_silver += (s_deb - s_crd)
    entries.append({
        "date": (l.date.strftime("%d-%b-%Y") if getattr(l, "date", None) else ""),
        "type": l.voucher_type or "Ledger",
        "number": l.voucher_number or "-",
        "description": l.description or "-",
        "debit": deb,
        "credit": crd,
        "balance": running_cash,
        "gold_debit": g_deb,
        "gold_credit": g_crd,
    })

print(f"\nStatement summary:")
print(f"  Total Entries: {len(entries)}")
print(f"  Final Running Cash: Rs. {running_cash:,.2f}")
print(f"  Final Running Gold: {running_gold:.3f}g")

db.close()
