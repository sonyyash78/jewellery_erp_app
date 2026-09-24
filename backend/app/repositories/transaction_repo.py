from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.billing import Bill, BillItem
from app.schemas.billing import BillCreate, BillItemCreate
from app.models.purchases import GoldPurchase, SilverPurchase
from app.schemas.purchases import GoldPurchaseCreate, SilverPurchaseCreate
from typing import Any, Dict, Union

class BillRepository(BaseRepository[Bill, BillCreate, BillCreate]): # Update schema will just be dict
    def get_by_invoice(self, db: Session, invoice_number: str) -> Bill | None:
        return db.query(Bill).filter(Bill.invoice_number == invoice_number).first()
        
    def create_with_items(self, db: Session, *, obj_in: BillCreate) -> Bill:
        # We override create because we need to handle items
        obj_in_data = obj_in.model_dump(exclude={"items"})
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.flush() # Get the ID
        
        for item in obj_in.items:
            item_data = item.model_dump()
            db_item = BillItem(**item_data, bill_id=db_obj.id)
            db.add(db_item)
            
        db.commit()
        db.refresh(db_obj)
        return db_obj

class GoldPurchaseRepository(BaseRepository[GoldPurchase, GoldPurchaseCreate, GoldPurchaseCreate]):
    def get_by_invoice(self, db: Session, invoice_number: str) -> GoldPurchase | None:
        return db.query(GoldPurchase).filter(GoldPurchase.invoice_number == invoice_number).first()

class SilverPurchaseRepository(BaseRepository[SilverPurchase, SilverPurchaseCreate, SilverPurchaseCreate]):
    def get_by_invoice(self, db: Session, invoice_number: str) -> SilverPurchase | None:
        return db.query(SilverPurchase).filter(SilverPurchase.invoice_number == invoice_number).first()

bill_repo = BillRepository(Bill)
gold_purchase_repo = GoldPurchaseRepository(GoldPurchase)
silver_purchase_repo = SilverPurchaseRepository(SilverPurchase)
