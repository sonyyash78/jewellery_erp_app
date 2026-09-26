from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal
from datetime import date, datetime

from app.api.dependencies import require_tenant_id, get_db, get_current_user
from app.models.user import User
from app.models.invoice import Invoice, InvoiceStatus
from app.models.invoice_item import InvoiceItem
from app.models.gold_calculation import GoldCalculation
from app.models.silver_calculation import SilverCalculation
from app.models.gold_rate import GoldRate
from app.models.silver_rate import SilverRate
from app.models.customer import Customer
from app.models.customer_ledger import CustomerLedger
from app.schemas.invoice import InvoiceCreate, InvoiceResponse, GoldCalcCreate, SilverCalcCreate
from app.services.calculation_service import CalculationService
from app.services.invoice_pdf_service import InvoicePDFService

router = APIRouter()

def generate_invoice_number(db: Session, store_id: int = 1) -> str:
    """
    Generate unique invoice number.
    Format: INV-YYYYMMDD-XXXX for store 1, or INV-S{store_id}-YYYYMMDD-XXXX for other stores.
    Guaranteed unique across database.
    """
    today = datetime.now().strftime('%Y%m%d')
    prefix = f"INV-{today}" if store_id == 1 else f"INV-S{store_id}-{today}"
    
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    count = db.query(Invoice).filter(
        Invoice.store_id == store_id,
        Invoice.invoice_date >= today_start
    ).count() + 1
    
    candidate = f"{prefix}-{str(count).zfill(4)}"
    while db.query(Invoice).filter(Invoice.invoice_number == candidate).first():
        count += 1
        candidate = f"{prefix}-{str(count).zfill(4)}"
        
    return candidate

@router.post("/", response_model=InvoiceResponse)
def create_invoice(
    invoice_in: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    store_id = require_tenant_id(current_user)
    # 1. Validate customer exists if provided
    if invoice_in.customer_id is not None:
        customer = db.query(Customer).filter(Customer.id == invoice_in.customer_id, Customer.store_id == store_id).first()
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
    
    # Allow up to 1.0 difference for round off
    if abs(calculated_grand_total - invoice_in.grand_total) > 1.0:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid grand_total: expected {calculated_grand_total:.2f}, got {invoice_in.grand_total:.2f}"
        )
    
    # 2.5 Lock and validate all StockItems upfront (atomic concurrency protection)
    from app.models.stock_item import StockItem
    stock_ids = [item.stock_item_id for item in invoice_in.items if hasattr(item, 'stock_item_id') and item.stock_item_id is not None]
    stock_items_map = {}
    if stock_ids:
        stock_items = db.query(StockItem).filter(
            StockItem.id.in_(stock_ids),
            StockItem.store_id == store_id
        ).with_for_update().all()
        if len(stock_items) != len(set(stock_ids)):
            raise HTTPException(status_code=404, detail="One or more stock items not found")
        for si in stock_items:
            if si.status != "Available":
                raise HTTPException(
                    status_code=400,
                    detail=f"Stock item '{si.item_name or si.item_code}' is already {si.status}"
                )
            stock_items_map[si.id] = si

    try:
        # 3. Create Invoice
        db_invoice = Invoice(
            store_id=store_id,
            customer_id=invoice_in.customer_id,
            invoice_number=generate_invoice_number(db, store_id),
            subtotal=invoice_in.subtotal,
            tax_amount=invoice_in.tax_amount,
            discount_amount=invoice_in.discount_amount,
            grand_total=invoice_in.grand_total,
            
            bill_type=invoice_in.bill_type,
            settlement_type=invoice_in.settlement_type,
            settlement_metal_type=invoice_in.settlement_metal_type,
            metal_received_value=invoice_in.metal_received_value,
            metal_received_str=invoice_in.metal_received_str,
            cash_received=invoice_in.cash_received,
            balance_amount=invoice_in.balance_amount,
            balance_metal_weight=invoice_in.balance_metal_weight,
            gold_balance_metal_weight=invoice_in.gold_balance_metal_weight,
            silver_balance_metal_weight=invoice_in.silver_balance_metal_weight,
            
            status=invoice_in.status,
            created_by=current_user.id
        )
        db.add(db_invoice)
        db.flush() # Get ID
        
        # 4. Create Items
        total_fine_gold = 0.0
        total_fine_silver = 0.0
        
        for item_in in invoice_in.items:
            db_item = InvoiceItem(
                invoice_id=db_invoice.id,
                inventory_item_id=item_in.inventory_item_id,
                stock_item_id=getattr(item_in, 'stock_item_id', None),
                item_name=item_in.item_name,
                item_type=item_in.item_type,
                final_price=item_in.final_price
            )
            db.add(db_item)
            db.flush()
            
            # 5. Create Specific Calculations using CalculationService
            if item_in.gold_calculation:
                calc_in = item_in.gold_calculation
                
                # Validate gold calculation fields
                if calc_in.gross_weight < 0:
                    raise HTTPException(
                        status_code=400,
                        detail="Gross weight cannot be negative"
                    )
                if calc_in.net_weight < 0:
                    raise HTTPException(
                        status_code=400,
                        detail="Net weight cannot be negative"
                    )
                if calc_in.net_weight > calc_in.gross_weight:
                    raise HTTPException(
                        status_code=400,
                        detail="Net weight cannot exceed gross weight"
                    )
                if calc_in.stone_weight < 0:
                    calc_in.stone_weight = 0.0
                
                # Use calculation service for selling calculation
                calc_result = CalculationService.calculate_selling(
                    net_weight=Decimal(str(calc_in.net_weight)),
                    metal_rate=Decimal(str(calc_in.applied_rate)) / Decimal('10'),
                    touch_purity=Decimal(str(calc_in.touch_purity)),
                    wastage=Decimal(str(calc_in.wastage)),
                    making_rate=Decimal(str(calc_in.making_charges_amount)),
                    making_type='FIXED',
                    hallmark=Decimal(str(calc_in.hallmark_charges)),
                    other=Decimal(str(calc_in.other_charges)),
                    discount=Decimal(str(calc_in.discount)),
                    gst_rate=Decimal('3')
                )
                
                db_gold = GoldCalculation(
                    invoice_item_id=db_item.id,
                    metal_rate_id=calc_in.metal_rate_id,
                    applied_rate=calc_in.applied_rate,
                    gross_weight=calc_in.gross_weight,
                    stone_weight=calc_in.stone_weight,
                    net_weight=calc_in.net_weight,
                    touch_purity=calc_in.touch_purity,
                    wastage=calc_in.wastage,
                    fine_weight=float(calc_result['fine_weight']),
                    making_charges_amount=float(calc_result['making_charge']),
                    hallmark_charges=calc_in.hallmark_charges,
                    other_charges=calc_in.other_charges,
                    discount=calc_in.discount,
                    total_gold_value=float(calc_result['metal_value'])
                )
                db.add(db_gold)
                
                if calc_in.applied_rate == 0:
                    if item_in.item_name and "deposit" in item_in.item_name.lower():
                        total_fine_gold -= float(calc_result['fine_weight'])
                    else:
                        total_fine_gold += float(calc_result['fine_weight'])
                
            elif item_in.silver_calculation:
                calc_in = item_in.silver_calculation
                
                # Validate silver calculation fields
                if calc_in.gross_weight < 0:
                    raise HTTPException(
                        status_code=400,
                        detail="Gross weight cannot be negative"
                    )
                
                # Use calculation service
                calc_result = CalculationService.calculate_selling(
                    net_weight=Decimal(str(calc_in.gross_weight - (calc_in.stone_weight or 0))),
                    metal_rate=Decimal(str(calc_in.applied_rate)) / Decimal('1000'),
                    touch_purity=Decimal(str(calc_in.tanch_percentage)),
                    wastage=Decimal(str(calc_in.wastage)),
                    making_rate=Decimal(str(calc_in.making_charges_amount)),
                    making_type='FIXED',
                    hallmark=Decimal('0'),
                    other=Decimal(str(calc_in.other_charges)),
                    discount=Decimal(str(calc_in.discount)),
                    gst_rate=Decimal('3')
                )
                
                db_silver = SilverCalculation(
                    invoice_item_id=db_item.id,
                    metal_rate_id=calc_in.metal_rate_id,
                    applied_rate=calc_in.applied_rate,
                    gross_weight=calc_in.gross_weight,
                    stone_weight=calc_in.stone_weight,
                    tanch_percentage=calc_in.tanch_percentage,
                    wastage=calc_in.wastage,
                    pure_weight=float(calc_result['fine_weight']),
                    making_charges_amount=float(calc_result['making_charge']),
                    other_charges=calc_in.other_charges,
                    discount=calc_in.discount,
                    total_silver_value=float(calc_result['metal_value'])
                )
                db.add(db_silver)
                
                if calc_in.applied_rate == 0:
                    if item_in.item_name and "deposit" in item_in.item_name.lower():
                        total_fine_silver -= float(calc_result['fine_weight'])
                    else:
                        total_fine_silver += float(calc_result['fine_weight'])
            
            # 6. Mark StockItem as Sold if this was a scanned item
            if hasattr(item_in, 'stock_item_id') and item_in.stock_item_id:
                stock_item = stock_items_map.get(item_in.stock_item_id)
                if stock_item:
                    stock_item.status = "Sold"

        # 7. Update Customer Ledger if Customer is provided
        if invoice_in.customer_id and customer:
            # Accumulate any metal that was sold 'unfixed' (applied_rate == 0)
            base_gold_change = total_fine_gold
            base_silver_change = total_fine_silver
            
            debit_amount = float(invoice_in.grand_total)
            credit_amount = float(invoice_in.cash_received + invoice_in.metal_received_value)
            balance_amt = float(invoice_in.balance_amount)
            balance_weight = float(invoice_in.balance_metal_weight)
            
            # Unified Ledger Logic
            # Final cash due to be added to Udhar
            new_balance = float(customer.outstanding_balance or 0) + balance_amt
            
            # Additional metal to be added to Metal Udhar
            gold_bal = float(invoice_in.gold_balance_metal_weight)
            silver_bal = float(invoice_in.silver_balance_metal_weight)
            
            base_gold_change += gold_bal
            base_silver_change += silver_bal
            
            customer.fine_gold_balance = float(customer.fine_gold_balance or 0) + base_gold_change
            customer.fine_silver_balance = float(customer.fine_silver_balance or 0) + base_silver_change
            customer.outstanding_balance = new_balance
            
            total_gold_received = 0.0
            total_silver_received = 0.0
            for item in invoice_in.items:
                if item.gold_calculation and item.item_name and "deposit" in item.item_name.lower():
                    total_gold_received += item.gold_calculation.fine_weight
                elif item.silver_calculation and item.item_name and "deposit" in item.item_name.lower():
                    total_silver_received += item.silver_calculation.pure_weight
            
            # The actual credit applied to the bill is Total - CashDue
            # Because anything NOT in CashDue was either paid in cash, paid in old metal, or converted to a metal loan!
            actual_credit = debit_amount - balance_amt
            if actual_credit < 0: actual_credit = 0.0
            
            # Gross metal tracking:
            # Credit is the metal they gave. Debit is what they gave + net change.
            actual_gold_credit = total_gold_received
            actual_gold_debit = max(0.0, total_gold_received + base_gold_change)
            
            actual_silver_credit = total_silver_received
            actual_silver_debit = max(0.0, total_silver_received + base_silver_change)
            
            settlement_desc = 'Cash'
            if invoice_in.settlement_type == 'Metal' or invoice_in.settlement_type == 'Hybrid':
                settlement_desc = 'Metal/Hybrid'
                
            ledger_entry = CustomerLedger(
                customer_id=customer.id,
                voucher_type='Invoice',
                voucher_number=db_invoice.invoice_number,
                description=f'Bill {db_invoice.invoice_number} ({settlement_desc})',
                debit=debit_amount,
                credit=actual_credit,
                balance=new_balance,
                
                gold_debit=actual_gold_debit,
                gold_credit=actual_gold_credit,
                gold_balance=customer.fine_gold_balance,
                
                silver_debit=actual_silver_debit,
                silver_credit=actual_silver_credit,
                silver_balance=customer.fine_silver_balance
            )
            db.add(ledger_entry)

        # Commit everything atomically in a single transaction
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
def list_invoices(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    customer_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List invoices with search, filter, and pagination.
    
    - search: Search by invoice number or customer name
    - status: Filter by status (Draft, Paid, Cancelled)
    - start_date: Filter from date
    - end_date: Filter to date
    - customer_id: Filter by customer
    """
    store_id = require_tenant_id(current_user)
    query = db.query(Invoice).filter(Invoice.store_id == store_id)
    
    # Search filter
    if search:
        query = query.join(Customer).filter(
            (Invoice.invoice_number.ilike(f"%{search}%")) |
            (Customer.first_name.ilike(f"%{search}%")) |
            (Customer.last_name.ilike(f"%{search}%"))
        )
    
    # Status filter
    if status:
        query = query.filter(Invoice.status == status)
    
    # Date range filter
    if start_date:
        query = query.filter(Invoice.invoice_date >= start_date)
    if end_date:
        query = query.filter(Invoice.invoice_date <= end_date)
    
    # Customer filter
    if customer_id:
        query = query.filter(Invoice.customer_id == customer_id)
    
    # Get total count
    total = query.count()
    
    # Apply pagination and order
    invoices = query.order_by(Invoice.invoice_date.desc()).offset(skip).limit(limit).all()
    
    return invoices

@router.get("/{id}", response_model=InvoiceResponse)
def get_invoice(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get single invoice by ID with all details."""
    store_id = require_tenant_id(current_user)
    invoice = db.query(Invoice).filter(Invoice.id == id, Invoice.store_id == store_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice

@router.delete("/{id}")
def delete_invoice(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete invoice (cancel with reversal of inventory, customer balances, and ledger)."""
    store_id = require_tenant_id(current_user)
    invoice = db.query(Invoice).filter(Invoice.id == id, Invoice.store_id == store_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    if invoice.status == InvoiceStatus.CANCELLED:
        raise HTTPException(status_code=400, detail="Invoice is already cancelled")
    
    try:
        # 1. Restore Stock Items to Available
        from app.models.stock_item import StockItem
        for item in invoice.items:
            stock_id = getattr(item, 'stock_item_id', None)
            if stock_id:
                stock_item = db.query(StockItem).filter(
                    StockItem.id == stock_id,
                    StockItem.store_id == store_id
                ).first()
                if stock_item and stock_item.status == "Sold":
                    stock_item.status = "Available"
        
        # 2. Reverse Customer Ledger and Balance if applicable
        if invoice.customer_id:
            customer = db.query(Customer).filter(
                Customer.id == invoice.customer_id,
                Customer.store_id == store_id
            ).first()
            if customer:
                # Find original invoice ledger entry
                orig_ledger = db.query(CustomerLedger).filter(
                    CustomerLedger.customer_id == customer.id,
                    CustomerLedger.voucher_number == invoice.invoice_number
                ).order_by(CustomerLedger.id.desc()).first()
                
                if orig_ledger:
                    net_cash = float(orig_ledger.debit or 0.0) - float(orig_ledger.credit or 0.0)
                    net_gold = float(orig_ledger.gold_debit or 0.0) - float(orig_ledger.gold_credit or 0.0)
                    net_silver = float(orig_ledger.silver_debit or 0.0) - float(orig_ledger.silver_credit or 0.0)
                else:
                    net_cash = float(invoice.balance_amount or 0.0)
                    net_gold = float(invoice.gold_balance_metal_weight or 0.0)
                    net_silver = float(invoice.silver_balance_metal_weight or 0.0)
                
                customer.outstanding_balance = float(customer.outstanding_balance or 0.0) - net_cash
                customer.fine_gold_balance = float(customer.fine_gold_balance or 0.0) - net_gold
                customer.fine_silver_balance = float(customer.fine_silver_balance or 0.0) - net_silver
                
                # Create reversal ledger entry
                reversal = CustomerLedger(
                    customer_id=customer.id,
                    voucher_type="Cancellation",
                    voucher_number=f"REV-{invoice.invoice_number}",
                    description=f"Cancellation reversal of Invoice {invoice.invoice_number}",
                    debit=float(orig_ledger.credit or 0.0) if orig_ledger else 0.0,
                    credit=float(orig_ledger.debit or 0.0) if orig_ledger else net_cash,
                    balance=customer.outstanding_balance,
                    gold_debit=float(orig_ledger.gold_credit or 0.0) if orig_ledger else 0.0,
                    gold_credit=float(orig_ledger.gold_debit or 0.0) if orig_ledger else net_gold,
                    gold_balance=customer.fine_gold_balance,
                    silver_debit=float(orig_ledger.silver_credit or 0.0) if orig_ledger else 0.0,
                    silver_credit=float(orig_ledger.silver_debit or 0.0) if orig_ledger else net_silver,
                    silver_balance=customer.fine_silver_balance
                )
                db.add(reversal)
        
        # 3. Mark status as Cancelled
        invoice.status = InvoiceStatus.CANCELLED
        db.commit()
        return {"message": "Invoice cancelled and reversed successfully"}
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to cancel invoice")

from pydantic import BaseModel
class LinkCustomerRequest(BaseModel):
    customer_id: int

@router.patch("/{id}/customer", response_model=InvoiceResponse)
def link_customer_to_invoice(
    id: int,
    req: LinkCustomerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Link an existing invoice to a customer."""
    store_id = require_tenant_id(current_user)
    invoice = db.query(Invoice).filter(Invoice.id == id, Invoice.store_id == store_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
        
    customer = db.query(Customer).filter(Customer.id == req.customer_id, Customer.store_id == store_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer with id {req.customer_id} not found")
        
    invoice.customer_id = req.customer_id
    db.commit()
    db.refresh(invoice)
    return invoice

@router.get("/stats/summary")
def get_invoice_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get invoice statistics for dashboard."""
    from sqlalchemy import func
    store_id = require_tenant_id(current_user)
    
    total_invoices = db.query(Invoice).filter(Invoice.store_id == store_id).count()
    total_paid = db.query(Invoice).filter(Invoice.store_id == store_id, Invoice.status == InvoiceStatus.PAID).count()
    total_draft = db.query(Invoice).filter(Invoice.store_id == store_id, Invoice.status == InvoiceStatus.DRAFT).count()
    
    total_revenue = db.query(func.sum(Invoice.grand_total)).filter(
        Invoice.store_id == store_id,
        Invoice.status == InvoiceStatus.PAID
    ).scalar() or 0
    
    return {
        "total_invoices": total_invoices,
        "total_paid": total_paid,
        "total_draft": total_draft,
        "total_revenue": float(total_revenue)
    }

@router.get("/{id}/pdf-data")
def get_invoice_pdf_data(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get invoice data formatted for PDF generation."""
    store_id = require_tenant_id(current_user)
    invoice = db.query(Invoice).filter(Invoice.id == id, Invoice.store_id == store_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    try:
        return InvoicePDFService.get_invoice_pdf_data(id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/pdf-by-voucher/{voucher_number}")
def get_pdf_data_by_voucher(
    voucher_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get pdf data using just the voucher string."""
    store_id = require_tenant_id(current_user)
    try:
        # If it's a payment row, try to extract the base bill number
        base_voucher = voucher_number
        if base_voucher.startswith("PAY-"):
            base_voucher = base_voucher[4:]
            
        if base_voucher.startswith("INV-"):
            invoice = db.query(Invoice).filter(Invoice.invoice_number == base_voucher, Invoice.store_id == store_id).first()
            if not invoice:
                raise ValueError(f"Invoice {base_voucher} not found")
            return InvoicePDFService.get_invoice_pdf_data(invoice.id, db)
            
        elif base_voucher.startswith("EXC-"):
            exchange_id = int(base_voucher.split("-")[1])
            from app.models.exchange import Exchange
            exchange = db.query(Exchange).filter(Exchange.id == exchange_id, Exchange.store_id == store_id).first()
            if not exchange:
                raise ValueError(f"Exchange {base_voucher} not found")
            return InvoicePDFService.get_exchange_pdf_data(exchange_id, db)
            
        elif base_voucher.startswith("PUR-"):
            from app.models.purchase import Purchase
            purchase = db.query(Purchase).filter(Purchase.purchase_number == base_voucher, Purchase.store_id == store_id).first()
            if not purchase:
                raise ValueError(f"Purchase {base_voucher} not found")
            return InvoicePDFService.get_purchase_pdf_data(purchase.id, db)
            
        else:
            raise ValueError(f"No PDF available for voucher type: {base_voucher}")
            
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
