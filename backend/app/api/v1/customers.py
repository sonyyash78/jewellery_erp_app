from typing import Any, List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from decimal import Decimal

from app.db.database import get_db
from app.api.dependencies import require_tenant_id, get_current_user
from app.models.user import User
from app.schemas.crm import CustomerCreate, CustomerUpdate, CustomerResponse, CustomerListResponse
from app.models.crm import Customer
from app.models.customer_ledger import CustomerLedger
from app.models.invoice import Invoice, InvoiceStatus
from app.models.exchange import Exchange
from app.models.metal_rates import MetalRate

router = APIRouter()


@router.get("/", response_model=CustomerListResponse)
def get_customers(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
) -> Any:
    store_id = require_tenant_id(current_user)
    query = db.query(Customer).filter(Customer.store_id == store_id)
    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(
                Customer.first_name.ilike(like),
                Customer.last_name.ilike(like),
                Customer.phone_number.ilike(like),
                Customer.city.ilike(like),
            )
        )
    total = query.count()
    items = query.order_by(Customer.id.desc()).offset(skip).limit(limit).all()
    total_outstanding = db.query(Customer).filter(Customer.store_id == store_id).with_entities(
        Customer.outstanding_balance
    ).all()
    outstanding_sum = sum((row[0] or Decimal("0")) for row in total_outstanding)
    return {
        "total": total,
        "total_outstanding": outstanding_sum,
        "items": items,
    }


@router.post("/", response_model=CustomerResponse)
def create_customer(
    *,
    db: Session = Depends(get_db),
    customer_in: CustomerCreate,
    current_user: User = Depends(get_current_user),
) -> Any:
    store_id = require_tenant_id(current_user)
    # Check uniqueness within the same store
    existing = db.query(Customer).filter(
        Customer.store_id == store_id,
        Customer.phone_number == customer_in.phone_number
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="A customer with this mobile number already exists in your store.",
        )
    
    db_obj = Customer(
        **customer_in.model_dump(),
        store_id=store_id
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


@router.get("/{id}", response_model=CustomerResponse)
def get_customer(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    store_id = require_tenant_id(current_user)
    customer = db.query(Customer).filter(Customer.id == id, Customer.store_id == store_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.put("/{id}", response_model=CustomerResponse)
def update_customer(
    *,
    db: Session = Depends(get_db),
    id: int,
    customer_in: CustomerUpdate,
    current_user: User = Depends(get_current_user),
) -> Any:
    store_id = require_tenant_id(current_user)
    customer = db.query(Customer).filter(Customer.id == id, Customer.store_id == store_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    update_data = customer_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(customer, field, val)
        
    db.commit()
    db.refresh(customer)
    return customer


@router.delete("/{id}")
def delete_customer(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    store_id = require_tenant_id(current_user)
    customer = db.query(Customer).filter(Customer.id == id, Customer.store_id == store_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    db.delete(customer)
    db.commit()
    return {"ok": True}


@router.get("/{id}/ledger")
def get_customer_ledger(
    id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    store_id = require_tenant_id(current_user)
    customer = db.query(Customer).filter(Customer.id == id, Customer.store_id == store_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    entries = db.query(CustomerLedger).filter(CustomerLedger.customer_id == id).order_by(CustomerLedger.date.desc(), CustomerLedger.id.desc()).all()
    return entries


@router.post("/{id}/ledger")
def add_customer_ledger_entry(
    id: int, 
    entry: Dict[str, Any], 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    store_id = require_tenant_id(current_user)
    customer = db.query(Customer).filter(Customer.id == id, Customer.store_id == store_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
        
    debit = float(entry.get('debit') or 0)
    credit = float(entry.get('credit') or 0)
    gold_debit = float(entry.get('gold_debit') or 0)
    gold_credit = float(entry.get('gold_credit') or 0)
    silver_debit = float(entry.get('silver_debit') or 0)
    silver_credit = float(entry.get('silver_credit') or 0)
    
    customer.outstanding_balance = float(customer.outstanding_balance or 0) + debit - credit
    customer.fine_gold_balance = float(customer.fine_gold_balance or 0) + gold_debit - gold_credit
    customer.fine_silver_balance = float(customer.fine_silver_balance or 0) + silver_debit - silver_credit
    
    ledger = CustomerLedger(
        customer_id=id,
        voucher_type=entry.get('voucher_type', 'Manual'),
        voucher_number=entry.get('voucher_number'),
        description=entry.get('description'),
        debit=debit,
        credit=credit,
        balance=customer.outstanding_balance,
        gold_debit=gold_debit,
        gold_credit=gold_credit,
        gold_balance=customer.fine_gold_balance,
        silver_debit=silver_debit,
        silver_credit=silver_credit,
        silver_balance=customer.fine_silver_balance
    )
    
    db.add(ledger)
    db.commit()
    db.refresh(ledger)
    return {"ledger": ledger, "new_balance": customer.outstanding_balance, "gold_balance": customer.fine_gold_balance, "silver_balance": customer.fine_silver_balance}

@router.get("/{id}/bills")
def get_customer_bills(
    id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    store_id = require_tenant_id(current_user)
    customer = db.query(Customer).filter(Customer.id == id, Customer.store_id == store_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    ledger_entries = db.query(CustomerLedger).filter(
        CustomerLedger.customer_id == id
    ).order_by(CustomerLedger.date.desc(), CustomerLedger.id.desc()).all()
    
    formatted_bills = []
    for entry in ledger_entries:
        gold_d = float(entry.gold_debit or 0.0)
        gold_c = float(entry.gold_credit or 0.0)
        silver_d = float(entry.silver_debit or 0.0)
        silver_c = float(entry.silver_credit or 0.0)
        deb = float(entry.debit or 0.0)
        cred = float(entry.credit or 0.0)
        bal = float(entry.balance or 0.0)
        formatted_bills.append({
            "id": entry.id,
            "date": str(entry.date) if entry.date else None,
            "type": entry.voucher_type,
            "bill_no": entry.voucher_number or '-',
            "summary": entry.description or '-',
            "gold_change": float(gold_d - gold_c),
            "silver_change": float(silver_d - silver_c),
            "debit": deb,
            "credit": cred,
            "balance": bal,
            "gold_balance": float(getattr(entry, 'gold_balance', None) if getattr(entry, 'gold_balance', None) is not None else (customer.fine_gold_balance or 0.0)),
            "silver_balance": float(getattr(entry, 'silver_balance', None) if getattr(entry, 'silver_balance', None) is not None else (customer.fine_silver_balance or 0.0)),
        })
    
    current_gold_rate = 7250.0
    current_silver_rate = 90.0
    try:
        latest_gold_rate = db.query(MetalRate).filter(MetalRate.metal_type == 'Gold').order_by(MetalRate.date.desc()).first()
        latest_silver_rate = db.query(MetalRate).filter(MetalRate.metal_type == 'Silver').order_by(MetalRate.date.desc()).first()
        if latest_gold_rate:
            current_gold_rate = float(getattr(latest_gold_rate, 'rate_per_gram', None) or getattr(latest_gold_rate, 'rate', None) or 7250.0)
        if latest_silver_rate:
            current_silver_rate = float(getattr(latest_silver_rate, 'rate_per_gram', None) or getattr(latest_silver_rate, 'rate', None) or 90.0)
    except Exception:
        pass
    
    return {
        "bills": formatted_bills,
        "current_gold_rate": float(current_gold_rate),
        "current_silver_rate": float(current_silver_rate),
        "outstanding_balance": float(customer.outstanding_balance or 0),
        "fine_gold_balance": float(customer.fine_gold_balance or 0),
        "fine_silver_balance": float(customer.fine_silver_balance or 0)
    }
