"""
Report Service - Unified financial reporting using CalculationService with Multi-Tenant Support.
All reports use historical transaction rates, not current live rates.
"""
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Any
from app.services.calculation_service import CalculationService
from app.models.invoice import Invoice, InvoiceStatus
from app.models.invoice_item import InvoiceItem
from app.models.purchase import Purchase, PurchaseStatus
from app.models.purchase_item import PurchaseItem
from app.models.expense import Expense
from app.models.gold_calculation import GoldCalculation
from app.models.silver_calculation import SilverCalculation
from app.models.exchange import Exchange
from app.models.exchange_new_item import ExchangeNewItem
from app.models.exchange_item import ExchangeItem
from app.models.stock_item import StockItem
from app.models.crm import Customer
from app.models.gold_rate import GoldRate
from app.models.silver_rate import SilverRate
from app.models.diamond_calculation import DiamondCalculation

def _company_filter(model, company_id: Optional[int]):
    if company_id is None:
        return True
    if company_id == 1:
        return or_(model.company_id == 1, model.company_id.is_(None))
    return model.company_id == company_id

def _dt_range(start_date: Optional[date], end_date: Optional[date]):
    start_dt = datetime.combine(start_date, datetime.min.time()) if start_date else None
    end_dt = datetime.combine(end_date, datetime.max.time()) if end_date else None
    return start_dt, end_dt

class ReportService:
    """Unified report service using CalculationService for all calculations."""
    
    @staticmethod
    def get_sales_report(
        db: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        store_id: Optional[int] = None,
        company_id: Optional[int] = None
    ) -> Dict[str, any]:
        """
        Generate sales report using actual database values.
        No recalculation - uses stored transaction values.
        Includes Sales from both Invoices and Exchanges.
        Uses SQL aggregates and indexed datetime bounds for sub-millisecond execution.
        """
        start_dt, end_dt = _dt_range(start_date, end_date)

        # INVOICES
        inv_q = db.query(
            func.coalesce(func.sum(Invoice.grand_total), 0),
            func.coalesce(func.sum(Invoice.subtotal), 0),
            func.coalesce(func.sum(Invoice.discount_amount), 0),
            func.coalesce(func.sum(Invoice.tax_amount), 0),
            func.count(Invoice.id)
        ).filter(Invoice.status != InvoiceStatus.CANCELLED)
        if store_id is not None:
            inv_q = inv_q.filter(Invoice.store_id == store_id)
        inv_q = inv_q.filter(_company_filter(Invoice, company_id))
        if start_dt:
            inv_q = inv_q.filter(Invoice.invoice_date >= start_dt)
        if end_dt:
            inv_q = inv_q.filter(Invoice.invoice_date <= end_dt)
        inv_sales, inv_taxable, inv_discount, inv_gst, inv_count = inv_q.first()
        
        # EXCHANGES
        exchange_query = db.query(
            func.coalesce(func.sum(Exchange.grand_total), 0),
            func.coalesce(func.sum(Exchange.total_new_value), 0),
            func.coalesce(func.sum(Exchange.gst_amount), 0),
            func.count(Exchange.id)
        ).filter(Exchange.status != 'Cancelled')
        if store_id is not None:
            exchange_query = exchange_query.filter(Exchange.store_id == store_id)
        exchange_query = exchange_query.filter(_company_filter(Exchange, company_id))
        if start_dt:
            exchange_query = exchange_query.filter(Exchange.exchange_date >= start_dt)
        if end_dt:
            exchange_query = exchange_query.filter(Exchange.exchange_date <= end_dt)
        exc_sales, exc_taxable, exc_gst, exc_count = exchange_query.first()
        
        total_sales = Decimal(str(inv_sales or 0)) + Decimal(str(exc_sales or 0))
        total_taxable = Decimal(str(inv_taxable or 0)) + Decimal(str(exc_taxable or 0))
        total_discount = Decimal(str(inv_discount or 0))
        total_gst = Decimal(str(inv_gst or 0)) + Decimal(str(exc_gst or 0))
        
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
            'invoice_count': int((inv_count or 0) + (exc_count or 0))
        }
    
    @staticmethod
    def get_purchase_report(
        db: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        store_id: Optional[int] = None,
        company_id: Optional[int] = None
    ) -> Dict[str, any]:
        start_dt, end_dt = _dt_range(start_date, end_date)

        pur_q = db.query(
            func.coalesce(func.sum(Purchase.grand_total), 0),
            func.coalesce(func.sum(Purchase.total_taxable), 0),
            func.coalesce(func.sum(Purchase.cgst), 0),
            func.coalesce(func.sum(Purchase.sgst), 0),
            func.coalesce(func.sum(Purchase.igst), 0),
            func.count(Purchase.id)
        ).filter(Purchase.status != PurchaseStatus.CANCELLED)
        if store_id is not None:
            pur_q = pur_q.filter(Purchase.store_id == store_id)
        pur_q = pur_q.filter(_company_filter(Purchase, company_id))
        if start_dt:
            pur_q = pur_q.filter(Purchase.created_at >= start_dt)
        if end_dt:
            pur_q = pur_q.filter(Purchase.created_at <= end_dt)
        pur_sales, pur_taxable, pur_cgst, pur_sgst, pur_igst, pur_count = pur_q.first()
        
        exchange_query = db.query(
            func.coalesce(func.sum(Exchange.total_old_value), 0),
            func.count(Exchange.id)
        ).filter(Exchange.status != 'Cancelled')
        if store_id is not None:
            exchange_query = exchange_query.filter(Exchange.store_id == store_id)
        exchange_query = exchange_query.filter(_company_filter(Exchange, company_id))
        if start_dt:
            exchange_query = exchange_query.filter(Exchange.exchange_date >= start_dt)
        if end_dt:
            exchange_query = exchange_query.filter(Exchange.exchange_date <= end_dt)
        exc_purchases, exc_count = exchange_query.first()
        
        total_purchases = Decimal(str(pur_sales or 0)) + Decimal(str(exc_purchases or 0))
        total_taxable = Decimal(str(pur_taxable or 0)) + Decimal(str(exc_purchases or 0))
        total_cgst = Decimal(str(pur_cgst or 0))
        total_sgst = Decimal(str(pur_sgst or 0))
        total_igst = Decimal(str(pur_igst or 0))
        
        input_gst = total_cgst + total_sgst + total_igst
        
        return {
            'total_purchases': float(CalculationService._round_final(total_purchases)),
            'total_taxable': float(CalculationService._round_final(total_taxable)),
            'total_cgst': float(CalculationService._round_final(total_cgst)),
            'total_sgst': float(CalculationService._round_final(total_sgst)),
            'total_igst': float(CalculationService._round_final(total_igst)),
            'input_gst': float(CalculationService._round_final(input_gst)),
            'purchase_count': int((pur_count or 0) + (exc_count or 0))
        }
    
    @staticmethod
    def get_gst_report(
        db: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        store_id: Optional[int] = None,
        company_id: Optional[int] = None
    ) -> Dict[str, any]:
        sales_report = ReportService.get_sales_report(db, start_date, end_date, store_id=store_id, company_id=company_id)
        purchase_report = ReportService.get_purchase_report(db, start_date, end_date, store_id=store_id, company_id=company_id)
        
        output_gst = Decimal(str(sales_report['output_gst']))
        input_gst = Decimal(str(purchase_report['input_gst']))
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
        end_date: Optional[date] = None,
        store_id: Optional[int] = None,
        company_id: Optional[int] = None
    ) -> Dict[str, any]:
        start_dt, end_dt = _dt_range(start_date, end_date)

        # 1. Invoice sales and discounts
        inv_query = db.query(
            func.coalesce(func.sum(Invoice.grand_total), 0),
            func.coalesce(func.sum(Invoice.discount_amount), 0)
        ).filter(Invoice.status != InvoiceStatus.CANCELLED)
        if store_id is not None:
            inv_query = inv_query.filter(Invoice.store_id == store_id)
        inv_query = inv_query.filter(_company_filter(Invoice, company_id))
        if start_dt:
            inv_query = inv_query.filter(Invoice.invoice_date >= start_dt)
        if end_dt:
            inv_query = inv_query.filter(Invoice.invoice_date <= end_dt)
        inv_grand_total, inv_discount = inv_query.first()
        total_invoice_sales = Decimal(str(inv_grand_total or 0))
        total_discount = Decimal(str(inv_discount or 0))

        # Gold calculation charges from active invoices
        gold_calc_q = db.query(
            func.coalesce(func.sum(GoldCalculation.making_charges_amount), 0),
            func.coalesce(func.sum(GoldCalculation.hallmark_charges), 0),
            func.coalesce(func.sum(GoldCalculation.other_charges), 0)
        ).join(InvoiceItem, GoldCalculation.invoice_item_id == InvoiceItem.id)\
         .join(Invoice, InvoiceItem.invoice_id == Invoice.id)\
         .filter(Invoice.status != InvoiceStatus.CANCELLED)
        if store_id is not None:
            gold_calc_q = gold_calc_q.filter(Invoice.store_id == store_id)
        gold_calc_q = gold_calc_q.filter(_company_filter(Invoice, company_id))
        if start_dt:
            gold_calc_q = gold_calc_q.filter(Invoice.invoice_date >= start_dt)
        if end_dt:
            gold_calc_q = gold_calc_q.filter(Invoice.invoice_date <= end_dt)
        g_making, g_hallmark, g_other = gold_calc_q.first()

        # Silver calculation charges from active invoices
        silver_calc_q = db.query(
            func.coalesce(func.sum(SilverCalculation.making_charges_amount), 0),
            func.coalesce(func.sum(SilverCalculation.other_charges), 0)
        ).join(InvoiceItem, SilverCalculation.invoice_item_id == InvoiceItem.id)\
         .join(Invoice, InvoiceItem.invoice_id == Invoice.id)\
         .filter(Invoice.status != InvoiceStatus.CANCELLED)
        if store_id is not None:
            silver_calc_q = silver_calc_q.filter(Invoice.store_id == store_id)
        silver_calc_q = silver_calc_q.filter(_company_filter(Invoice, company_id))
        if start_dt:
            silver_calc_q = silver_calc_q.filter(Invoice.invoice_date >= start_dt)
        if end_dt:
            silver_calc_q = silver_calc_q.filter(Invoice.invoice_date <= end_dt)
        s_making, s_other = silver_calc_q.first()

        total_making = Decimal(str(g_making or 0)) + Decimal(str(s_making or 0))
        total_hallmark = Decimal(str(g_hallmark or 0))
        total_other = Decimal(str(g_other or 0)) + Decimal(str(s_other or 0))

        # 2. Exchanges
        exc_q = db.query(
            func.coalesce(func.sum(Exchange.grand_total), 0),
            func.coalesce(func.sum(Exchange.total_old_value), 0)
        ).filter(Exchange.status != 'Cancelled')
        if store_id is not None:
            exc_q = exc_q.filter(Exchange.store_id == store_id)
        exc_q = exc_q.filter(_company_filter(Exchange, company_id))
        if start_dt:
            exc_q = exc_q.filter(Exchange.exchange_date >= start_dt)
        if end_dt:
            exc_q = exc_q.filter(Exchange.exchange_date <= end_dt)
        exc_sales, exc_purchases = exc_q.first()
        total_exchange_sales = Decimal(str(exc_sales or 0))
        total_exchange_purchases = Decimal(str(exc_purchases or 0))

        exc_new_q = db.query(
            func.coalesce(func.sum(ExchangeNewItem.making_charges_amount), 0),
            func.coalesce(func.sum(ExchangeNewItem.hallmark_charges), 0),
            func.coalesce(func.sum(ExchangeNewItem.other_charges), 0),
            func.coalesce(func.sum(ExchangeNewItem.discount), 0)
        ).join(Exchange, ExchangeNewItem.exchange_id == Exchange.id)\
         .filter(Exchange.status != 'Cancelled')
        if store_id is not None:
            exc_new_q = exc_new_q.filter(Exchange.store_id == store_id)
        exc_new_q = exc_new_q.filter(_company_filter(Exchange, company_id))
        if start_dt:
            exc_new_q = exc_new_q.filter(Exchange.exchange_date >= start_dt)
        if end_dt:
            exc_new_q = exc_new_q.filter(Exchange.exchange_date <= end_dt)
        ex_making, ex_hallmark, ex_other, ex_disc = exc_new_q.first()

        total_making += Decimal(str(ex_making or 0))
        total_hallmark += Decimal(str(ex_hallmark or 0))
        total_other += Decimal(str(ex_other or 0))
        total_discount += Decimal(str(ex_disc or 0))

        # 3. Purchases
        pur_q = db.query(
            func.coalesce(func.sum(Purchase.grand_total), 0)
        ).filter(Purchase.status != PurchaseStatus.CANCELLED)
        if store_id is not None:
            pur_q = pur_q.filter(Purchase.store_id == store_id)
        if start_dt:
            pur_q = pur_q.filter(Purchase.created_at >= start_dt)
        if end_dt:
            pur_q = pur_q.filter(Purchase.created_at <= end_dt)
        total_regular_purchases = Decimal(str(pur_q.scalar() or 0))

        total_sales = total_invoice_sales + total_exchange_sales
        total_purchases = total_regular_purchases + total_exchange_purchases

        # 4. Expenses
        expense_query = db.query(
            func.coalesce(func.sum(Expense.amount), 0)
        )
        if store_id is not None:
            expense_query = expense_query.filter(Expense.store_id == store_id)
        if start_date:
            expense_query = expense_query.filter(Expense.expense_date >= start_date)
        if end_date:
            expense_query = expense_query.filter(Expense.expense_date <= end_date)
        total_expenses = Decimal(str(expense_query.scalar() or 0))

        gross_amount_profit = total_making + total_hallmark + total_other - total_discount
        net_amount_profit = gross_amount_profit - total_expenses
        net_cash_flow = total_sales - total_purchases
        
        return {
            'net_profit': float(CalculationService._round_final(net_amount_profit)),
            'gross_profit': float(CalculationService._round_final(gross_amount_profit)),
            'net_cash_flow': float(CalculationService._round_final(net_cash_flow)),
            'total_expenses': float(CalculationService._round_final(total_expenses)),
            'business_cash_flow': {
                'Sales (Invoices)': float(CalculationService._round_final(total_invoice_sales)),
                'Sales (Exchange)': float(CalculationService._round_final(total_exchange_sales)),
                'Total Sales': float(CalculationService._round_final(total_sales)),
                'Purchases (Suppliers)': float(CalculationService._round_final(total_regular_purchases)),
                'Purchases (Exchange)': float(CalculationService._round_final(total_exchange_purchases)),
                'Total Purchases': float(CalculationService._round_final(total_purchases)),
                'Net Cash Flow': float(CalculationService._round_final(net_cash_flow)),
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
        end_date: Optional[date] = None,
        store_id: Optional[int] = None,
        company_id: Optional[int] = None
    ) -> Dict[str, any]:
        start_dt, end_dt = _dt_range(start_date, end_date)

        # 1. Invoice sales metal flow (excluding counter deposit items)
        inv_not_deposit = ~func.lower(func.coalesce(InvoiceItem.item_name, '')).like('%deposit%')
        inv_is_deposit = func.lower(func.coalesce(InvoiceItem.item_name, '')).like('%deposit%')

        g_inv_q = db.query(
            func.coalesce(func.sum(GoldCalculation.fine_weight), 0)
        ).join(InvoiceItem, GoldCalculation.invoice_item_id == InvoiceItem.id)\
         .join(Invoice, InvoiceItem.invoice_id == Invoice.id)\
         .filter(Invoice.status != InvoiceStatus.CANCELLED, inv_not_deposit)
        if store_id is not None:
            g_inv_q = g_inv_q.filter(Invoice.store_id == store_id)
        if company_id is not None:
            g_inv_q = g_inv_q.filter(_company_filter(Invoice, company_id))
        if start_dt:
            g_inv_q = g_inv_q.filter(Invoice.invoice_date >= start_dt)
        if end_dt:
            g_inv_q = g_inv_q.filter(Invoice.invoice_date <= end_dt)
        gold_given_invoices = Decimal(str(g_inv_q.scalar() or 0))

        s_inv_q = db.query(
            func.coalesce(func.sum(SilverCalculation.pure_weight), 0)
        ).join(InvoiceItem, SilverCalculation.invoice_item_id == InvoiceItem.id)\
         .join(Invoice, InvoiceItem.invoice_id == Invoice.id)\
         .filter(Invoice.status != InvoiceStatus.CANCELLED, inv_not_deposit)
        if store_id is not None:
            s_inv_q = s_inv_q.filter(Invoice.store_id == store_id)
        if company_id is not None:
            s_inv_q = s_inv_q.filter(_company_filter(Invoice, company_id))
        if start_dt:
            s_inv_q = s_inv_q.filter(Invoice.invoice_date >= start_dt)
        if end_dt:
            s_inv_q = s_inv_q.filter(Invoice.invoice_date <= end_dt)
        silver_given_invoices = Decimal(str(s_inv_q.scalar() or 0))

        # Counter deposits received from customers during Invoice checkout
        g_inv_dep_q = db.query(
            func.coalesce(func.sum(GoldCalculation.fine_weight), 0)
        ).join(InvoiceItem, GoldCalculation.invoice_item_id == InvoiceItem.id)\
         .join(Invoice, InvoiceItem.invoice_id == Invoice.id)\
         .filter(Invoice.status != InvoiceStatus.CANCELLED, inv_is_deposit)
        if store_id is not None:
            g_inv_dep_q = g_inv_dep_q.filter(Invoice.store_id == store_id)
        if company_id is not None:
            g_inv_dep_q = g_inv_dep_q.filter(_company_filter(Invoice, company_id))
        if start_dt:
            g_inv_dep_q = g_inv_dep_q.filter(Invoice.invoice_date >= start_dt)
        if end_dt:
            g_inv_dep_q = g_inv_dep_q.filter(Invoice.invoice_date <= end_dt)
        gold_dep_invoices = Decimal(str(g_inv_dep_q.scalar() or 0))

        s_inv_dep_q = db.query(
            func.coalesce(func.sum(SilverCalculation.pure_weight), 0)
        ).join(InvoiceItem, SilverCalculation.invoice_item_id == InvoiceItem.id)\
         .join(Invoice, InvoiceItem.invoice_id == Invoice.id)\
         .filter(Invoice.status != InvoiceStatus.CANCELLED, inv_is_deposit)
        if store_id is not None:
            s_inv_dep_q = s_inv_dep_q.filter(Invoice.store_id == store_id)
        if company_id is not None:
            s_inv_dep_q = s_inv_dep_q.filter(_company_filter(Invoice, company_id))
        if start_dt:
            s_inv_dep_q = s_inv_dep_q.filter(Invoice.invoice_date >= start_dt)
        if end_dt:
            s_inv_dep_q = s_inv_dep_q.filter(Invoice.invoice_date <= end_dt)
        silver_dep_invoices = Decimal(str(s_inv_dep_q.scalar() or 0))

        # 2. Exchange new items (metal given/sold)
        exc_new_gold_q = db.query(
            func.coalesce(func.sum(ExchangeNewItem.fine_weight), 0)
        ).join(Exchange, ExchangeNewItem.exchange_id == Exchange.id)\
         .filter(Exchange.status != 'Cancelled', func.lower(ExchangeNewItem.metal) == 'gold')
        if store_id is not None:
            exc_new_gold_q = exc_new_gold_q.filter(Exchange.store_id == store_id)
        if company_id is not None:
            exc_new_gold_q = exc_new_gold_q.filter(_company_filter(Exchange, company_id))
        if start_dt:
            exc_new_gold_q = exc_new_gold_q.filter(Exchange.exchange_date >= start_dt)
        if end_dt:
            exc_new_gold_q = exc_new_gold_q.filter(Exchange.exchange_date <= end_dt)
        gold_given_exchange = Decimal(str(exc_new_gold_q.scalar() or 0))

        exc_new_silver_q = db.query(
            func.coalesce(func.sum(ExchangeNewItem.fine_weight), 0)
        ).join(Exchange, ExchangeNewItem.exchange_id == Exchange.id)\
         .filter(Exchange.status != 'Cancelled', func.lower(ExchangeNewItem.metal) == 'silver')
        if store_id is not None:
            exc_new_silver_q = exc_new_silver_q.filter(Exchange.store_id == store_id)
        if company_id is not None:
            exc_new_silver_q = exc_new_silver_q.filter(_company_filter(Exchange, company_id))
        if start_dt:
            exc_new_silver_q = exc_new_silver_q.filter(Exchange.exchange_date >= start_dt)
        if end_dt:
            exc_new_silver_q = exc_new_silver_q.filter(Exchange.exchange_date <= end_dt)
        silver_given_exchange = Decimal(str(exc_new_silver_q.scalar() or 0))

        # 3. Exchange old items (metal received/purchased)
        exc_old_gold_q = db.query(
            func.coalesce(func.sum(ExchangeItem.fine_weight), 0)
        ).join(Exchange, ExchangeItem.exchange_id == Exchange.id)\
         .filter(Exchange.status != 'Cancelled', func.lower(ExchangeItem.metal) == 'gold')
        if store_id is not None:
            exc_old_gold_q = exc_old_gold_q.filter(Exchange.store_id == store_id)
        if company_id is not None:
            exc_old_gold_q = exc_old_gold_q.filter(_company_filter(Exchange, company_id))
        if start_dt:
            exc_old_gold_q = exc_old_gold_q.filter(Exchange.exchange_date >= start_dt)
        if end_dt:
            exc_old_gold_q = exc_old_gold_q.filter(Exchange.exchange_date <= end_dt)
        gold_received_exchange = Decimal(str(exc_old_gold_q.scalar() or 0)) + gold_dep_invoices

        exc_old_silver_q = db.query(
            func.coalesce(func.sum(ExchangeItem.fine_weight), 0)
        ).join(Exchange, ExchangeItem.exchange_id == Exchange.id)\
         .filter(Exchange.status != 'Cancelled', func.lower(ExchangeItem.metal) == 'silver')
        if store_id is not None:
            exc_old_silver_q = exc_old_silver_q.filter(Exchange.store_id == store_id)
        if company_id is not None:
            exc_old_silver_q = exc_old_silver_q.filter(_company_filter(Exchange, company_id))
        if start_dt:
            exc_old_silver_q = exc_old_silver_q.filter(Exchange.exchange_date >= start_dt)
        if end_dt:
            exc_old_silver_q = exc_old_silver_q.filter(Exchange.exchange_date <= end_dt)
        silver_received_exchange = Decimal(str(exc_old_silver_q.scalar() or 0)) + silver_dep_invoices

        # 4. Purchases (metal received/purchased vs counter metal given to supplier)
        pur_not_deposit = and_(
            ~func.lower(func.coalesce(PurchaseItem.category, '')).like('%deposit%'),
            ~func.lower(func.coalesce(PurchaseItem.item_name, '')).like('%metal given%'),
            ~func.lower(func.coalesce(PurchaseItem.item_name, '')).like('%deposit%')
        )
        pur_is_deposit = ~pur_not_deposit

        pur_gold_q = db.query(
            func.coalesce(func.sum(PurchaseItem.fine_weight), 0)
        ).join(Purchase, PurchaseItem.purchase_id == Purchase.id)\
         .filter(Purchase.status != PurchaseStatus.CANCELLED, func.lower(PurchaseItem.metal_type) == 'gold', pur_not_deposit)
        if store_id is not None:
            pur_gold_q = pur_gold_q.filter(Purchase.store_id == store_id)
        if company_id is not None:
            pur_gold_q = pur_gold_q.filter(_company_filter(Purchase, company_id))
        if start_dt:
            pur_gold_q = pur_gold_q.filter(Purchase.created_at >= start_dt)
        if end_dt:
            pur_gold_q = pur_gold_q.filter(Purchase.created_at <= end_dt)
        gold_received_purchases = Decimal(str(pur_gold_q.scalar() or 0))

        pur_silver_q = db.query(
            func.coalesce(func.sum(PurchaseItem.fine_weight), 0)
        ).join(Purchase, PurchaseItem.purchase_id == Purchase.id)\
         .filter(Purchase.status != PurchaseStatus.CANCELLED, func.lower(PurchaseItem.metal_type) == 'silver', pur_not_deposit)
        if store_id is not None:
            pur_silver_q = pur_silver_q.filter(Purchase.store_id == store_id)
        if company_id is not None:
            pur_silver_q = pur_silver_q.filter(_company_filter(Purchase, company_id))
        if start_dt:
            pur_silver_q = pur_silver_q.filter(Purchase.created_at >= start_dt)
        if end_dt:
            pur_silver_q = pur_silver_q.filter(Purchase.created_at <= end_dt)
        silver_received_purchases = Decimal(str(pur_silver_q.scalar() or 0))

        pur_gold_given_q = db.query(
            func.coalesce(func.sum(PurchaseItem.fine_weight), 0)
        ).join(Purchase, PurchaseItem.purchase_id == Purchase.id)\
         .filter(Purchase.status != PurchaseStatus.CANCELLED, func.lower(PurchaseItem.metal_type) == 'gold', pur_is_deposit)
        if store_id is not None:
            pur_gold_given_q = pur_gold_given_q.filter(Purchase.store_id == store_id)
        if company_id is not None:
            pur_gold_given_q = pur_gold_given_q.filter(_company_filter(Purchase, company_id))
        if start_dt:
            pur_gold_given_q = pur_gold_given_q.filter(Purchase.created_at >= start_dt)
        if end_dt:
            pur_gold_given_q = pur_gold_given_q.filter(Purchase.created_at <= end_dt)
        gold_given_purchases = Decimal(str(pur_gold_given_q.scalar() or 0))

        pur_silver_given_q = db.query(
            func.coalesce(func.sum(PurchaseItem.fine_weight), 0)
        ).join(Purchase, PurchaseItem.purchase_id == Purchase.id)\
         .filter(Purchase.status != PurchaseStatus.CANCELLED, func.lower(PurchaseItem.metal_type) == 'silver', pur_is_deposit)
        if store_id is not None:
            pur_silver_given_q = pur_silver_given_q.filter(Purchase.store_id == store_id)
        if company_id is not None:
            pur_silver_given_q = pur_silver_given_q.filter(_company_filter(Purchase, company_id))
        if start_dt:
            pur_silver_given_q = pur_silver_given_q.filter(Purchase.created_at >= start_dt)
        if end_dt:
            pur_silver_given_q = pur_silver_given_q.filter(Purchase.created_at <= end_dt)
        silver_given_purchases = Decimal(str(pur_silver_given_q.scalar() or 0))

        total_gold_received = gold_received_purchases + gold_received_exchange
        total_gold_given = gold_given_invoices + gold_given_exchange + gold_given_purchases
        gold_balance = total_gold_received - total_gold_given
        
        total_silver_received = silver_received_purchases + silver_received_exchange
        total_silver_given = silver_given_invoices + silver_given_exchange + silver_given_purchases
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
        db: Session,
        store_id: Optional[int] = None,
        company_id: Optional[int] = None
    ) -> Dict[str, any]:
        stock_query = db.query(StockItem)
        if store_id is not None:
            stock_query = stock_query.filter(StockItem.store_id == store_id)
        inventory_items_all = stock_query.all()
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
        db: Session,
        store_id: Optional[int] = None,
        company_id: Optional[int] = None
    ) -> Dict[str, any]:
        today = date.today()
        today_sales_report = ReportService.get_sales_report(db, start_date=today, end_date=today, store_id=store_id, company_id=company_id)
        today_purchase_report = ReportService.get_purchase_report(db, start_date=today, end_date=today, store_id=store_id, company_id=company_id)
        today_profit_report = ReportService.get_profit_report(db, start_date=today, end_date=today, store_id=store_id, company_id=company_id)
        
        cust_query = db.query(Customer).filter(Customer.is_deleted == False)
        if store_id is not None:
            cust_query = cust_query.filter(Customer.store_id == store_id)
        total_customers = cust_query.count()
        
        inventory_report = ReportService.get_inventory_report(db, store_id=store_id)
        
        return {
            'today_sales': today_sales_report['total_sales'],
            'today_bills': today_sales_report['invoice_count'],
            'today_purchases': today_purchase_report['total_purchases'],
            'today_profit': today_profit_report['net_profit'],
            'total_customers': total_customers,
            'inventory_items': inventory_report['items_currently_in_stock'],
            'inventory_weight': inventory_report['current_stock_weight (g)'],
            'inventory_value': inventory_report['estimated_value_in_stock'],
            'low_stock_count': 0
        }

    @staticmethod
    def get_dashboard_charts_data(
        db: Session,
        store_id: Optional[int] = None,
        company_id: Optional[int] = None
    ) -> Dict[str, any]:
        today = date.today()
        start_date = today - timedelta(days=6)
        trend_query = db.query(
            func.date(Invoice.invoice_date).label('day'),
            func.sum(Invoice.grand_total).label('total')
        ).filter(
            func.date(Invoice.invoice_date) >= start_date,
            func.date(Invoice.invoice_date) <= today,
            Invoice.status != InvoiceStatus.CANCELLED
        )
        if store_id is not None:
            trend_query = trend_query.filter(Invoice.store_id == store_id)
        trend_query = trend_query.filter(_company_filter(Invoice, company_id))
        rows = trend_query.group_by(func.date(Invoice.invoice_date)).all()
        day_map = {str(r.day): float(r.total or 0) for r in rows}

        sales_trend = []
        for i in range(6, -1, -1):
            target_date = today - timedelta(days=i)
            key = target_date.strftime("%Y-%m-%d")
            sales_trend.append({
                "name": target_date.strftime("%a"),
                "sales": day_map.get(key, 0.0)
            })
            
        thirty_days_ago = today - timedelta(days=30)
        items_query = db.query(
            InvoiceItem.item_name, 
            func.count(InvoiceItem.id).label('qty')
        ).join(Invoice, Invoice.id == InvoiceItem.invoice_id).filter(
            func.date(Invoice.invoice_date) >= thirty_days_ago,
            Invoice.status != InvoiceStatus.CANCELLED
        )
        if store_id is not None:
            items_query = items_query.filter(Invoice.store_id == store_id)
        top_items = items_query.group_by(InvoiceItem.item_name).order_by(func.count(InvoiceItem.id).desc()).limit(5).all()
        
        top_categories = []
        for item in top_items:
            top_categories.append({
                "name": item.item_name,
                "qty": item.qty
            })
            
        if not top_categories:
            top_categories = [{"name": "No data yet", "qty": 0}]
            
        return {
            "sales_trend": sales_trend,
            "top_categories": top_categories
        }


    @staticmethod
    def get_company_profit_analysis(
        db: Session,
        company_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Company-wise Actual Purchase vs Selling Profit Analysis.
        COGS based on actual purchase metal rate / purity / weight.
        """
        start_dt, end_dt = _dt_range(start_date, end_date)

        # 1. Total Selling Revenue for Company
        inv_q = db.query(
            func.coalesce(func.sum(Invoice.subtotal), 0),
            func.coalesce(func.sum(Invoice.discount_amount), 0),
            func.coalesce(func.sum(Invoice.grand_total), 0),
            func.count(Invoice.id)
        ).filter(
            Invoice.company_id == company_id,
            Invoice.status != InvoiceStatus.CANCELLED
        )
        if start_dt:
            inv_q = inv_q.filter(Invoice.invoice_date >= start_dt)
        if end_dt:
            inv_q = inv_q.filter(Invoice.invoice_date <= end_dt)

        subtotal, discount, grand_total, inv_count = inv_q.first()
        selling_revenue = Decimal(str(subtotal or 0)) - Decimal(str(discount or 0))

        # 2. Total Purchase Cost for Company
        pur_q = db.query(
            func.coalesce(func.sum(Purchase.total_taxable), 0),
            func.coalesce(func.sum(Purchase.grand_total), 0),
            func.count(Purchase.id)
        ).filter(
            Purchase.company_id == company_id,
            Purchase.status != PurchaseStatus.CANCELLED
        )
        if start_dt:
            pur_q = pur_q.filter(Purchase.created_at >= start_dt)
        if end_dt:
            pur_q = pur_q.filter(Purchase.created_at <= end_dt)

        p_taxable, p_grand_total, pur_count = pur_q.first()
        purchase_cost = Decimal(str(p_taxable or 0))

        # 3. Profit metrics
        gross_profit = selling_revenue - purchase_cost
        margin_pct = (gross_profit / selling_revenue * Decimal('100')) if selling_revenue > 0 else Decimal('0.00')

        return {
            "company_id": company_id,
            "invoice_count": inv_count,
            "purchase_count": pur_count,
            "selling_revenue": float(CalculationService._round_final(selling_revenue)),
            "purchase_cost": float(CalculationService._round_final(purchase_cost)),
            "gross_profit": float(CalculationService._round_final(gross_profit)),
            "profit_margin_pct": float(CalculationService._round_final(margin_pct)),
            "selling_grand_total": float(CalculationService._round_final(Decimal(str(grand_total or 0)))),
            "purchase_grand_total": float(CalculationService._round_final(Decimal(str(p_grand_total or 0))))
        }

    @staticmethod
    def get_company_wastage_analysis(
        db: Session,
        company_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Metal Wastage & Margin Profit Report:
        Calculates separate wastage (Ghat) and making/labour profit for Gold, Silver, and Diamond:
        Net Wastage Profit (g) = Customer Sold Wastage (g) - Supplier Purchased Wastage (g)
        """
        start_dt, end_dt = _dt_range(start_date, end_date)

        # -------------------------------------------------------------
        # 1. GOLD ANALYSIS
        # -------------------------------------------------------------
        # 1a. Sold Gold (Invoices)
        g_sold_q = db.query(
            func.coalesce(func.sum(GoldCalculation.net_weight * GoldCalculation.wastage / 100), 0),
            func.coalesce(func.sum(GoldCalculation.fine_weight), 0),
            func.coalesce(func.sum(GoldCalculation.making_charges_amount), 0),
            func.coalesce(func.sum(GoldCalculation.total_gold_value), 0)
        ).join(InvoiceItem, InvoiceItem.id == GoldCalculation.invoice_item_id)\
         .join(Invoice, Invoice.id == InvoiceItem.invoice_id)\
         .filter(Invoice.company_id == company_id, Invoice.status != InvoiceStatus.CANCELLED)

        if start_dt:
            g_sold_q = g_sold_q.filter(Invoice.invoice_date >= start_dt)
        if end_dt:
            g_sold_q = g_sold_q.filter(Invoice.invoice_date <= end_dt)

        g_sold_w, g_sold_fine, g_sold_making, g_sold_val = g_sold_q.first()

        # 1b. Purchased Gold (Purchases)
        g_pur_q = db.query(
            func.coalesce(func.sum(PurchaseItem.net_weight * PurchaseItem.wastage / 100), 0),
            func.coalesce(func.sum(PurchaseItem.fine_weight), 0),
            func.coalesce(func.sum(PurchaseItem.labour_charge), 0),
            func.coalesce(func.sum(PurchaseItem.taxable_amount), 0)
        ).join(Purchase, Purchase.id == PurchaseItem.purchase_id)\
         .filter(Purchase.company_id == company_id, Purchase.status != PurchaseStatus.CANCELLED, func.lower(PurchaseItem.metal_type) == 'gold')

        if start_dt:
            g_pur_q = g_pur_q.filter(Purchase.created_at >= start_dt)
        if end_dt:
            g_pur_q = g_pur_q.filter(Purchase.created_at <= end_dt)

        g_pur_w, g_pur_fine, g_pur_labour, g_pur_val = g_pur_q.first()

        gold_sold_wastage = Decimal(str(g_sold_w or 0))
        gold_pur_wastage = Decimal(str(g_pur_w or 0))
        gold_net_wastage_profit = gold_sold_wastage - gold_pur_wastage

        gold_sold_making = Decimal(str(g_sold_making or 0))
        gold_pur_labour = Decimal(str(g_pur_labour or 0))
        gold_net_labour_profit = gold_sold_making - gold_pur_labour

        gold_sold_val = Decimal(str(g_sold_val or 0))
        gold_pur_val = Decimal(str(g_pur_val or 0))
        gold_net_val_profit = gold_sold_val - gold_pur_val

        # -------------------------------------------------------------
        # 2. SILVER ANALYSIS
        # -------------------------------------------------------------
        # 2a. Sold Silver (Invoices)
        s_sold_q = db.query(
            func.coalesce(func.sum(SilverCalculation.wastage * (SilverCalculation.gross_weight - SilverCalculation.stone_weight) / 100), 0),
            func.coalesce(func.sum(SilverCalculation.pure_weight), 0),
            func.coalesce(func.sum(SilverCalculation.making_charges_amount), 0),
            func.coalesce(func.sum(SilverCalculation.total_silver_value), 0)
        ).join(InvoiceItem, InvoiceItem.id == SilverCalculation.invoice_item_id)\
         .join(Invoice, Invoice.id == InvoiceItem.invoice_id)\
         .filter(Invoice.company_id == company_id, Invoice.status != InvoiceStatus.CANCELLED)

        if start_dt:
            s_sold_q = s_sold_q.filter(Invoice.invoice_date >= start_dt)
        if end_dt:
            s_sold_q = s_sold_q.filter(Invoice.invoice_date <= end_dt)

        s_sold_w, s_sold_pure, s_sold_making, s_sold_val = s_sold_q.first()

        # 2b. Purchased Silver (Purchases)
        s_pur_q = db.query(
            func.coalesce(func.sum(PurchaseItem.net_weight * PurchaseItem.wastage / 100), 0),
            func.coalesce(func.sum(PurchaseItem.fine_weight), 0),
            func.coalesce(func.sum(PurchaseItem.labour_charge), 0),
            func.coalesce(func.sum(PurchaseItem.taxable_amount), 0)
        ).join(Purchase, Purchase.id == PurchaseItem.purchase_id)\
         .filter(Purchase.company_id == company_id, Purchase.status != PurchaseStatus.CANCELLED, func.lower(PurchaseItem.metal_type) == 'silver')

        if start_dt:
            s_pur_q = s_pur_q.filter(Purchase.created_at >= start_dt)
        if end_dt:
            s_pur_q = s_pur_q.filter(Purchase.created_at <= end_dt)

        s_pur_w, s_pur_pure, s_pur_labour, s_pur_val = s_pur_q.first()

        silver_sold_wastage = Decimal(str(s_sold_w or 0))
        silver_pur_wastage = Decimal(str(s_pur_w or 0))
        silver_net_wastage_profit = silver_sold_wastage - silver_pur_wastage

        silver_sold_making = Decimal(str(s_sold_making or 0))
        silver_pur_labour = Decimal(str(s_pur_labour or 0))
        silver_net_labour_profit = silver_sold_making - silver_pur_labour

        silver_sold_val = Decimal(str(s_sold_val or 0))
        silver_pur_val = Decimal(str(s_pur_val or 0))
        silver_net_val_profit = silver_sold_val - silver_pur_val

        # -------------------------------------------------------------
        # 3. DIAMOND ANALYSIS
        # -------------------------------------------------------------
        # 3a. Sold Diamond (Invoices)
        d_sold_q = db.query(
            func.coalesce(func.sum(DiamondCalculation.carat_weight), 0),
            func.coalesce(func.sum(DiamondCalculation.weight_gm), 0),
            func.coalesce(func.sum(DiamondCalculation.making_charges), 0),
            func.coalesce(func.sum(DiamondCalculation.total_diamond_value), 0)
        ).join(InvoiceItem, InvoiceItem.id == DiamondCalculation.invoice_item_id)\
         .join(Invoice, Invoice.id == InvoiceItem.invoice_id)\
         .filter(Invoice.company_id == company_id, Invoice.status != InvoiceStatus.CANCELLED)

        if start_dt:
            d_sold_q = d_sold_q.filter(Invoice.invoice_date >= start_dt)
        if end_dt:
            d_sold_q = d_sold_q.filter(Invoice.invoice_date <= end_dt)

        d_sold_cts, d_sold_gm, d_sold_making, d_sold_val = d_sold_q.first()

        # 3b. Purchased Diamond (Purchases)
        d_pur_q = db.query(
            func.coalesce(func.sum(PurchaseItem.gross_weight), 0),
            func.coalesce(func.sum(PurchaseItem.labour_charge), 0),
            func.coalesce(func.sum(PurchaseItem.taxable_amount), 0)
        ).join(Purchase, Purchase.id == PurchaseItem.purchase_id)\
         .filter(Purchase.company_id == company_id, Purchase.status != PurchaseStatus.CANCELLED, func.lower(PurchaseItem.metal_type) == 'diamond')

        if start_dt:
            d_pur_q = d_pur_q.filter(Purchase.created_at >= start_dt)
        if end_dt:
            d_pur_q = d_pur_q.filter(Purchase.created_at <= end_dt)

        d_pur_wt, d_pur_labour, d_pur_val = d_pur_q.first()

        diamond_sold_cts = Decimal(str(d_sold_cts or 0))
        diamond_sold_making = Decimal(str(d_sold_making or 0))
        diamond_pur_labour = Decimal(str(d_pur_labour or 0))
        diamond_net_making_profit = diamond_sold_making - diamond_pur_labour

        diamond_sold_val = Decimal(str(d_sold_val or 0))
        diamond_pur_val = Decimal(str(d_pur_val or 0))
        diamond_net_val_profit = diamond_sold_val - diamond_pur_val

        # -------------------------------------------------------------
        # 4. RECENT TRANSACTION LINE ITEMS
        # -------------------------------------------------------------
        transactions = []

        # Gold sales lines
        g_lines = db.query(
            Invoice.invoice_date,
            Invoice.invoice_number,
            InvoiceItem.item_name,
            GoldCalculation.gross_weight,
            GoldCalculation.touch_purity,
            GoldCalculation.wastage,
            GoldCalculation.fine_weight,
            GoldCalculation.making_charges_amount,
            GoldCalculation.total_gold_value
        ).join(InvoiceItem, InvoiceItem.id == GoldCalculation.invoice_item_id)\
         .join(Invoice, Invoice.id == InvoiceItem.invoice_id)\
         .filter(Invoice.company_id == company_id, Invoice.status != InvoiceStatus.CANCELLED)
        if start_dt:
            g_lines = g_lines.filter(Invoice.invoice_date >= start_dt)
        if end_dt:
            g_lines = g_lines.filter(Invoice.invoice_date <= end_dt)

        for row in g_lines.order_by(Invoice.invoice_date.desc()).limit(20).all():
            w_gms = float(Decimal(str(row[3] or 0)) * Decimal(str(row[5] or 0)) / Decimal('100'))
            transactions.append({
                "date": row[0].strftime("%Y-%m-%d") if row[0] else "",
                "type": "Sale",
                "bill_no": row[1],
                "item_name": row[2] or "Gold Item",
                "metal": "Gold",
                "weight_g": float(row[3] or 0),
                "touch_pct": float(row[4] or 0),
                "wastage_pct": float(row[5] or 0),
                "wastage_g": round(w_gms, 3),
                "fine_weight_g": float(row[6] or 0),
                "making_charges": float(row[7] or 0),
                "total_amount": float(row[8] or 0)
            })

        # Gold purchase lines
        g_pur_lines = db.query(
            Purchase.created_at,
            Purchase.purchase_number,
            PurchaseItem.item_name,
            PurchaseItem.gross_weight,
            PurchaseItem.touch_purity,
            PurchaseItem.wastage,
            PurchaseItem.fine_weight,
            PurchaseItem.labour_charge,
            PurchaseItem.taxable_amount
        ).join(Purchase, Purchase.id == PurchaseItem.purchase_id)\
         .filter(Purchase.company_id == company_id, Purchase.status != PurchaseStatus.CANCELLED, func.lower(PurchaseItem.metal_type) == 'gold')
        if start_dt:
            g_pur_lines = g_pur_lines.filter(Purchase.created_at >= start_dt)
        if end_dt:
            g_pur_lines = g_pur_lines.filter(Purchase.created_at <= end_dt)

        for row in g_pur_lines.order_by(Purchase.created_at.desc()).limit(20).all():
            w_gms = float(Decimal(str(row[3] or 0)) * Decimal(str(row[5] or 0)) / Decimal('100'))
            transactions.append({
                "date": row[0].strftime("%Y-%m-%d") if row[0] else "",
                "type": "Purchase",
                "bill_no": row[1],
                "item_name": row[2] or "Gold Purchase",
                "metal": "Gold",
                "weight_g": float(row[3] or 0),
                "touch_pct": float(row[4] or 0),
                "wastage_pct": float(row[5] or 0),
                "wastage_g": round(w_gms, 3),
                "fine_weight_g": float(row[6] or 0),
                "making_charges": float(row[7] or 0),
                "total_amount": float(row[8] or 0)
            })

        # Total combined profits
        total_making_profit = gold_net_labour_profit + silver_net_labour_profit + diamond_net_making_profit
        total_val_profit = gold_net_val_profit + silver_net_val_profit + diamond_net_val_profit

        return {
            "company_id": company_id,
            "gold_wastage_earned_gms": float(round(gold_sold_wastage, 3)),
            "gold_fine_sold_gms": float(round(Decimal(str(g_sold_fine or 0)), 3)),
            "silver_wastage_earned_gms": float(round(silver_sold_wastage, 3)),
            "silver_pure_sold_gms": float(round(Decimal(str(s_sold_pure or 0)), 3)),
            "summary": {
                "gold_net_wastage_profit_g": float(round(gold_net_wastage_profit, 3)),
                "silver_net_wastage_profit_g": float(round(silver_net_wastage_profit, 3)),
                "diamond_carats_sold": float(round(diamond_sold_cts, 4)),
                "total_making_profit_rs": float(round(total_making_profit, 2)),
                "total_value_profit_rs": float(round(total_val_profit, 2))
            },
            "gold": {
                "sold_fine_g": float(round(Decimal(str(g_sold_fine or 0)), 3)),
                "sold_wastage_g": float(round(gold_sold_wastage, 3)),
                "sold_making_rs": float(round(gold_sold_making, 2)),
                "sold_total_val_rs": float(round(gold_sold_val, 2)),
                "purchased_fine_g": float(round(Decimal(str(g_pur_fine or 0)), 3)),
                "purchased_wastage_g": float(round(gold_pur_wastage, 3)),
                "purchased_labour_rs": float(round(gold_pur_labour, 2)),
                "purchased_total_val_rs": float(round(gold_pur_val, 2)),
                "net_wastage_profit_g": float(round(gold_net_wastage_profit, 3)),
                "net_labour_profit_rs": float(round(gold_net_labour_profit, 2)),
                "net_val_profit_rs": float(round(gold_net_val_profit, 2))
            },
            "silver": {
                "sold_pure_g": float(round(Decimal(str(s_sold_pure or 0)), 3)),
                "sold_wastage_g": float(round(silver_sold_wastage, 3)),
                "sold_making_rs": float(round(silver_sold_making, 2)),
                "sold_total_val_rs": float(round(silver_sold_val, 2)),
                "purchased_pure_g": float(round(Decimal(str(s_pur_pure or 0)), 3)),
                "purchased_wastage_g": float(round(silver_pur_wastage, 3)),
                "purchased_labour_rs": float(round(silver_pur_labour, 2)),
                "purchased_total_val_rs": float(round(silver_pur_val, 2)),
                "net_wastage_profit_g": float(round(silver_net_wastage_profit, 3)),
                "net_labour_profit_rs": float(round(silver_net_labour_profit, 2)),
                "net_val_profit_rs": float(round(silver_net_val_profit, 2))
            },
            "diamond": {
                "sold_carats": float(round(diamond_sold_cts, 4)),
                "sold_weight_g": float(round(Decimal(str(d_sold_gm or 0)), 3)),
                "sold_making_rs": float(round(diamond_sold_making, 2)),
                "sold_total_val_rs": float(round(diamond_sold_val, 2)),
                "purchased_labour_rs": float(round(diamond_pur_labour, 2)),
                "purchased_total_val_rs": float(round(diamond_pur_val, 2)),
                "net_making_profit_rs": float(round(diamond_net_making_profit, 2)),
                "net_val_profit_rs": float(round(diamond_net_val_profit, 2))
            },
            "transactions": transactions
        }
