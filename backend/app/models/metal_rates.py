from sqlalchemy import Column, Integer, Numeric, Date, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class MetalRate(Base):
    __tablename__ = "metal_rates"
    id = Column(Integer, primary_key=True, index=True)
    metal_type = Column(String(20), nullable=False) # Gold, Silver
    rate_per_gram = Column(Numeric(12, 2), nullable=False)
    purity = Column(String(20)) # e.g. 22K, 24K, 999
    date = Column(Date, nullable=False, unique=True) # Usually one rate per day per metal/purity
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Legacy simple exchange schema kept for reference only (not mapped).
# Active Exchange model lives in app.models.exchange.
