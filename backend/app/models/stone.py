from typing import List, Optional
from sqlalchemy import Integer, String, DECIMAL
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

class Stone(Base):
    __tablename__ = "stones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    stone_type: Mapped[str] = mapped_column(String(100))
    default_rate_per_carat: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 2))

    variant_stones: Mapped[List["ProductVariantStone"]] = relationship("ProductVariantStone", back_populates="stone")
