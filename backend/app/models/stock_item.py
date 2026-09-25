from sqlalchemy import Integer, String, DECIMAL, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from app.db.base_class import Base
from datetime import datetime

class StockItem(Base):
    __tablename__ = "stock_items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    store_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=1, index=True)
    item_code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    item_name: Mapped[str] = mapped_column(String(255))
    metal: Mapped[str] = mapped_column(String(50), index=True)
    category: Mapped[str] = mapped_column(String(100), index=True)
    hsn: Mapped[str] = mapped_column(String(50), nullable=True)
    
    purity: Mapped[str] = mapped_column(String(50), nullable=True)
    tanch: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=True)
    wastage: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=True)
    
    gross_weight: Mapped[float] = mapped_column(DECIMAL(10, 3))
    stone_weight: Mapped[float] = mapped_column(DECIMAL(10, 3), default=0)
    net_weight: Mapped[float] = mapped_column(DECIMAL(10, 3))
    
    making_type: Mapped[str] = mapped_column(String(50), nullable=True) # flat, per_gram, percentage
    making_charge: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0)
    hallmark: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0)
    other_charges: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0)
    
    location: Mapped[str] = mapped_column(String(100), nullable=True)
    shelf: Mapped[str] = mapped_column(String(100), nullable=True)
    
    image_path: Mapped[str] = mapped_column(String(255), nullable=True)
    qr_code_path: Mapped[str] = mapped_column(String(255), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="Available")
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
