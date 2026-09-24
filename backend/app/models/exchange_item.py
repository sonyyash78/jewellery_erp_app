from sqlalchemy import Integer, DECIMAL, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

class ExchangeItem(Base):
    __tablename__ = "exchange_items" # Represents Old Items given to us

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    exchange_id: Mapped[int] = mapped_column(Integer, ForeignKey("exchanges.id", ondelete="CASCADE"))
    
    item_name: Mapped[str] = mapped_column(String(100))
    metal: Mapped[str] = mapped_column(String(50)) # Gold, Silver
    purity: Mapped[str] = mapped_column(String(50))
    touch: Mapped[float] = mapped_column(DECIMAL(5, 2))
    
    gross_weight: Mapped[float] = mapped_column(DECIMAL(10, 3))
    stone_weight: Mapped[float] = mapped_column(DECIMAL(10, 3), default=0)
    net_weight: Mapped[float] = mapped_column(DECIMAL(10, 3))
    
    wastage: Mapped[float] = mapped_column(DECIMAL(5, 2), default=0.0)
    fine_weight: Mapped[float] = mapped_column(DECIMAL(10, 3), default=0.0)
    
    labour_charge: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0.0)
    testing_melting_charge: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0.0)
    hallmark_charge: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0.0)
    other_charges: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0.0)
    discount: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0.0)
    
    rate_applied: Mapped[float] = mapped_column(DECIMAL(10, 2))
    calculated_value: Mapped[float] = mapped_column(DECIMAL(12, 2))

    exchange: Mapped["Exchange"] = relationship("Exchange", back_populates="old_items")
