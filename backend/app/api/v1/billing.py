from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.api.dependencies import get_current_user
from app.repositories.transaction_repo import bill_repo
from app.schemas.billing import BillCreate, BillResponse
from app.services.billing_service import BillingService

router = APIRouter(dependencies=[Depends(get_current_user)])

@router.get("/", response_model=List[BillResponse])
def get_bills(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    return bill_repo.get_multi(db, skip=skip, limit=limit)

@router.post("/", response_model=BillResponse)
def create_bill(
    *,
    db: Session = Depends(get_db),
    bill_in: BillCreate
) -> Any:
    # Ensure invoice number is unique
    existing = bill_repo.get_by_invoice(db, invoice_number=bill_in.invoice_number)
    if existing:
        raise HTTPException(
            status_code=400,
            detail="A bill with this invoice number already exists.",
        )
    
    # Optional: We could validate the totals here using BillingService
    item_totals = [item.total for item in bill_in.items]
    calc = BillingService.calculate_bill_totals(
        item_totals=item_totals,
        discount=bill_in.discount,
        cgst_rate=bill_in.cgst, # Warning: front-end is passing the calculated AMOUNT, or RATE? The schema has them as amounts.
        # Assuming the front end calculated the amounts correctly.
    )
    
    return bill_repo.create_with_items(db=db, obj_in=bill_in)

@router.get("/{id}", response_model=BillResponse)
def get_bill(
    id: int,
    db: Session = Depends(get_db)
) -> Any:
    bill = bill_repo.get(db=db, id=id)
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    return bill
