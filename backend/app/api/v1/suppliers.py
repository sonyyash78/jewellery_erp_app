from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.api.dependencies import require_tenant_id, get_current_user
from app.models.user import User
from app.models.crm import Supplier
from app.schemas.crm import SupplierCreate, SupplierUpdate, SupplierResponse

router = APIRouter()

@router.get("/", response_model=List[SupplierResponse])
def get_suppliers(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
) -> Any:
    store_id = require_tenant_id(current_user)
    return db.query(Supplier).filter(Supplier.store_id == store_id).offset(skip).limit(limit).all()

@router.post("/", response_model=SupplierResponse)
def create_supplier(
    *,
    db: Session = Depends(get_db),
    supplier_in: SupplierCreate,
    current_user: User = Depends(get_current_user)
) -> Any:
    store_id = require_tenant_id(current_user)
    existing = db.query(Supplier).filter(
        Supplier.store_id == store_id,
        Supplier.mobile == supplier_in.mobile
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="A supplier with this mobile already exists in your store.",
        )
    db_obj = Supplier(
        **supplier_in.model_dump(),
        store_id=store_id
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.get("/{id}", response_model=SupplierResponse)
def get_supplier(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    store_id = require_tenant_id(current_user)
    supplier = db.query(Supplier).filter(Supplier.id == id, Supplier.store_id == store_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier

@router.put("/{id}", response_model=SupplierResponse)
def update_supplier(
    *,
    db: Session = Depends(get_db),
    id: int,
    supplier_in: SupplierUpdate,
    current_user: User = Depends(get_current_user)
) -> Any:
    store_id = require_tenant_id(current_user)
    supplier = db.query(Supplier).filter(Supplier.id == id, Supplier.store_id == store_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    update_data = supplier_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(supplier, field, val)
    db.commit()
    db.refresh(supplier)
    return supplier

@router.delete("/{id}")
def delete_supplier(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: User = Depends(get_current_user)
) -> Any:
    store_id = require_tenant_id(current_user)
    supplier = db.query(Supplier).filter(Supplier.id == id, Supplier.store_id == store_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    db.delete(supplier)
    db.commit()
    return {"ok": True}
