from typing import Optional
from sqlalchemy import Integer, DECIMAL, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

class ExchangeNewItem(Base):
    __tablename__ = "exchange_new_items" # Represents New Items sold to customer

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    exchange_id: Mapped[int] = mapped_column(Integer, ForeignKey("exchanges.id", ondelete="CASCADE"))
    stock_item_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("stock_items.id", ondelete="SET NULL"), nullable=True)
    
    item_name: Mapped[str] = mapped_column(String(100))
    metal: Mapped[str] = mapped_column(String(50))
    net_weight: Mapped[float] = mapped_column(DECIMAL(10, 3))
    gross_weight: Mapped[float] = mapped_column(DECIMAL(10, 3), default=0.0)
    stone_weight: Mapped[float] = mapped_column(DECIMAL(10, 3), default=0.0)
    
    touch_purity: Mapped[float] = mapped_column(DECIMAL(5, 2), default=100.0)
    wastage: Mapped[float] = mapped_column(DECIMAL(5, 2), default=0.0)
    fine_weight: Mapped[float] = mapped_column(DECIMAL(10, 3), default=0.0)
    
    making_charge_type: Mapped[str] = mapped_column(String(20), default="flat")
    making_charge_rate: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0.0)
    making_charges_amount: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0.0)
    hallmark_charges: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0.0)
    other_charges: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0.0)
    discount: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0.0)
    
    rate_applied: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0.0)
    final_price: Mapped[float] = mapped_column(DECIMAL(12, 2))

    exchange: Mapped["Exchange"] = relationship("Exchange", back_populates="new_items")
    stock_item: Mapped["StockItem"] = relationship("StockItem")
