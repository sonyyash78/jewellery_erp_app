from sqlalchemy import Integer, DECIMAL, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

class ProductVariantStone(Base):
    __tablename__ = "product_variant_stones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    variant_id: Mapped[int] = mapped_column(Integer, ForeignKey("product_variants.id", ondelete="CASCADE"))
    stone_id: Mapped[int] = mapped_column(Integer, ForeignKey("stones.id", ondelete="RESTRICT"))
    weight_carat: Mapped[float] = mapped_column(DECIMAL(10, 3))
    pieces: Mapped[int] = mapped_column(Integer, default=1)

    variant: Mapped["ProductVariant"] = relationship("ProductVariant", back_populates="stones")
    stone: Mapped["Stone"] = relationship("Stone", back_populates="variant_stones")
