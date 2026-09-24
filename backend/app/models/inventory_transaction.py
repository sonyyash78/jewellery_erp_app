from datetime import datetime
from sqlalchemy import Integer, Integer, ForeignKey, Enum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base
import enum

class TransactionType(str, enum.Enum):
    IN = "In"
    OUT = "Out"
    TRANSFER = "Transfer"
    ADJUSTMENT = "Adjustment"

class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    inventory_item_id: Mapped[int] = mapped_column(Integer, ForeignKey("inventory_items.id", ondelete="CASCADE"))
    transaction_type: Mapped[TransactionType] = mapped_column(Enum(TransactionType))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    date: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="RESTRICT"))

    inventory_item: Mapped["InventoryItem"] = relationship("InventoryItem", back_populates="transactions")
    user: Mapped["User"] = relationship("User", back_populates="inventory_transactions")
