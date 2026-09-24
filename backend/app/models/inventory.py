from sqlalchemy import Column, Integer, String, Numeric, Boolean, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum

class MetalType(str, enum.Enum):
    GOLD = "Gold"
    SILVER = "Silver"

class ItemStatus(str, enum.Enum):
    AVAILABLE = "Available"
    SOLD = "Sold"
    RESERVED = "Reserved"

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(255))
    metal_type = Column(Enum(MetalType), nullable=False)

    inventory_items = relationship("Inventory", back_populates="category")
    products = relationship("Product", back_populates="category")

class Inventory(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String(100), nullable=False)
    item_code = Column(String(20), unique=True, index=True, nullable=False)  # Auto-generated: GLD-000001
    category_id = Column(Integer, ForeignKey("categories.id"))
    metal_type = Column(Enum(MetalType), nullable=False)
    gross_weight = Column(Numeric(10, 3), nullable=False)
    net_weight = Column(Numeric(10, 3), nullable=False)
    purity = Column(String(20)) # e.g., "22K", "18K", "92.5%"
    touch = Column(Numeric(5, 2))  # Touch/Purity percentage, e.g., 91.5, 99.9
    design_code = Column(String(50))
    status = Column(Enum(ItemStatus), default=ItemStatus.AVAILABLE)
    qr_code_id = Column(Integer, ForeignKey("qr_inventory.id"), unique=True)
    qr_image_path = Column(String(255))  # Path to generated QR image
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    category = relationship("Category", back_populates="inventory_items")
    qr_code = relationship("QRInventory", back_populates="inventory_item")

class QRInventory(Base):
    __tablename__ = "qr_inventory"
    id = Column(Integer, primary_key=True, index=True)
    item_code = Column(String(20), unique=True, index=True, nullable=False) # GLD-000001
    qr_image_path = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    inventory_item = relationship("Inventory", back_populates="qr_code", uselist=False)
