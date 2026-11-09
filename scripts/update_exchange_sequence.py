p = r'C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\api\v1\exchanges.py'
with open(p, 'r', encoding='utf-8') as f:
    text = f.read()

old_block = '''    # Create Exchange
    exchange = Exchange(
        store_id=store_id,
        company_id=target_company_id,

        customer_id=exchange_in.customer_id,'''

new_block = '''    # Create Exchange
    from app.services.sequence_service import SequenceService
    exc_num = SequenceService.generate_document_number(db, company_id=target_company_id, doc_type="EXCHANGE")
    exchange = Exchange(
        store_id=store_id,
        company_id=target_company_id,
        exchange_number=exc_num,

        customer_id=exchange_in.customer_id,'''

if old_block in text:
    text = text.replace(old_block, new_block, 1)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(text)
    print("Successfully updated exchanges.py!")
else:
    print("Could not find old_block in exchanges.py")
