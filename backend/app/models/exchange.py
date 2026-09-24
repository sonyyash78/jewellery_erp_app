from typing import List, Optional
from datetime import datetime
from sqlalchemy import Integer, DECIMAL, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

class Exchange(Base):
    __tablename__ = "exchanges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("customers.id", ondelete="RESTRICT"), index=True)
    exchange_date: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    total_old_value: Mapped[float] = mapped_column(DECIMAL(12, 2), default=0.0)
    total_new_value: Mapped[float] = mapped_column(DECIMAL(12, 2), default=0.0)
    gst_amount: Mapped[float] = mapped_column(DECIMAL(12, 2), default=0.0)
    grand_total: Mapped[float] = mapped_column(DECIMAL(12, 2), default=0.0)
    difference_amount: Mapped[float] = mapped_column(DECIMAL(12, 2), default=0.0) # Positive means customer pays, Negative means we owe

    customer: Mapped["Customer"] = relationship("Customer", back_populates="exchanges")
    
    old_items: Mapped[List["ExchangeItem"]] = relationship("ExchangeItem", back_populates="exchange", cascade="all, delete-orphan")
    new_items: Mapped[List["ExchangeNewItem"]] = relationship("ExchangeNewItem", back_populates="exchange", cascade="all, delete-orphan")
