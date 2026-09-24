from sqlalchemy import Column, Integer, String, Numeric, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum

class PaymentStatus(str, enum.Enum):
    PENDING = "Pending"
    PARTIAL = "Partial"
    COMPLETED = "Completed"

class Bill(Base):
    __tablename__ = "bills"
    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    
    total_amount = Column(Numeric(12, 2), nullable=False)
    discount = Column(Numeric(12, 2), default=0.0)
    cgst = Column(Numeric(12, 2), default=0.0)
    sgst = Column(Numeric(12, 2), default=0.0)
    igst = Column(Numeric(12, 2), default=0.0)
    round_off = Column(Numeric(5, 2), default=0.0)
    grand_total = Column(Numeric(12, 2), nullable=False)
    
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    customer = relationship("Customer", back_populates="bills")
    items = relationship("BillItem", back_populates="bill")
    payments = relationship("Payment", back_populates="bill")

class BillItem(Base):
    __tablename__ = "bill_items"
    id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(Integer, ForeignKey("bills.id"), nullable=False)
    inventory_id = Column(Integer, ForeignKey("inventory.id"), nullable=True) # Optional, can sell adhoc
    item_name = Column(String(100), nullable=False)
    metal_type = Column(String(20), nullable=False)
    
    gross_weight = Column(Numeric(10, 3), nullable=False)
    net_weight = Column(Numeric(10, 3), nullable=False)
    
    rate = Column(Numeric(12, 2), nullable=False)
    making_charge = Column(Numeric(12, 2), default=0.0)
    making_charge_type = Column(String(20)) # PERCENTAGE, PER_GRAM, FLAT
    hallmark_charge = Column(Numeric(12, 2), default=0.0)
    other_charges = Column(Numeric(12, 2), default=0.0)
    
    total = Column(Numeric(12, 2), nullable=False)

    bill = relationship("Bill", back_populates="items")
    inventory_item = relationship("Inventory")
