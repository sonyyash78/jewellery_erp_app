from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal
from datetime import datetime

from app.api.dependencies import get_db, get_current_user, require_tenant_id
from app.models.user import User
from app.models.invoice import Invoice, InvoiceStatus
from app.models.invoice_item import InvoiceItem
from app.models.gold_calculation import GoldCalculation
from app.models.silver_calculation import SilverCalculation
from app.models.gold_rate import GoldRate
from app.models.silver_rate import SilverRate
from app.models.customer import Customer
from app.schemas.invoice import InvoiceCreate, InvoiceResponse
from app.services.calculation_service import CalculationService

router = APIRouter()

def generate_invoice_number(db: Session) -> str:
    # A simple generator for the prototype. In prod, we would use a sequence table.
    count = db.query(Invoice).count()
    return f"INV-{1000 + count + 1}"

@router.post("/", response_model=InvoiceResponse)
def create_sale(
    invoice_in: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a sale (invoice)."""
    store_id = require_tenant_id(current_user)
    # 1. Validate customer exists (if provided) — scoped to tenant
    if invoice_in.customer_id is not None:
        customer = db.query(Customer).filter(
            Customer.id == invoice_in.customer_id,
            Customer.store_id == store_id,
        ).first()
        if not customer:
            raise HTTPException(
                status_code=404,
                detail=f"Customer with id {invoice_in.customer_id} not found"
            )
    
    # 2. Validate tax calculation
    calculated_subtotal = sum(item.final_price for item in invoice_in.items)
    calculated_grand_total = calculated_subtotal + invoice_in.tax_amount - invoice_in.discount_amount
    
    # Allow small floating point differences (< 0.01)
    if abs(calculated_subtotal - invoice_in.subtotal) > 0.01:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid subtotal: expected {calculated_subtotal:.2f}, got {invoice_in.subtotal:.2f}"
        )
    
    if abs(calculated_grand_total - invoice_in.grand_total) > 0.01:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid grand_total: expected {calculated_grand_total:.2f}, got {invoice_in.grand_total:.2f}"
        )
    
    try:
        # 3. Create Invoice
        db_invoice = Invoice(
            customer_id=invoice_in.customer_id,
            invoice_number=generate_invoice_number(db),
            subtotal=invoice_in.subtotal,
            tax_amount=invoice_in.tax_amount,
            discount_amount=invoice_in.discount_amount,
            grand_total=invoice_in.grand_total,
            status=invoice_in.status,
            created_by=current_user.id,
            store_id=store_id,
        )
        db.add(db_invoice)
        db.flush() # Get ID
        
        # 4. Create Items
        for item_in in invoice_in.items:
            db_item = InvoiceItem(
                invoice_id=db_invoice.id,
                inventory_item_id=item_in.inventory_item_id,
                item_name=item_in.item_name,
                item_type=item_in.item_type,
                final_price=item_in.final_price
            )
            db.add(db_item)
            db.flush()
            
            # 5. Create Specific Calculations
            if item_in.gold_calculation:
                calc_in = item_in.gold_calculation
                
                # Validate gold calculation fields
                if calc_in.gross_weight <= 0:
                    raise HTTPException(status_code=400, detail="Gross weight must be positive")
                if calc_in.net_weight <= 0:
                    raise HTTPException(status_code=400, detail="Net weight must be positive")
                if calc_in.net_weight > calc_in.gross_weight:
                    raise HTTPException(status_code=400, detail="Net weight cannot exceed gross weight")
                
                # Fetch latest gold rate (optional, just for linking)
                latest_gold_rate = (
                    db.query(GoldRate)
                    .order_by(GoldRate.effective_datetime.desc())
                    .first()
                )
                metal_rate_val = Decimal(str(calc_in.applied_rate))
                
                touch_purity_val = Decimal(str(getattr(calc_in, 'touch_purity', 100.0) or 100.0))
                wastage_val = Decimal(str(getattr(calc_in, 'wastage', 0.0) or 0.0))
                
                # Use calculation service for selling calculation
                calc_result = CalculationService.calculate_selling(
                    net_weight=Decimal(str(calc_in.net_weight)),
                    metal_rate=metal_rate_val / Decimal('10'),
                    touch_purity=touch_purity_val,
                    wastage=wastage_val,
                    making_rate=Decimal(str(calc_in.making_charges_amount)),
                    making_type='FIXED',
                    hallmark=Decimal(str(calc_in.hallmark_charges)),
                    other=Decimal('0'),
                    discount=Decimal('0'),
                    gst_rate=Decimal('3')
                )
                
                db_gold = GoldCalculation(
                    invoice_item_id=db_item.id,
                    metal_rate_id=latest_gold_rate.id if latest_gold_rate else None,
                    applied_rate=float(metal_rate_val),
                    gross_weight=calc_in.gross_weight,
                    stone_weight=calc_in.stone_weight,
                    net_weight=calc_in.net_weight,
                    touch_purity=float(touch_purity_val),
                    wastage=float(wastage_val),
                    fine_weight=float(calc_result['fine_weight']),
                    making_charges_amount=float(calc_result['making_charge']),
                    hallmark_charges=calc_in.hallmark_charges,
                    total_gold_value=float(calc_result['metal_value'])
                )
                db.add(db_gold)
                
            elif item_in.silver_calculation:
                calc_in = item_in.silver_calculation
                
                # Validate silver calculation fields
                if calc_in.gross_weight <= 0:
                    raise HTTPException(status_code=400, detail="Gross weight must be positive")
                if calc_in.net_weight <= 0:
                    raise HTTPException(status_code=400, detail="Net weight must be positive")
                if calc_in.net_weight > calc_in.gross_weight:
                    raise HTTPException(status_code=400, detail="Net weight cannot exceed gross weight")
                
                # Fetch latest silver rate (optional, just for linking)
                latest_silver_rate = (
                    db.query(SilverRate)
                    .order_by(SilverRate.effective_datetime.desc())
                    .first()
                )
                metal_rate_val = Decimal(str(calc_in.applied_rate))
                
                touch_purity_val = Decimal(str(getattr(calc_in, 'tanch_percentage', 100.0) or 100.0))
                wastage_val = Decimal(str(getattr(calc_in, 'wastage', 0.0) or 0.0))
                
                # Use calculation service
                calc_result = CalculationService.calculate_selling(
                    net_weight=Decimal(str(calc_in.net_weight)),
                    metal_rate=metal_rate_val / Decimal('1000'),
                    touch_purity=touch_purity_val,
                    wastage=wastage_val,
                    making_rate=Decimal(str(calc_in.making_charges_amount)),
                    making_type='FIXED',
                    hallmark=Decimal('0'),
                    other=Decimal('0'),
                    discount=Decimal('0'),
                    gst_rate=Decimal('3')
                )
                
                pure_weight = float(calc_result['fine_weight'])
                tanch_percentage = float(touch_purity_val)
                
                db_silver = SilverCalculation(
                    invoice_item_id=db_item.id,
                    metal_rate_id=latest_silver_rate.id if latest_silver_rate else None,
                    applied_rate=float(metal_rate_val),
                    gross_weight=calc_in.gross_weight,
                    tanch_percentage=tanch_percentage,
                    pure_weight=pure_weight,
                    making_charges_amount=float(calc_result['making_charge']),
                    total_silver_value=float(calc_result['metal_value'])
                )
                db.add(db_silver)
            
            # 6. Mark StockItem as Sold if this was a scanned item (with row locking)
            if hasattr(item_in, "stock_item_id") and item_in.stock_item_id:
                from app.models.stock_item import StockItem
                stock_item = db.query(StockItem).filter(
                    StockItem.id == item_in.stock_item_id,
                    StockItem.store_id == store_id,
                ).with_for_update().first()
                if not stock_item:
                    raise HTTPException(status_code=404, detail=f"Stock item {item_in.stock_item_id} not found")
                if stock_item.status != "Available":
                    raise HTTPException(
                        status_code=400,
                        detail=f"Stock item '{stock_item.item_name or stock_item.item_code}' is already {stock_item.status}"
                    )
                stock_item.status = "Sold"
                
        db.commit()
        db.refresh(db_invoice)
        return db_invoice
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/", response_model=List[InvoiceResponse])
def list_sales(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all sales (invoices)."""
    store_id = require_tenant_id(current_user)
    invoices = db.query(Invoice).filter(
        Invoice.store_id == store_id,
    ).order_by(Invoice.id.desc()).offset(skip).limit(limit).all()
    return invoices

@router.get("/{id}", response_model=InvoiceResponse)
def get_sale(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific sale (invoice)."""
    store_id = require_tenant_id(current_user)
    invoice = db.query(Invoice).filter(
        Invoice.id == id,
        Invoice.store_id == store_id,
    ).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Sale not found")
    return invoice

from typing import Dict, Any

@router.patch("/{id}/customer", response_model=InvoiceResponse)
def link_customer_to_invoice(
    id: int,
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Link a customer to an existing invoice."""
    store_id = require_tenant_id(current_user)
    invoice = db.query(Invoice).filter(
        Invoice.id == id,
        Invoice.store_id == store_id,
    ).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
        
    customer_id = payload.get("customer_id")
    if not customer_id:
        raise HTTPException(status_code=400, detail="customer_id is required")
        
    customer = db.query(Customer).filter(
        Customer.id == customer_id,
        Customer.store_id == store_id,
    ).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
        
    invoice.customer_id = customer_id
    db.commit()
    db.refresh(invoice)
    return invoice