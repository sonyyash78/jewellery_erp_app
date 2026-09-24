from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base_class import Base

class NumberSequence(Base):
    __tablename__ = "number_sequences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entity: Mapped[str] = mapped_column(String(100), unique=True)
    prefix: Mapped[str] = mapped_column(String(50))
    next_number: Mapped[int] = mapped_column(Integer, default=1)
