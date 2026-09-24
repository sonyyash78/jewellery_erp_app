from typing import List
from sqlalchemy import Integer, String, DECIMAL, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base
import enum

class InventoryStatus(str, enum.Enum):
    AVAILABLE = "Available"
    SOLD = "Sold"
    RESERVED = "Reserved"

class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_variant_id: Mapped[int] = mapped_column(Integer, ForeignKey("product_variants.id", ondelete="RESTRICT"))
    warehouse_id: Mapped[int] = mapped_column(Integer, ForeignKey("warehouses.id", ondelete="RESTRICT"))
    barcode: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    gross_weight: Mapped[float] = mapped_column(DECIMAL(10, 3))
    net_weight: Mapped[float] = mapped_column(DECIMAL(10, 3))
    status: Mapped[InventoryStatus] = mapped_column(Enum(InventoryStatus), default=InventoryStatus.AVAILABLE, index=True)

    variant: Mapped["ProductVariant"] = relationship("ProductVariant", back_populates="inventory_items")
    warehouse: Mapped["Warehouse"] = relationship("Warehouse", back_populates="inventory_items")
    transactions: Mapped[List["InventoryTransaction"]] = relationship("InventoryTransaction", back_populates="inventory_item", cascade="all, delete-orphan")
    invoice_items: Mapped[List["InvoiceItem"]] = relationship("InvoiceItem", back_populates="inventory_item")
