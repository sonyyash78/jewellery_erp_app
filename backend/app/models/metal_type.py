from typing import List
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

class MetalType(Base):
    __tablename__ = "metal_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)

    purities: Mapped[List["Purity"]] = relationship("Purity", back_populates="metal_type", cascade="all, delete-orphan")
    products: Mapped[List["Product"]] = relationship("Product", back_populates="metal_type")
