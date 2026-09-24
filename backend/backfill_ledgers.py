import os
import sys
from decimal import Decimal
from sqlalchemy.orm import Session

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.models.customer_ledger import CustomerLedger
from app.models.invoice import Invoice
from app.models.exchange import Exchange
from app.models.purchase import Purchase
from app.models.supplier_ledger import SupplierLedger
from app.models.customer import Customer
from app.models.seller import Seller

def backfill():
    db = SessionLocal()
    try:
        print("Backfilling Invoices...")
        invoices = db.query(Invoice).all()
        for inv in invoices:
            total_fine_gold = 0.0
            total_fine_silver = 0.0
            for item in inv.items:
                if item.gold_calculation:
                    total_fine_gold += float(item.gold_calculation.fine_weight)
                if item.silver_calculation:
                    total_fine_silver += float(item.silver_calculation.pure_weight)
            
            if total_fine_gold > 0 or total_fine_silver > 0:
                # Update ledger entry for this invoice
                ledgers = db.query(CustomerLedger).filter(
                    CustomerLedger.voucher_type == 'Invoice',
                    CustomerLedger.voucher_number == inv.invoice_number
                ).all()
                for ledger in ledgers:
                    ledger.gold_debit = total_fine_gold
                    ledger.silver_debit = total_fine_silver
                    
        print("Backfilling Exchanges...")
        exchanges = db.query(Exchange).all()
        for exc in exchanges:
            gold_credit = 0.0
            silver_credit = 0.0
            for old_item in exc.old_items:
                if old_item.metal.lower() == 'gold':
                    gold_credit += float(old_item.fine_weight)
                elif old_item.metal.lower() == 'silver':
                    silver_credit += float(old_item.fine_weight)
                    
            gold_debit = 0.0
            silver_debit = 0.0
            for new_item in exc.new_items:
                if new_item.metal.lower() == 'gold':
                    gold_debit += float(new_item.fine_weight)
                elif new_item.metal.lower() == 'silver':
                    silver_debit += float(new_item.fine_weight)
            
            if gold_credit > 0 or silver_credit > 0 or gold_debit > 0 or silver_debit > 0:
                ledgers = db.query(CustomerLedger).filter(
                    CustomerLedger.voucher_type == 'Exchange',
                    CustomerLedger.voucher_number == f"EXC-{exc.id}"
                ).all()
                for ledger in ledgers:
                    ledger.gold_debit = gold_debit
                    ledger.gold_credit = gold_credit
                    ledger.silver_debit = silver_debit
                    ledger.silver_credit = silver_credit
                    
        print("Backfilling Purchases...")
        purchases = db.query(Purchase).all()
        for pur in purchases:
            total_gold_credit = 0.0
            total_silver_credit = 0.0
            for item in pur.items:
                if item.metal_type.lower() == 'gold':
                    total_gold_credit += float(item.fine_weight)
                elif item.metal_type.lower() == 'silver':
                    total_silver_credit += float(item.fine_weight)
            
            if total_gold_credit > 0 or total_silver_credit > 0:
                ledgers = db.query(SupplierLedger).filter(
                    SupplierLedger.voucher_type == 'Purchase',
                    SupplierLedger.voucher_number == pur.purchase_number
                ).all()
                for ledger in ledgers:
                    ledger.gold_credit = total_gold_credit
                    ledger.silver_credit = total_silver_credit

        db.commit()
        
        # Now recalculate running balances for all ledgers
        print("Recalculating Customer Ledger Balances...")
        customers = db.query(Customer).all()
        for customer in customers:
            ledgers = db.query(CustomerLedger).filter(
                CustomerLedger.customer_id == customer.id
            ).order_by(CustomerLedger.date.asc(), CustomerLedger.id.asc()).all()
            
            running_rupees = 0.0
            running_gold = 0.0
            running_silver = 0.0
            
            for ledger in ledgers:
                running_rupees += float(ledger.debit) - float(ledger.credit)
                running_gold += float(ledger.gold_debit) - float(ledger.gold_credit)
                running_silver += float(ledger.silver_debit) - float(ledger.silver_credit)
                
                ledger.balance = running_rupees
                ledger.gold_balance = running_gold
                ledger.silver_balance = running_silver
            
            customer.outstanding_balance = running_rupees
            customer.fine_gold_balance = running_gold
            customer.fine_silver_balance = running_silver
            
        print("Recalculating Supplier Ledger Balances...")
        sellers = db.query(Seller).all()
        for seller in sellers:
            ledgers = db.query(SupplierLedger).filter(
                SupplierLedger.seller_id == seller.id
            ).order_by(SupplierLedger.date.asc(), SupplierLedger.id.asc()).all()
            
            running_rupees = 0.0
            running_gold = 0.0
            running_silver = 0.0
            
            for ledger in ledgers:
                running_rupees += float(ledger.credit) - float(ledger.debit)
                running_gold += float(ledger.gold_credit) - float(ledger.gold_debit)
                running_silver += float(ledger.silver_credit) - float(ledger.silver_debit)
                
                ledger.balance = running_rupees
                ledger.gold_balance = running_gold
                ledger.silver_balance = running_silver
            
            seller.outstanding_balance = running_rupees
            seller.fine_gold_balance = running_gold
            seller.fine_silver_balance = running_silver

        db.commit()
        print("Done!")
        
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    backfill()
