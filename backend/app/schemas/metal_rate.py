from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class RateCreate(BaseModel):
    purity_id: int
    rate_per_gram: float
    metal_type: str  # 'Gold' or 'Silver'

class PurityResponse(BaseModel):
    id: int
    karat_name: str
    percentage: float

    model_config = ConfigDict(from_attributes=True)

class MetalRateResponse(BaseModel):
    id: int
    purity_id: int
    rate_per_gram: float
    effective_datetime: datetime
    purity: Optional[PurityResponse] = None
    purity_name: Optional[str] = None
    metal_type: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class CustomRateItemSchema(BaseModel):
    id: Optional[str] = None
    name: str
    metal_type: str = "Gold"
    purity_percent: float = 91.6
    rate: float
    unit: Optional[str] = None

class LiveRatesConfigUpdate(BaseModel):
    auto_sync_live: Optional[bool] = None
    active_rates: Optional[dict[str, float]] = None
    custom_rates: Optional[List[CustomRateItemSchema]] = None

class RateHistoryResponse(BaseModel):
    purity: PurityResponse
    history: List[MetalRateResponse]
