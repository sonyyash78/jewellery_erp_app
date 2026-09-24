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

    model_config = ConfigDict(from_attributes=True)

class RateHistoryResponse(BaseModel):
    purity: PurityResponse
    history: List[MetalRateResponse]
