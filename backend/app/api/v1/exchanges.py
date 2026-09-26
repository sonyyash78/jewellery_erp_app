from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from app.api.dependencies import require_tenant_id, get_db, get_current_user
from app.models.user import User
from app.models.exchange import Exchange
from app.models.exchange_item import ExchangeItem
from app.models.exchange_new_item import ExchangeNewItem
from app.models.stock_item import StockItem
from app.models.customer import Customer
from app.models.customer_ledger import CustomerLedger
from app.schemas.exchange import ExchangeCreate, ExchangeResponse
import logging

router = APIRouter()

@router.post("/", response_model=ExchangeResponse)
def create_exchange(
    exchange_in: ExchangeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    store_id = require_tenant_id(current_user)
    # Verify customer
    customer = db.query(Customer).filter(Customer.id == exchange_in.customer_id, Customer.store_id == store_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Verify stock items (only for items that came from inventory, not manual entries)
    stock_ids = [item.stock_item_id for item in exchange_in.new_items if item.stock_item_id is not None]
    stock_items = db.query(StockItem).filter(StockItem.id.in_(stock_ids), StockItem.store_id == store_id).with_for_update().all() if stock_ids else []
    if len(stock_items) != len(stock_ids):
        raise HTTPException(status_code=400, detail="One or more stock items not found")
        
    for item in stock_items:
        if item.status.lower() == 'sold':
            raise HTTPException(status_code=400, detail=f"Stock item {item.item_code} is already sold")

    import secrets
    v_token = secrets.token_hex(6).upper()

    # Create Exchange
    exchange = Exchange(
        store_id=store_id,
        customer_id=exchange_in.customer_id,
        total_old_value=exchange_in.total_old_value,
        total_new_value=exchange_in.total_new_value,
        gst_amount=exchange_in.gst_amount,
        grand_total=exchange_in.grand_total,
        difference_amount=exchange_in.difference_amount,
        amount_paid=float(getattr(exchange_in, 'amount_paid', 0.0) or 0.0),
        balance_amount=float(getattr(exchange_in, 'balance_amount', 0.0) or 0.0),
        settlement_type=getattr(exchange_in, 'settlement_type', 'Cash') or "Cash",
        gold_balance_metal_weight=float(getattr(exchange_in, 'gold_balance_metal_weight', 0.0) or 0.0),
        silver_balance_metal_weight=float(getattr(exchange_in, 'silver_balance_metal_weight', 0.0) or 0.0),
        status="Completed",
        verification_token=v_token
    )
    db.add(exchange)
    db.flush() # get ID

    base_gold_change = 0.0
    base_silver_change = 0.0

    # Old items (credit customer)
    for old_item_in in exchange_in.old_items:
        old_item = ExchangeItem(
            exchange_id=exchange.id,
            metal=old_item_in.metal,
            item_name=old_item_in.item_name,
            purity=old_item_in.purity,
            touch=old_item_in.touch,
            gross_weight=old_item_in.gross_weight,
            stone_weight=old_item_in.stone_weight,
            net_weight=old_item_in.net_weight,
            wastage=old_item_in.wastage,
            fine_weight=old_item_in.fine_weight,
            labour_charge=old_item_in.labour_charge,
            testing_melting_charge=old_item_in.testing_melting_charge,
            hallmark_charge=old_item_in.hallmark_charge,
            other_charges=old_item_in.other_charges,
            discount=old_item_in.discount,
            rate_applied=old_item_in.rate_applied,
            calculated_value=old_item_in.calculated_value
        )
        db.add(old_item)
        if old_item_in.rate_applied == 0:
            if old_item_in.metal.lower() == 'gold':
                base_gold_change -= float(old_item_in.fine_weight)
            elif old_item_in.metal.lower() == 'silver':
                base_silver_change -= float(old_item_in.fine_weight)

    # New items (debit customer)
    for new_item_in in exchange_in.new_items:
        new_item = ExchangeNewItem(
            exchange_id=exchange.id,
            metal=new_item_in.metal,
            item_name=new_item_in.item_name,
            stock_item_id=new_item_in.stock_item_id,
            gross_weight=new_item_in.gross_weight,
            stone_weight=new_item_in.stone_weight,
            net_weight=new_item_in.net_weight,
            touch_purity=new_item_in.touch_purity,
            wastage=new_item_in.wastage,
            fine_weight=new_item_in.fine_weight,
            making_charge_type=new_item_in.making_charge_type,
            making_charge_rate=new_item_in.making_charge_rate,
            making_charges_amount=new_item_in.making_charges_amount,
            hallmark_charges=new_item_in.hallmark_charges,
            other_charges=new_item_in.other_charges,
            discount=new_item_in.discount,
            rate_applied=new_item_in.rate_applied,
            final_price=new_item_in.final_price
        )
        db.add(new_item)
        if new_item_in.stock_item_id:
            stock = next((s for s in stock_items if s.id == new_item_in.stock_item_id), None)
            if stock:
                stock.status = "Sold"
        if new_item_in.rate_applied == 0:
            if new_item_in.metal.lower() == 'gold':
                base_gold_change += float(new_item_in.fine_weight)
            elif new_item_in.metal.lower() == 'silver':
                base_silver_change += float(new_item_in.fine_weight)

    # Now apply the user's chosen settlement type for the remaining balance
    balance_amt = float(exchange_in.balance_amount)
    
    debit_amount = float(exchange_in.difference_amount) if exchange_in.difference_amount > 0 else 0
    credit_amount = abs(float(exchange_in.difference_amount)) if exchange_in.difference_amount < 0 else 0
    
    if exchange_in.amount_paid:
        if exchange_in.amount_paid > 0:
            credit_amount += float(exchange_in.amount_paid)
        else:
            debit_amount += abs(float(exchange_in.amount_paid))

    if exchange_in.settlement_type == 'Metal' or exchange_in.settlement_type == 'Hybrid':
        # Apply the metal conversion to the ledger
        base_gold_change += float(exchange_in.gold_balance_metal_weight)
        base_silver_change += float(exchange_in.silver_balance_metal_weight)
            
        # The cash ledger is impacted by the remaining balance_amount (hybrid cash portion)
        new_balance = float(customer.outstanding_balance or 0) + balance_amt
        
        customer.fine_gold_balance = float(customer.fine_gold_balance or 0) + base_gold_change
        customer.fine_silver_balance = float(customer.fine_silver_balance or 0) + base_silver_change
        customer.outstanding_balance = new_balance
        
        ledger_entry = CustomerLedger(
            customer_id=customer.id,
            voucher_type="Exchange",
            voucher_number=f"EXC-{exchange.id}",
            description=f'Hybrid Exchange {exchange.id} (Settled in Metal)',
            debit=debit_amount,
            credit=debit_amount if balance_amt == 0 else (debit_amount - balance_amt),
            balance=new_balance,
            
            gold_debit=base_gold_change if base_gold_change > 0 else 0.0,
            gold_credit=abs(base_gold_change) if base_gold_change < 0 else 0.0,
            gold_balance=customer.fine_gold_balance,
            
            silver_debit=base_silver_change if base_silver_change > 0 else 0.0,
            silver_credit=abs(base_silver_change) if base_silver_change < 0 else 0.0,
            silver_balance=customer.fine_silver_balance
        )
        db.add(ledger_entry)

    else:
        # Settlement in Cash
        new_balance = float(customer.outstanding_balance or 0) + balance_amt
        
        customer.fine_gold_balance = float(customer.fine_gold_balance or 0) + base_gold_change
        customer.fine_silver_balance = float(customer.fine_silver_balance or 0) + base_silver_change
        customer.outstanding_balance = new_balance
        
        ledger_entry = CustomerLedger(
            customer_id=customer.id,
            voucher_type="Exchange",
            voucher_number=f"EXC-{exchange.id}",
            description=f'Exchange {exchange.id} (Settled in Cash)',
            debit=debit_amount,
            credit=credit_amount,
            balance=new_balance,
            
            gold_debit=base_gold_change if base_gold_change > 0 else 0.0,
            gold_credit=abs(base_gold_change) if base_gold_change < 0 else 0.0,
            gold_balance=customer.fine_gold_balance,
            
            silver_debit=base_silver_change if base_silver_change > 0 else 0.0,
            silver_credit=abs(base_silver_change) if base_silver_change < 0 else 0.0,
            silver_balance=customer.fine_silver_balance
        )
        db.add(ledger_entry)
        
    db.commit()

    db.commit()
    db.refresh(exchange)
    return exchange

@router.get("/", response_model=Dict[str, Any])
def list_exchanges(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    store_id = require_tenant_id(current_user)
    query = db.query(Exchange).filter(Exchange.store_id == store_id)
    total = query.count()
    items = query.order_by(Exchange.id.desc()).offset(skip).limit(limit).all()
    
    results = []
    for e in items:
        results.append({
            "id": e.id,
            "invoice_number": f"EXC-{e.id}",
            "invoice_date": e.exchange_date,
            "grand_total": e.total_new_value if e.total_new_value > 0 else e.total_old_value,
            "status": "Completed",
            "has_new_items": e.total_new_value > 0,
            "has_old_items": e.total_old_value > 0,
            "customer": {
                "first_name": e.customer.first_name if e.customer else 'Unknown',
                "last_name": e.customer.last_name if e.customer else '',
                "phone_number": e.customer.phone_number if e.customer else ''
            }
        })
    
    return {"total": total, "items": results}

@router.get("/{id}/pdf-data")
def get_exchange_pdf_data(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get exchange data formatted for PDF generation."""
    store_id = require_tenant_id(current_user)
    exchange = db.query(Exchange).filter(Exchange.id == id, Exchange.store_id == store_id).first()
    if not exchange:
        raise HTTPException(status_code=404, detail="Exchange not found")
    try:
        from app.services.invoice_pdf_service import InvoicePDFService
        return InvoicePDFService.get_exchange_pdf_data(id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{id}")
def get_exchange(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a single exchange formatted for the Invoice View Modal."""
    store_id = require_tenant_id(current_user)
    exchange = db.query(Exchange).filter(Exchange.id == id, Exchange.store_id == store_id).first()
    if not exchange:
        raise HTTPException(status_code=404, detail="Exchange not found")
        
    items = []
    # Old items
    for item in exchange.old_items:
        items.append({
            "item_name": f"(OLD) {item.item_name}",
            "item_type": item.metal,
            "final_price": item.calculated_value
        })
    # New items
    for item in exchange.new_items:
        items.append({
            "item_name": item.item_name,
            "item_type": item.metal,
            "final_price": item.final_price
        })

    return {
        "id": exchange.id,
        "invoice_number": f"EXC-{exchange.id}",
        "customer": {
            "first_name": exchange.customer.first_name if exchange.customer else "Unknown",
            "last_name": exchange.customer.last_name if exchange.customer else "",
            "phone_number": exchange.customer.phone_number if exchange.customer else ""
        },
        "items": items,
        "subtotal": exchange.total_new_value,
        "tax_amount": exchange.gst_amount,
        "discount_amount": exchange.total_old_value,
        "grand_total": exchange.difference_amount
    }

@router.delete("/{id}")
def delete_exchange(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel exchange with reversal of inventory, customer balances, and ledger."""
    store_id = require_tenant_id(current_user)
    exchange = db.query(Exchange).filter(Exchange.id == id, Exchange.store_id == store_id).first()
    if not exchange:
        raise HTTPException(status_code=404, detail="Exchange not found")
        
    if getattr(exchange, 'status', None) == "Cancelled":
        raise HTTPException(status_code=400, detail="Exchange is already cancelled")

    try:
        from app.models.stock_item import StockItem
        from app.models.customer import Customer
        from app.models.customer_ledger import CustomerLedger

        # 1. Restore Stock Items to Available
        for new_item in exchange.new_items:
            if new_item.stock_item_id:
                stock = db.query(StockItem).filter(
                    StockItem.id == new_item.stock_item_id,
                    StockItem.store_id == store_id
                ).first()
                if stock and stock.status == "Sold":
                    stock.status = "Available"

        # 2. Reverse Customer Ledger and Balance
        if exchange.customer_id:
            customer = db.query(Customer).filter(
                Customer.id == exchange.customer_id,
                Customer.store_id == store_id
            ).first()
            if customer:
                orig_ledger = db.query(CustomerLedger).filter(
                    CustomerLedger.customer_id == customer.id,
                    CustomerLedger.voucher_number == f"EXC-{exchange.id}"
                ).order_by(CustomerLedger.id.desc()).first()

                if orig_ledger:
                    net_cash = float(orig_ledger.debit or 0.0) - float(orig_ledger.credit or 0.0)
                    net_gold = float(orig_ledger.gold_debit or 0.0) - float(orig_ledger.gold_credit or 0.0)
                    net_silver = float(orig_ledger.silver_debit or 0.0) - float(orig_ledger.silver_credit or 0.0)
                else:
                    net_cash = float(exchange.difference_amount or exchange.balance_amount or 0.0)
                    net_gold = float(exchange.gold_balance_metal_weight or 0.0)
                    net_silver = float(exchange.silver_balance_metal_weight or 0.0)

                customer.outstanding_balance = float(customer.outstanding_balance or 0.0) - net_cash
                customer.fine_gold_balance = float(customer.fine_gold_balance or 0.0) - net_gold
                customer.fine_silver_balance = float(customer.fine_silver_balance or 0.0) - net_silver

                reversal = CustomerLedger(
                    customer_id=customer.id,
                    voucher_type="Cancellation",
                    voucher_number=f"REV-EXC-{exchange.id}",
                    description=f"Cancellation reversal of Exchange EXC-{exchange.id}",
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

        exchange.status = "Cancelled"
        db.commit()
        return {"message": "Exchange cancelled and reversed successfully"}
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to cancel exchange")
