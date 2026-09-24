from typing import Optional
from datetime import datetime
from sqlalchemy import Integer, String, DateTime, DECIMAL, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

class CustomerLedger(Base):
    __tablename__ = "customer_ledgers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), index=True)
    
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    voucher_type: Mapped[str] = mapped_column(String(50)) # Invoice, Payment, Opening Balance
    voucher_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True) # INV-1001, PAY-001
    
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    debit: Mapped[float] = mapped_column(DECIMAL(12, 2), default=0)  # Amount customer owes us (Invoice)
    credit: Mapped[float] = mapped_column(DECIMAL(12, 2), default=0) # Amount customer paid us (Payment)
    balance: Mapped[float] = mapped_column(DECIMAL(12, 2)) # Running balance after this transaction
    
    gold_debit: Mapped[float] = mapped_column(DECIMAL(10, 3), default=0)
    gold_credit: Mapped[float] = mapped_column(DECIMAL(10, 3), default=0)
    gold_balance: Mapped[float] = mapped_column(DECIMAL(10, 3), default=0)
    
    silver_debit: Mapped[float] = mapped_column(DECIMAL(10, 3), default=0)
    silver_credit: Mapped[float] = mapped_column(DECIMAL(10, 3), default=0)
    silver_balance: Mapped[float] = mapped_column(DECIMAL(10, 3), default=0)
    
    customer: Mapped["Customer"] = relationship("Customer")
