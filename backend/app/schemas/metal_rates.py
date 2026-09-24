from pydantic import BaseModel, ConfigDict
from typing import Optional
from decimal import Decimal
from datetime import datetime, date

class MetalRateBase(BaseModel):
    metal_type: str
    rate_per_gram: Decimal
    purity: Optional[str] = None
    date: date

class MetalRateCreate(MetalRateBase):
    pass

class MetalRateResponse(MetalRateBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ExchangeBase(BaseModel):
    customer_id: int
    metal_type: str
    gross_weight: Decimal
    net_weight: Decimal
    purity: Optional[str] = None
    exchange_rate: Decimal
    exchange_value: Decimal
    adjustment_type: Optional[str] = None
    related_bill_id: Optional[int] = None

class ExchangeCreate(ExchangeBase):
    pass

class ExchangeResponse(ExchangeBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
