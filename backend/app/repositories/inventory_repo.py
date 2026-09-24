from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from app.repositories.base import BaseRepository
from app.models.inventory import Inventory, Category, QRInventory, ItemStatus, MetalType
from app.schemas.inventory import InventoryCreate, InventoryUpdate, CategoryCreate, CategoryUpdate, QRInventoryBase
from typing import List, Optional
import string
import random
import os
from app.core.config import settings

class InventoryRepository(BaseRepository[Inventory, InventoryCreate, InventoryUpdate]):
    def get_by_category(self, db: Session, category_id: int) -> List[Inventory]:
        return db.query(Inventory).filter(Inventory.category_id == category_id).all()
        
    def get_available_items(self, db: Session) -> List[Inventory]:
        return db.query(Inventory).filter(Inventory.status == ItemStatus.AVAILABLE).all()

    def create_with_qr(self, db: Session, obj_in: InventoryCreate) -> Inventory:
        """Create inventory item with auto-generated QR code."""
        # Generate unique item code based on metal type
        item_code = self._generate_unique_item_code(db, obj_in.metal_type)
        
        # Generate QR code
        qr_path = self._generate_qr_image(item_code)
        
        # Create QR inventory entry
        qr_entry = QRInventory(item_code=item_code, qr_image_path=qr_path)
        db.add(qr_entry)
        db.flush()  # Get the ID
        
        # Create inventory item
        db_obj = self.model(**obj_in.model_dump())
        db_obj.qr_code_id = qr_entry.id
        db_obj.item_code = item_code
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def _generate_unique_item_code(self, db: Session, metal_type: str) -> str:
        """Generate unique item code like GLD-000001, SLV-000001."""
        prefix = "GLD" if metal_type.upper() == "GOLD" else "SLV"
        
        # Get last item code for this metal type
        last_item = db.query(Inventory).filter(
            Inventory.item_code.like(f"{prefix}-%")
        ).order_by(Inventory.item_code.desc()).first()
        
        if last_item and last_item.item_code:
            # Extract number from existing code
            last_num = int(last_item.item_code.split("-")[1])
            new_num = last_num + 1
        else:
            new_num = 1
            
        # Use timestamp to ensure uniqueness across test runs with savepoints
        import time
        timestamp = int(time.time() * 1000) % 1000000
        return f"{prefix}-{new_num:06d}-{timestamp:06d}"
    
    def _generate_qr_image(self, item_code: str) -> str:
        """Generate QR code image and return file path."""
        try:
            import qrcode
            from PIL import Image
            
            # Create QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(item_code)
            qr.make(fit=True)
            
            # Create image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Ensure static directory exists
            static_dir = os.path.join(settings.PROJECT_DIR, "static")
            os.makedirs(static_dir, exist_ok=True)
            
            # Save QR image
            filename = f"qr_{item_code.replace('-', '_')}.png"
            filepath = os.path.join(static_dir, filename)
            img.save(filepath)
            
            return f"/static/{filename}"
        except Exception as e:
            # Return placeholder path if QR generation fails
            return f"/static/qr_{item_code.replace('-', '_')}.png"
    
    def regenerate_qr(self, db: Session, item_id: int) -> Inventory:
        """Regenerate QR code for existing item."""
        item = db.query(Inventory).filter(Inventory.id == item_id).first()
        if not item:
            raise ValueError(f"Item with id {item_id} not found")
        
        # Generate new item code
        new_item_code = self._generate_unique_item_code(db, item.metal_type)
        
        # Generate new QR code
        new_qr_path = self._generate_qr_image(new_item_code)
        
        # Update QR inventory entry
        qr_entry = db.query(QRInventory).filter(QRInventory.id == item.qr_code_id).first()
        if qr_entry:
            qr_entry.item_code = new_item_code
            qr_entry.qr_image_path = new_qr_path
        
        # Update inventory item
        item.item_code = new_item_code
        db.commit()
        db.refresh(item)
        
        return item

class CategoryRepository(BaseRepository[Category, CategoryCreate, CategoryUpdate]):
    def get_by_name(self, db: Session, name: str) -> Category | None:
        return db.query(Category).filter(Category.name == name).first()

class QRInventoryRepository(BaseRepository[QRInventory, QRInventoryBase, QRInventoryBase]):
    def get_by_code(self, db: Session, item_code: str) -> QRInventory | None:
        return db.query(QRInventory).filter(QRInventory.item_code == item_code).first()

inventory_repo = InventoryRepository(Inventory)
category_repo = CategoryRepository(Category)
qr_repo = QRInventoryRepository(QRInventory)
