from typing import Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class CompanyBase(BaseModel):
    code: str
    name: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    state_code: Optional[str] = None
    gstin: Optional[str] = None
    pan: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    gst_enabled: bool = False
    diamond_enabled: bool = True
    invoice_prefix: str = "INV"
    invoice_series: str = "S"
    bank_name: Optional[str] = None
    bank_account_no: Optional[str] = None
    bank_ifsc: Optional[str] = None
    bank_branch: Optional[str] = None
    upi_id: Optional[str] = None
    upi_name: Optional[str] = None
    logo_url: Optional[str] = None
    signature_url: Optional[str] = None
    stamp_url: Optional[str] = None
    declaration: Optional[str] = None
    jurisdiction_city: Optional[str] = None
    tax_label_style: str = "STANDARD"
    computer_generated_note: str = "This is a computer generated invoice."
    financial_year_start: int = 4
    rounding_mode: str = "HALF_UP"
    storage_root: Optional[str] = None
    is_active: bool = True


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    state_code: Optional[str] = None
    gstin: Optional[str] = None
    pan: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    gst_enabled: Optional[bool] = None
    diamond_enabled: Optional[bool] = None
    invoice_prefix: Optional[str] = None
    invoice_series: Optional[str] = None
    bank_name: Optional[str] = None
    bank_account_no: Optional[str] = None
    bank_ifsc: Optional[str] = None
    bank_branch: Optional[str] = None
    upi_id: Optional[str] = None
    upi_name: Optional[str] = None
    logo_url: Optional[str] = None
    signature_url: Optional[str] = None
    stamp_url: Optional[str] = None
    declaration: Optional[str] = None
    jurisdiction_city: Optional[str] = None
    tax_label_style: Optional[str] = None
    computer_generated_note: Optional[str] = None
    financial_year_start: Optional[int] = None
    rounding_mode: Optional[str] = None
    storage_root: Optional[str] = None
    is_active: Optional[bool] = None


class CompanyResponse(CompanyBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class HSNMasterResponse(BaseModel):
    id: int
    hsn_code: str
    description: str
    category: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class GSTRateResponse(BaseModel):
    id: int
    hsn_code: str
    total_rate: Decimal
    cgst_rate: Decimal
    sgst_rate: Decimal
    igst_rate: Decimal
    description: Optional[str] = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
