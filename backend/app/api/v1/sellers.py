from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.seller import Seller
from app.schemas.seller import SellerCreate, SellerUpdate, SellerResponse
from app.models.purchase import Purchase
from app.models.metal_rates import MetalRate

router = APIRouter()

@router.post("/", response_model=SellerResponse)
def create_seller(seller_in: SellerCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_seller = Seller(**seller_in.model_dump())
    db.add(db_seller)
    db.commit()
    db.refresh(db_seller)
    return db_seller

@router.get("/", response_model=Dict[str, Any])
def list_sellers(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1), search: str = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Seller).filter(Seller.is_active == True)
    if search:
        query = query.filter(Seller.name.ilike(f"%{search}%") | Seller.mobile.ilike(f"%{search}%"))
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    
    total_outstanding = sum(s.outstanding_balance for s in db.query(Seller).all())
    
    # Convert items to SellerResponse
    items_data = [SellerResponse.model_validate(item) for item in items]
    return {"total": total, "items": items_data, "total_outstanding": total_outstanding}

@router.get("/{seller_id}", response_model=SellerResponse)
def get_seller(seller_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    seller = db.query(Seller).filter(Seller.id == seller_id, Seller.is_active == True).first()
    if not seller:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return seller

@router.put("/{seller_id}", response_model=SellerResponse)
def update_seller(seller_id: int, seller_in: SellerUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    seller = db.query(Seller).filter(Seller.id == seller_id, Seller.is_active == True).first()
    if not seller:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    update_data = seller_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(seller, key, value)
        
    db.commit()
    db.refresh(seller)
    return seller

@router.delete("/{seller_id}")
def delete_seller(seller_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    seller = db.query(Seller).filter(Seller.id == seller_id, Seller.is_active == True).first()
    if not seller:
        raise HTTPException(status_code=404, detail="Supplier not found")
        
    seller.is_active = False
    db.commit()
    return {"message": "Supplier deleted successfully"}

@router.get("/{seller_id}/ledger")
def get_supplier_ledger(seller_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from app.models.supplier_ledger import SupplierLedger
    entries = db.query(SupplierLedger).filter(SupplierLedger.seller_id == seller_id).order_by(SupplierLedger.date.desc(), SupplierLedger.id.desc()).all()
    return entries

from fastapi import HTTPException

@router.post("/{seller_id}/ledger")
def add_supplier_ledger_entry(
    seller_id: int, 
    entry: Dict[str, Any], 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    from app.models.supplier_ledger import SupplierLedger
    seller = db.query(Seller).filter(Seller.id == seller_id).first()
    if not seller:
        raise HTTPException(status_code=404, detail="Supplier not found")
        
    debit = float(entry.get('debit', 0)) # We pay them
    credit = float(entry.get('credit', 0)) # We buy from them
    gold_debit = float(entry.get('gold_debit', 0))
    gold_credit = float(entry.get('gold_credit', 0))
    silver_debit = float(entry.get('silver_debit', 0))
    silver_credit = float(entry.get('silver_credit', 0))
    
    # Update balance: Outstanding = Old Outstanding + Credit (Purchase) - Debit (Payment)
    seller.outstanding_balance = float(seller.outstanding_balance or 0) + credit - debit
    seller.fine_gold_balance = float(seller.fine_gold_balance or 0) + gold_credit - gold_debit
    seller.fine_silver_balance = float(seller.fine_silver_balance or 0) + silver_credit - silver_debit
    
    ledger = SupplierLedger(
        seller_id=seller_id,
        voucher_type=entry.get('voucher_type', 'Manual'),
        voucher_number=entry.get('voucher_number'),
        description=entry.get('description'),
        debit=debit,
        credit=credit,
        balance=seller.outstanding_balance,
        gold_debit=gold_debit,
        gold_credit=gold_credit,
        gold_balance=seller.fine_gold_balance,
        silver_debit=silver_debit,
        silver_credit=silver_credit,
        silver_balance=seller.fine_silver_balance
    )
    
    db.add(ledger)
    db.commit()
    db.refresh(ledger)
    return {"ledger": ledger, "new_balance": seller.outstanding_balance, "gold_balance": seller.fine_gold_balance, "silver_balance": seller.fine_silver_balance}

@router.get("/{seller_id}/bills")
def get_supplier_bills(seller_id: int, db: Session = Depends(get_db)):
    from app.models.supplier_ledger import SupplierLedger
    ledger_entries = db.query(SupplierLedger).filter(SupplierLedger.seller_id == seller_id).order_by(SupplierLedger.date.desc(), SupplierLedger.id.desc()).all()
    
    formatted_bills = []
    for entry in ledger_entries:
        formatted_bills.append({
            "id": entry.id,
            "date": entry.date,
            "type": entry.voucher_type,
            "bill_no": entry.voucher_number or '-',
            "summary": entry.description or '-',
            "gold_change": float(entry.gold_credit - entry.gold_debit),
            "silver_change": float(entry.silver_credit - entry.silver_debit),
            "debit": float(entry.debit),
            "credit": float(entry.credit),
            "balance": float(entry.balance)
        })
    
    # Supplier balances
    seller = db.query(Seller).filter(Seller.id == seller_id).first()
    
    # Get current metal rates
    latest_gold_rate = db.query(MetalRate).filter(MetalRate.metal_type == 'Gold').order_by(MetalRate.date.desc()).first()
    latest_silver_rate = db.query(MetalRate).filter(MetalRate.metal_type == 'Silver').order_by(MetalRate.date.desc()).first()
    
    current_gold_rate = latest_gold_rate.rate if latest_gold_rate else 7000
    current_silver_rate = latest_silver_rate.rate if latest_silver_rate else 85
    
    return {
        "bills": formatted_bills,
        "current_gold_rate": float(current_gold_rate),
        "current_silver_rate": float(current_silver_rate),
        "outstanding_balance": float(seller.outstanding_balance or 0),
        "fine_gold_balance": float(seller.fine_gold_balance or 0),
        "fine_silver_balance": float(seller.fine_silver_balance or 0)
    }
