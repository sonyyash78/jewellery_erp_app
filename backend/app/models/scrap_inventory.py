from sqlalchemy import Integer, String, DECIMAL, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base
from datetime import datetime

class ScrapInventory(Base):
    __tablename__ = 'scrap_inventory'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    metal_type: Mapped[str] = mapped_column(String(50), index=True) # 'Gold' or 'Silver'
    total_fine_weight: Mapped[float] = mapped_column(DECIMAL(12, 3), default=0)
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
