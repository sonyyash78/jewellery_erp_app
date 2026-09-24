from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.services.report_service import ReportService

router = APIRouter()

@router.get("/sales")
def get_sales_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get sales report with correct totals using ReportService.
    Uses historical transaction rates.
    """
    return ReportService.get_sales_report(db, start_date, end_date)

@router.get("/purchases")
def get_purchase_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get purchase report with correct totals using ReportService.
    Uses historical transaction rates.
    """
    return ReportService.get_purchase_report(db, start_date, end_date)

@router.get("/gst")
def get_gst_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get GST report with Input Tax Credit calculation.
    
    Output GST = Sum(Sales GST)
    Input GST = Sum(Purchase GST)  
    Net GST = Output GST - Input GST (ITC)
    """
    return ReportService.get_gst_report(db, start_date, end_date)

@router.get("/profit")
def get_profit_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get profit report with correct formulas.
    
    COGS = Purchase Cost + Making + Labour + Hallmark + Stone + Other
    Gross Profit = Sales - COGS
    Net Profit = Gross Profit - Expenses
    
    GST is NOT included in profit calculations.
    """
    return ReportService.get_profit_report(db, start_date, end_date)

@router.get("/metal-flow")
def get_metal_flow_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed breakdown of physical metal movement.
    """
    return ReportService.get_metal_flow_report(db, start_date, end_date)

@router.get("/inventory")
def get_inventory_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get inventory report.
    Uses purchase cost (historical rates), not current live rates.
    """
    return ReportService.get_inventory_report(db)

@router.get("/customers")
def get_customer_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.models.customer import Customer
    from sqlalchemy import func
    from decimal import Decimal
    
    total_customers = db.query(Customer).count()
    total_receivables = db.query(func.sum(Customer.outstanding_balance)).filter(Customer.outstanding_balance > 0).scalar() or 0
    
    return {
        "total": total_customers, 
        "receivables": float(Decimal(str(total_receivables)))
    }

@router.get("/suppliers")
def get_supplier_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.models.seller import Seller
    from sqlalchemy import func
    from decimal import Decimal
    
    total_suppliers = db.query(Seller).count()
    total_payables = db.query(func.sum(Seller.outstanding_balance)).filter(Seller.outstanding_balance < 0).scalar() or 0
    
    return {
        "total": total_suppliers, 
        "payables": abs(float(Decimal(str(total_payables))))
    }

@router.get("/expenses")
def get_expenses_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get expenses report grouped by category."""
    from app.models.expense import Expense as ExpenseModel
    from sqlalchemy import func
    
    query = db.query(ExpenseModel)
    if start_date:
        query = query.filter(ExpenseModel.expense_date >= start_date)
    if end_date:
        query = query.filter(ExpenseModel.expense_date <= end_date)
    
    expenses = query.all()
    total = sum(float(e.amount) for e in expenses)
    
    # Group by category
    category_totals = {}
    for e in expenses:
        cat = e.category or "Misc"
        category_totals[cat] = category_totals.get(cat, 0) + float(e.amount)
    
    return {
        "total_expenses": total,
        "by_category": category_totals,
        "expenses": [
            {
                "id": e.id,
                "category": e.category,
                "amount": float(e.amount),
                "description": e.description,
                "date": str(e.expense_date)
            }
            for e in expenses
        ]
    }
