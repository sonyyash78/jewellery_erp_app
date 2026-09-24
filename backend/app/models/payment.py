"""Compatibility shim — payments table is owned by accounting.Payment (bill payments).
Invoice-linked payments are not wired in this release to avoid dual-model conflicts.
"""
from app.models.accounting import Payment

__all__ = ["Payment"]
