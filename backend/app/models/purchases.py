from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class GoldPurchase(Base):
    __tablename__ = "gold_purchases"
    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    invoice_number = Column(String(50), unique=True, nullable=False)
    
    gross_weight = Column(Numeric(10, 3), nullable=False)
    stone_weight = Column(Numeric(10, 3), default=0.0)
    net_weight = Column(Numeric(10, 3), nullable=False)
    
    touch = Column(Numeric(5, 2), nullable=False) # e.g. 85.5
    purity = Column(String(20))
    todays_rate = Column(Numeric(12, 2), nullable=False)
    purchase_rate = Column(Numeric(12, 2), nullable=False)
    
    amount = Column(Numeric(12, 2), nullable=False)
    gst_amount = Column(Numeric(12, 2), default=0.0)
    total_amount = Column(Numeric(12, 2), nullable=False)
    
    purchase_date = Column(DateTime(timezone=True), server_default=func.now())

    supplier = relationship("Supplier", back_populates="gold_purchases")

class SilverPurchase(Base):
    __tablename__ = "silver_purchases"
    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    invoice_number = Column(String(50), unique=True, nullable=False)
    
    weight = Column(Numeric(10, 3), nullable=False)
    tanch = Column(Numeric(5, 2), nullable=False)
    wastage = Column(Numeric(5, 2), default=0.0)
    final_tanch = Column(Numeric(5, 2), nullable=False)
    recovered_silver = Column(Numeric(10, 3), nullable=False)
    
    todays_rate = Column(Numeric(12, 2), nullable=False)
    silver_value = Column(Numeric(12, 2), nullable=False)
    
    amount = Column(Numeric(12, 2), nullable=False)
    gst_amount = Column(Numeric(12, 2), default=0.0)
    total_amount = Column(Numeric(12, 2), nullable=False)
    
    purchase_date = Column(DateTime(timezone=True), server_default=func.now())

    supplier = relationship("Supplier", back_populates="silver_purchases")
