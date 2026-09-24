from datetime import datetime
from sqlalchemy import Integer, DECIMAL, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

class GoldRate(Base):
    __tablename__ = "gold_rates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    purity_id: Mapped[int] = mapped_column(Integer, ForeignKey("purities.id", ondelete="RESTRICT"))
    rate_per_gram: Mapped[float] = mapped_column(DECIMAL(10, 2))
    effective_datetime: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)

    purity: Mapped["Purity"] = relationship("Purity", back_populates="gold_rates")
    gold_calculations: Mapped[list["GoldCalculation"]] = relationship("GoldCalculation", back_populates="metal_rate")
