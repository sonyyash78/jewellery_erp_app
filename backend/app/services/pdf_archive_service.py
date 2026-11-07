import os
import re
from pathlib import Path
from decimal import Decimal
from typing import Dict, Any, List, Optional
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from app.models.setting import Setting
from app.models.store import Store
from app.models.invoice import Invoice
from app.models.invoice_item import InvoiceItem
from app.models.purchase import Purchase
from app.models.purchase_item import PurchaseItem
from app.models.exchange import Exchange
from app.models.exchange_item import ExchangeItem
from app.models.customer import Customer
from app.models.customer_ledger import CustomerLedger
from app.models.seller import Seller
from app.models.supplier_ledger import SupplierLedger


def _sanitize_name(name: Optional[str], default: str = "Unknown") -> str:
    """Sanitizes names for Windows folder and file naming."""
    if not name or not str(name).strip():
        return default
    clean = re.sub(r'[\\/*?:"<>|]', '_', str(name).strip())
    clean = re.sub(r'\s+', '_', clean)
    return clean[:60]


def _format_curr(val: Any) -> str:
    try:
        f = float(val or 0.0)
        return f"Rs. {f:,.2f}"
    except Exception:
        return "Rs. 0.00"


def _format_weight(val: Any) -> str:
    try:
        f = float(val or 0.0)
        return f"{f:.3f}g"
    except Exception:
        return "0.000g"


def _get_store_header(db: Session, store_id: int = 1) -> Dict[str, str]:
    settings = db.query(Setting).all()
    s_map = {s.key: s.value for s in settings}

    store = db.query(Store).filter(Store.id == store_id).first() if store_id else None

    name = (store.name if store and store.name else None) or s_map.get("business_name") or s_map.get("store_name") or "SAIDEEP JEWELLERS"
    address = (store.address if store and store.address else None) or s_map.get("address") or s_map.get("store_address") or "Takhatgarh, Rajasthan"
    phone = (store.phone if store and store.phone else None) or s_map.get("phone") or s_map.get("store_phone") or "8504837854"
    gstin = (store.gstin if store and store.gstin else None) or s_map.get("gstin") or s_map.get("store_gstin") or ""
    tagline = (store.tagline if store and store.tagline else None) or s_map.get("tagline") or "Trust. Purity. Elegance."

    return {
        "name": name,
        "address": address,
        "phone": phone,
        "gstin": gstin,
        "tagline": tagline
    }


def _build_header_flowables(store_info: Dict[str, str], title: str, subtitle: str) -> List[Any]:
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=colors.HexColor('#1E293B'),
        alignment=0
    )
    meta_style = ParagraphStyle(
        'StoreMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#475569'),
        alignment=0
    )
    badge_style = ParagraphStyle(
        'DocBadge',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#B45309'),
        alignment=2
    )
    badge_sub_style = ParagraphStyle(
        'DocBadgeSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#64748B'),
        alignment=2
    )

    left_cell = [
        Paragraph(f"<b>{store_info['name']}</b>", title_style),
        Paragraph(f"{store_info['address']} &bull; Ph: {store_info['phone']}", meta_style),
        Paragraph(f"GSTIN: {store_info['gstin'] or 'N/A'} &bull; <i>{store_info['tagline']}</i>", meta_style),
    ]

    right_cell = [
        Paragraph(f"<b>{title}</b>", badge_style),
        Paragraph(subtitle, badge_sub_style),
    ]

    header_table = Table([[left_cell, right_cell]], colWidths=[340, 195])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))

    return [
        header_table,
        Spacer(1, 6),
        HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#D97706'), spaceBefore=2, spaceAfter=8)
    ]


# -------------------------------------------------------------
# 1. SALES INVOICE PDF GENERATION
# -------------------------------------------------------------
def generate_invoice_pdf(invoice: Invoice, store_info: Dict[str, str], output_file: Path):
    doc = SimpleDocTemplate(
        str(output_file),
        pagesize=A4,
        leftMargin=30,
        rightMargin=30,
        topMargin=26,
        bottomMargin=26
    )
    styles = getSampleStyleSheet()
    elements = []

    date_str = invoice.invoice_date.strftime("%d-%b-%Y") if invoice.invoice_date else "N/A"
    elements.extend(_build_header_flowables(store_info, "TAX INVOICE", f"No: {invoice.invoice_number}<br/>Date: {date_str}"))

    cust_name = f"{invoice.customer.first_name} {invoice.customer.last_name or ''}".strip() if invoice.customer else "Walk-in Customer"
    cust_phone = invoice.customer.phone_number if invoice.customer else "N/A"
    cust_addr = f"{invoice.customer.address or ''} {invoice.customer.city or ''}".strip() if invoice.customer else ""

    info_data = [
        [
            Paragraph(f"<b>Billed To:</b> {cust_name}<br/><b>Phone:</b> {cust_phone}<br/><b>Address:</b> {cust_addr or 'N/A'}", styles['Normal']),
            Paragraph(f"<b>Invoice #:</b> {invoice.invoice_number}<br/><b>Date:</b> {date_str}<br/><b>Status:</b> {invoice.status.value if hasattr(invoice.status, 'value') else invoice.status}", styles['Normal']),
        ]
    ]
    info_table = Table(info_data, colWidths=[310, 225])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 10))

    headers = ['Item Description', 'Metal', 'Gross Wt', 'Net Wt', 'Purity', 'Rate/g', 'Making', 'Total (Rs)']
    rows = [headers]
    for it in (invoice.items or []):
        name = it.item_name or "Jewellery Item"
        metal = it.item_type.value if hasattr(it.item_type, 'value') else (str(it.item_type) if it.item_type else "Gold")
        
        gross_wt = 0.0
        net_wt = 0.0
        purity_str = "91.6%"
        rate_str = "-"
        making_str = "0"

        if it.gold_calculation:
            gross_wt = float(it.gold_calculation.gross_weight or 0)
            net_wt = float(it.gold_calculation.net_weight or 0)
            purity_str = f"{float(it.gold_calculation.touch_purity or 91.6):.1f}%"
            rate_str = f"{float(it.gold_calculation.applied_rate or 0):,.0f}"
            making_str = f"{float(it.gold_calculation.making_charges_amount or 0):,.0f}"
        elif it.silver_calculation:
            gross_wt = float(it.silver_calculation.gross_weight or 0)
            net_wt = gross_wt - float(it.silver_calculation.stone_weight or 0)
            purity_str = f"{float(it.silver_calculation.tanch_percentage or 80.0):.1f}%"
            rate_str = f"{float(it.silver_calculation.applied_rate or 0):,.0f}"
            making_str = f"{float(it.silver_calculation.making_charges_amount or 0):,.0f}"
        elif it.stock_item:
            gross_wt = float(it.stock_item.gross_weight or 0)
            net_wt = float(it.stock_item.net_weight or it.stock_item.gross_weight or 0)
            purity_str = str(it.stock_item.purity or "91.6%")

        gross = _format_weight(gross_wt) if gross_wt > 0 else "-"
        net = _format_weight(net_wt) if net_wt > 0 else "-"
        total = f"{float(it.final_price or 0):,.2f}"
        rows.append([name, metal, gross, net, purity_str, rate_str, making_str, total])

    if len(rows) == 1:
        rows.append(["Standard Jewellery Sale", "Gold", "-", "-", "-", "-", "-", _format_curr(invoice.grand_total)])

    items_table = Table(rows, colWidths=[155, 45, 55, 55, 45, 55, 55, 70])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('ALIGN', (0,0), (1,-1), 'LEFT'),
        ('ALIGN', (2,0), (-1,-1), 'RIGHT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 10))

    metal_val = float(invoice.metal_received_value or 0)
    if metal_val > 0:
        ex_p = Paragraph(f"<b>Old Metal Exchange Settlement:</b> Less {_format_curr(metal_val)} ({invoice.metal_received_str or 'Old Gold/Silver Adjusted'})", styles['Normal'])
        elements.append(ex_p)
        elements.append(Spacer(1, 6))

    subtotal = float(invoice.subtotal or invoice.grand_total or 0)
    tax = float(invoice.tax_amount or 0)
    grand = float(invoice.grand_total or 0)
    paid = float(invoice.cash_received or 0)
    bal = float(invoice.balance_amount if invoice.balance_amount is not None else (grand - paid))

    summary_data = [
        ['Subtotal:', _format_curr(subtotal)],
        ['GST (3%):', _format_curr(tax)],
        ['Grand Total:', _format_curr(grand)],
        ['Paid (Cash/UPI):', _format_curr(paid)],
        ['Balance Due:', _format_curr(bal)],
    ]
    if float(invoice.gold_balance_metal_weight or 0) > 0:
        summary_data.append(['Gold Due (g):', _format_weight(invoice.gold_balance_metal_weight)])
    if float(invoice.silver_balance_metal_weight or 0) > 0:
        summary_data.append(['Silver Due (g):', _format_weight(invoice.silver_balance_metal_weight)])

    sum_table = Table(summary_data, colWidths=[100, 110])
    sum_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (0,-1), 'RIGHT'),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('FONTNAME', (0,2), (1,2), 'Helvetica-Bold'),
        ('LINEBELOW', (0,2), (1,2), 1, colors.HexColor('#D97706')),
        ('FONTNAME', (0,-1), (1,-1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0,-1), (1,-1), colors.HexColor('#DC2626') if bal > 0 else colors.HexColor('#16A34A')),
    ]))

    sign_p = Paragraph("<br/><br/>Authorized Signatory<br/><b>" + store_info['name'] + "</b>", styles['Normal'])
    bottom_table = Table([[sign_p, sum_table]], colWidths=[325, 210])
    bottom_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
        ('ALIGN', (0,0), (0,0), 'LEFT'),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
    ]))
    elements.append(KeepTogether([bottom_table]))

    doc.build(elements)


# -------------------------------------------------------------
# 2. EXCHANGE VOUCHER PDF GENERATION
# -------------------------------------------------------------
def generate_exchange_pdf(exchange: Exchange, store_info: Dict[str, str], output_file: Path):
    doc = SimpleDocTemplate(
        str(output_file),
        pagesize=A4,
        leftMargin=30,
        rightMargin=30,
        topMargin=26,
        bottomMargin=26
    )
    styles = getSampleStyleSheet()
    elements = []

    date_str = exchange.exchange_date.strftime("%d-%b-%Y") if exchange.exchange_date else "N/A"
    exc_no = f"EXC-{exchange.id}"
    elements.extend(_build_header_flowables(store_info, "EXCHANGE VOUCHER", f"No: {exc_no}<br/>Date: {date_str}"))

    cust_name = f"{exchange.customer.first_name} {exchange.customer.last_name or ''}".strip() if exchange.customer else "Walk-in Customer"
    cust_phone = exchange.customer.phone_number if exchange.customer else "N/A"

    info_data = [
        [
            Paragraph(f"<b>Customer:</b> {cust_name}<br/><b>Phone:</b> {cust_phone}", styles['Normal']),
            Paragraph(f"<b>Voucher #:</b> {exc_no}<br/><b>Date:</b> {date_str}", styles['Normal']),
        ]
    ]
    info_table = Table(info_data, colWidths=[310, 225])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("<b>Old Jewellery Received (Return / Scrap):</b>", styles['Heading4']))
    elements.append(Spacer(1, 4))
    old_rows = [['Description', 'Metal', 'Gross Wt', 'Net Wt', 'Melt Touch', 'Rate/g', 'Credit Value (Rs)']]
    for oi in (exchange.old_items or []):
        old_rows.append([
            oi.item_name or "Old Ornament",
            oi.metal or "Gold",
            _format_weight(oi.gross_weight),
            _format_weight(oi.net_weight),
            f"{float(oi.touch or 80):.1f}%",
            f"{float(oi.rate_applied or 0):,.0f}",
            _format_curr(oi.calculated_value)
        ])
    if len(old_rows) == 1:
        old_rows.append(["Old Jewellery Lot", "Gold", "-", "-", "-", "-", _format_curr(exchange.total_old_value)])

    t_old = Table(old_rows, colWidths=[155, 55, 60, 60, 60, 65, 80])
    t_old.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#334155')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('ALIGN', (2,0), (-1,-1), 'RIGHT'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(t_old)
    elements.append(Spacer(1, 10))

    diff = float(exchange.difference_amount or 0)
    paid = float(exchange.amount_paid or 0)
    bal = float(exchange.balance_amount or 0)

    summary_data = [
        ['Total Old Jewellery Value:', _format_curr(exchange.total_old_value)],
        ['Total New Jewellery Value:', _format_curr(exchange.total_new_value)],
        ['Net Difference:', _format_curr(diff)],
        ['Cash Paid / Settled:', _format_curr(paid)],
        ['Balance Due:', _format_curr(bal)],
    ]
    sum_t = Table(summary_data, colWidths=[150, 110])
    sum_t.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('FONTNAME', (0,2), (1,2), 'Helvetica-Bold'),
        ('LINEBELOW', (0,2), (1,2), 1, colors.HexColor('#D97706')),
        ('FONTNAME', (0,-1), (1,-1), 'Helvetica-Bold'),
    ]))
    sign_p = Paragraph("<br/><br/>Customer Signature &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Authorized Signatory", styles['Normal'])
    elements.append(KeepTogether([Table([[sign_p, sum_t]], colWidths=[275, 260])]))

    doc.build(elements)


# -------------------------------------------------------------
# 3. PURCHASE BILL PDF GENERATION
# -------------------------------------------------------------
def generate_purchase_pdf(purchase: Purchase, store_info: Dict[str, str], output_file: Path):
    doc = SimpleDocTemplate(
        str(output_file),
        pagesize=A4,
        leftMargin=30,
        rightMargin=30,
        topMargin=26,
        bottomMargin=26
    )
    styles = getSampleStyleSheet()
    elements = []

    date_str = purchase.created_at.strftime("%d-%b-%Y") if purchase.created_at else "N/A"
    pur_no = purchase.purchase_number or f"PUR-{purchase.id}"
    elements.extend(_build_header_flowables(store_info, "PURCHASE VOUCHER", f"No: {pur_no}<br/>Date: {date_str}"))

    seller_name = purchase.seller.name if purchase.seller else "Wholesale Supplier"
    seller_phone = purchase.seller.mobile if purchase.seller else "N/A"
    seller_addr = purchase.seller.address if purchase.seller else ""

    info_data = [
        [
            Paragraph(f"<b>Supplier / Karigar:</b> {seller_name}<br/><b>Phone:</b> {seller_phone}<br/><b>Address:</b> {seller_addr or 'N/A'}", styles['Normal']),
            Paragraph(f"<b>Purchase #:</b> {pur_no}<br/><b>Date:</b> {date_str}<br/><b>Bill Type:</b> {purchase.bill_type or 'Regular'}", styles['Normal']),
        ]
    ]
    info_table = Table(info_data, colWidths=[310, 225])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 10))

    headers = ['Item Description', 'Metal', 'Gross Wt', 'Net Wt', 'Rate (Rs)', 'Making', 'Total (Rs)']
    rows = [headers]
    for pi in (purchase.items or []):
        rows.append([
            pi.item_name or "Purchase Stock Item",
            pi.metal_type or "Gold",
            _format_weight(pi.gross_weight),
            _format_weight(pi.net_weight),
            f"{float(pi.metal_rate or 0):,.0f}" if pi.metal_rate else "-",
            f"{float(pi.labour_charge or 0):,.0f}" if pi.labour_charge else "0",
            _format_curr(pi.taxable_amount)
        ])
    if len(rows) == 1:
        rows.append(["Jewellery Purchase Inward", "Gold", "-", "-", "-", "-", _format_curr(purchase.grand_total)])

    t_items = Table(rows, colWidths=[175, 50, 60, 60, 60, 60, 70])
    t_items.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('ALIGN', (2,0), (-1,-1), 'RIGHT'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(t_items)
    elements.append(Spacer(1, 10))

    grand = float(purchase.grand_total or 0)
    paid = float(purchase.cash_paid or 0)
    bal = float(purchase.balance_amount if purchase.balance_amount is not None else (grand - paid))

    sum_data = [
        ['Taxable Subtotal:', _format_curr(purchase.total_taxable or grand)],
        ['GST:', _format_curr(float(purchase.cgst or 0) + float(purchase.sgst or 0))],
        ['Grand Total:', _format_curr(grand)],
        ['Cash/Bank Paid:', _format_curr(paid)],
        ['Balance Due to Supplier:', _format_curr(bal)],
    ]
    if float(purchase.gold_balance_metal_weight or 0) > 0:
        sum_data.append(['Gold Due (g):', _format_weight(purchase.gold_balance_metal_weight)])
    if float(purchase.silver_balance_metal_weight or 0) > 0:
        sum_data.append(['Silver Due (g):', _format_weight(purchase.silver_balance_metal_weight)])

    sum_t = Table(sum_data, colWidths=[150, 110])
    sum_t.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('FONTNAME', (0,2), (1,2), 'Helvetica-Bold'),
        ('LINEBELOW', (0,2), (1,2), 1, colors.HexColor('#D97706')),
        ('FONTNAME', (0,-1), (1,-1), 'Helvetica-Bold'),
    ]))
    sign_p = Paragraph("<br/><br/>Supplier Stamp / Signature &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Store Receiver Sign", styles['Normal'])
    elements.append(KeepTogether([Table([[sign_p, sum_t]], colWidths=[275, 260])]))

    doc.build(elements)


# -------------------------------------------------------------
# 4. CUSTOMER STATEMENT / LEDGER PDF GENERATION
# -------------------------------------------------------------
def generate_customer_statement_pdf(customer: Customer, db: Session, store_info: Dict[str, str], output_file: Path):
    doc = SimpleDocTemplate(
        str(output_file),
        pagesize=A4,
        leftMargin=30,
        rightMargin=30,
        topMargin=26,
        bottomMargin=26
    )
    styles = getSampleStyleSheet()
    elements = []

    now_str = datetime.now().strftime("%d-%b-%Y %I:%M %p")
    cust_full = f"{customer.first_name} {customer.last_name or ''}".strip()
    elements.extend(_build_header_flowables(store_info, "ACCOUNT STATEMENT", f"Customer Ledger<br/>Generated: {now_str}"))

    bal = float(customer.outstanding_balance or 0)
    fine_gold = float(customer.fine_gold_balance or 0)
    fine_silver = float(customer.fine_silver_balance or 0)

    summary_box_data = [
        [
            Paragraph(f"<b>Customer Profile:</b><br/><b>Name:</b> {cust_full}<br/><b>Phone:</b> {customer.phone_number}<br/><b>Address:</b> {customer.address or ''} {customer.city or ''}", styles['Normal']),
            Paragraph(f"<b>Current Outstanding Dues:</b><br/>"
                      f"<font color='{'#DC2626' if bal > 0 else '#16A34A'}' size='12'><b>{_format_curr(bal)}</b></font><br/>"
                      f"Fine Gold Due: <b>{_format_weight(fine_gold)}</b><br/>"
                      f"Fine Silver Due: <b>{_format_weight(fine_silver)}</b>", styles['Normal']),
        ]
    ]
    sb_table = Table(summary_box_data, colWidths=[295, 240])
    sb_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F1F5F9')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(sb_table)
    elements.append(Spacer(1, 10))

    entries = db.query(CustomerLedger).filter(
        CustomerLedger.customer_id == customer.id
    ).order_by(CustomerLedger.date.asc(), CustomerLedger.id.asc()).all()

    headers = ['Date', 'Voucher Type', 'Ref Number', 'Debit (Bill)', 'Credit (Paid)', 'Balance (Rs)']
    rows = [headers]
    running_bal = 0.0

    for e in entries:
        d_str = e.date.strftime("%d-%b-%Y") if e.date else ""
        v_type = e.voucher_type or "Sale"
        v_no = e.voucher_number or f"#{e.id}"
        debit = float(e.debit or 0)
        credit = float(e.credit or 0)
        running_bal += (debit - credit)

        rows.append([
            d_str,
            v_type,
            v_no,
            _format_curr(debit) if debit > 0 else "-",
            _format_curr(credit) if credit > 0 else "-",
            _format_curr(running_bal)
        ])

    if len(rows) == 1:
        rows.append(["-", "Initial Opening", "-", "-", "-", _format_curr(bal)])

    t_ledger = Table(rows, colWidths=[75, 95, 95, 90, 90, 90])
    t_ledger.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('ALIGN', (3,0), (-1,-1), 'RIGHT'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
    ]))
    elements.append(t_ledger)

    doc.build(elements)


# -------------------------------------------------------------
# 5. SUPPLIER STATEMENT / LEDGER PDF GENERATION
# -------------------------------------------------------------
def generate_supplier_statement_pdf(seller: Seller, db: Session, store_info: Dict[str, str], output_file: Path):
    doc = SimpleDocTemplate(
        str(output_file),
        pagesize=A4,
        leftMargin=30,
        rightMargin=30,
        topMargin=26,
        bottomMargin=26
    )
    styles = getSampleStyleSheet()
    elements = []

    now_str = datetime.now().strftime("%d-%b-%Y %I:%M %p")
    elements.extend(_build_header_flowables(store_info, "SUPPLIER STATEMENT", f"Karigar & Wholesaler Ledger<br/>Generated: {now_str}"))

    bal = float(seller.outstanding_balance or 0)
    fine_gold = float(seller.fine_gold_balance or 0)
    fine_silver = float(seller.fine_silver_balance or 0)

    summary_box_data = [
        [
            Paragraph(f"<b>Supplier Profile:</b><br/><b>Name:</b> {seller.name}<br/><b>Mobile:</b> {seller.mobile}<br/><b>Address:</b> {seller.address or 'N/A'}", styles['Normal']),
            Paragraph(f"<b>Payable Balance to Supplier:</b><br/>"
                      f"<font color='{'#DC2626' if bal > 0 else '#16A34A'}' size='12'><b>{_format_curr(bal)}</b></font><br/>"
                      f"Fine Gold Due: <b>{_format_weight(fine_gold)}</b><br/>"
                      f"Fine Silver Due: <b>{_format_weight(fine_silver)}</b>", styles['Normal']),
        ]
    ]
    sb_table = Table(summary_box_data, colWidths=[295, 240])
    sb_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F1F5F9')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(sb_table)
    elements.append(Spacer(1, 10))

    entries = db.query(SupplierLedger).filter(
        SupplierLedger.seller_id == seller.id
    ).order_by(SupplierLedger.date.asc(), SupplierLedger.id.asc()).all()

    headers = ['Date', 'Voucher Type', 'Ref Number', 'Purchase (Credit)', 'Paid (Debit)', 'Balance (Rs)']
    rows = [headers]
    running_bal = 0.0

    for e in entries:
        d_str = e.date.strftime("%d-%b-%Y") if e.date else ""
        v_type = e.voucher_type or "Purchase"
        v_no = e.voucher_number or f"#{e.id}"
        credit = float(e.credit or 0)
        debit = float(e.debit or 0)
        running_bal += (credit - debit)

        rows.append([
            d_str,
            v_type,
            v_no,
            _format_curr(credit) if credit > 0 else "-",
            _format_curr(debit) if debit > 0 else "-",
            _format_curr(running_bal)
        ])

    if len(rows) == 1:
        rows.append(["-", "Initial Balance", "-", "-", "-", _format_curr(bal)])

    t_ledger = Table(rows, colWidths=[75, 95, 95, 90, 90, 90])
    t_ledger.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('ALIGN', (3,0), (-1,-1), 'RIGHT'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
    ]))
    elements.append(t_ledger)

    doc.build(elements)


# -------------------------------------------------------------
# MAIN MASTER ORCHESTRATOR: ARCHIVE ALL STORE DOCUMENTS
# -------------------------------------------------------------
def archive_all_store_documents(db: Session, store_id: int, base_dir: Path, force_refresh: bool = False) -> Dict[str, Any]:
    """
    Scans the database and exports all documents into:
    base_dir / "Archived_PDFs" /
        Purchases / [Supplier_Name] / (Purchases + Statement)
        Sales / [Customer_Name] / (Invoices + Exchanges + Statement)
        Sales / Walkin_Customers /
    """
    store_info = _get_store_header(db, store_id)
    archive_root = base_dir / "Archived_PDFs"
    sales_root = archive_root / "Sales"
    purchases_root = archive_root / "Purchases"

    sales_root.mkdir(parents=True, exist_ok=True)
    purchases_root.mkdir(parents=True, exist_ok=True)

    counts = {
        "sales_invoices": 0,
        "exchanges": 0,
        "customer_statements": 0,
        "purchases": 0,
        "supplier_statements": 0,
        "total_files": 0
    }

    # 1. PROCESS PURCHASES & SUPPLIER STATEMENTS
    sellers = db.query(Seller).filter(Seller.store_id == store_id).all()
    seller_map = {s.id: s for s in sellers}

    for s in sellers:
        folder_name = _sanitize_name(f"{s.name}_{s.mobile}", default=f"Supplier_{s.id}")
        s_dir = purchases_root / folder_name
        s_dir.mkdir(parents=True, exist_ok=True)

        stmt_pdf = s_dir / f"Statement_{_sanitize_name(s.name)}.pdf"
        try:
            generate_supplier_statement_pdf(s, db, store_info, stmt_pdf)
            counts["supplier_statements"] += 1
            counts["total_files"] += 1
        except Exception as e:
            print(f"[Archive] Error generating supplier statement for {s.name}: {e}")

    all_purchases = db.query(Purchase).filter(Purchase.store_id == store_id).all()
    for pur in all_purchases:
        s_obj = seller_map.get(pur.seller_id) if pur.seller_id else None
        folder_name = _sanitize_name(f"{s_obj.name}_{s_obj.mobile}", default=f"Supplier_{pur.seller_id}") if s_obj else "Unassigned_Suppliers"
        target_dir = purchases_root / folder_name
        target_dir.mkdir(parents=True, exist_ok=True)

        p_no = _sanitize_name(pur.purchase_number or f"PUR-{pur.id}")
        p_date = pur.created_at.strftime("%Y-%m-%d") if pur.created_at else "date"
        pur_pdf = target_dir / f"Purchase_{p_no}_{p_date}.pdf"

        if force_refresh or not pur_pdf.exists():
            try:
                generate_purchase_pdf(pur, store_info, pur_pdf)
                counts["purchases"] += 1
                counts["total_files"] += 1
            except Exception as e:
                print(f"[Archive] Error generating purchase PDF {p_no}: {e}")
        else:
            counts["purchases"] += 1

    # 2. PROCESS SALES (INVOICES + EXCHANGES) & CUSTOMER STATEMENTS
    customers = db.query(Customer).filter(Customer.store_id == store_id).all()
    cust_map = {c.id: c for c in customers}

    for c in customers:
        c_full = f"{c.first_name} {c.last_name or ''}".strip()
        folder_name = _sanitize_name(f"{c_full}_{c.phone_number}", default=f"Customer_{c.id}")
        c_dir = sales_root / folder_name
        c_dir.mkdir(parents=True, exist_ok=True)

        stmt_pdf = c_dir / f"Statement_{_sanitize_name(c_full)}.pdf"
        try:
            generate_customer_statement_pdf(c, db, store_info, stmt_pdf)
            counts["customer_statements"] += 1
            counts["total_files"] += 1
        except Exception as e:
            print(f"[Archive] Error generating customer statement for {c_full}: {e}")

    all_invoices = db.query(Invoice).filter(Invoice.store_id == store_id).all()
    for inv in all_invoices:
        c_obj = cust_map.get(inv.customer_id) if inv.customer_id else None
        if c_obj:
            c_full = f"{c_obj.first_name} {c_obj.last_name or ''}".strip()
            folder_name = _sanitize_name(f"{c_full}_{c_obj.phone_number}", default=f"Customer_{inv.customer_id}")
        else:
            folder_name = "Walkin_Customers"

        target_dir = sales_root / folder_name
        target_dir.mkdir(parents=True, exist_ok=True)

        inv_no = _sanitize_name(inv.invoice_number or f"INV-{inv.id}")
        inv_date = inv.invoice_date.strftime("%Y-%m-%d") if inv.invoice_date else "date"
        inv_pdf = target_dir / f"Invoice_{inv_no}_{inv_date}.pdf"

        if force_refresh or not inv_pdf.exists():
            try:
                generate_invoice_pdf(inv, store_info, inv_pdf)
                counts["sales_invoices"] += 1
                counts["total_files"] += 1
            except Exception as e:
                print(f"[Archive] Error generating invoice PDF {inv_no}: {e}")
        else:
            counts["sales_invoices"] += 1

    all_exchanges = db.query(Exchange).filter(Exchange.store_id == store_id).all()
    for exc in all_exchanges:
        c_obj = cust_map.get(exc.customer_id) if exc.customer_id else None
        if c_obj:
            c_full = f"{c_obj.first_name} {c_obj.last_name or ''}".strip()
            folder_name = _sanitize_name(f"{c_full}_{c_obj.phone_number}", default=f"Customer_{exc.customer_id}")
        else:
            folder_name = "Walkin_Customers"

        target_dir = sales_root / folder_name
        target_dir.mkdir(parents=True, exist_ok=True)

        exc_no = _sanitize_name(f"EXC-{exc.id}")
        exc_date = exc.exchange_date.strftime("%Y-%m-%d") if exc.exchange_date else "date"
        exc_pdf = target_dir / f"Exchange_{exc_no}_{exc_date}.pdf"

        if force_refresh or not exc_pdf.exists():
            try:
                generate_exchange_pdf(exc, store_info, exc_pdf)
                counts["exchanges"] += 1
                counts["total_files"] += 1
            except Exception as e:
                print(f"[Archive] Error generating exchange PDF {exc_no}: {e}")
        else:
            counts["exchanges"] += 1

    return {
        "status": "success",
        "counts": counts,
        "archive_dir": str(archive_root)
    }
