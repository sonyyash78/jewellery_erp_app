"""
Diamond Calculation Model
=========================
Stores isolated diamond-specific calculation details for items.
Zero impact on gold/silver calculations.
"""
from typing import Optional
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Integer, String, DECIMAL, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base


class DiamondCalculation(Base):
    __tablename__ = "diamond_calculations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    invoice_item_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("invoice_items.id", ondelete="CASCADE"), nullable=True, index=True)
    purchase_item_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("purchase_items.id", ondelete="CASCADE"), nullable=True, index=True)
    exchange_item_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("exchange_items.id", ondelete="CASCADE"), nullable=True, index=True)

    # Diamond Specifications
    diamond_type: Mapped[str] = mapped_column(String(50), default="NATURAL", nullable=False)   # NATURAL, SYNTHETIC/LAB_GROWN
    diamond_form: Mapped[str] = mapped_column(String(50), default="CUT_AND_POLISHED", nullable=False) # UNWORKED, CUT_AND_POLISHED, MOUNTED_IN_JEWELLERY
    shape: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)                     # Round, Princess, Emerald, Oval, etc.
    carat_weight: Mapped[Decimal] = mapped_column(DECIMAL(10, 4), default=0, nullable=False)
    weight_gm: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 4), default=0, nullable=True)   # Carat (e.g. 1.2500)
    pieces: Mapped[int] = mapped_column(Integer, default=1, nullable=False)                    # Number of stones
    colour: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)                    # D, E, F, G, H, etc.
    clarity: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)                   # IF, VVS1, VVS2, VS1, VS2, SI1, etc.
    cut: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)                       # Excellent, Very Good, Good, etc.
    certificate_no: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)          # GIA / IGI / SGL / etc.
    certifying_lab: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)           # GIA, IGI, etc.

    # Financials
    rate_per_carat: Mapped[Decimal] = mapped_column(DECIMAL(12, 2), default=0, nullable=False)
    rate_per_gm: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(12, 2), default=0, nullable=True)
    subtotal_diamond_value: Mapped[Decimal] = mapped_column(DECIMAL(12, 2), default=0, nullable=False) # carat * rate_per_carat
    discount: Mapped[Decimal] = mapped_column(DECIMAL(12, 2), default=0, nullable=False)
    making_charges: Mapped[Decimal] = mapped_column(DECIMAL(12, 2), default=0, nullable=False)
    other_charges: Mapped[Decimal] = mapped_column(DECIMAL(12, 2), default=0, nullable=False)
    total_diamond_value: Mapped[Decimal] = mapped_column(DECIMAL(12, 2), default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=func.now(), nullable=True)
