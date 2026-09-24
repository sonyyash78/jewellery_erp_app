from typing import Optional
from sqlalchemy import Integer, DECIMAL, ForeignKey, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base
import enum

class ItemType(str, enum.Enum):
    GOLD = "Gold"
    SILVER = "Silver"
    DIAMOND = "Diamond"

class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    invoice_id: Mapped[int] = mapped_column(Integer, ForeignKey("invoices.id", ondelete="CASCADE"))
    inventory_item_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("inventory_items.id", ondelete="SET NULL"), nullable=True)
    item_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    item_type: Mapped[ItemType] = mapped_column(Enum(ItemType))
    final_price: Mapped[float] = mapped_column(DECIMAL(12, 2))

    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="items")
    inventory_item: Mapped["InventoryItem"] = relationship("InventoryItem", back_populates="invoice_items")
    
    gold_calculation: Mapped[Optional["GoldCalculation"]] = relationship("GoldCalculation", back_populates="invoice_item", uselist=False, cascade="all, delete-orphan")
    silver_calculation: Mapped[Optional["SilverCalculation"]] = relationship("SilverCalculation", back_populates="invoice_item", uselist=False, cascade="all, delete-orphan")
