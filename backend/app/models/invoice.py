from typing import List, Optional
from datetime import datetime
from sqlalchemy import Integer, String, DECIMAL, ForeignKey, Enum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base
import enum

class InvoiceStatus(str, enum.Enum):
    DRAFT = "Draft"
    PARTIAL = "Partial"
    PAID = "Paid"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

class BillType(str, enum.Enum):
    CASH = "Cash"
    METAL = "Metal"
    HYBRID = "Hybrid"

class SettlementType(str, enum.Enum):
    CASH = "Cash"
    METAL = "Metal"

class MetalType(str, enum.Enum):
    GOLD = "Gold"
    SILVER = "Silver"

class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("customers.id", ondelete="SET NULL"), nullable=True)
    invoice_number: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    invoice_date: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)
    
    subtotal: Mapped[float] = mapped_column(DECIMAL(12, 2), default=0.0)
    tax_amount: Mapped[float] = mapped_column(DECIMAL(12, 2), default=0.0)
    discount_amount: Mapped[float] = mapped_column(DECIMAL(12, 2), default=0.0)
    grand_total: Mapped[float] = mapped_column(DECIMAL(12, 2), default=0.0)
    
    # New Fields for Hybrid Settlement
    bill_type: Mapped[BillType] = mapped_column(Enum(BillType, values_callable=lambda obj: [e.value for e in obj]), default=BillType.CASH)
    settlement_type: Mapped[SettlementType] = mapped_column(Enum(SettlementType, values_callable=lambda obj: [e.value for e in obj]), default=SettlementType.CASH)
    settlement_metal_type: Mapped[str] = mapped_column(String, nullable=True) # Gold or Silver (for old metal balance logic)
    metal_received_value: Mapped[float] = mapped_column(DECIMAL(12, 2), default=0.0)
    metal_received_str: Mapped[str] = mapped_column(String, nullable=True)
    cash_received: Mapped[float] = mapped_column(DECIMAL(12, 2), default=0.0)
    balance_amount: Mapped[float] = mapped_column(DECIMAL(12, 2), default=0.0)
    balance_metal_weight: Mapped[float] = mapped_column(DECIMAL(12, 3), default=0.0)
    gold_balance_metal_weight: Mapped[float] = mapped_column(DECIMAL(12, 3), default=0.0)
    silver_balance_metal_weight: Mapped[float] = mapped_column(DECIMAL(12, 3), default=0.0)

    status: Mapped[InvoiceStatus] = mapped_column(Enum(InvoiceStatus, values_callable=lambda obj: [e.value for e in obj]), default=InvoiceStatus.DRAFT, index=True)
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="RESTRICT"))

    customer: Mapped["Customer"] = relationship("Customer", back_populates="invoices", foreign_keys=[customer_id])
    creator: Mapped["User"] = relationship("User", back_populates="invoices", foreign_keys=[created_by])
    items: Mapped[List["InvoiceItem"]] = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    # payments relationship optional — Payment model may use a different invoice FK stack
