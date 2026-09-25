from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from app.models.invoice import InvoiceStatus
from app.models.invoice_item import ItemType

class GoldCalcCreate(BaseModel):
    metal_rate_id: Optional[int] = None
    applied_rate: float
    gross_weight: float
    stone_weight: float = 0.0
    net_weight: float
    touch_purity: float = 100.0
    wastage: float = 0.0
    fine_weight: float = 0.0
    making_charge_type: str = "flat"
    making_charge_rate: float = 0.0
    making_charges_amount: float = 0.0
    hallmark_charges: float = 0.0
    other_charges: float = 0.0
    discount: float = 0.0
    total_gold_value: float

class SilverCalcCreate(BaseModel):
    metal_rate_id: Optional[int] = None
    applied_rate: float
    gross_weight: float
    stone_weight: float = 0.0
    tanch_percentage: float = 100.0
    wastage: float = 0.0
    pure_weight: float = 0.0
    making_charge_type: str = "flat"
    making_charge_rate: float = 0.0
    making_charges_amount: float = 0.0
    other_charges: float = 0.0
    discount: float = 0.0
    total_silver_value: float

class InvoiceItemCreate(BaseModel):
    inventory_item_id: Optional[int] = None
    stock_item_id: Optional[int] = None
    item_name: str
    item_type: ItemType
    final_price: float
    gold_calculation: Optional[GoldCalcCreate] = None
    silver_calculation: Optional[SilverCalcCreate] = None

from app.models.invoice import InvoiceStatus, BillType, SettlementType, MetalType

class InvoiceCreate(BaseModel):
    customer_id: Optional[int] = None
    subtotal: float
    tax_amount: float
    discount_amount: float = 0.0
    grand_total: float
    amount_paid: Optional[float] = None
    status: InvoiceStatus = InvoiceStatus.DRAFT
    items: List[InvoiceItemCreate]
    
    # New Hybrid Billing fields
    bill_type: Optional[str] = "Cash"
    settlement_type: Optional[str] = "Cash"
    settlement_metal_type: Optional[str] = None
    metal_received_value: float = 0.0
    metal_received_str: str | None = None
    cash_received: float = 0.0
    balance_amount: float = 0.0
    balance_metal_weight: float = 0.0
    gold_balance_metal_weight: float = 0.0
    silver_balance_metal_weight: float = 0.0

class InvoiceCustomerInfo(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    phone_number: str

    model_config = ConfigDict(from_attributes=True)

class InvoiceResponse(BaseModel):
    id: int
    invoice_number: str
    customer_id: Optional[int] = None
    customer: Optional[InvoiceCustomerInfo] = None
    invoice_date: datetime
    subtotal: float
    tax_amount: float
    discount_amount: float
    grand_total: float
    status: InvoiceStatus
    
    bill_type: Optional[str] = "Cash"
    settlement_type: Optional[str] = "Cash"
    settlement_metal_type: Optional[str] = None
    metal_received_value: float
    cash_received: float
    balance_amount: float
    balance_metal_weight: float
    
    model_config = ConfigDict(from_attributes=True)
