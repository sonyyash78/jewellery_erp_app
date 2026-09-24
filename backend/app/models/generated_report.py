from typing import Optional
from datetime import datetime
from sqlalchemy import Integer, String, ForeignKey, DateTime, func, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

class GeneratedReport(Base):
    __tablename__ = "generated_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    report_name: Mapped[str] = mapped_column(String(255))
    report_type: Mapped[str] = mapped_column(String(100), index=True)
    generated_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="RESTRICT"))
    generated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)
    s3_file_url: Mapped[Optional[str]] = mapped_column(Text)

    generator: Mapped["User"] = relationship("User", back_populates="reports")
