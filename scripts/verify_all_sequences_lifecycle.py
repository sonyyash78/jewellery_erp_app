import sys
sys.path.append(r'C:\Users\YASH SONI\Desktop\jeweller-app\backend')

from app.db.database import SessionLocal
from app.models.company import Company, CompanyNumberSequence
from app.models.invoice import Invoice
from app.models.purchase import Purchase
from app.models.exchange import Exchange
from app.services.sequence_service import SequenceService

db = SessionLocal()

print("--- 1. VERIFY COMPANIES ---")
c1 = db.query(Company).filter(Company.id == 1).first()
c2 = db.query(Company).filter(Company.id == 2).first()
print(f"Company 1: ID={c1.id}, Name='{c1.name}', GST={c1.gst_enabled}")
print(f"Company 2: ID={c2.id}, Name='{c2.name}', GST={c2.gst_enabled}, GSTIN='{c2.gstin}'")
assert "SAIDEEP" in c1.name, "Company 1 name must be SAIDEEP JEWELLERS"
assert "SAIDEEP" in c2.name, "Company 2 name must be SAIDEEP JEWELLERS"
assert c2.gst_enabled is True or c2.gst_enabled == 1, "Company 2 must have GST enabled"

print("\n--- 2. VERIFY INVOICE SEQUENCE (01 Start & Rollback) ---")
# Reset company 2 invoice sequence to 0
seq_inv = db.query(CompanyNumberSequence).filter(
    CompanyNumberSequence.company_id == 2,
    CompanyNumberSequence.doc_type == "INVOICE"
).first()
if seq_inv:
    seq_inv.last_sequence = 0
    db.commit()

num1 = SequenceService.generate_document_number(db, company_id=2, doc_type="INVOICE")
print(f"Generated Invoice 1: {num1}")
assert num1 == "SJ/S/01/26-27", f"Expected SJ/S/01/26-27, got {num1}"

num2 = SequenceService.generate_document_number(db, company_id=2, doc_type="INVOICE")
print(f"Generated Invoice 2: {num2}")
assert num2 == "SJ/S/02/26-27", f"Expected SJ/S/02/26-27, got {num2}"

# Rollback Invoice 2
rb2 = SequenceService.rollback_document_number(db, company_id=2, doc_number=num2, doc_type="INVOICE")
db.commit()
print(f"Rollback {num2}: {rb2}")
num2_again = SequenceService.generate_document_number(db, company_id=2, doc_type="INVOICE")
print(f"Regenerated Invoice 2: {num2_again}")
assert num2_again == "SJ/S/02/26-27", f"Expected SJ/S/02/26-27 after rollback, got {num2_again}"

# Rollback both
SequenceService.rollback_document_number(db, company_id=2, doc_number=num2_again, doc_type="INVOICE")
SequenceService.rollback_document_number(db, company_id=2, doc_number=num1, doc_type="INVOICE")
db.commit()

print("\n--- 3. VERIFY PURCHASE SEQUENCE (01 Start & Rollback) ---")
seq_pur = db.query(CompanyNumberSequence).filter(
    CompanyNumberSequence.company_id == 2,
    CompanyNumberSequence.doc_type == "PURCHASE"
).first()
if seq_pur:
    seq_pur.last_sequence = 0
    db.commit()

p_num1 = SequenceService.generate_document_number(db, company_id=2, doc_type="PURCHASE")
print(f"Generated Purchase 1: {p_num1}")
assert p_num1 == "SJ/P/01/26-27", f"Expected SJ/P/01/26-27, got {p_num1}"

SequenceService.rollback_document_number(db, company_id=2, doc_number=p_num1, doc_type="PURCHASE")
db.commit()
p_num1_again = SequenceService.generate_document_number(db, company_id=2, doc_type="PURCHASE")
print(f"Regenerated Purchase 1 after rollback: {p_num1_again}")
assert p_num1_again == "SJ/P/01/26-27", f"Expected SJ/P/01/26-27 after rollback, got {p_num1_again}"

SequenceService.rollback_document_number(db, company_id=2, doc_number=p_num1_again, doc_type="PURCHASE")
db.commit()

print("\n--- 4. VERIFY EXCHANGE SEQUENCE (01 Start & Rollback) ---")
seq_exc = db.query(CompanyNumberSequence).filter(
    CompanyNumberSequence.company_id == 2,
    CompanyNumberSequence.doc_type == "EXCHANGE"
).first()
if seq_exc:
    seq_exc.last_sequence = 0
    db.commit()

e_num1 = SequenceService.generate_document_number(db, company_id=2, doc_type="EXCHANGE")
print(f"Generated Exchange 1: {e_num1}")
assert e_num1 == "SJ/E/01/26-27", f"Expected SJ/E/01/26-27, got {e_num1}"

SequenceService.rollback_document_number(db, company_id=2, doc_number=e_num1, doc_type="EXCHANGE")
db.commit()
e_num1_again = SequenceService.generate_document_number(db, company_id=2, doc_type="EXCHANGE")
print(f"Regenerated Exchange 1 after rollback: {e_num1_again}")
assert e_num1_again == "SJ/E/01/26-27", f"Expected SJ/E/01/26-27 after rollback, got {e_num1_again}"

SequenceService.rollback_document_number(db, company_id=2, doc_number=e_num1_again, doc_type="EXCHANGE")
db.commit()

print("\n=== ALL SEQUENCE LIFECYCLE TESTS PASSED! ===")
