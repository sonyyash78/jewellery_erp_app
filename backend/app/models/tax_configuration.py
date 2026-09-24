from sqlalchemy import Integer, String, DECIMAL, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base_class import Base

class TaxConfiguration(Base):
    __tablename__ = "tax_configurations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tax_name: Mapped[str] = mapped_column(String(100), unique=True)
    percentage: Mapped[float] = mapped_column(DECIMAL(5, 2))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
