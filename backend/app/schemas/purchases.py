from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime

class SellerInfo(BaseModel):
    name: str
    mobile: str
    aadhaar_pan: Optional[str] = None
    address: Optional[str] = None

class PurchaseItemInput(BaseModel):
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

class GoldPurchaseBase(BaseModel):
    supplier_id: int
    invoice_number: str
    gross_weight: Decimal = Field(..., gt=0)
    stone_weight: Decimal = Decimal('0.00')
    net_weight: Decimal = Field(..., gt=0)
    touch: Decimal = Field(..., gt=0, le=100)
    purity: Optional[str] = None
    todays_rate: Decimal = Field(..., gt=0)
    purchase_rate: Decimal = Field(..., gt=0)
    amount: Decimal = Field(..., ge=0)
    gst_amount: Decimal = Decimal('0.00')
    total_amount: Decimal = Field(..., ge=0)

class GoldPurchaseCreate(GoldPurchaseBase):
    pass

class GoldPurchaseResponse(GoldPurchaseBase):
    id: int
    purchase_date: datetime
    model_config = ConfigDict(from_attributes=True)

class SilverPurchaseBase(BaseModel):
    supplier_id: int
    invoice_number: str
    weight: Decimal = Field(..., gt=0)
    tanch: Decimal = Field(..., gt=0, le=100)
    wastage: Decimal = Decimal('0.00')
    final_tanch: Decimal = Field(..., gt=0)
    recovered_silver: Decimal = Field(..., gt=0)
    todays_rate: Decimal = Field(..., gt=0)
    silver_value: Decimal = Field(..., gt=0)
    amount: Decimal = Field(..., ge=0)
    gst_amount: Decimal = Decimal('0.00')
    total_amount: Decimal = Field(..., ge=0)

class SilverPurchaseCreate(SilverPurchaseBase):
    pass

class SilverPurchaseResponse(SilverPurchaseBase):
    id: int
    purchase_date: datetime
    model_config = ConfigDict(from_attributes=True)

class UnifiedPurchaseCreate(BaseModel):
    seller_id: Optional[int] = None
    seller: Optional[SellerInfo] = None
    amount_paid: Optional[float] = None
    total_taxable: float
    cgst: float = 0
    sgst: float = 0
    igst: float = 0
    grand_total: float
    status: str = "Completed"
    
    bill_type: str = "Cash"
    settlement_type: str = "Cash"
    settlement_metal_type: Optional[str] = None
    metal_given_value: float = 0.0
    cash_paid: float = 0.0
    balance_amount: float = 0.0
    gold_balance_metal_weight: float = 0.0
    silver_balance_metal_weight: float = 0.0
    
    items: List[PurchaseItemInput]
