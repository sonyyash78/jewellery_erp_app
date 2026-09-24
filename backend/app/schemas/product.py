from pydantic import BaseModel, ConfigDict
from typing import List, Optional

# Sub-Schemas
class CategoryBase(BaseModel):
    name: str
    parent_id: Optional[int] = None

class CategoryResponse(CategoryBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class DesignBase(BaseModel):
    name: str
    design_code: str
    description: Optional[str] = None

class DesignResponse(DesignBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class StoneBase(BaseModel):
    name: str
    stone_type: str
    default_rate_per_carat: Optional[float] = None

class StoneResponse(StoneBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class ImageCreate(BaseModel):
    image_url: str
    is_primary: bool = False

class ImageResponse(ImageCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)

class VariantStoneCreate(BaseModel):
    stone_id: int
    weight_carat: float
    pieces: int = 1

class VariantStoneResponse(VariantStoneCreate):
    id: int
    stone: StoneResponse
    model_config = ConfigDict(from_attributes=True)

class VariantCreate(BaseModel):
    purity_id: int
    standard_weight: Optional[float] = None
    size: Optional[str] = None
    making_charge_type: Optional[str] = None
    stones: List[VariantStoneCreate] = []

class VariantResponse(BaseModel):
    id: int
    purity_id: int
    standard_weight: Optional[float]
    size: Optional[str]
    making_charge_type: Optional[str]
    stones: List[VariantStoneResponse] = []
    model_config = ConfigDict(from_attributes=True)

# Main Product Schema
class ProductCreate(BaseModel):
    category_id: Optional[int] = None
    design_id: Optional[int] = None
    metal_type_id: int
    name: str
    sku_prefix: str
    description: Optional[str] = None
    images: List[ImageCreate] = []
    variants: List[VariantCreate] = []

class ProductResponse(BaseModel):
    id: int
    category_id: Optional[int]
    design_id: Optional[int]
    metal_type_id: int
    name: str
    sku_prefix: str
    description: Optional[str]
    images: List[ImageResponse] = []
    variants: List[VariantResponse] = []
    model_config = ConfigDict(from_attributes=True)

class ProductListResponse(BaseModel):
    total: int
    items: List[ProductResponse]
