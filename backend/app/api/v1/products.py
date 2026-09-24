from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.product import ProductCreate, ProductResponse, ProductListResponse
from app.services import product_service

router = APIRouter()

@router.post("/", response_model=ProductResponse)
def create_product(
    product_in: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new Product, including its Variants, Stones, and Images."""
    return product_service.create_product(db, product_in, current_user.id)

@router.get("/", response_model=ProductListResponse)
def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List products with pagination and search."""
    total, items = product_service.get_products(db, skip, limit, search)
    return {"total": total, "items": items}

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific product tree by ID."""
    return product_service.get_product(db, product_id)

@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Soft delete a product."""
    product_service.delete_product(db, product_id, current_user.id)
    return {"message": "Product soft deleted"}
