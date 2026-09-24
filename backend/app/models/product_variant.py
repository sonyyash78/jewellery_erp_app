from typing import List, Optional
from sqlalchemy import Integer, String, DECIMAL, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

class ProductVariant(Base):
    __tablename__ = "product_variants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id", ondelete="CASCADE"))
    purity_id: Mapped[int] = mapped_column(Integer, ForeignKey("purities.id", ondelete="RESTRICT"))
    standard_weight: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 3))
    size: Mapped[Optional[str]] = mapped_column(String(50))
    making_charge_type: Mapped[Optional[str]] = mapped_column(String(50))

    product: Mapped["Product"] = relationship("Product", back_populates="variants")
    purity: Mapped["Purity"] = relationship("Purity", back_populates="product_variants")
    inventory_items: Mapped[List["InventoryItem"]] = relationship("InventoryItem", back_populates="variant")
    stones: Mapped[List["ProductVariantStone"]] = relationship("ProductVariantStone", back_populates="variant", cascade="all, delete-orphan")
