from sqlalchemy import Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from app.db.base_class import Base

class Seller(Base):
    __tablename__ = 'sellers'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    mobile: Mapped[str] = mapped_column(String(20), index=True)
    aadhaar_pan: Mapped[str] = mapped_column(String(50), nullable=True)
    address: Mapped[str] = mapped_column(String(255), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=True)
    gst_number: Mapped[str] = mapped_column(String(20), nullable=True)
    from sqlalchemy import DECIMAL
    outstanding_balance: Mapped[float] = mapped_column(DECIMAL(12, 2), default=0) # positive means we owe them
    fine_gold_balance: Mapped[float] = mapped_column(DECIMAL(10, 3), default=0)
    fine_silver_balance: Mapped[float] = mapped_column(DECIMAL(10, 3), default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    purchases: Mapped[List['Purchase']] = relationship('Purchase', back_populates='seller')
