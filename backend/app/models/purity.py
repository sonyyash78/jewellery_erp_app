from typing import List
from sqlalchemy import Integer, String, DECIMAL, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

class Purity(Base):
    __tablename__ = "purities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    metal_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("metal_types.id", ondelete="CASCADE"))
    karat_name: Mapped[str] = mapped_column(String(50))
    percentage: Mapped[float] = mapped_column(DECIMAL(5, 2))

    metal_type: Mapped["MetalType"] = relationship("MetalType", back_populates="purities")
    product_variants: Mapped[List["ProductVariant"]] = relationship("ProductVariant", back_populates="purity")
    gold_rates: Mapped[List["GoldRate"]] = relationship("GoldRate", back_populates="purity")
    silver_rates: Mapped[List["SilverRate"]] = relationship("SilverRate", back_populates="purity")
