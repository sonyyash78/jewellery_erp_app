from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.api.dependencies import get_current_user
from app.repositories.crm_repo import supplier_repo
from app.schemas.crm import SupplierCreate, SupplierUpdate, SupplierResponse

router = APIRouter(dependencies=[Depends(get_current_user)])

@router.get("/", response_model=List[SupplierResponse])
def get_suppliers(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    return supplier_repo.get_multi(db, skip=skip, limit=limit)

@router.post("/", response_model=SupplierResponse)
def create_supplier(
    *,
    db: Session = Depends(get_db),
    supplier_in: SupplierCreate
) -> Any:
    supplier = supplier_repo.get_by_mobile(db, mobile=supplier_in.mobile)
    if supplier:
        raise HTTPException(
            status_code=400,
            detail="A supplier with this mobile already exists.",
        )
    return supplier_repo.create(db=db, obj_in=supplier_in)

@router.get("/{id}", response_model=SupplierResponse)
def get_supplier(
    id: int,
    db: Session = Depends(get_db)
) -> Any:
    supplier = supplier_repo.get(db=db, id=id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier

@router.put("/{id}", response_model=SupplierResponse)
def update_supplier(
    *,
    db: Session = Depends(get_db),
    id: int,
    supplier_in: SupplierUpdate
) -> Any:
    supplier = supplier_repo.get(db=db, id=id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier_repo.update(db=db, db_obj=supplier, obj_in=supplier_in)

@router.delete("/{id}")
def delete_supplier(
    *,
    db: Session = Depends(get_db),
    id: int
) -> Any:
    supplier = supplier_repo.get(db=db, id=id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    supplier_repo.remove(db=db, id=id)
    return {"ok": True}
