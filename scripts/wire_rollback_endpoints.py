import re

# 1. Update backend/app/api/v1/invoices.py
with open(r'C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\api\v1\invoices.py', 'r', encoding='utf-8') as f:
    inv_code = f.read()

if "SequenceService.rollback_document_number(db, target_company_id, invoice.invoice_number, \"INVOICE\")" not in inv_code:
    inv_target = "invoice.status = InvoiceStatus.CANCELLED\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n        db.commit()"
    inv_replacement = """invoice.status = InvoiceStatus.CANCELLED
        from app.services.sequence_service import SequenceService
        target_company_id = getattr(invoice, 'company_id', None) or 1
        SequenceService.rollback_document_number(db, target_company_id, invoice.invoice_number, "INVOICE")
        db.commit()"""
    if inv_target in inv_code:
        inv_code = inv_code.replace(inv_target, inv_replacement, 1)
        print("Updated delete_invoice in invoices.py (exact match)")
    else:
        # Regex match
        pattern = r"(invoice\.status\s*=\s*InvoiceStatus\.CANCELLED\s+)(db\.commit\(\))"
        inv_code = re.sub(
            pattern,
            r"\1from app.services.sequence_service import SequenceService\n        target_company_id = getattr(invoice, 'company_id', None) or 1\n        SequenceService.rollback_document_number(db, target_company_id, invoice.invoice_number, 'INVOICE')\n        \2",
            inv_code,
            count=1
        )
        print("Updated delete_invoice in invoices.py (regex)")

    # Also fix the exception handler in create_invoice to log the error
    err_target = "except Exception as e:\n\n\n\n\n\n\n\n        db.rollback()\n\n\n\n\n\n\n\n        raise HTTPException(status_code=500, detail=\"Internal server error\")"
    err_replacement = """except Exception as e:
        db.rollback()
        import logging, traceback
        logging.getLogger(__name__).error(f"Error in create_invoice: {e}", exc_info=True)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")"""
    if err_target in inv_code:
        inv_code = inv_code.replace(err_target, err_replacement, 1)
        print("Updated exception logging in create_invoice (exact match)")
    else:
        pattern_err = r"(except Exception as e:\s+db\.rollback\(\)\s+)(raise HTTPException\(status_code=500,\s*detail=[\"']Internal server error[\"']\))"
        inv_code = re.sub(
            pattern_err,
            r"\1import logging, traceback\n        logging.getLogger(__name__).error(f'Error in create_invoice: {e}', exc_info=True)\n        traceback.print_exc()\n        raise HTTPException(status_code=500, detail=f'Internal server error: {str(e)}')",
            inv_code,
            count=1
        )
        print("Updated exception logging in create_invoice (regex)")

    with open(r'C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\api\v1\invoices.py', 'w', encoding='utf-8') as f:
        f.write(inv_code)

# 2. Update backend/app/api/v1/purchases.py
with open(r'C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\api\v1\purchases.py', 'r', encoding='utf-8') as f:
    pur_code = f.read()

if "SequenceService.rollback_document_number(db, target_company_id, purchase.purchase_number, \"PURCHASE\")" not in pur_code:
    pur_pattern = r"(purchase\.status\s*=\s*PurchaseStatus\.CANCELLED\s+)(db\.commit\(\))"
    pur_code = re.sub(
        pur_pattern,
        r"\1from app.services.sequence_service import SequenceService\n        target_company_id = getattr(purchase, 'company_id', None) or 1\n        SequenceService.rollback_document_number(db, target_company_id, purchase.purchase_number, 'PURCHASE')\n        \2",
        pur_code,
        count=1
    )
    with open(r'C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\api\v1\purchases.py', 'w', encoding='utf-8') as f:
        f.write(pur_code)
    print("Updated delete_unified_purchase in purchases.py")

# 3. Update backend/app/api/v1/exchanges.py
with open(r'C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\api\v1\exchanges.py', 'r', encoding='utf-8') as f:
    exc_code = f.read()

if "SequenceService.rollback_document_number(db, target_company_id, exc_num, \"EXCHANGE\")" not in exc_code:
    exc_pattern = r"(exchange\.status\s*=\s*[\"']Cancelled[\"']\s+)(db\.commit\(\))"
    exc_code = re.sub(
        exc_pattern,
        r"\1from app.services.sequence_service import SequenceService\n        target_company_id = getattr(exchange, 'company_id', None) or 1\n        exc_num = getattr(exchange, 'exchange_number', None) or f'EXC-{exchange.id}'\n        SequenceService.rollback_document_number(db, target_company_id, exc_num, 'EXCHANGE')\n        \2",
        exc_code,
        count=1
    )
    with open(r'C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\api\v1\exchanges.py', 'w', encoding='utf-8') as f:
        f.write(exc_code)
    print("Updated delete_exchange in exchanges.py")
