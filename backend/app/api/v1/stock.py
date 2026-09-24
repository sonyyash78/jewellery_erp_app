from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import qrcode
import os

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.stock_item import StockItem
from app.schemas.stock import StockItemCreate, StockItemUpdate, StockItemResponse

router = APIRouter()

QR_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'static', 'qrcodes')
os.makedirs(QR_DIR, exist_ok=True)

@router.post("/", response_model=StockItemResponse)
def create_stock_item(item_in: StockItemCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Generate Item Code
    prefix = "GLD" if item_in.metal.lower() == 'gold' else "SLV" if item_in.metal.lower() == 'silver' else "ITM"
    
    # Get last item to increment sequence
    last_item = db.query(StockItem).filter(StockItem.item_code.startswith(prefix)).order_by(StockItem.id.desc()).first()
    if last_item:
        last_num = int(last_item.item_code.split('-')[1])
        new_num = last_num + 1
    else:
        new_num = 1
    item_code = f"{prefix}-{str(new_num).zfill(6)}"
    
    # Generate QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(item_code)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    qr_filename = f"{item_code}.png"
    qr_path = os.path.join(QR_DIR, qr_filename)
    img.save(qr_path)
    
    db_item = StockItem(
        **item_in.model_dump(),
        item_code=item_code,
        qr_code_path=f"/static/qrcodes/{qr_filename}"
    )
    
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/", response_model=Dict[str, Any])
def list_stock_items(
    skip: int = Query(0, ge=0), 
    limit: int = Query(100, ge=1), 
    search: str = None, 
    category: str = None,
    metal: str = None,
    status: str = None,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    query = db.query(StockItem)
    if search:
        query = query.filter(StockItem.item_name.ilike(f"%{search}%") | StockItem.item_code.ilike(f"%{search}%"))
    if category:
        query = query.filter(StockItem.category == category)
    if metal:
        query = query.filter(StockItem.metal == metal)
    if status:
        query = query.filter(StockItem.status == status)
        
    total = query.count()
    items = query.order_by(StockItem.id.desc()).offset(skip).limit(limit).all()
    
    # Calculate stats
    total_weight = sum([item.net_weight for item in db.query(StockItem).all()])
    
    # Convert items to dict for serialization
    items_data = [StockItemResponse.model_validate(item) for item in items]
    return {"total": total, "items": items_data, "total_weight": float(total_weight)}

@router.get("/scan/{item_code}", response_model=StockItemResponse)
def scan_stock_item(item_code: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = db.query(StockItem).filter(StockItem.item_code == item_code).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.status.lower() == "sold":
        raise HTTPException(status_code=400, detail="Item already sold")
    return item

@router.delete("/{item_id}")
def delete_stock_item(item_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = db.query(StockItem).filter(StockItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return {"ok": True}

@router.put("/{item_id}", response_model=StockItemResponse)
def update_stock_item(item_id: int, item_in: StockItemUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = db.query(StockItem).filter(StockItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    update_data = item_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
        
    db.commit()
    db.refresh(item)
    return item
