from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.services.report_service import ReportService

router = APIRouter()

@router.get("/metrics")
def get_dashboard_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get dashboard metrics using unified ReportService.
    All calculations use CalculationService with correct formulas.
    """
    return ReportService.get_dashboard_metrics(db)

@router.get("/chart-data")
def get_dashboard_charts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get dashboard charts data: sales trend and top categories.
    """
    return ReportService.get_dashboard_charts_data(db)

@router.get("/recent-activity")
def get_recent_activity(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.models.invoice import Invoice
    from app.models.purchase import Purchase
    
    recent_bills = db.query(Invoice).order_by(Invoice.invoice_date.desc()).limit(5).all()
    recent_purchases = db.query(Purchase).order_by(Purchase.created_at.desc()).limit(5).all()
    
    bills = [{"id": b.id, "invoice_number": b.invoice_number, "date": b.invoice_date, "amount": float(b.grand_total)} for b in recent_bills]
    purchases = [{"id": p.id, "description": p.purchase_number, "date": p.created_at, "amount": float(p.grand_total)} for p in recent_purchases]
    
    return {
        "recent_bills": bills,
        "recent_purchases": purchases
    }
