import re
from pydantic import BaseModel, ConfigDict, constr, Field, field_validator
from typing import Optional
from decimal import Decimal
from datetime import datetime

# Customers
class CustomerBase(BaseModel):
    first_name: str = Field(..., min_length=1)
    last_name: Optional[str] = None
    phone_number: str = Field(..., pattern=r'^\d{10}$')
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    aadhaar_pan: Optional[str] = None
    gst_number: Optional[str] = None
    credit_limit: Optional[Decimal] = Decimal('0.00')
    outstanding_balance: Optional[Decimal] = Decimal('0.00')
    is_active: bool = True

    @field_validator('phone_number', mode='before')
    @classmethod
    def clean_phone_number(cls, v):
        if not v:
            return v
        cleaned = re.sub(r'[^0-9]', '', str(v))
        if len(cleaned) == 12 and cleaned.startswith('91'):
            cleaned = cleaned[2:]
        return cleaned

    @field_validator('credit_limit', 'outstanding_balance', mode='before')
    @classmethod
    def default_decimal_zero(cls, v):
        if v is None or v == '':
            return Decimal('0.00')
        return Decimal(str(v))

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = Field(None, pattern=r'^\d{10}$')

    @field_validator('phone_number', mode='before')
    @classmethod
    def clean_phone_number(cls, v):
        if not v:
            return v
        cleaned = re.sub(r'[^0-9]', '', str(v))
        if len(cleaned) == 12 and cleaned.startswith('91'):
            cleaned = cleaned[2:]
        return cleaned

    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    aadhaar_pan: Optional[str] = None
    gst_number: Optional[str] = None
    credit_limit: Optional[Decimal] = None
    outstanding_balance: Optional[Decimal] = None
    is_active: Optional[bool] = None

class CustomerResponse(CustomerBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class CustomerListResponse(BaseModel):
    total: int
    total_outstanding: Optional[Decimal] = Decimal('0.00')
    items: list[CustomerResponse]

    @field_validator('total_outstanding', mode='before')
    @classmethod
    def default_total_outstanding(cls, v):
        if v is None or v == '':
            return Decimal('0.00')
        return Decimal(str(v))

# Suppliers
class SupplierBase(BaseModel):
    name: str = Field(..., min_length=1)
    contact_person: Optional[str] = None
    mobile: str = Field(..., pattern=r'^\d{10}$')
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    gst_number: Optional[str] = None
    outstanding_balance: Optional[Decimal] = Decimal('0.00')
    is_active: bool = True

    @field_validator('mobile', mode='before')
    @classmethod
    def clean_supplier_mobile(cls, v):
        if not v:
            return v
        cleaned = re.sub(r'[^0-9]', '', str(v))
        if len(cleaned) == 12 and cleaned.startswith('91'):
            cleaned = cleaned[2:]
        return cleaned

    @field_validator('outstanding_balance', mode='before')
    @classmethod
    def default_supplier_outstanding(cls, v):
        if v is None or v == '':
            return Decimal('0.00')
        return Decimal(str(v))

class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    contact_person: Optional[str] = None
    mobile: Optional[str] = Field(None, pattern=r'^\d{10}$')

    @field_validator('mobile', mode='before')
    @classmethod
    def clean_supplier_mobile(cls, v):
        if not v:
            return v
        cleaned = re.sub(r'[^0-9]', '', str(v))
        if len(cleaned) == 12 and cleaned.startswith('91'):
            cleaned = cleaned[2:]
        return cleaned

    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    gst_number: Optional[str] = None
    outstanding_balance: Optional[Decimal] = None
    is_active: Optional[bool] = None

class SupplierResponse(SupplierBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)
