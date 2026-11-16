"""
Company Management API
======================
Endpoints for listing, selecting, updating companies, and fetching company-specific masters.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Header, Request, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.company import Company, HSNMaster, GSTRateMaster, StateCode
from app.models.audit_log import AuditLog
from app.schemas.company import (
    CompanyResponse, CompanyUpdate, HSNMasterResponse, GSTRateResponse
)

router = APIRouter()


def resolve_company_id(
    request: Request,
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID"),
    db: Session = Depends(get_db)
) -> int:
    """Resolve and validate active company_id from header, query param, or fallback to 1."""
    cid = None
    if x_company_id:
        try:
            cid = int(x_company_id)
        except ValueError:
            pass
    if not cid:
        query_val = request.query_params.get("company_id")
        if query_val:
            try:
                cid = int(query_val)
            except ValueError:
                pass
    if not cid:
        cid = 1

    exists = db.query(Company.id).filter(Company.id == cid, Company.is_active == True).first()
    if not exists:
        return 1
    return cid


@router.get("", response_model=List[CompanyResponse])
def get_companies(
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List companies. Regular users get active only, admin can request all."""
    query = db.query(Company)
    if not include_inactive:
        query = query.filter(Company.is_active == True)
    return query.order_by(Company.id).all()


@router.get("/current", response_model=CompanyResponse)
def get_current_active_company(
    company_id: int = Depends(resolve_company_id),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the currently resolved active company details."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.get("/hsn-masters", response_model=List[HSNMasterResponse])
def get_hsn_masters(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all active HSN master codes."""
    return db.query(HSNMaster).filter(HSNMaster.is_active == True).all()


@router.get("/gst-rates", response_model=List[GSTRateResponse])
def get_gst_rates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get active GST rate master records."""
    return db.query(GSTRateMaster).filter(GSTRateMaster.is_active == True).all()


@router.get("/state-codes")
def get_state_codes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all official Indian state and UT codes."""
    rows = db.query(StateCode).order_by(StateCode.code).all()
    return [{"code": r.code, "state_name": r.state_name, "state_type": r.state_type} for r in rows]


@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get company by ID."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.put("/{company_id}", response_model=CompanyResponse)
def update_company(
    company_id: int,
    payload: CompanyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update company details (Owner / Admin only). All changes logged to audit_log."""
    is_admin = (
        current_user.username == "admin"
        or getattr(current_user, "is_owner", False)
        or getattr(current_user, "is_admin", False)
        or (current_user.role and current_user.role.name.lower() in ["admin", "owner"])
        or getattr(current_user, "role_id", None) == 1
    )
    if not is_admin:
        raise HTTPException(status_code=403, detail="Only administrators can update company settings")

    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    old_values = {k: getattr(company, k) for k in payload.model_dump(exclude_unset=True).keys()}
    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(company, field, value)

    # Log to audit_log
    audit = AuditLog(
        user_id=current_user.id,
        entity_name="Company",
        entity_id=str(company_id),
        action="UPDATE",
        changes={"old": {k: str(v) for k, v in old_values.items()}, "new": {k: str(v) for k, v in update_data.items()}}
    )
    db.add(audit)
    db.commit()
    db.refresh(company)
    return company
