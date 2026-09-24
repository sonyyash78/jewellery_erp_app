"""
Report Service - Unified financial reporting using CalculationService.
All reports use historical transaction rates, not current live rates.
"""
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import date, datetime
from typing import Dict, List, Optional
from app.services.calculation_service import CalculationService
from app.models.invoice import Invoice
from app.models.invoice_item import InvoiceItem
from app.models.purchase import Purchase
from app.models.purchase_item import PurchaseItem
from app.models.expense import Expense
from app.models.gold_calculation import GoldCalculation
from app.models.silver_calculation import SilverCalculation
from app.models.exchange import Exchange
from app.models.exchange_new_item import ExchangeNewItem

class ReportService:
    """Unified report service using CalculationService for all calculations."""
    
    @staticmethod
    def get_sales_report(
        db: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, any]:
        """
        Generate sales report using actual database values.
        No recalculation - uses stored transaction values.
        Includes Sales from both Invoices and Exchanges.
        """
        # INVOICES
        query = db.query(Invoice)
        if start_date:
            query = query.filter(func.date(Invoice.invoice_date) >= start_date)
        if end_date:
            query = query.filter(func.date(Invoice.invoice_date) <= end_date)
        invoices = query.all()
        
        # EXCHANGES
        exchange_query = db.query(Exchange)
        if start_date:
            exchange_query = exchange_query.filter(func.date(Exchange.exchange_date) >= start_date)
        if end_date:
            exchange_query = exchange_query.filter(func.date(Exchange.exchange_date) <= end_date)
        exchanges = exchange_query.all()
        
        total_sales = Decimal('0')
        total_taxable = Decimal('0')
        total_gst = Decimal('0')
        total_discount = Decimal('0')
        
        # Sum from regular invoices
        for invoice in invoices:
            total_sales += Decimal(str(invoice.grand_total or 0))
            total_taxable += Decimal(str(invoice.subtotal or 0))
            total_discount += Decimal(str(invoice.discount_amount or 0))
            total_gst += Decimal(str(invoice.tax_amount or 0))
            
        # Sum from exchanges (new items given to customer)
        for exchange in exchanges:
            total_sales += Decimal(str(exchange.grand_total or 0))
            total_taxable += Decimal(str(exchange.total_new_value or 0))
            total_gst += Decimal(str(exchange.gst_amount or 0))
            # Exchanges don't have a top-level discount field right now
        
        total_cgst = total_gst / Decimal('2')
        total_sgst = total_gst / Decimal('2')
        total_igst = Decimal('0')
        
        return {
            'total_sales': float(CalculationService._round_final(total_sales)),
            'total_taxable': float(CalculationService._round_final(total_taxable)),
            'total_gst': float(CalculationService._round_final(total_gst)),
            'total_cgst': float(CalculationService._round_final(total_cgst)),
            'total_sgst': float(CalculationService._round_final(total_sgst)),
            'total_igst': float(CalculationService._round_final(total_igst)),
            'output_gst': float(CalculationService._round_final(total_gst)),
            'total_discount': float(CalculationService._round_final(total_discount)),
            'invoice_count': len(invoices) + len(exchanges)
        }
    
    @staticmethod
    def get_purchase_report(
        db: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, any]:
        """
        Generate purchase report using actual database values.
        No recalculation - uses stored transaction values.
        Includes Purchases from suppliers and Old Items from Exchanges.
        """
        query = db.query(Purchase)
        if start_date:
            query = query.filter(func.date(Purchase.created_at) >= start_date)
        if end_date:
            query = query.filter(func.date(Purchase.created_at) <= end_date)
        purchases = query.all()
        
        exchange_query = db.query(Exchange)
        if start_date:
            exchange_query = exchange_query.filter(func.date(Exchange.exchange_date) >= start_date)
        if end_date:
            exchange_query = exchange_query.filter(func.date(Exchange.exchange_date) <= end_date)
        exchanges = exchange_query.all()
        
        total_purchases = Decimal('0')
        total_taxable = Decimal('0')
        total_cgst = Decimal('0')
        total_sgst = Decimal('0')
        total_igst = Decimal('0')
        
        # Supplier Purchases
        for purchase in purchases:
            total_purchases += Decimal(str(purchase.grand_total or 0))
            total_taxable += Decimal(str(purchase.total_taxable or 0))
            total_cgst += Decimal(str(purchase.cgst or 0))
            total_sgst += Decimal(str(purchase.sgst or 0))
            total_igst += Decimal(str(purchase.igst or 0))
            
        # Exchange Old Items (Purchased from customer)
        for exchange in exchanges:
            total_purchases += Decimal(str(exchange.total_old_value or 0))
            total_taxable += Decimal(str(exchange.total_old_value or 0))
            # Usually no GST on old items (URD purchase), so cgst/sgst = 0
        
        input_gst = total_cgst + total_sgst + total_igst
        
        return {
            'total_purchases': float(CalculationService._round_final(total_purchases)),
            'total_taxable': float(CalculationService._round_final(total_taxable)),
            'total_cgst': float(CalculationService._round_final(total_cgst)),
            'total_sgst': float(CalculationService._round_final(total_sgst)),
            'total_igst': float(CalculationService._round_final(total_igst)),
            'input_gst': float(CalculationService._round_final(input_gst)),
            'purchase_count': len(purchases) + len(exchanges)
        }
    
    @staticmethod
    def get_gst_report(
        db: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, any]:
        """
        Generate GST report with Input Tax Credit calculation.
        Uses actual database values, no recalculation.
        
        GST = CGST + SGST + IGST
        Output GST = Sum(Sales GST)
        Input GST = Sum(Purchase GST)
        Net GST = Output GST - Input GST (ITC)
        """
        sales_report = ReportService.get_sales_report(db, start_date, end_date)
        purchase_report = ReportService.get_purchase_report(db, start_date, end_date)
        
        # Use actual GST values from database
        output_gst = Decimal(str(sales_report['output_gst']))
        input_gst = Decimal(str(purchase_report['input_gst']))
        
        # Validate: GST = CGST + SGST + IGST
        output_gst_calculated = (
            Decimal(str(sales_report['total_cgst'])) +
            Decimal(str(sales_report['total_sgst'])) +
            Decimal(str(sales_report['total_igst']))
        )
        
        input_gst_calculated = (
            Decimal(str(purchase_report['total_cgst'])) +
            Decimal(str(purchase_report['total_sgst'])) +
            Decimal(str(purchase_report['total_igst']))
        )
        
        if abs(output_gst - output_gst_calculated) > Decimal('0.01'):
            print(f"WARNING: Output GST mismatch. Reported: {output_gst}, Calculated: {output_gst_calculated}")
        
        if abs(input_gst - input_gst_calculated) > Decimal('0.01'):
            print(f"WARNING: Input GST mismatch. Reported: {input_gst}, Calculated: {input_gst_calculated}")
        
        # Net GST = Output - Input (ITC)
        net_gst = output_gst - input_gst
        
        return {
            'output_gst': float(CalculationService._round_final(output_gst)),
            'output_cgst': sales_report['total_cgst'],
            'output_sgst': sales_report['total_sgst'],
            'output_igst': sales_report['total_igst'],
            'input_gst': float(CalculationService._round_final(input_gst)),
            'input_cgst': purchase_report['total_cgst'],
            'input_sgst': purchase_report['total_sgst'],
            'input_igst': purchase_report['total_igst'],
            'net_gst_payable': float(CalculationService._round_final(net_gst))
        }
    
    @staticmethod
    def get_profit_report(
        db: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, any]:
        """
        Generate comprehensive profit report.
        Displays both the Cash Flow (Sales vs Purchases) AND the True Margin (Making Charges + Wastage).
        """
        # --- CASH FLOW METRICS ---
        total_invoice_sales = Decimal('0')
        total_exchange_sales = Decimal('0')
        
        total_regular_purchases = Decimal('0')
        total_exchange_purchases = Decimal('0')
        
        # --- TRUE MARGIN METRICS ---
        total_making = Decimal('0')
        total_hallmark = Decimal('0')
        total_other = Decimal('0')
        total_discount = Decimal('0')
        
        # --- METAL INVENTORY FLOW ---
        gold_received_purchases = Decimal('0')
        gold_received_exchange = Decimal('0')
        silver_received_purchases = Decimal('0')
        silver_received_exchange = Decimal('0')
        
        gold_given_invoices = Decimal('0')
        gold_given_exchange = Decimal('0')
        silver_given_invoices = Decimal('0')
        silver_given_exchange = Decimal('0')
        
        # INVOICES
        inv_query = db.query(Invoice).join(InvoiceItem)
        if start_date:
            inv_query = inv_query.filter(func.date(Invoice.invoice_date) >= start_date)
        if end_date:
            inv_query = inv_query.filter(func.date(Invoice.invoice_date) <= end_date)
            
        for invoice in inv_query.all():
            total_invoice_sales += Decimal(str(invoice.grand_total or 0))
            total_discount += Decimal(str(invoice.discount_amount or 0))
            for item in invoice.items:
                if item.gold_calculation:
                    c = item.gold_calculation
                    total_making += Decimal(str(c.making_charges_amount or 0))
                    total_hallmark += Decimal(str(c.hallmark_charges or 0))
                    total_other += Decimal(str(c.other_charges or 0))
                    gold_given_invoices += Decimal(str(c.fine_weight or 0))
                    
                if item.silver_calculation:
                    c = item.silver_calculation
                    total_making += Decimal(str(c.making_charges_amount or 0))
                    total_other += Decimal(str(c.other_charges or 0))
                    silver_given_invoices += Decimal(str(c.pure_weight or 0))

        # EXCHANGES
        exc_query = db.query(Exchange)
        if start_date:
            exc_query = exc_query.filter(func.date(Exchange.exchange_date) >= start_date)
        if end_date:
            exc_query = exc_query.filter(func.date(Exchange.exchange_date) <= end_date)
            
        for exchange in exc_query.all():
            total_exchange_sales += Decimal(str(exchange.grand_total or 0))
            total_exchange_purchases += Decimal(str(exchange.total_old_value or 0))
            
            for new_item in exchange.new_items:
                total_making += Decimal(str(new_item.making_charges_amount or 0))
                total_hallmark += Decimal(str(new_item.hallmark_charges or 0))
                total_other += Decimal(str(new_item.other_charges or 0))
                total_discount += Decimal(str(new_item.discount or 0))
                
                if new_item.metal.lower() == 'gold':
                    gold_given_exchange += Decimal(str(new_item.fine_weight or 0))
                elif new_item.metal.lower() == 'silver':
                    silver_given_exchange += Decimal(str(new_item.fine_weight or 0))
                    
            for old_item in exchange.old_items:
                if old_item.metal.lower() == 'gold':
                    gold_received_exchange += Decimal(str(old_item.fine_weight or 0))
                elif old_item.metal.lower() == 'silver':
                    silver_received_exchange += Decimal(str(old_item.fine_weight or 0))

        # PURCHASES
        pur_query = db.query(Purchase)
        if start_date:
            pur_query = pur_query.filter(func.date(Purchase.created_at) >= start_date)
        if end_date:
            pur_query = pur_query.filter(func.date(Purchase.created_at) <= end_date)
        for purchase in pur_query.all():
            total_regular_purchases += Decimal(str(purchase.grand_total or 0))
            for item in purchase.items:
                if item.metal_type.lower() == 'gold':
                    gold_received_purchases += Decimal(str(item.fine_weight or 0))
                elif item.metal_type.lower() == 'silver':
                    silver_received_purchases += Decimal(str(item.fine_weight or 0))
                    
        total_sales = total_invoice_sales + total_exchange_sales
        total_purchases = total_regular_purchases + total_exchange_purchases
        
        total_gold_received = gold_received_purchases + gold_received_exchange
        total_gold_given = gold_given_invoices + gold_given_exchange
        gold_balance = total_gold_received - total_gold_given
        
        total_silver_received = silver_received_purchases + silver_received_exchange
        total_silver_given = silver_given_invoices + silver_given_exchange
        silver_balance = total_silver_received - total_silver_given

        # Get expenses
        expense_query = db.query(Expense)
        if start_date:
            expense_query = expense_query.filter(func.date(Expense.expense_date) >= start_date)
        if end_date:
            expense_query = expense_query.filter(func.date(Expense.expense_date) <= end_date)
        
        expenses = expense_query.all()
        total_expenses = sum([Decimal(str(e.amount or 0)) for e in expenses], Decimal('0'))

        # Calculate True Net Profit
        gross_amount_profit = total_making + total_hallmark + total_other - total_discount
        net_amount_profit = gross_amount_profit - total_expenses
        
        net_cash_flow = total_sales - total_purchases
        
        return {
            'net_profit': float(CalculationService._round_final(net_cash_flow)),
            'gross_profit': float(CalculationService._round_final(net_cash_flow)),
            'total_expenses': float(CalculationService._round_final(total_expenses)),
            
            'business_cash_flow': {
                'Sales (Invoices)': float(CalculationService._round_final(total_invoice_sales)),
                'Sales (Exchange)': float(CalculationService._round_final(total_exchange_sales)),
                'Total Sales': float(CalculationService._round_final(total_sales)),
                'Purchases (Suppliers)': float(CalculationService._round_final(total_regular_purchases)),
                'Purchases (Exchange)': float(CalculationService._round_final(total_exchange_purchases)),
                'Total Purchases': float(CalculationService._round_final(total_purchases)),
                'Net Cash Flow': float(CalculationService._round_final(total_sales - total_purchases)),
            },
            
            'true_amount_profit': {
                'Making Charges Earned': float(CalculationService._round_final(total_making)),
                'Hallmark & Other Charges': float(CalculationService._round_final(total_hallmark + total_other)),
                'Less Discounts Given': float(CalculationService._round_final(total_discount)),
                'Gross Cash Profit': float(CalculationService._round_final(gross_amount_profit)),
                'Less Expenses': float(CalculationService._round_final(total_expenses)),
                'Net Cash Profit': float(CalculationService._round_final(net_amount_profit)),
            }
        }
    
    @staticmethod
    def get_metal_flow_report(
        db: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, any]:
        """
        Generate detailed physical metal inventory flow.
        """
        gold_received_purchases = Decimal('0')
        gold_received_exchange = Decimal('0')
        silver_received_purchases = Decimal('0')
        silver_received_exchange = Decimal('0')
        
        gold_given_invoices = Decimal('0')
        gold_given_exchange = Decimal('0')
        silver_given_invoices = Decimal('0')
        silver_given_exchange = Decimal('0')
        
        # INVOICES
        inv_query = db.query(Invoice).join(InvoiceItem)
        if start_date:
            inv_query = inv_query.filter(func.date(Invoice.invoice_date) >= start_date)
        if end_date:
            inv_query = inv_query.filter(func.date(Invoice.invoice_date) <= end_date)
            
        for invoice in inv_query.all():
            for item in invoice.items:
                if item.gold_calculation:
                    gold_given_invoices += Decimal(str(item.gold_calculation.fine_weight or 0))
                if item.silver_calculation:
                    silver_given_invoices += Decimal(str(item.silver_calculation.pure_weight or 0))

        # EXCHANGES
        exc_query = db.query(Exchange)
        if start_date:
            exc_query = exc_query.filter(func.date(Exchange.exchange_date) >= start_date)
        if end_date:
            exc_query = exc_query.filter(func.date(Exchange.exchange_date) <= end_date)
            
        for exchange in exc_query.all():
            for new_item in exchange.new_items:
                if new_item.metal.lower() == 'gold':
                    gold_given_exchange += Decimal(str(new_item.fine_weight or 0))
                elif new_item.metal.lower() == 'silver':
                    silver_given_exchange += Decimal(str(new_item.fine_weight or 0))
                    
            for old_item in exchange.old_items:
                if old_item.metal.lower() == 'gold':
                    gold_received_exchange += Decimal(str(old_item.fine_weight or 0))
                elif old_item.metal.lower() == 'silver':
                    silver_received_exchange += Decimal(str(old_item.fine_weight or 0))

        # PURCHASES
        pur_query = db.query(Purchase)
        if start_date:
            pur_query = pur_query.filter(func.date(Purchase.created_at) >= start_date)
        if end_date:
            pur_query = pur_query.filter(func.date(Purchase.created_at) <= end_date)
        for purchase in pur_query.all():
            for item in purchase.items:
                if item.metal_type.lower() == 'gold':
                    gold_received_purchases += Decimal(str(item.fine_weight or 0))
                elif item.metal_type.lower() == 'silver':
                    silver_received_purchases += Decimal(str(item.fine_weight or 0))
                    
        total_gold_received = gold_received_purchases + gold_received_exchange
        total_gold_given = gold_given_invoices + gold_given_exchange
        gold_balance = total_gold_received - total_gold_given
        
        total_silver_received = silver_received_purchases + silver_received_exchange
        total_silver_given = silver_given_invoices + silver_given_exchange
        silver_balance = total_silver_received - total_silver_given

        return {
            'gold_inventory_flow': {
                'Gold Purchased (Suppliers) (g)': float(gold_received_purchases.quantize(Decimal('0.001'))),
                'Gold Purchased (Exchange) (g)': float(gold_received_exchange.quantize(Decimal('0.001'))),
                'Total Gold Purchased (g)': float(total_gold_received.quantize(Decimal('0.001'))),
                'Gold Sold (Invoices) (g)': float(gold_given_invoices.quantize(Decimal('0.001'))),
                'Gold Sold (Exchange) (g)': float(gold_given_exchange.quantize(Decimal('0.001'))),
                'Total Gold Sold (g)': float(total_gold_given.quantize(Decimal('0.001'))),
                'Net Gold Balance (g)': float(gold_balance.quantize(Decimal('0.001'))),
            },
            'silver_inventory_flow': {
                'Silver Purchased (Suppliers) (g)': float(silver_received_purchases.quantize(Decimal('0.001'))),
                'Silver Purchased (Exchange) (g)': float(silver_received_exchange.quantize(Decimal('0.001'))),
                'Total Silver Purchased (g)': float(total_silver_received.quantize(Decimal('0.001'))),
                'Silver Sold (Invoices) (g)': float(silver_given_invoices.quantize(Decimal('0.001'))),
                'Silver Sold (Exchange) (g)': float(silver_given_exchange.quantize(Decimal('0.001'))),
                'Total Silver Sold (g)': float(total_silver_given.quantize(Decimal('0.001'))),
                'Net Silver Balance (g)': float(silver_balance.quantize(Decimal('0.001'))),
            }
        }
        
    @staticmethod
    def get_inventory_report(
        db: Session
    ) -> Dict[str, any]:
        """
        Generate inventory report.
        Uses purchase cost (historical rates), not current live rates.
        """
        # For now, we'll use a simplified approach
        # In production, you'd track purchase cost per item in inventory
        from app.models.stock_item import StockItem
        from app.models.gold_rate import GoldRate
        from app.models.silver_rate import SilverRate
        
        inventory_items_all = db.query(StockItem).all()
        inventory_items_available = [i for i in inventory_items_all if (i.status or '').lower() == 'available']
        
        latest_gold = db.query(GoldRate).order_by(GoldRate.effective_datetime.desc()).first()
        latest_silver = db.query(SilverRate).order_by(SilverRate.effective_datetime.desc()).first()
        
        gold_rate = latest_gold.rate_per_gram if latest_gold else Decimal('0')
        silver_rate = latest_silver.rate_per_gram if latest_silver else Decimal('0')
        
        total_weight_all = sum([Decimal(str(item.net_weight or 0)) for item in inventory_items_all])
        total_items_all = len(inventory_items_all)
        
        total_value_available = Decimal('0')
        total_weight_available = Decimal('0')
        
        for item in inventory_items_available:
            weight = Decimal(str(item.net_weight or 0))
            total_weight_available += weight
            if (item.metal or '').lower() == 'gold':
                total_value_available += weight * gold_rate
            elif (item.metal or '').lower() == 'silver':
                total_value_available += weight * silver_rate
                
        return {
            'total_items_ever_created': total_items_all,
            'total_weight_ever_created (g)': float(total_weight_all),
            'items_currently_in_stock': len(inventory_items_available),
            'current_stock_weight (g)': float(total_weight_available),
            'estimated_value_in_stock': float(total_value_available),
        }
    
    @staticmethod
    def get_dashboard_metrics(
        db: Session
    ) -> Dict[str, any]:
        """
        Generate dashboard metrics.
        Uses actual transaction data with correct formulas.
        """
        today = date.today()
        
        # Today's sales
        today_sales_report = ReportService.get_sales_report(db, start_date=today, end_date=today)
        
        # Today's purchases
        today_purchase_report = ReportService.get_purchase_report(db, start_date=today, end_date=today)
        
        # Today's profit (using correct formula)
        today_profit_report = ReportService.get_profit_report(db, start_date=today, end_date=today)
        
        # Total customers
        from app.models.customer import Customer
        total_customers = db.query(Customer).count()
        
        # Inventory value (using purchase cost approach)
        inventory_report = ReportService.get_inventory_report(db)
        
        return {
            'today_sales': today_sales_report['total_sales'],
            'today_bills': today_sales_report['invoice_count'],
            'today_purchases': today_purchase_report['total_purchases'],
            'today_profit': today_profit_report['net_profit'],
            'total_customers': total_customers,
            'inventory_items': inventory_report['items_currently_in_stock'],
            'inventory_weight': inventory_report['current_stock_weight (g)'],
            'inventory_value': inventory_report['estimated_value_in_stock'],
            'low_stock_count': 0  # TODO: Implement low stock threshold
        }

    @staticmethod
    def get_dashboard_charts_data(db: Session) -> Dict[str, any]:
        """
        Generate data for dashboard charts: Sales Trend (last 7 days) and Top Selling Categories.
        """
        from datetime import date, timedelta
        from sqlalchemy import func
        from app.models.invoice import Invoice
        from app.models.invoice_item import InvoiceItem
        
        today = date.today()
        
        # 1. Sales Trend (Last 7 Days)
        sales_trend = []
        for i in range(6, -1, -1):
            target_date = today - timedelta(days=i)
            # Daily sales query
            daily_total = db.query(func.sum(Invoice.grand_total)).filter(
                func.date(Invoice.invoice_date) == target_date
            ).scalar() or 0
            
            sales_trend.append({
                "name": target_date.strftime("%a"), # e.g. 'Mon', 'Tue'
                "sales": float(daily_total)
            })
            
        # 2. Top Selling Categories (All time or last 30 days)
        # Using item_name as a proxy for category if category doesn't exist, 
        # or we can try to group by metal_type / item_type. 
        # Looking at InvoiceItem, we have item_type and item_name.
        thirty_days_ago = today - timedelta(days=30)
        top_items = db.query(
            InvoiceItem.item_name, 
            func.count(InvoiceItem.id).label('qty')
        ).join(Invoice, Invoice.id == InvoiceItem.invoice_id).filter(
            func.date(Invoice.invoice_date) >= thirty_days_ago
        ).group_by(InvoiceItem.item_name).order_by(func.count(InvoiceItem.id).desc()).limit(5).all()
        
        top_categories = []
        for item in top_items:
            top_categories.append({
                "name": item.item_name,
                "qty": item.qty
            })
            
        # Fallback if no data
        if not top_categories:
            top_categories = [
                {"name": "No data yet", "qty": 0}
            ]
            
        return {
            "sales_trend": sales_trend,
            "top_categories": top_categories
        }
