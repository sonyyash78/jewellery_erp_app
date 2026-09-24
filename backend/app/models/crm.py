from sqlalchemy import Column, Integer, String, Boolean, Numeric, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100))
    phone_number = Column(String(20), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True)
    address = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    pincode = Column(String(20))
    aadhaar_pan = Column(String(50))
    gst_number = Column(String(50))
    credit_limit = Column(Numeric(12, 2), default=0.0)
    outstanding_balance = Column(Numeric(12, 2), default=0.0)
    fine_gold_balance = Column(Numeric(10, 3), default=0.0)
    fine_silver_balance = Column(Numeric(10, 3), default=0.0)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    bills = relationship("Bill", back_populates="customer")
    invoices = relationship("Invoice", back_populates="customer")
    exchanges = relationship("Exchange", back_populates="customer")
    addresses = relationship("CustomerAddress", back_populates="customer", cascade="all, delete-orphan")

class Supplier(Base):
    __tablename__ = "suppliers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    contact_person = Column(String(100))
    mobile = Column(String(20), unique=True, index=True, nullable=False)
    email = Column(String(100))
    address = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    pincode = Column(String(20))
    gst_number = Column(String(20))
    outstanding_balance = Column(Numeric(12, 2), default=0.0)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    gold_purchases = relationship("GoldPurchase", back_populates="supplier")
    silver_purchases = relationship("SilverPurchase", back_populates="supplier")
