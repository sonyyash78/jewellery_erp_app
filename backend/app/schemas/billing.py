from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from app.models.billing import PaymentStatus

class BillItemBase(BaseModel):
    inventory_id: Optional[int] = None
    item_name: str
    metal_type: str
    gross_weight: Decimal = Field(..., gt=0)
    net_weight: Decimal = Field(..., gt=0)
    rate: Decimal = Field(..., gt=0)
    making_charge: Decimal = Decimal('0.00')
    making_charge_type: Optional[str] = None
    hallmark_charge: Decimal = Decimal('0.00')
    other_charges: Decimal = Decimal('0.00')
    total: Decimal = Field(..., ge=0)

class BillItemCreate(BillItemBase):
    pass

class BillItemResponse(BillItemBase):
    id: int
    bill_id: int
    model_config = ConfigDict(from_attributes=True)

class BillBase(BaseModel):
    customer_id: int
    invoice_number: str
    total_amount: Decimal = Field(..., ge=0)
    discount: Decimal = Decimal('0.00')
    cgst: Decimal = Decimal('0.00')
    sgst: Decimal = Decimal('0.00')
    igst: Decimal = Decimal('0.00')
    round_off: Decimal = Decimal('0.00')
    grand_total: Decimal = Field(..., ge=0)
    payment_status: PaymentStatus = PaymentStatus.PENDING

class BillCreate(BillBase):
    items: List[BillItemCreate]

class BillResponse(BillBase):
    id: int
    created_at: datetime
    items: List[BillItemResponse] = []
    model_config = ConfigDict(from_attributes=True)
