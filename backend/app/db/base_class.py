"""Unified declarative Base — all models share MySQL metadata from database.py."""
from app.db.database import Base

__all__ = ["Base"]
