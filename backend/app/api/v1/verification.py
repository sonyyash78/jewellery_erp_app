from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any, Dict
from app.db.database import get_db
from app.models.invoice import Invoice
from app.models.exchange import Exchange
from app.models.purchase import Purchase
from app.services.invoice_pdf_service import InvoicePDFService

router = APIRouter()

@router.get("/verify/{voucher_number}")
def verify_voucher(voucher_number: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Public verification endpoint to verify authenticity of Invoices, Exchanges, and Purchases.
    No login required.
    """
    clean_voucher = voucher_number.strip().upper()
    base_voucher = clean_voucher
    if base_voucher.startswith("PAY-"):
        base_voucher = base_voucher[4:]

    try:
        if base_voucher.startswith("INV-"):
            invoice = db.query(Invoice).filter(Invoice.invoice_number == base_voucher).first()
            if not invoice:
                # Also try partial match
                invoice = db.query(Invoice).filter(Invoice.invoice_number.ilike(f"%{base_voucher}%")).first()
            if not invoice:
                raise ValueError(f"Invoice {base_voucher} not found in official registry.")
            data = InvoicePDFService.get_invoice_pdf_data(invoice.id, db)

        elif base_voucher.startswith("EXC-"):
            exchange_id = int(base_voucher.split("-")[1])
            exchange = db.query(Exchange).filter(Exchange.id == exchange_id).first()
            if not exchange:
                raise ValueError(f"Exchange {base_voucher} not found in official registry.")
            data = InvoicePDFService.get_exchange_pdf_data(exchange.id, db)

        elif base_voucher.startswith("PUR-"):
            purchase = db.query(Purchase).filter(Purchase.purchase_number == base_voucher).first()
            if not purchase:
                raise ValueError(f"Purchase {base_voucher} not found in official registry.")
            data = InvoicePDFService.get_purchase_pdf_data(purchase.id, db)

        else:
            # Fallback search in Invoices, Exchanges, or Purchases
            invoice = db.query(Invoice).filter(Invoice.invoice_number.ilike(f"%{base_voucher}%")).first()
            if invoice:
                data = InvoicePDFService.get_invoice_pdf_data(invoice.id, db)
            else:
                raise ValueError(f"No official record found for voucher code: {clean_voucher}")

        return {
            "valid": True,
            "status": "VERIFIED_AUTHENTIC",
            "voucher_number": clean_voucher,
            "type": data.get("type"),
            "invoice": data.get("invoice"),
            "customer": data.get("customer"),
            "company": data.get("company"),
            "totals": data.get("totals"),
            "items": data.get("items", []),
            "old_items": data.get("old_items", []),
            "message": "Official Authentic Bill Verified by Saideep Jewellers System"
        }
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=str(e) or f"Verification record not found for voucher '{clean_voucher}'."
        )
