from typing import Any, List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from decimal import Decimal

from app.db.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.repositories.crm_repo import customer_repo
from app.schemas.crm import CustomerCreate, CustomerUpdate, CustomerResponse, CustomerListResponse
from app.models.crm import Customer
from app.models.customer_ledger import CustomerLedger
from app.models.invoice import Invoice, InvoiceStatus
from app.models.exchange import Exchange
from app.models.metal_rates import MetalRate

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/", response_model=CustomerListResponse)
def get_customers(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = Query(None),
) -> Any:
    query = db.query(Customer)
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
    total_outstanding = db.query(Customer).with_entities(
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
    customer_in: CustomerCreate
) -> Any:
    customer = customer_repo.get_by_phone(db, phone=customer_in.phone_number)
    if customer:
        raise HTTPException(
            status_code=400,
            detail="A customer with this mobile number already exists.",
        )
    return customer_repo.create(db=db, obj_in=customer_in)


@router.get("/{id}", response_model=CustomerResponse)
def get_customer(
    id: int,
    db: Session = Depends(get_db)
) -> Any:
    customer = customer_repo.get(db=db, id=id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.put("/{id}", response_model=CustomerResponse)
def update_customer(
    *,
    db: Session = Depends(get_db),
    id: int,
    customer_in: CustomerUpdate
) -> Any:
    customer = customer_repo.get(db=db, id=id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer_repo.update(db=db, db_obj=customer, obj_in=customer_in)


@router.delete("/{id}")
def delete_customer(
    *,
    db: Session = Depends(get_db),
    id: int
) -> Any:
    customer = customer_repo.get(db=db, id=id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    customer_repo.remove(db=db, id=id)
    return {"ok": True}


@router.get("/{id}/ledger")
def get_customer_ledger(
    id: int, 
    db: Session = Depends(get_db)
):
    entries = db.query(CustomerLedger).filter(CustomerLedger.customer_id == id).order_by(CustomerLedger.date.desc(), CustomerLedger.id.desc()).all()
    return entries


@router.post("/{id}/ledger")
def add_customer_ledger_entry(
    id: int, 
    entry: Dict[str, Any], 
    db: Session = Depends(get_db)
):
    customer = db.query(Customer).filter(Customer.id == id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
        
    debit = float(entry.get('debit') or 0) # Customer owes us (e.g. Bill)
    credit = float(entry.get('credit') or 0) # Customer paid us (e.g. Cash received)
    gold_debit = float(entry.get('gold_debit') or 0)
    gold_credit = float(entry.get('gold_credit') or 0)
    silver_debit = float(entry.get('silver_debit') or 0)
    silver_credit = float(entry.get('silver_credit') or 0)
    
    # Update balance: Outstanding = Old Outstanding + Debit (Bill) - Credit (Payment)
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
def get_customer_bills(id: int, db: Session = Depends(get_db)):
    ledger_entries = db.query(CustomerLedger).filter(CustomerLedger.customer_id == id).order_by(CustomerLedger.date.desc(), CustomerLedger.id.desc()).all()
    
    formatted_bills = []
    for entry in ledger_entries:
        formatted_bills.append({
            "id": entry.id,
            "date": entry.date,
            "type": entry.voucher_type,
            "bill_no": entry.voucher_number or '-',
            "summary": entry.description or '-',
            "gold_change": float(entry.gold_debit - entry.gold_credit),
            "silver_change": float(entry.silver_debit - entry.silver_credit),
            "debit": float(entry.debit),
            "credit": float(entry.credit),
            "balance": float(entry.balance)
        })
    
    # Customer balances
    customer = db.query(Customer).filter(Customer.id == id).first()
    
    # Get current metal rates
    latest_gold_rate = db.query(MetalRate).filter(MetalRate.metal_type == 'Gold').order_by(MetalRate.date.desc()).first()
    latest_silver_rate = db.query(MetalRate).filter(MetalRate.metal_type == 'Silver').order_by(MetalRate.date.desc()).first()
    
    current_gold_rate = latest_gold_rate.rate if latest_gold_rate else 7000
    current_silver_rate = latest_silver_rate.rate if latest_silver_rate else 85
    
    return {
        "bills": formatted_bills,
        "current_gold_rate": float(current_gold_rate),
        "current_silver_rate": float(current_silver_rate),
        "outstanding_balance": float(customer.outstanding_balance or 0),
        "fine_gold_balance": float(customer.fine_gold_balance or 0),
        "fine_silver_balance": float(customer.fine_silver_balance or 0)
    }
