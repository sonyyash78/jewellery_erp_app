from sqlalchemy.orm import Session
from sqlalchemy import func
from app.repositories.base import BaseRepository
from app.models.crm import Customer, Supplier
from app.schemas.crm import CustomerCreate, CustomerUpdate, SupplierCreate, SupplierUpdate
from decimal import Decimal
from typing import Tuple, List

class CustomerRepository(BaseRepository[Customer, CustomerCreate, CustomerUpdate]):
    def get_by_phone(self, db: Session, phone: str) -> Customer | None:
        return db.query(Customer).filter(Customer.phone_number == phone).first()
        
    def get_total_outstanding(self, db: Session) -> Decimal:
        result = db.query(func.sum(Customer.outstanding_balance)).scalar()
        return result if result else Decimal('0.00')

class SupplierRepository(BaseRepository[Supplier, SupplierCreate, SupplierUpdate]):
    def get_by_mobile(self, db: Session, mobile: str) -> Supplier | None:
        return db.query(Supplier).filter(Supplier.mobile == mobile).first()
        
    def get_total_outstanding(self, db: Session) -> Decimal:
        result = db.query(func.sum(Supplier.outstanding_balance)).scalar()
        return result if result else Decimal('0.00')

customer_repo = CustomerRepository(Customer)
supplier_repo = SupplierRepository(Supplier)
