from pydantic import BaseModel, ConfigDict, constr, Field
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
    credit_limit: Decimal = Decimal('0.00')
    outstanding_balance: Decimal = Decimal('0.00')
    is_active: bool = True

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = Field(None, pattern=r'^\d{10}$')
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
    total_outstanding: Decimal
    items: list[CustomerResponse]

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
    outstanding_balance: Decimal = Decimal('0.00')
    is_active: bool = True

class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    contact_person: Optional[str] = None
    mobile: Optional[str] = Field(None, pattern=r'^\d{10}$')
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

class SupplierListResponse(BaseModel):
    total: int
    total_outstanding: Decimal
    items: list[SupplierResponse]
