from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class StockItemBase(BaseModel):
    item_name: str
    metal: str
    category: str
    hsn: Optional[str] = None
    purity: Optional[str] = None
    tanch: Optional[float] = None
    wastage: Optional[float] = None
    gross_weight: float
    stone_weight: float = 0
    net_weight: float
    making_type: Optional[str] = None
    making_charge: float = 0
    hallmark: float = 0
    other_charges: float = 0
    location: Optional[str] = None
    shelf: Optional[str] = None
    image_path: Optional[str] = None
    description: Optional[str] = None
    status: str = "Available"

class StockItemCreate(StockItemBase):
    pass

class StockItemUpdate(StockItemBase):
    item_code: Optional[str] = None

class StockItemResponse(StockItemBase):
    id: int
    item_code: str
    qr_code_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
