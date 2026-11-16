from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict, model_validator
from typing import Optional, Any
from datetime import datetime
import re

class CustomerBase(BaseModel):
    first_name: str = Field(default="Customer", max_length=100)
    last_name: Optional[str] = Field(default="", max_length=100)
    phone_number: str = Field(default="910000000000", max_length=20)
    email: Optional[EmailStr] = None
    pan_card: Optional[str] = None
    aadhar_card: Optional[str] = None
    aadhaar_pan: Optional[str] = None
    gst_number: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    credit_limit: float = 0
    outstanding_balance: float = 0
    fine_gold_balance: float = 0
    fine_silver_balance: float = 0
    company_id: Optional[int] = 1

    model_config = ConfigDict(extra="ignore")

    @model_validator(mode="before")
    @classmethod
    def normalize_fields(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
            
        d = dict(data)

        # 1. Map name -> first_name, last_name
        if "name" in d and d.get("name"):
            raw_name = str(d["name"]).strip()
            parts = raw_name.split(maxsplit=1)
            if not d.get("first_name"):
                d["first_name"] = parts[0] if parts else "Customer"
            if len(parts) > 1 and not d.get("last_name"):
                d["last_name"] = parts[1]

        if not d.get("first_name") or str(d.get("first_name")).strip() == "":
            d["first_name"] = "Customer"

        # 2. Map mobile / phone -> phone_number
        if "phone_number" not in d or not d.get("phone_number"):
            if d.get("mobile"):
                d["phone_number"] = str(d["mobile"]).strip()
            elif d.get("phone"):
                d["phone_number"] = str(d["phone"]).strip()

        # 3. Map aadhaar_pan <-> pan_card / aadhar_card
        raw_pan = d.get("aadhaar_pan") or d.get("pan_card") or d.get("aadhar_card")
        if raw_pan:
            clean_pan = str(raw_pan).strip().upper()
            d["aadhaar_pan"] = clean_pan
            if re.match(r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$", clean_pan):
                d["pan_card"] = clean_pan
            else:
                d["aadhar_card"] = clean_pan

        return d

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v: Any) -> str:
        if not v:
            return "910000000000"
        cleaned = re.sub(r"\D", "", str(v))
        if len(cleaned) == 10:
            cleaned = "91" + cleaned
        elif len(cleaned) == 12 and cleaned.startswith("91"):
            pass
        elif len(cleaned) > 10:
            cleaned = "91" + cleaned[-10:]
        elif len(cleaned) >= 5:
            cleaned = "91" + cleaned.zfill(10)
        else:
            cleaned = "910000000000"
        return cleaned

    @field_validator("pan_card")
    @classmethod
    def validate_pan(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return None
        clean = str(v).strip().upper()
        return clean if clean else None

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    pan_card: Optional[str] = None
    aadhar_card: Optional[str] = None
    aadhaar_pan: Optional[str] = None
    gst_number: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    credit_limit: Optional[float] = None
    outstanding_balance: Optional[float] = None
    fine_gold_balance: Optional[float] = None
    fine_silver_balance: Optional[float] = None
    company_id: Optional[int] = None

    model_config = ConfigDict(extra="ignore")

    @model_validator(mode="before")
    @classmethod
    def normalize_update_fields(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        d = dict(data)
        if "name" in d and d.get("name"):
            parts = str(d["name"]).strip().split(maxsplit=1)
            if not d.get("first_name"):
                d["first_name"] = parts[0]
            if len(parts) > 1 and not d.get("last_name"):
                d["last_name"] = parts[1]
        if "phone_number" not in d or not d.get("phone_number"):
            if d.get("mobile"):
                d["phone_number"] = str(d["mobile"]).strip()
            elif d.get("phone"):
                d["phone_number"] = str(d["phone"]).strip()
        raw_pan = d.get("aadhaar_pan") or d.get("pan_card")
        if raw_pan:
            d["aadhaar_pan"] = str(raw_pan).strip().upper()
        return d

class CustomerResponse(CustomerBase):
    id: int
    is_deleted: Optional[bool] = False
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True, extra="ignore")

class CustomerList(BaseModel):
    total: int
    items: list[CustomerResponse]
