from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from .seller import SellerResponse

class PurchaseItemCreate(BaseModel):
    metal_type: str
    item_name: str
    category: Optional[str] = None
    gross_weight: float
    stone_weight: float = 0
    net_weight: float
    touch_purity: float
    wastage: float = 0
    fine_weight: float
    metal_rate: float
    metal_value: float
    labour_charge: float = 0
    testing_melting_charge: float = 0
    hallmark_charge: float = 0
    other_charges: float = 0
    discount: float = 0
    taxable_amount: float

class PurchaseCreate(BaseModel):
    seller_id: Optional[int] = None
    seller: Optional[dict] = None # Support inline seller creation
    total_taxable: float
    cgst: float = 0
    sgst: float = 0
    igst: float = 0
    grand_total: float
    status: str = 'Completed'
    items: List[PurchaseItemCreate]

class PurchaseItemResponse(PurchaseItemCreate):
    id: int
    purchase_id: int
    model_config = ConfigDict(from_attributes=True)

class PurchaseResponse(BaseModel):
    id: int
    purchase_number: str
    seller_id: int
    created_by_id: int
    created_at: datetime
    total_taxable: float
    cgst: float
    sgst: float
    igst: float
    grand_total: float
    status: str
    items: List[PurchaseItemResponse]
    seller: SellerResponse
    model_config = ConfigDict(from_attributes=True)
