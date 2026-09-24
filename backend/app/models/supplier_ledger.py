from typing import Optional
from datetime import datetime
from sqlalchemy import Integer, String, DateTime, DECIMAL, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

class SupplierLedger(Base):
    __tablename__ = "supplier_ledgers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    seller_id: Mapped[int] = mapped_column(Integer, ForeignKey("sellers.id", ondelete="CASCADE"), index=True)
    
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    voucher_type: Mapped[str] = mapped_column(String(50)) # Purchase, Payment, Opening Balance
    voucher_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True) # PUR-1001, PAY-001
    
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    debit: Mapped[float] = mapped_column(DECIMAL(12, 2), default=0)  # Amount we paid supplier (Payment)
    credit: Mapped[float] = mapped_column(DECIMAL(12, 2), default=0) # Amount we owe supplier (Purchase)
    balance: Mapped[float] = mapped_column(DECIMAL(12, 2)) # Running balance after this transaction (Credit - Debit)
    
    gold_debit: Mapped[float] = mapped_column(DECIMAL(10, 3), default=0)
    gold_credit: Mapped[float] = mapped_column(DECIMAL(10, 3), default=0)
    gold_balance: Mapped[float] = mapped_column(DECIMAL(10, 3), default=0)
    
    silver_debit: Mapped[float] = mapped_column(DECIMAL(10, 3), default=0)
    silver_credit: Mapped[float] = mapped_column(DECIMAL(10, 3), default=0)
    silver_balance: Mapped[float] = mapped_column(DECIMAL(10, 3), default=0)
    
    seller: Mapped["Seller"] = relationship("Seller")
