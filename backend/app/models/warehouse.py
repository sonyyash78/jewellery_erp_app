from typing import List, Optional
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

class Warehouse(Base):
    __tablename__ = "warehouses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    location_address: Mapped[Optional[str]] = mapped_column(Text)

    inventory_items: Mapped[List["InventoryItem"]] = relationship("InventoryItem", back_populates="warehouse")
