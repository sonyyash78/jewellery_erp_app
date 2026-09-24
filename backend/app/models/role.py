"""Compatibility shim — use the auth Role model (MySQL roles table)."""
from app.models.user import Role

__all__ = ["Role"]
