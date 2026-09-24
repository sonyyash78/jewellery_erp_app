from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
import re

class CustomerBase(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    phone_number: str = Field(..., min_length=10, max_length=15)
    email: Optional[EmailStr] = None
    pan_card: Optional[str] = None
    aadhar_card: Optional[str] = None
    gst_number: Optional[str] = None
    credit_limit: float = 0
    outstanding_balance: float = 0
    fine_gold_balance: float = 0
    fine_silver_balance: float = 0

    @field_validator('phone_number')
    @classmethod
    def validate_phone(cls, v):
        # Enforce exactly 12 digits (2 digit country code + 10 digit number)
        # If exactly 10 digits are provided, assume India country code '91'
        cleaned = re.sub(r'\D', '', v)
        if len(cleaned) == 10:
            cleaned = '91' + cleaned
        if len(cleaned) != 12:
            raise ValueError("Phone number must be exactly 10 digits or 12 digits with country code (e.g., 919876543210)")
        return cleaned
        
    @field_validator('pan_card')
    @classmethod
    def validate_pan(cls, v):
        if v and not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', v.upper()):
            raise ValueError("Invalid PAN format")
        return v.upper() if v else v

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=2, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    phone_number: Optional[str] = Field(None, min_length=10, max_length=15)
    email: Optional[EmailStr] = None
    pan_card: Optional[str] = None
    aadhar_card: Optional[str] = None
    gst_number: Optional[str] = None
    credit_limit: Optional[float] = None
    outstanding_balance: Optional[float] = None
    fine_gold_balance: Optional[float] = None
    fine_silver_balance: Optional[float] = None

class CustomerResponse(CustomerBase):
    id: int
    is_deleted: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CustomerList(BaseModel):
    total: int
    items: list[CustomerResponse]
