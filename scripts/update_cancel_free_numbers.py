import re

# 1. invoices.py
with open(r'C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\api\v1\invoices.py', 'r', encoding='utf-8') as f:
    inv = f.read()

inv_pattern = r'invoice\.status\s*=\s*InvoiceStatus\.CANCELLED[\s\S]*?SequenceService\.rollback_document_number\(db,\s*target_company_id,\s*invoice\.invoice_number,\s*[\'"]INVOICE[\'"]\)\s+db\.commit\(\)'

inv_replacement = '''orig_invoice_number = invoice.invoice_number
        invoice.status = InvoiceStatus.CANCELLED
        invoice.invoice_number = f"{orig_invoice_number}-CAN-{invoice.id}"
        from app.services.sequence_service import SequenceService
        target_company_id = getattr(invoice, 'company_id', None) or 1
        SequenceService.rollback_document_number(db, target_company_id, orig_invoice_number, 'INVOICE')
        db.commit()'''

inv, count1 = re.subn(inv_pattern, inv_replacement, inv, count=1)
if count1 > 0:
    with open(r'C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\api\v1\invoices.py', 'w', encoding='utf-8') as f:
        f.write(inv)
    print("Updated invoices.py to free cancelled invoice number")
else:
    print("Could not match invoices.py pattern!")

# 2. purchases.py
with open(r'C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\api\v1\purchases.py', 'r', encoding='utf-8') as f:
    pur = f.read()

pur_pattern = r'purchase\.status\s*=\s*PurchaseStatus\.CANCELLED[\s\S]*?SequenceService\.rollback_document_number\(db,\s*target_company_id,\s*purchase\.purchase_number,\s*[\'"]PURCHASE[\'"]\)\s+db\.commit\(\)'

pur_replacement = '''orig_purchase_number = purchase.purchase_number
        purchase.status = PurchaseStatus.CANCELLED
        purchase.purchase_number = f"{orig_purchase_number}-CAN-{purchase.id}"
        from app.services.sequence_service import SequenceService
        target_company_id = getattr(purchase, 'company_id', None) or 1
        SequenceService.rollback_document_number(db, target_company_id, orig_purchase_number, 'PURCHASE')
        db.commit()'''

pur, count2 = re.subn(pur_pattern, pur_replacement, pur, count=1)
if count2 > 0:
    with open(r'C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\api\v1\purchases.py', 'w', encoding='utf-8') as f:
        f.write(pur)
    print("Updated purchases.py to free cancelled purchase number")
else:
    print("Could not match purchases.py pattern!")

# 3. exchanges.py
with open(r'C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\api\v1\exchanges.py', 'r', encoding='utf-8') as f:
    exc = f.read()

exc_pattern = r'exchange\.status\s*=\s*[\'"]Cancelled[\'"][\s\S]*?SequenceService\.rollback_document_number\(db,\s*target_company_id,\s*exc_num,\s*[\'"]EXCHANGE[\'"]\)\s+db\.commit\(\)'

exc_replacement = '''orig_exchange_number = getattr(exchange, 'exchange_number', None) or f"EXC-{exchange.id}"
        exchange.status = "Cancelled"
        if hasattr(exchange, 'exchange_number') and exchange.exchange_number:
            exchange.exchange_number = f"{orig_exchange_number}-CAN-{exchange.id}"
        from app.services.sequence_service import SequenceService
        target_company_id = getattr(exchange, 'company_id', None) or 1
        SequenceService.rollback_document_number(db, target_company_id, orig_exchange_number, 'EXCHANGE')
        db.commit()'''

exc, count3 = re.subn(exc_pattern, exc_replacement, exc, count=1)
if count3 > 0:
    with open(r'C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\api\v1\exchanges.py', 'w', encoding='utf-8') as f:
        f.write(exc)
    print("Updated exchanges.py to free cancelled exchange number")
else:
    print("Could not match exchanges.py pattern!")
