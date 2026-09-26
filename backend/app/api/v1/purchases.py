from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from decimal import Decimal
from app.db.database import get_db
from app.repositories.transaction_repo import gold_purchase_repo, silver_purchase_repo
from app.schemas.purchases import GoldPurchaseCreate, GoldPurchaseResponse, SilverPurchaseCreate, SilverPurchaseResponse, UnifiedPurchaseCreate, PurchaseItemInput, SellerInfo
from app.services.calculation_service import CalculationService
from app.models.purchase import Purchase, PurchaseStatus
from app.models.purchase_item import PurchaseItem
from app.models.seller import Seller
from app.models.user import User
from app.models.gold_rate import GoldRate
from app.models.silver_rate import SilverRate
from datetime import datetime
from app.api.dependencies import require_tenant_id, get_current_user

router = APIRouter()

def get_or_create_seller(db: Session, seller_info: SellerInfo, store_id: int = 1):
    """Get existing seller by mobile or create a new one for specific store."""
    existing = db.query(Seller).filter(Seller.store_id == store_id, Seller.mobile == seller_info.mobile).first()
    if existing:
        return existing
    seller = Seller(
        store_id=store_id,
        name=seller_info.name,
        mobile=seller_info.mobile,
        address=seller_info.address,
        city=seller_info.address.split(',')[0] if seller_info.address else None,
        gst_number=seller_info.aadhaar_pan,
        outstanding_balance=0,
        is_active=True
    )
    db.add(seller)
    db.flush()
    return seller

@router.post("/", response_model=dict)
def create_unified_purchase(
    purchase_in: UnifiedPurchaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Create a unified purchase with seller info and items array. Backend recalculates all totals."""
    store_id = require_tenant_id(current_user)
    
    # Get or create seller
    if purchase_in.seller_id:
        seller = db.query(Seller).filter(Seller.id == purchase_in.seller_id, Seller.store_id == store_id).first()
        if not seller:
            raise HTTPException(status_code=404, detail="Seller not found")
    elif purchase_in.seller:
        seller = get_or_create_seller(db, purchase_in.seller, store_id=store_id)
    else:
        raise HTTPException(status_code=400, detail="Seller information is required")
    # Create purchase record first
    db_purchase = Purchase(
        store_id=store_id,
        purchase_number=f"PUR-{int(datetime.now().timestamp() * 1000) % 1000000}",
        seller_id=seller.id,
        created_by_id=current_user.id,
        total_taxable=purchase_in.total_taxable,
        cgst=purchase_in.cgst,
        sgst=purchase_in.sgst,
        igst=purchase_in.igst,
        grand_total=purchase_in.grand_total,
        status=PurchaseStatus[purchase_in.status] if purchase_in.status in ['COMPLETED', 'DRAFT', 'CANCELLED'] else PurchaseStatus.COMPLETED,
        
        bill_type=purchase_in.bill_type,
        settlement_type=purchase_in.settlement_type,
        settlement_metal_type=purchase_in.settlement_metal_type,
        metal_given_value=purchase_in.metal_given_value,
        cash_paid=purchase_in.cash_paid,
        balance_amount=purchase_in.balance_amount,
        gold_balance_metal_weight=purchase_in.gold_balance_metal_weight,
        silver_balance_metal_weight=purchase_in.silver_balance_metal_weight
    )
    db.add(db_purchase)
    db.flush()
    
    # Process each item
    for item_in in purchase_in.items:
        # Create item with values from frontend
        db_item = PurchaseItem(
            purchase_id=db_purchase.id,
            metal_type=item_in.metal_type,
            item_name=item_in.item_name,
            category=item_in.category,
            gross_weight=item_in.gross_weight,
            stone_weight=item_in.stone_weight,
            net_weight=item_in.net_weight,
            touch_purity=item_in.touch_purity,
            wastage=item_in.wastage,
            fine_weight=item_in.fine_weight,
            metal_rate=item_in.metal_rate,
            metal_value=item_in.metal_value,
            labour_charge=item_in.labour_charge,
            testing_melting_charge=item_in.testing_melting_charge,
            hallmark_charge=item_in.hallmark_charge,
            other_charges=item_in.other_charges,
            discount=item_in.discount,
            taxable_amount=item_in.taxable_amount
        )
        db.add(db_item)
    
    # Update seller outstanding balance (We owe them)
    # 1. Update Monetary Balance
    amount_paid = float(purchase_in.cash_paid or purchase_in.amount_paid or 0)
    seller.outstanding_balance = float(seller.outstanding_balance or 0) + float(purchase_in.balance_amount)
    
    # 2. Update Metal Balance
    seller.fine_gold_balance = float(seller.fine_gold_balance or 0) + float(purchase_in.gold_balance_metal_weight)
    seller.fine_silver_balance = float(seller.fine_silver_balance or 0) + float(purchase_in.silver_balance_metal_weight)
    
    # Calculate gross metal flow for the ledger
    total_gold_given = 0.0
    total_silver_given = 0.0
    for item_in in purchase_in.items:
        if item_in.metal_type == 'Gold' and ("metal given" in item_in.item_name.lower() or "deposit" in item_in.item_name.lower()):
            total_gold_given += float(item_in.fine_weight)
        elif item_in.metal_type == 'Silver' and ("metal given" in item_in.item_name.lower() or "deposit" in item_in.item_name.lower()):
            total_silver_given += float(item_in.fine_weight)

    gold_bal = float(purchase_in.gold_balance_metal_weight)
    silver_bal = float(purchase_in.silver_balance_metal_weight)
    
    actual_gold_debit = total_gold_given
    actual_gold_credit = max(0.0, total_gold_given + gold_bal)
    
    actual_silver_debit = total_silver_given
    actual_silver_credit = max(0.0, total_silver_given + silver_bal)
    
    # Calculate gross cash flow
    # grand_total is the total bill value (Credit to supplier)
    # debit is the total value we settled via cash or metal (grand_total - balance_amount)
    grand_total = float(purchase_in.grand_total)
    balance_amt = float(purchase_in.balance_amount)
    actual_cash_debit = max(0.0, grand_total - balance_amt)
    
    # Create supplier ledger entry for the purchase
    from app.models.supplier_ledger import SupplierLedger
    ledger_entry = SupplierLedger(
        seller_id=seller.id,
        voucher_type='Purchase',
        voucher_number=db_purchase.purchase_number,
        description=f"Purchase {db_purchase.purchase_number}",
        debit=actual_cash_debit,
        credit=grand_total,
        balance=seller.outstanding_balance,
        gold_debit=actual_gold_debit,
        gold_credit=actual_gold_credit,
        gold_balance=seller.fine_gold_balance,
        silver_debit=actual_silver_debit,
        silver_credit=actual_silver_credit,
        silver_balance=seller.fine_silver_balance
    )
    db.add(ledger_entry)
    
    # Process payment if any amount was paid
    amount_paid = float(purchase_in.amount_paid or 0)
    if amount_paid > 0:
        seller.outstanding_balance -= amount_paid
        payment_entry = SupplierLedger(
            seller_id=seller.id,
            voucher_type='Payment',
            voucher_number=f"PAY-{db_purchase.purchase_number}",
            description=f"Payment for Purchase {db_purchase.purchase_number}",
            debit=amount_paid,
            credit=0,
            balance=seller.outstanding_balance,
            gold_balance=seller.fine_gold_balance,
            silver_balance=seller.fine_silver_balance
        )
        db.add(payment_entry)
    
    db.commit()
    db.refresh(db_purchase)
    
    return {"message": "Purchase saved", "id": db_purchase.id, "purchase_number": db_purchase.purchase_number}

@router.get("/", response_model=List[GoldPurchaseResponse])
def get_purchases(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Get all gold purchases (legacy endpoint). Auth required."""
    return gold_purchase_repo.get_multi(db, skip=skip, limit=limit)

@router.get("/history")
def get_unified_purchases_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get all unified purchases."""
    store_id = require_tenant_id(current_user)
    query = db.query(Purchase).filter(Purchase.store_id == store_id)
    total = query.count()
    items = query.order_by(Purchase.id.desc()).offset(skip).limit(limit).all()
    
    # We need to construct a basic dictionary response that matches the invoice history structure somewhat
    results = []
    for p in items:
        results.append({
            "id": p.id,
            "invoice_number": p.purchase_number,
            "invoice_date": p.created_at,
            "grand_total": p.grand_total,
            "status": p.status,
            "customer": {
                "first_name": p.seller.name if p.seller else 'Unknown',
                "last_name": '',
                "phone_number": p.seller.mobile if p.seller else ''
            }
        })
    return {"total": total, "items": results}

@router.get("/gold", response_model=List[GoldPurchaseResponse])
def get_gold_purchases(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    return gold_purchase_repo.get_multi(db, skip=skip, limit=limit)

@router.get("/gold/{id}", response_model=GoldPurchaseResponse)
def get_gold_purchase(
    id: int,
    db: Session = Depends(get_db)
) -> Any:
    purchase = gold_purchase_repo.get(db=db, id=id)
    if not purchase:
        raise HTTPException(status_code=404, detail="Gold purchase not found")
    return purchase

@router.post("/gold", response_model=GoldPurchaseResponse)
def create_gold_purchase(
    *,
    db: Session = Depends(get_db),
    purchase_in: GoldPurchaseCreate
) -> Any:
    # Check for duplicate invoice number
    existing = gold_purchase_repo.get_by_invoice(db, invoice_number=purchase_in.invoice_number)
    if existing:
        raise HTTPException(
            status_code=400,
            detail="A gold purchase with this invoice number already exists.",
        )
    return gold_purchase_repo.create(db=db, obj_in=purchase_in)

@router.get("/silver", response_model=List[SilverPurchaseResponse])
def get_silver_purchases(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    return silver_purchase_repo.get_multi(db, skip=skip, limit=limit)

@router.get("/silver/{id}", response_model=SilverPurchaseResponse)
def get_silver_purchase(
    id: int,
    db: Session = Depends(get_db)
) -> Any:
    purchase = silver_purchase_repo.get(db=db, id=id)
    if not purchase:
        raise HTTPException(status_code=404, detail="Silver purchase not found")
    return purchase

@router.post("/silver", response_model=SilverPurchaseResponse)
def create_silver_purchase(
    *,
    db: Session = Depends(get_db),
    purchase_in: SilverPurchaseCreate
) -> Any:
    # Check for duplicate invoice number
    existing = silver_purchase_repo.get_by_invoice(db, invoice_number=purchase_in.invoice_number)
    if existing:
        raise HTTPException(
            status_code=400,
            detail="A silver purchase with this invoice number already exists.",
        )
    
    # Validate using CalculationService (no longer using old PurchaseService)
    # The calculation is already done by frontend, we just validate
    net_weight = Decimal(str(purchase_in.weight)) * (Decimal(str(purchase_in.final_tanch)) / Decimal('100'))
    expected_recovered = CalculationService._round_final(net_weight, CalculationService.WEIGHT_PLACES)
    
    if abs(Decimal(str(purchase_in.recovered_silver)) - expected_recovered) > Decimal('0.01'):
        raise HTTPException(status_code=400, detail="Invalid silver calculation")
        
    return silver_purchase_repo.create(db=db, obj_in=purchase_in)

@router.get("/{id}/pdf-data")
def get_purchase_pdf_data(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get purchase data formatted for PDF generation."""
    store_id = require_tenant_id(current_user)
    purchase = db.query(Purchase).filter(Purchase.id == id, Purchase.store_id == store_id).first()
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")
    try:
        from app.services.invoice_pdf_service import InvoicePDFService
        return InvoicePDFService.get_purchase_pdf_data(id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/pdf-by-voucher/{voucher_number}")
def get_purchase_pdf_data_by_voucher(
    voucher_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get purchase data formatted for PDF generation using voucher number."""
    store_id = require_tenant_id(current_user)
    purchase = db.query(Purchase).filter(Purchase.store_id == store_id, Purchase.purchase_number == voucher_number).first()
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")
        
    try:
        from app.services.invoice_pdf_service import InvoicePDFService
        return InvoicePDFService.get_purchase_pdf_data(purchase.id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{id}")
def get_unified_purchase(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a single unified purchase formatted for the Invoice View Modal."""
    store_id = require_tenant_id(current_user)
    purchase = db.query(Purchase).filter(Purchase.id == id, Purchase.store_id == store_id).first()
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")
        
    return {
        "id": purchase.id,
        "invoice_number": purchase.purchase_number,
        "customer": {
            "first_name": purchase.seller.name if purchase.seller else "Unknown",
            "last_name": "",
            "phone_number": purchase.seller.mobile if purchase.seller else ""
        },
        "items": [
            {
                "item_name": item.item_name,
                "item_type": item.metal_type,
                "final_price": item.metal_value + item.labour_charge + item.testing_melting_charge + item.hallmark_charge + item.other_charges - item.discount
            }
            for item in purchase.items
        ],
        "subtotal": purchase.total_taxable,
        "tax_amount": purchase.cgst + purchase.sgst + purchase.igst,
        "discount_amount": sum(i.discount for i in purchase.items),
        "grand_total": purchase.grand_total
    }


@router.delete("/{id}")
def delete_unified_purchase(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Soft delete (cancel) a unified purchase and reverse supplier ledger and balances."""
    store_id = require_tenant_id(current_user)
    purchase = db.query(Purchase).filter(Purchase.id == id, Purchase.store_id == store_id).first()
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")
        
    if purchase.status == PurchaseStatus.CANCELLED:
        raise HTTPException(status_code=400, detail="Purchase is already cancelled")

    try:
        from app.models.supplier_ledger import SupplierLedger
        from app.models.seller import Seller

        if purchase.seller_id:
            seller = db.query(Seller).filter(
                Seller.id == purchase.seller_id,
                Seller.store_id == store_id
            ).first()
            if seller:
                orig_ledger = db.query(SupplierLedger).filter(
                    SupplierLedger.seller_id == seller.id,
                    SupplierLedger.voucher_number == purchase.purchase_number
                ).order_by(SupplierLedger.id.desc()).first()

                if orig_ledger:
                    net_cash = float(orig_ledger.credit or 0.0) - float(orig_ledger.debit or 0.0)
                    net_gold = float(orig_ledger.gold_credit or 0.0) - float(orig_ledger.gold_debit or 0.0)
                    net_silver = float(orig_ledger.silver_credit or 0.0) - float(orig_ledger.silver_debit or 0.0)
                else:
                    net_cash = float(purchase.grand_total or 0.0)
                    net_gold = 0.0
                    net_silver = 0.0

                seller.outstanding_balance = float(seller.outstanding_balance or 0.0) - net_cash
                seller.fine_gold_balance = float(seller.fine_gold_balance or 0.0) - net_gold
                seller.fine_silver_balance = float(seller.fine_silver_balance or 0.0) - net_silver

                reversal = SupplierLedger(
                    seller_id=seller.id,
                    voucher_type="Cancellation",
                    voucher_number=f"REV-{purchase.purchase_number}",
                    description=f"Cancellation reversal of Purchase {purchase.purchase_number}",
                    debit=float(orig_ledger.credit or 0.0) if orig_ledger else net_cash,
                    credit=float(orig_ledger.debit or 0.0) if orig_ledger else 0.0,
                    balance=seller.outstanding_balance,
                    gold_debit=float(orig_ledger.gold_credit or 0.0) if orig_ledger else net_gold,
                    gold_credit=float(orig_ledger.gold_debit or 0.0) if orig_ledger else 0.0,
                    gold_balance=seller.fine_gold_balance,
                    silver_debit=float(orig_ledger.silver_credit or 0.0) if orig_ledger else net_silver,
                    silver_credit=float(orig_ledger.silver_debit or 0.0) if orig_ledger else 0.0,
                    silver_balance=seller.fine_silver_balance
                )
                db.add(reversal)

        purchase.status = PurchaseStatus.CANCELLED
        db.commit()
        return {"message": "Purchase cancelled and reversed successfully"}
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to cancel purchase")
