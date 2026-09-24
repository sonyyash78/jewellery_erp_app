from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class ExchangeItemCreate(BaseModel):
    item_name: str
    metal: str
    purity: str
    touch: float
    gross_weight: float
    stone_weight: float = 0
    net_weight: float
    wastage: float = 0.0
    fine_weight: float = 0.0
    labour_charge: float = 0.0
    testing_melting_charge: float = 0.0
    hallmark_charge: float = 0.0
    other_charges: float = 0.0
    discount: float = 0.0
    rate_applied: float
    calculated_value: float

class ExchangeNewItemCreate(BaseModel):
    stock_item_id: Optional[int] = None
    item_name: str
    metal: str
    net_weight: float
    gross_weight: float = 0.0
    stone_weight: float = 0.0
    touch_purity: float = 100.0
    wastage: float = 0.0
    fine_weight: float = 0.0
    making_charge_type: str = "flat"
    making_charge_rate: float = 0.0
    making_charges_amount: float = 0.0
    hallmark_charges: float = 0.0
    other_charges: float = 0.0
    discount: float = 0.0
    rate_applied: float = 0.0
    final_price: float

class ExchangeCreate(BaseModel):
    customer_id: int
    amount_paid: Optional[float] = None
    total_old_value: float
    total_new_value: float
    gst_amount: float
    grand_total: float
    difference_amount: float
    
    settlement_type: str = "Cash"
    balance_amount: float = 0.0
    gold_balance_metal_weight: float = 0.0
    silver_balance_metal_weight: float = 0.0
    
    old_items: List[ExchangeItemCreate]
    new_items: List[ExchangeNewItemCreate]

class ExchangeItemResponse(ExchangeItemCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)

class ExchangeNewItemResponse(ExchangeNewItemCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)

class ExchangeResponse(BaseModel):
    id: int
    customer_id: int
    exchange_date: datetime
    total_old_value: float
    total_new_value: float
    gst_amount: float
    grand_total: float
    difference_amount: float
    
    old_items: List[ExchangeItemResponse]
    new_items: List[ExchangeNewItemResponse]
    
    model_config = ConfigDict(from_attributes=True)
