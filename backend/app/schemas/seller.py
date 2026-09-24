from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional

class SellerBase(BaseModel):
    name: str
    mobile: str
    aadhaar_pan: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    gst_number: Optional[str] = None
    outstanding_balance: float = 0
    fine_gold_balance: float = 0
    fine_silver_balance: float = 0
    is_active: bool = True

    @field_validator('mobile')
    @classmethod
    def validate_mobile(cls, v):
        import re
        cleaned = re.sub(r'\D', '', v)
        if len(cleaned) == 10:
            cleaned = '91' + cleaned
        if len(cleaned) != 12:
            raise ValueError("Mobile number must be exactly 10 digits or 12 digits with country code (e.g., 919876543210)")
        return cleaned

class SellerCreate(SellerBase):
    pass

class SellerUpdate(SellerBase):
    pass

class SellerResponse(SellerBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
