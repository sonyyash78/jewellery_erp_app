from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime
from app.models.inventory import MetalType, ItemStatus

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    metal_type: MetalType

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    metal_type: Optional[MetalType] = None

class CategoryResponse(CategoryBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class InventoryBase(BaseModel):
    item_name: str
    item_code: Optional[str] = None  # Auto-generated if not provided
    category_id: Optional[int] = None
    metal_type: MetalType
    gross_weight: Decimal = Field(..., gt=0)
    net_weight: Decimal = Field(..., gt=0)
    purity: Optional[str] = None
    touch: Optional[Decimal] = None  # Touch/Purity percentage
    design_code: Optional[str] = None
    status: ItemStatus = ItemStatus.AVAILABLE

class InventoryCreate(InventoryBase):
    pass

class InventoryUpdate(BaseModel):
    item_name: Optional[str] = None
    category_id: Optional[int] = None
    metal_type: Optional[MetalType] = None
    gross_weight: Optional[Decimal] = Field(None, gt=0)
    net_weight: Optional[Decimal] = Field(None, gt=0)
    purity: Optional[str] = None
    touch: Optional[Decimal] = None  # Touch/Purity percentage
    design_code: Optional[str] = None
    status: Optional[ItemStatus] = None

class InventoryResponse(InventoryBase):
    id: int
    item_code: str
    qr_code_id: Optional[int] = None
    qr_image_path: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class QRInventoryBase(BaseModel):
    item_code: str
    qr_image_path: Optional[str] = None

class QRInventoryResponse(QRInventoryBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
