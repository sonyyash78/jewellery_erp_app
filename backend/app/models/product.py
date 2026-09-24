from typing import List, Optional
from sqlalchemy import Integer, String, ForeignKey, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("categories.id", ondelete="SET NULL"))
    design_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("designs.id", ondelete="SET NULL"))
    metal_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("metal_types.id", ondelete="RESTRICT"))
    name: Mapped[str] = mapped_column(String(255))
    sku_prefix: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    category: Mapped[Optional["Category"]] = relationship("Category", back_populates="products")
    design: Mapped[Optional["Design"]] = relationship("Design", back_populates="products")
    metal_type: Mapped["MetalType"] = relationship("MetalType", back_populates="products")
    variants: Mapped[List["ProductVariant"]] = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")
    images: Mapped[List["ProductImage"]] = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
