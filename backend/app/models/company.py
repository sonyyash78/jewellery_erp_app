"""
Company and Multi-Tenant GST Models
===================================
Models for multi-company isolation, GST management, HSN masters, state codes, and e-invoicing.
"""
from typing import Optional
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, DECIMAL, ForeignKey, JSON, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    gstin: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    pan: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Flags
    gst_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    diamond_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Numbering
    invoice_prefix: Mapped[str] = mapped_column(String(20), default="INV", nullable=False)
    invoice_series: Mapped[str] = mapped_column(String(20), default="S", nullable=False)

    # Banking
    bank_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    bank_account_no: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    bank_ifsc: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    bank_branch: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    upi_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    upi_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Visuals
    logo_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    signature_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    stamp_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Legal & Print
    declaration: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    jurisdiction_city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tax_label_style: Mapped[str] = mapped_column(String(50), default="STANDARD", nullable=False)
    computer_generated_note: Mapped[str] = mapped_column(
        String(255), default="This is a computer generated invoice.", nullable=False
    )
    financial_year_start: Mapped[int] = mapped_column(Integer, default=4, nullable=False)  # 4 = April
    rounding_mode: Mapped[str] = mapped_column(String(20), default="HALF_UP", nullable=False)
    storage_root: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=func.now(), nullable=True)


class CompanyNumberSequence(Base):
    __tablename__ = "company_number_sequences"
    __table_args__ = (
        UniqueConstraint("company_id", "financial_year", "doc_type", name="uq_company_fy_doctype"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    financial_year: Mapped[str] = mapped_column(String(10), nullable=False, index=True)  # e.g., "26-27"
    doc_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)        # "INVOICE", "PURCHASE", "EXCHANGE", "CREDIT_NOTE", "DEBIT_NOTE"
    last_sequence: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    prefix: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    series: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class HSNMaster(Base):
    __tablename__ = "hsn_master"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    hsn_code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # GOLD, SILVER, DIAMOND, OTHER
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=func.now())


class GSTRateMaster(Base):
    __tablename__ = "gst_rate_master"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    hsn_code: Mapped[str] = mapped_column(String(20), ForeignKey("hsn_master.hsn_code", ondelete="CASCADE"), nullable=False, index=True)
    total_rate: Mapped[Decimal] = mapped_column(DECIMAL(6, 4), nullable=False)  # e.g., 3.0000, 1.5000, 0.2500
    cgst_rate: Mapped[Decimal] = mapped_column(DECIMAL(6, 4), nullable=False)   # e.g., 1.5000, 0.7500, 0.1250
    sgst_rate: Mapped[Decimal] = mapped_column(DECIMAL(6, 4), nullable=False)   # e.g., 1.5000, 0.7500, 0.1250
    igst_rate: Mapped[Decimal] = mapped_column(DECIMAL(6, 4), nullable=False)   # e.g., 3.0000, 1.5000, 0.2500
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    effective_from: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    effective_to: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    updated_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=func.now())


class StateCode(Base):
    __tablename__ = "state_codes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(10), unique=True, index=True, nullable=False)  # "08"
    state_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)        # "Rajasthan"
    state_type: Mapped[str] = mapped_column(String(20), default="STATE", nullable=False)    # "STATE" or "UT"


class InvoiceGSTLine(Base):
    __tablename__ = "invoice_gst_lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    invoice_id: Mapped[int] = mapped_column(Integer, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False, index=True)
    invoice_item_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("invoice_items.id", ondelete="SET NULL"), nullable=True)
    hsn_code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    taxable_amount: Mapped[Decimal] = mapped_column(DECIMAL(12, 2), nullable=False)
    gst_rate: Mapped[Decimal] = mapped_column(DECIMAL(6, 4), nullable=False)
    cgst_rate: Mapped[Decimal] = mapped_column(DECIMAL(6, 4), default=0, nullable=False)
    cgst_amount: Mapped[Decimal] = mapped_column(DECIMAL(12, 2), default=0, nullable=False)
    sgst_rate: Mapped[Decimal] = mapped_column(DECIMAL(6, 4), default=0, nullable=False)
    sgst_amount: Mapped[Decimal] = mapped_column(DECIMAL(12, 2), default=0, nullable=False)
    igst_rate: Mapped[Decimal] = mapped_column(DECIMAL(6, 4), default=0, nullable=False)
    igst_amount: Mapped[Decimal] = mapped_column(DECIMAL(12, 2), default=0, nullable=False)
    total_tax_amount: Mapped[Decimal] = mapped_column(DECIMAL(12, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class InvoiceEInvoice(Base):
    __tablename__ = "invoice_einvoice"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    invoice_id: Mapped[int] = mapped_column(Integer, ForeignKey("invoices.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    irn: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    ack_no: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    ack_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    qr_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    qr_image_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    entered_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=func.now())
