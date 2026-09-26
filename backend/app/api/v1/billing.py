from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.api.dependencies import require_tenant_id, get_current_user
from app.models.user import User
from app.models.billing import Bill, BillItem
from app.schemas.billing import BillCreate, BillResponse
from app.services.billing_service import BillingService

router = APIRouter()

@router.get("/", response_model=List[BillResponse])
def get_bills(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
) -> Any:
    store_id = require_tenant_id(current_user)
    return db.query(Bill).filter(Bill.store_id == store_id).offset(skip).limit(limit).all()

@router.post("/", response_model=BillResponse)
def create_bill(
    *,
    db: Session = Depends(get_db),
    bill_in: BillCreate,
    current_user: User = Depends(get_current_user)
) -> Any:
    store_id = require_tenant_id(current_user)
    if bill_in.customer_id:
        from app.models.customer import Customer
        customer = db.query(Customer).filter(
            Customer.id == bill_in.customer_id,
            Customer.store_id == store_id
        ).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")

    existing = db.query(Bill).filter(
        Bill.store_id == store_id,
        Bill.invoice_number == bill_in.invoice_number
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="A bill with this invoice number already exists.",
        )
    
    obj_in_data = bill_in.model_dump(exclude={"items"})
    db_obj = Bill(**obj_in_data, store_id=store_id)
    db.add(db_obj)
    db.flush()
    
    for item in bill_in.items:
        item_data = item.model_dump()
        db_item = BillItem(**item_data, bill_id=db_obj.id)
        db.add(db_item)
        
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.get("/{id}", response_model=BillResponse)
def get_bill(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    store_id = require_tenant_id(current_user)
    bill = db.query(Bill).filter(Bill.id == id, Bill.store_id == store_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    return bill
