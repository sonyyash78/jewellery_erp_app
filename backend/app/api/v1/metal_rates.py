from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.api.dependencies import get_db, get_current_user, RoleChecker
from app.models.user import User
from app.schemas.metal_rate import RateCreate, MetalRateResponse, RateHistoryResponse
from app.services import metal_rate_service

router = APIRouter()

@router.post("/seed")
def seed_metals(db: Session = Depends(get_db)):
    """Seed initial Gold and Silver purities if they don't exist."""
    return metal_rate_service.seed_default_metals(db)

@router.post("/", response_model=MetalRateResponse)
def add_rate(
    rate_in: RateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["Admin", "Manager"]))
):
    """Add a new metal rate (implicitly stores history by inserting new row)."""
    return metal_rate_service.add_rate(db, rate_in)

@router.get("/", response_model=List[MetalRateResponse])
def list_rates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all metal rates (same as /latest - most recent active rates)."""
    return metal_rate_service.get_latest_rates(db)

@router.get("/latest", response_model=List[MetalRateResponse])
def get_latest_rates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the currently active rates for all purities."""
    return metal_rate_service.get_latest_rates(db)

@router.get("/{purity_id}/history", response_model=RateHistoryResponse)
def get_history(
    purity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get historical rates for a specific purity."""
    return metal_rate_service.get_rate_history(db, purity_id)
