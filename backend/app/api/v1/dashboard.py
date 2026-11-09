from fastapi import APIRouter, Depends, Header
from typing import Optional
from sqlalchemy.orm import Session
from app.api.dependencies import require_tenant_id, get_db, get_current_user
from app.models.user import User
from app.services.report_service import ReportService

router = APIRouter()

@router.get("/metrics")
def get_dashboard_metrics(
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get dashboard metrics scoped to current user's tenant store and active company.
    """
    store_id = require_tenant_id(current_user)
    active_company = int(x_company_id) if (x_company_id and x_company_id.isdigit()) else 1
    return ReportService.get_dashboard_metrics(db, store_id=store_id, company_id=active_company)

@router.get("/chart-data")
def get_dashboard_charts(
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get dashboard charts data scoped to current user's tenant store and active company.
    """
    store_id = require_tenant_id(current_user)
    active_company = int(x_company_id) if (x_company_id and x_company_id.isdigit()) else 1
    return ReportService.get_dashboard_charts_data(db, store_id=store_id, company_id=active_company)

@router.get("/recent-activity")
def get_recent_activity(
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.models.invoice import Invoice
    from app.models.purchase import Purchase
    
    store_id = require_tenant_id(current_user)
    active_company = int(x_company_id) if (x_company_id and x_company_id.isdigit()) else 1

    if active_company == 1:
        recent_bills = db.query(Invoice).filter(Invoice.store_id == store_id, (Invoice.company_id == 1) | (Invoice.company_id.is_(None))).order_by(Invoice.invoice_date.desc()).limit(5).all()
        recent_purchases = db.query(Purchase).filter(Purchase.store_id == store_id, (Purchase.company_id == 1) | (Purchase.company_id.is_(None))).order_by(Purchase.created_at.desc()).limit(5).all()
    else:
        recent_bills = db.query(Invoice).filter(Invoice.store_id == store_id, Invoice.company_id == active_company).order_by(Invoice.invoice_date.desc()).limit(5).all()
        recent_purchases = db.query(Purchase).filter(Purchase.store_id == store_id, Purchase.company_id == active_company).order_by(Purchase.created_at.desc()).limit(5).all()
    
    bills = [{"id": b.id, "invoice_number": b.invoice_number, "date": b.invoice_date, "amount": float(b.grand_total)} for b in recent_bills]
    purchases = [{"id": p.id, "description": p.purchase_number, "date": p.created_at, "amount": float(p.grand_total)} for p in recent_purchases]
    
    return {
        "recent_bills": bills,
        "recent_purchases": purchases
    }
