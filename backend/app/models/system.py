from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # None = global broadcast
    title = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Integer, default=0) # 0 = unread, 1 = read
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(50), nullable=False) # e.g. "Create", "Update", "Delete", "Login"
    entity = Column(String(50)) # e.g. "Customer", "Bill"
    entity_id = Column(Integer)
    details = Column(JSON) # JSON object describing the change
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")

class Settings(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(50), unique=True, index=True, nullable=False)
    value = Column(JSON, nullable=False) # Can be a string, dict, array, etc.
    description = Column(String(255))
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
