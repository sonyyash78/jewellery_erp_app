p = r'C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\api\v1\purchases.py'
with open(p, 'r', encoding='utf-8') as f:
    text = f.read()

target = 'purchase_number=f"PUR-{int(datetime.now().timestamp() * 1000) % 1000000}",'
replacement = '''from app.services.sequence_service import SequenceService
    pur_num = SequenceService.generate_document_number(db, company_id=target_company_id, doc_type="PURCHASE")
    purchase_number=pur_num,'''

# Let's place the generation before `db_purchase = Purchase(`
old_block = '''    # Create purchase record first
    db_purchase = Purchase(
        store_id=store_id,
        company_id=target_company_id,

        purchase_number=f"PUR-{int(datetime.now().timestamp() * 1000) % 1000000}",'''

new_block = '''    # Create purchase record first
    from app.services.sequence_service import SequenceService
    pur_num = SequenceService.generate_document_number(db, company_id=target_company_id, doc_type="PURCHASE")
    db_purchase = Purchase(
        store_id=store_id,
        company_id=target_company_id,

        purchase_number=pur_num,'''

if old_block in text:
    text = text.replace(old_block, new_block, 1)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(text)
    print("Successfully updated purchases.py!")
else:
    print("Could not find old_block in purchases.py")
