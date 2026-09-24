from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.api.dependencies import get_current_user
from app.repositories.inventory_repo import inventory_repo, category_repo, qr_repo
from app.schemas.inventory import InventoryCreate, InventoryUpdate, InventoryResponse, CategoryCreate, CategoryResponse, CategoryUpdate
import os
from app.core.config import settings

router = APIRouter(dependencies=[Depends(get_current_user)])

@router.get("/", response_model=List[InventoryResponse])
def list_inventory(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    search: str = None,
) -> Any:
    """List all inventory items. Supports ?search= query."""
    if search:
        return [i for i in inventory_repo.get_multi(db, skip=skip, limit=limit) if search.lower() in i.item_name.lower()]
    return inventory_repo.get_multi(db, skip=skip, limit=limit)



@router.get("/categories", response_model=List[CategoryResponse])
def get_categories(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    return category_repo.get_multi(db, skip=skip, limit=limit)

@router.post("/categories", response_model=CategoryResponse)
def create_category(
    *,
    db: Session = Depends(get_db),
    category_in: CategoryCreate
) -> Any:
    category = category_repo.get_by_name(db, name=category_in.name)
    if category:
        raise HTTPException(
            status_code=400,
            detail="A category with this name already exists.",
        )
    return category_repo.create(db=db, obj_in=category_in)

@router.get("/items", response_model=List[InventoryResponse])
def get_items(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    return inventory_repo.get_multi(db, skip=skip, limit=limit)

@router.get("/items/{id}", response_model=InventoryResponse)
def get_item(
    id: int,
    db: Session = Depends(get_db),
) -> Any:
    item = inventory_repo.get(db=db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.post("/items", response_model=InventoryResponse)
def create_item(
    *,
    db: Session = Depends(get_db),
    item_in: InventoryCreate
) -> Any:
    """Create inventory item with auto-generated QR code."""
    return inventory_repo.create_with_qr(db=db, obj_in=item_in)

@router.put("/items/{id}", response_model=InventoryResponse)
def update_item(
    *,
    db: Session = Depends(get_db),
    id: int,
    item_in: InventoryUpdate
) -> Any:
    item = inventory_repo.get(db=db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return inventory_repo.update(db=db, db_obj=item, obj_in=item_in)

@router.delete("/items/{id}")
def delete_item(
    *,
    db: Session = Depends(get_db),
    id: int
) -> Any:
    item = inventory_repo.get(db=db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    inventory_repo.remove(db=db, id=id)
    return {"ok": True}

@router.post("/items/{id}/regenerate-qr", response_model=InventoryResponse)
def regenerate_qr(
    *,
    db: Session = Depends(get_db),
    id: int
) -> Any:
    """Admin endpoint to regenerate QR code for existing item."""
    try:
        return inventory_repo.regenerate_qr(db=db, item_id=id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/items/{id}/qr", response_class=FileResponse)
def download_qr(
    *,
    db: Session = Depends(get_db),
    id: int
) -> Any:
    """Download QR code as PNG image."""
    item = inventory_repo.get(db=db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    qr_entry = qr_repo.get(db, id=item.qr_code_id)
    if not qr_entry or not qr_entry.qr_image_path:
        raise HTTPException(status_code=404, detail="QR code not found")
    
    # Construct full file path
    static_dir = os.path.join(settings.PROJECT_DIR, "static")
    filepath = os.path.join(static_dir, qr_entry.qr_image_path.lstrip("/"))
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="QR image file not found")
    
    return FileResponse(filepath, media_type="image/png", filename=f"qr_{item.item_code}.png")

@router.get("/items/{id}/print-label", response_class=FileResponse)
def print_label(
    *,
    db: Session = Depends(get_db),
    id: int
) -> Any:
    """Generate printable label with QR code."""
    item = inventory_repo.get(db=db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    qr_entry = qr_repo.get(db, id=item.qr_code_id)
    if not qr_entry or not qr_entry.qr_image_path:
        raise HTTPException(status_code=404, detail="QR code not found")
    
    # Construct full file path
    static_dir = os.path.join(settings.PROJECT_DIR, "static")
    filepath = os.path.join(static_dir, qr_entry.qr_image_path.lstrip("/"))
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="QR image file not found")
    
    return FileResponse(filepath, media_type="image/png", filename=f"label_{item.item_code}.png")
