"""
Invoice PDF Generation Service
Generates professional PDF invoices with company details, items, and calculations.
"""
from decimal import Decimal
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from app.models.invoice import Invoice
from app.models.invoice_item import InvoiceItem
from app.models.gold_calculation import GoldCalculation
from app.models.silver_calculation import SilverCalculation
from app.models.purchase import Purchase
from app.models.exchange import Exchange
from app.models.supplier_ledger import SupplierLedger
from app.services.calculation_service import CalculationService
from app.models.setting import Setting


class InvoicePDFService:
    """Service to generate invoice PDF data for frontend rendering."""
    
    COMPANY_NAME = "SAIDEEP JEWELLERS"
    COMPANY_ADDRESS = "Takhatgarh khedawas"
    COMPANY_PHONE = "8504837854"
    COMPANY_EMAIL = ""
    COMPANY_GSTIN = ""
    
    @staticmethod
    def _get_company_details(db: Session, store_id: int = 1) -> Dict[str, str]:
        settings = db.query(Setting).all()
        settings_dict = {s.key: s.value for s in settings}
        
        # Override with store-specific settings if store_id != 1
        if store_id and store_id != 1:
            prefix = f"store_{store_id}_"
            for s in settings:
                if s.key.startswith(prefix):
                    pure_key = s.key[len(prefix):]
                    settings_dict[pure_key] = s.value

        from app.models.store import Store
        store = db.query(Store).filter(Store.id == store_id).first() if store_id else None

        default_name = "SAIDEEP JEWELLERS" if (store_id == 1) else (f"Store #{store_id}" if store_id else "Jewellery Store")
        name = store.name if (store and store.name) else (settings_dict.get('business_name') or default_name)
        address = store.address if (store and store.address) else (settings_dict.get('address') if store_id == 1 else (store.address if store else ""))
        phone = store.phone if (store and store.phone) else (settings_dict.get('phone') if store_id == 1 else (store.phone if store else ""))
        email = store.email if (store and store.email) else (settings_dict.get('email') if store_id == 1 else (store.email if store else ""))
        gstin = store.gstin if (store and store.gstin) else (settings_dict.get('gstin') if store_id == 1 else (store.gstin if store else ""))
        pan = store.pan if (store and store.pan) else (settings_dict.get('pan') or "")
        tagline = store.tagline if (store and store.tagline) else (settings_dict.get('tagline') or "Trust. Purity. Elegance.")
        logo_url = store.logo_url if (store and store.logo_url) else settings_dict.get('logo_url', '')
        
        # Read logo directly from disk and encode to base64 Data URL for instant, reliable rendering in PDFs
        logo_data_url = ""
        try:
            import os, base64
            search_dirs = [
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "static"),
                r"C:\Users\YASH SONI\Desktop\Saideep\jewellery-erp\backend\static",
                r"C:\Users\YASH SONI\Desktop\jeweller-app\backend\static"
            ]
            
            candidate_files = []
            if logo_url:
                clean_name = logo_url.split('/static/')[-1].split('?')[0].lstrip('/')
                if clean_name:
                    candidate_files.append(clean_name)
            if store_id:
                candidate_files.append(f"logo_store_{store_id}.png")
                candidate_files.append(f"logo_store_{store_id}.jpg")
                candidate_files.append(f"logo_store_{store_id}.jpeg")
                candidate_files.append(f"logo_store_{store_id}.webp")
            if store_id == 1:
                candidate_files.extend(["logo_store_1.png", "logo.png"])
            
            chosen_path = None
            for s_dir in search_dirs:
                if not os.path.exists(s_dir):
                    continue
                for c_name in candidate_files:
                    full_p = os.path.join(s_dir, c_name)
                    if os.path.exists(full_p) and os.path.getsize(full_p) > 0:
                        chosen_path = full_p
                        break
                if chosen_path:
                    break

            if chosen_path:
                with open(chosen_path, "rb") as f:
                    file_bytes = f.read()
                    encoded = base64.b64encode(file_bytes).decode("utf-8")
                    mime = "image/png"
                    if chosen_path.lower().endswith(('.jpg', '.jpeg')) or file_bytes.startswith(b'\xff\xd8'):
                        mime = "image/jpeg"
                    elif chosen_path.lower().endswith('.webp'):
                        mime = "image/webp"
                    logo_data_url = f"data:{mime};base64,{encoded}"
        except Exception:
            pass

        upi_name = settings_dict.get('upi_name') or name
        upi_id = settings_dict.get('upi_id') or ""

        return {
            'name': name,
            'address': address,
            'phone': phone,
            'email': email,
            'gstin': gstin,
            'pan': pan,
            'tagline': tagline,
            'logo_url': logo_url,
            'logo_data_url': logo_data_url,
            'upi_id': upi_id,
            'upi_name': upi_name,
            'bank_name': settings_dict.get('bank_name') or "",
            'bank_account_no': settings_dict.get('bank_account_no') or "",
            'bank_ifsc': settings_dict.get('bank_ifsc') or "",
            'print_hallmark': settings_dict.get('print_hallmark'),
            'print_wastage': settings_dict.get('print_wastage'),
            'print_making_charges': settings_dict.get('print_making_charges'),
            'print_remarks': settings_dict.get('print_remarks'),
        }

    @staticmethod
    def get_invoice_pdf_data(invoice_id: int, db: Session) -> Dict[str, Any]:
        """
        Get complete invoice data formatted for PDF generation.
        
        Returns:
        {
            'invoice': {...},
            'customer': {...},
            'items': [{...}],
            'company': {...},
            'totals': {...}
        }
        """
        # Fetch invoice with relationships
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            raise ValueError(f"Invoice {invoice_id} not found")
        
        # Company details
        company = InvoicePDFService._get_company_details(db, getattr(invoice, 'store_id', 1) or 1)
        
        # Invoice details
        invoice_data = {
            'invoice_number': invoice.invoice_number,
            'invoice_date': invoice.invoice_date.strftime('%Y-%m-%d'),
            'status': invoice.status.value,
            'subtotal': float(invoice.subtotal),
            'tax_amount': float(invoice.tax_amount),
            'discount_amount': float(invoice.discount_amount),
            'grand_total': float(invoice.grand_total)
        }
        
        # Calculate amount paid from the invoice's own cash_received field for hybrid billing,
        # or fallback to ledger if older legacy invoices used separate Payment vouchers.
        amount_paid = float(invoice.cash_received or 0)
        if amount_paid == 0 and invoice.customer_id:
            from app.models.customer_ledger import CustomerLedger
            payment_entry = db.query(CustomerLedger).filter(
                CustomerLedger.voucher_type == 'Payment',
                CustomerLedger.voucher_number == invoice.invoice_number
            ).first()
            if payment_entry:
                amount_paid = float(payment_entry.credit)
                
        # For hybrid/metal settlement bills, the true balance is tracked in the DB
        balance_due = float(invoice.balance_amount) if invoice.balance_amount is not None else (float(invoice.grand_total) - amount_paid)
        
        invoice_data['amount_paid'] = amount_paid
        invoice_data['balance_due'] = balance_due
        
        # Expose all hybrid fields directly to the PDF generator
        invoice_data['bill_type'] = invoice.bill_type.value if hasattr(invoice.bill_type, 'value') else invoice.bill_type
        invoice_data['settlement_type'] = invoice.settlement_type.value if hasattr(invoice.settlement_type, 'value') else invoice.settlement_type
        invoice_data['settlement_metal_type'] = invoice.settlement_metal_type.value if hasattr(invoice.settlement_metal_type, 'value') else invoice.settlement_metal_type
        invoice_data['metal_received_value'] = float(invoice.metal_received_value or 0)
        invoice_data['cash_received'] = float(invoice.cash_received or 0)
        invoice_data['balance_amount'] = float(invoice.balance_amount or 0)
        invoice_data['balance_metal_weight'] = float(invoice.balance_metal_weight or 0)
        invoice_data['gold_balance_metal_weight'] = float(invoice.gold_balance_metal_weight or 0)
        invoice_data['silver_balance_metal_weight'] = float(invoice.silver_balance_metal_weight or 0)
        invoice_data['metal_received_str'] = invoice.metal_received_str or ''
        customer_address_parts = []
        if invoice.customer:
            if invoice.customer.address:
                customer_address_parts.append(invoice.customer.address)
            if invoice.customer.city:
                customer_address_parts.append(invoice.customer.city)
                
        # Customer details
        customer_data = {
            'name': f"{invoice.customer.first_name} {invoice.customer.last_name or ''}".strip() if invoice.customer else 'Walk-in Customer',
            'phone': invoice.customer.phone_number if invoice.customer else '',
            'email': invoice.customer.email if invoice.customer else '',
            'address': ', '.join(customer_address_parts),
            'gstin': invoice.customer.gst_number if invoice.customer else '',
            'pan': invoice.customer.aadhaar_pan if invoice.customer else ''
        }
        
        # Items details
        items_data = []
        for item in invoice.items:
            item_dict = {
                'item_name': item.item_name,
                'item_type': item.item_type,
                'final_price': float(item.final_price)
            }
            
            # Add gold calculation details if present
            gold_calc = db.query(GoldCalculation).filter(
                GoldCalculation.invoice_item_id == item.id
            ).first()
            
            if gold_calc:
                item_dict.update({
                    'metal_type': 'GOLD',
                    'gross_weight': float(gold_calc.gross_weight),
                    'stone_weight': float(gold_calc.stone_weight),
                    'net_weight': float(gold_calc.net_weight),
                    'touch_purity': float(gold_calc.touch_purity),
                    'wastage': float(gold_calc.wastage),
                    'fine_weight': float(gold_calc.fine_weight),
                    'making_charges': float(gold_calc.making_charges_amount),
                    'making_charge_type': gold_calc.making_charge_type,
                    'making_charge_rate': float(gold_calc.making_charge_rate),
                    'hallmark_charges': float(gold_calc.hallmark_charges),
                    'other_charges': float(gold_calc.other_charges),
                    'discount': float(gold_calc.discount),
                    'metal_value': float(gold_calc.total_gold_value),
                    'applied_rate': float(gold_calc.applied_rate)
                })
            
            # Add silver calculation details if present
            silver_calc = db.query(SilverCalculation).filter(
                SilverCalculation.invoice_item_id == item.id
            ).first()
            
            if silver_calc:
                item_dict.update({
                    'metal_type': 'SILVER',
                    'gross_weight': float(silver_calc.gross_weight),
                    'stone_weight': float(silver_calc.stone_weight),
                    'pure_weight': float(silver_calc.pure_weight),
                    'tanch_percentage': float(silver_calc.tanch_percentage),
                    'wastage': float(silver_calc.wastage),
                    'fine_weight': float(silver_calc.pure_weight), # same thing
                    'making_charges': float(silver_calc.making_charges_amount),
                    'making_charge_type': silver_calc.making_charge_type,
                    'making_charge_rate': float(silver_calc.making_charge_rate),
                    'other_charges': float(silver_calc.other_charges),
                    'discount': float(silver_calc.discount),
                    'metal_value': float(silver_calc.total_silver_value),
                    'applied_rate': float(silver_calc.applied_rate)
                })
            
            items_data.append(item_dict)
        
        # Calculate totals
        total_items = len(items_data)
        total_weight = sum(
            item.get('net_weight', item.get('pure_weight', 0)) 
            for item in items_data
        )
        
        totals = {
            'total_items': total_items,
            'total_weight': float(CalculationService._round_final(
                Decimal(str(total_weight)),
                CalculationService.WEIGHT_PLACES
            )),
            'subtotal': float(invoice.subtotal),
            'tax_amount': float(invoice.tax_amount),
            'discount_amount': float(invoice.discount_amount),
            'grand_total': float(invoice.grand_total)
        }
        
        return {
            'type': 'sale',
            'invoice': invoice_data,
            'customer': customer_data,
            'items': items_data,
            'company': company,
            'totals': totals
        }

    @staticmethod
    def get_purchase_pdf_data(purchase_id: int, db: Session) -> Dict[str, Any]:
        """
        Get purchase data formatted for PDF generation.
        """
        purchase = db.query(Purchase).filter(Purchase.id == purchase_id).first()
        if not purchase:
            raise ValueError(f"Purchase {purchase_id} not found")
        
        company = InvoicePDFService._get_company_details(db, getattr(purchase, 'store_id', 1) or 1)
        
        cash_paid = float(purchase.cash_paid or 0)
        balance_due = float(purchase.balance_amount if purchase.balance_amount is not None else (purchase.grand_total - cash_paid))
        
        invoice_data = {
            'invoice_number': purchase.purchase_number,
            'invoice_date': purchase.created_at.strftime('%Y-%m-%d'),
            'status': purchase.status.value,
            'subtotal': float(purchase.total_taxable),
            'tax_amount': float(purchase.cgst + purchase.sgst + purchase.igst),
            'discount_amount': 0.0,
            'grand_total': float(purchase.grand_total),
            'amount_paid': cash_paid,
            'cash_paid': cash_paid,
            'cash_received': cash_paid,
            'balance_due': balance_due,
            'balance_amount': balance_due,
            'bill_type': purchase.bill_type or 'Cash',
            'settlement_type': purchase.settlement_type or 'Cash',
            'settlement_metal_type': purchase.settlement_metal_type,
            'metal_given_value': float(purchase.metal_given_value or 0),
            'metal_received_value': float(purchase.metal_given_value or 0),
            'gold_balance_metal_weight': float(purchase.gold_balance_metal_weight or 0),
            'silver_balance_metal_weight': float(purchase.silver_balance_metal_weight or 0)
        }

        address_parts = []
        if purchase.seller:
            if purchase.seller.address:
                address_parts.append(purchase.seller.address)
            if purchase.seller.city:
                address_parts.append(purchase.seller.city)
                
        customer_data = {
            'name': purchase.seller.name if purchase.seller else 'Unknown Seller',
            'phone': purchase.seller.mobile if purchase.seller else '',
            'email': '',
            'address': ', '.join(address_parts),
            'gstin': purchase.seller.gst_number if purchase.seller else '',
            'pan': purchase.seller.aadhaar_pan if purchase.seller else ''
        }
        
        items_data = []
        for item in purchase.items:
            items_data.append({
                'item_name': item.item_name,
                'metal_type': item.metal_type,
                'gross_weight': float(item.gross_weight),
                'stone_weight': float(item.stone_weight),
                'net_weight': float(item.net_weight),
                'pure_weight': float(item.fine_weight),
                'fine_weight': float(item.fine_weight),
                'touch_purity': float(item.touch_purity),
                'tanch_percentage': float(item.touch_purity),
                'making_charges': float(item.labour_charge + item.testing_melting_charge + item.hallmark_charge + item.other_charges),
                'metal_value': float(item.metal_value),
                'applied_rate': float(item.metal_rate),
                'final_price': float(item.taxable_amount)
            })
            
        total_weight = sum(item.get('net_weight', 0) for item in items_data)
        totals = {
            'total_items': len(items_data),
            'total_weight': float(total_weight),
            'subtotal': float(purchase.total_taxable),
            'tax_amount': float(purchase.cgst + purchase.sgst + purchase.igst),
            'discount_amount': 0.0,
            'grand_total': float(purchase.grand_total)
        }
        
        return {
            'type': 'purchase',
            'invoice': invoice_data,
            'customer': customer_data,
            'items': items_data,
            'company': company,
            'totals': totals
        }

    @staticmethod
    def get_exchange_pdf_data(exchange_id: int, db: Session) -> Dict[str, Any]:
        """
        Get exchange data formatted for PDF generation.
        """
        exchange = db.query(Exchange).filter(Exchange.id == exchange_id).first()
        if not exchange:
            raise ValueError(f"Exchange {exchange_id} not found")
        
        company = InvoicePDFService._get_company_details(db, getattr(exchange, 'store_id', 1) or 1)
        
        # Read settlement values from exchange entity with fallback to CustomerLedger
        amount_paid = float(getattr(exchange, 'amount_paid', 0.0) or 0.0)
        gold_balance_metal = float(getattr(exchange, 'gold_balance_metal_weight', 0.0) or 0.0)
        silver_balance_metal = float(getattr(exchange, 'silver_balance_metal_weight', 0.0) or 0.0)
        balance_due = float(exchange.balance_amount if getattr(exchange, 'balance_amount', None) is not None else exchange.difference_amount)
        settlement_type = getattr(exchange, 'settlement_type', None) or 'Cash'

        # Fallback to CustomerLedger if not populated on Exchange (for historical records)
        if amount_paid == 0.0 and gold_balance_metal == 0.0 and silver_balance_metal == 0.0:
            from app.models.customer_ledger import CustomerLedger
            ledger_entry = db.query(CustomerLedger).filter(
                CustomerLedger.voucher_number == f"EXC-{exchange.id}"
            ).first()
            if ledger_entry:
                is_metal = 'Settled in Metal' in (ledger_entry.description or '')
                settlement_type = 'Metal' if is_metal else 'Cash'
                gold_balance_metal = float(ledger_entry.gold_debit or 0.0)
                silver_balance_metal = float(ledger_entry.silver_debit or 0.0)
                amount_paid = float(ledger_entry.credit or 0.0)
                balance_due = max(0.0, float(ledger_entry.debit or 0.0) - amount_paid)

        # Ensure unpaid non-metal charges (GST, etc.) are always payable in cash and never zeroed out
        non_metal_charges = float(exchange.gst_amount or 0.0)
        if settlement_type in ('Metal', 'Hybrid') and balance_due < (non_metal_charges - amount_paid) - 0.01:
            balance_due = max(0.0, non_metal_charges - amount_paid)

        settlement_metal_type = None
        if gold_balance_metal > 0.001 and silver_balance_metal > 0.001:
            settlement_metal_type = 'Both'
        elif gold_balance_metal > 0.001:
            settlement_metal_type = 'Gold'
        elif silver_balance_metal > 0.001:
            settlement_metal_type = 'Silver'

        vouch_number = f"EXC-{exchange.id}-{exchange.verification_token}" if getattr(exchange, 'verification_token', None) else f"EXC-{exchange.id}"
        invoice_data = {
            'invoice_number': vouch_number,
            'invoice_date': exchange.exchange_date.strftime('%Y-%m-%d'),
            'status': "Completed",
            'subtotal': float(exchange.total_new_value),
            'tax_amount': float(exchange.gst_amount),
            'discount_amount': 0.0,
            'grand_total': float(exchange.total_new_value + exchange.gst_amount),
            'total_old_value': float(exchange.total_old_value),
            'total_new_value': float(exchange.total_new_value),
            'difference_amount': float(exchange.difference_amount),
            'amount_paid': amount_paid,
            'cash_paid': amount_paid,
            'cash_received': amount_paid,
            'balance_due': balance_due,
            'balance_amount': balance_due,
            'gold_balance_metal_weight': gold_balance_metal,
            'silver_balance_metal_weight': silver_balance_metal,
            'settlement_type': settlement_type,
            'settlement_metal_type': settlement_metal_type,
            'metal_received_value': float(exchange.total_old_value or 0.0),
            'bill_type': 'Exchange'
        }
        
        customer_data = {
            'name': f"{exchange.customer.first_name} {exchange.customer.last_name or ''}".strip() if exchange.customer else 'Unknown Customer',
            'phone': exchange.customer.phone_number if exchange.customer else '',
            'email': exchange.customer.email if exchange.customer else '',
            'address': exchange.customer.address if exchange.customer else ''
        }
        
        old_items_data = []
        for item in exchange.old_items:
            old_items_data.append({
                'item_name': item.item_name,
                'metal_type': item.metal,
                'gross_weight': float(item.gross_weight),
                'stone_weight': float(item.stone_weight),
                'net_weight': float(item.net_weight),
                'tanch_percentage': float(item.touch),
                'wastage': float(item.wastage),
                'fine_weight': float(item.fine_weight),
                'labour_charge': float(item.labour_charge),
                'testing_melting_charge': float(item.testing_melting_charge),
                'hallmark_charge': float(item.hallmark_charge),
                'other_charges': float(item.other_charges),
                'discount': float(item.discount),
                'applied_rate': float(item.rate_applied),
                'final_price': float(item.calculated_value)
            })

        new_items_data = []
        for item in exchange.new_items:
            stock = item.stock_item
            
            # Extract fields if stock exists, else defaults
            gross_weight = float(stock.gross_weight) if stock else float(item.net_weight)
            stone_weight = float(stock.stone_weight) if stock else 0.0
            
            making_type = (stock.making_type or 'flat').lower() if stock else 'flat'
            raw_making = float(stock.making_charge) if stock else 0.0
            hallmark = float(stock.hallmark) if stock else 0.0
            other = float(stock.other_charges) if stock else 0.0
            
            final_p = float(item.final_price)
            net_wt = float(item.net_weight)
            
            # Calculate total making charges and derive metal value and rate
            if making_type == 'percent':
                making_charge_rate = raw_making
                # final_p = metal_val + metal_val * (rate/100) + hallmark + other
                metal_value = (final_p - hallmark - other) / (1 + making_charge_rate / 100) if (1 + making_charge_rate / 100) > 0 else 0
                making_charges = metal_value * (making_charge_rate / 100)
            elif making_type == 'per_gram':
                making_charge_rate = raw_making
                making_charges = making_charge_rate * net_wt
                metal_value = final_p - making_charges - hallmark - other
            else: # flat
                making_charge_rate = None
                making_charges = raw_making
                metal_value = final_p - making_charges - hallmark - other
                
            applied_rate = metal_value / net_wt if net_wt > 0 else 0.0

            new_items_data.append({
                'item_name': item.item_name,
                'metal_type': item.metal,
                'gross_weight': float(item.gross_weight),
                'stone_weight': float(item.stone_weight),
                'net_weight': net_wt,
                'touch_purity': float(item.touch_purity),
                'wastage': float(item.wastage),
                'fine_weight': float(item.fine_weight),
                'making_charge_type': item.making_charge_type,
                'making_charge_rate': float(item.making_charge_rate),
                'making_charges': float(item.making_charges_amount),
                'hallmark_charges': float(item.hallmark_charges),
                'other_charges': float(item.other_charges),
                'discount': float(item.discount),
                'applied_rate': float(item.rate_applied),
                'final_price': final_p
            })
            
        totals = {
            'total_items': len(old_items_data) + len(new_items_data),
            'total_weight': float(sum(item.get('net_weight', 0) for item in new_items_data)),
            'subtotal': float(exchange.total_new_value),
            'tax_amount': float(exchange.gst_amount),
            'discount_amount': float(exchange.total_old_value),
            'grand_total': float(exchange.difference_amount)
        }
        
        return {
            'type': 'exchange',
            'invoice': invoice_data,
            'customer': customer_data,
            'items': new_items_data,
            'old_items': old_items_data,
            'company': company,
            'totals': totals
        }
