import string
import os
import shutil
import threading
import time
import re
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

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


def get_gst_subfolder(company_id: Optional[int], doc_number: Optional[str]) -> str:
    """Returns 'GST' if company_id == 2 or document number indicates GST, else 'Without_GST'."""
    if company_id == 2:
        return "GST"
    if doc_number:
        clean = str(doc_number).upper()
        if clean.startswith(("SJ/S", "SJ_S", "SJ/P", "SJ_P", "SJ/E", "SJ_E", "PG/S", "PG_S", "PG/P", "PG_P", "PG/E", "PG_E")):
            return "GST"
        if "/S/" in clean or "/P/" in clean or "/E/" in clean:
            return "GST"
    return "Without_GST"

def _sanitize_name(name: Optional[str], default: str = "Unknown") -> str:
    """Sanitizes names for Windows folder and file naming."""
    if not name or not str(name).strip():
        return default
    raw = str(name).strip()
    if re.fullmatch(r'walk[\s_-]*in(?:[\s_-]*customer)?s?', raw, flags=re.IGNORECASE):
        return "Walkin_Customer"
    clean = re.sub(r'[\\/*?:"<>|]', '_', raw)
    clean = re.sub(r'\s+', '_', clean)
    return clean[:60]

def remove_archived_document(category: str, folder_name: Optional[str], doc_number: str, doc_date: Optional[str] = None) -> bool:
    """
    Deletes the archived PDF file of a deleted or cancelled document from both
    local PC storage and all connected USB drives, and prunes empty folders.
    """
    from app.core.config import DATA_DIR
    import shutil

    if not doc_number:
        return False

    clean_doc = _sanitize_name(doc_number).lower()
    clean_date = _sanitize_name(doc_date).lower() if doc_date else ""
    success = False

    roots = [DATA_DIR / "Archived_PDFs"]
    for letter in ["D", "E", "F", "G", "H"]:
        r = Path(f"{letter}:\\JewelleryERP_Data\\Archived_PDFs")
        if Path(f"{letter}:\\").exists():
            roots.append(r)

    for root in roots:
        cat_dir = root / category
        if not cat_dir.exists():
            continue

        search_dirs = []
        if folder_name:
            exact = cat_dir / folder_name
            if exact.exists():
                search_dirs.append(exact)
            else:
                for d in cat_dir.iterdir():
                    if d.is_dir() and folder_name.lower() in d.name.lower():
                        search_dirs.append(d)
        else:
            search_dirs = [d for d in cat_dir.iterdir() if d.is_dir()]

        for d in search_dirs:
            for f in list(d.glob("*.pdf")):
                f_lower = f.name.lower()
                matches = (clean_doc in f_lower or f_lower == f"{clean_doc}.pdf")
                if clean_date:
                    matches = matches or (clean_date in f_lower or f_lower == f"{clean_date}.pdf")
                if matches:
                    try:
                        f.unlink()
                        print(f"[Archive Delete] Removed {f}")
                        success = True
                    except Exception as e:
                        print(f"[Archive Delete Error] Could not remove {f}: {e}")

            # Prune if no transaction bills remain
            remaining_bills = [f for f in d.glob("*.pdf") if not f.name.lower().startswith("statement_")]
            if len(remaining_bills) == 0:
                for stmt in d.glob("*.pdf"):
                    try:
                        stmt.unlink()
                    except Exception:
                        pass
                try:
                    d.rmdir()
                    print(f"[Archive Delete] Pruned empty folder {d}")
                except Exception:
                    pass

    return success


def remove_party_folder(category: str, folder_name: str) -> bool:
    """Removes an entire customer or supplier folder when that party is deleted."""
    from app.core.config import DATA_DIR
    import shutil

    if not folder_name:
        return False

    roots = [DATA_DIR / "Archived_PDFs"]
    for letter in ["D", "E", "F", "G", "H"]:
        r = Path(f"{letter}:\\JewelleryERP_Data\\Archived_PDFs")
        if Path(f"{letter}:\\").exists():
            roots.append(r)

    success = False
    for root in roots:
        cat_dir = root / category
        if not cat_dir.exists():
            continue
        exact = cat_dir / folder_name
        if exact.exists() and exact.is_dir():
            try:
                shutil.rmtree(exact, ignore_errors=True)
                success = True
                print(f"[Archive Delete] Removed party folder {exact}")
            except Exception as e:
                print(f"[Archive Delete Error] Could not remove {exact}: {e}")
        else:
            for d in list(cat_dir.iterdir()):
                if d.is_dir() and folder_name.lower() in d.name.lower():
                    try:
                        shutil.rmtree(d, ignore_errors=True)
                        success = True
                    except Exception:
                        pass
    return success


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

    name = (store.name if store and store.name else None) or s_map.get("business_name") or s_map.get("store_name") or "Jewellery Store"

    address = (store.address if store and store.address else None) or s_map.get("address") or s_map.get("store_address") or ""

    phone = (store.phone if store and store.phone else None) or s_map.get("phone") or s_map.get("store_phone") or ""

    gstin = (store.gstin if store and store.gstin else None) or s_map.get("gstin") or s_map.get("store_gstin") or ""

    tagline = (store.tagline if store and store.tagline else None) or s_map.get("tagline") or ""

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
    is_gst_doc = (getattr(invoice, "company_id", None) == 2) or ("/S/" in str(getattr(invoice, "invoice_number", "")))
    doc_title = "TAX INVOICE" if is_gst_doc else "RETAIL INVOICE"

    elements.extend(_build_header_flowables(store_info, doc_title, f"No: {invoice.invoice_number}<br/>Date: {date_str}"))

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

            purity_str = f"{float(it.gold_calculation.touch_purity or 91.6):.1f}"

            rate_str = f"{float(it.gold_calculation.applied_rate or 0):,.0f}"

            making_str = f"{float(it.gold_calculation.making_charges_amount or 0):,.0f}"

        elif it.silver_calculation:

            gross_wt = float(it.silver_calculation.gross_weight or 0)

            net_wt = gross_wt - float(it.silver_calculation.stone_weight or 0)

            purity_str = f"{float(it.silver_calculation.tanch_percentage or 80.0):.1f}"

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

    if getattr(exchange, 'new_items', None) and len(exchange.new_items) > 0:

        elements.append(Paragraph("<b>New Jewellery Purchased / Selected:</b>", styles['Heading4']))

        elements.append(Spacer(1, 4))

        new_rows = [['Description', 'Metal', 'Gross Wt', 'Net Wt', 'Purity', 'Rate/g', 'Total (Rs)']]

        for ni in exchange.new_items:

            new_rows.append([

                ni.item_name or "New Ornament",

                ni.metal or "Gold",

                _format_weight(ni.gross_weight),

                _format_weight(ni.net_weight),

                f"{float(ni.touch_purity or 91.6):.1f}",

                f"{float(ni.rate_applied or 0):,.0f}",

                _format_curr(ni.final_price)

            ])

        t_new = Table(new_rows, colWidths=[155, 55, 60, 60, 60, 65, 80])

        t_new.setStyle(TableStyle([

            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),

            ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#D4AF37')),

            ('FONTSIZE', (0,0), (-1,-1), 8),

            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),

            ('ALIGN', (2,0), (-1,-1), 'RIGHT'),

            ('TOPPADDING', (0,0), (-1,-1), 4),

            ('BOTTOMPADDING', (0,0), (-1,-1), 4),

        ]))

        elements.append(t_new)

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

            f"{float(oi.touch or 80):.1f}",

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

def _collect_statement_targets(
    archive_root: Path,
    category: str,
    folder_name: str,
    active_dirs: set,
    has_ledger: bool,
) -> List[str]:
    """Return active GST/Without_GST subfolders needing a party statement."""
    targets: List[str] = []
    for g_sub in ["GST", "Without_GST"]:
        d = archive_root / g_sub / category / folder_name
        has_docs = d.exists() and any(not f.name.startswith("Statement_") for f in d.glob("*.pdf"))
        if (g_sub, folder_name) in active_dirs or has_docs:
            targets.append(g_sub)
    if not targets and has_ledger:
        targets.append("Without_GST")
    return targets


_ARCHIVE_LOCK = threading.Lock()


def _load_statement_state(archive_root: Path) -> Dict[str, str]:
    state_file = archive_root / ".statement_state.json"
    if not state_file.exists():
        return {}
    try:
        data = json.loads(state_file.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save_statement_state(archive_root: Path, state: Dict[str, str]):
    state_file = archive_root / ".statement_state.json"
    tmp_file = archive_root / f".statement_state_{os.getpid()}.tmp"
    try:
        tmp_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
        os.replace(tmp_file, state_file)
    except Exception:
        if tmp_file.exists():
            try:
                tmp_file.unlink()
            except Exception:
                pass


def _bill_needs_refresh(
    prev_state: Dict[str, str],
    next_state: Dict[str, str],
    bill_key: str,
    bill_sig: str,
    pdf_path: Path,
    force_refresh: bool,
) -> bool:
    """Only generate when missing, forced, or an already-tracked bill changed."""
    prev_sig = prev_state.get(bill_key)
    next_state[bill_key] = bill_sig
    if force_refresh or not pdf_path.exists():
        return True
    return prev_sig is not None and prev_sig != bill_sig


def _cleanup_legacy_duplicates(archive_root: Path):
    """Remove obsolete *_new.pdf duplicates and duplicate space-named Walk-in Customer folders."""
    try:
        for dup in archive_root.rglob("*_new.pdf"):
            clean_peer = dup.with_name(f"{dup.stem[:-4]}.pdf")
            if clean_peer.exists():
                try:
                    dup.unlink()
                except Exception:
                    pass
    except Exception:
        pass

    for g_sub in ("GST", "Without_GST"):
        for cat in ("Sales", "Purchases", "Exchanges"):
            cat_dir = archive_root / g_sub / cat
            walkin_clean = cat_dir / "Walkin_Customer"
            walkin_space = cat_dir / "Walk-in Customer"
            if walkin_space.exists() and walkin_space.is_dir():
                try:
                    for item in list(walkin_space.iterdir()):
                        if item.is_file():
                            dest_peer = walkin_clean / item.name
                            if not dest_peer.exists():
                                walkin_clean.mkdir(parents=True, exist_ok=True)
                                shutil.move(str(item), str(dest_peer))
                            else:
                                item.unlink()
                    if not any(walkin_space.iterdir()):
                        walkin_space.rmdir()
                except Exception:
                    pass


def archive_all_store_documents(
    db: Session,
    store_id: int,
    base_dir: Path,
    force_refresh: bool = False,
    refresh_statements: bool = False,
) -> Dict[str, Any]:
    """Thread-safe wrapper preventing concurrent archive jobs from colliding on PDFs or Edge processes."""
    with _ARCHIVE_LOCK:
        return _archive_all_store_documents_impl(
            db,
            store_id=store_id,
            base_dir=base_dir,
            force_refresh=force_refresh,
            refresh_statements=refresh_statements,
        )


def _archive_all_store_documents_impl(
    db: Session,
    store_id: int,
    base_dir: Path,
    force_refresh: bool = False,
    refresh_statements: bool = False,
) -> Dict[str, Any]:
    """
    Scans the database and exports all documents into:
    base_dir / "Archived_PDFs" /
        GST /
            Purchases / [Supplier_Name] / ([Purchase_No].pdf + Statement)
            Sales / [Customer_Name] / ([Invoice_No].pdf + Statement)
            Exchanges / [Customer_Name] / ([Exchange_No].pdf)
        Without_GST /
            Purchases / [Supplier_Name] / ([Purchase_No].pdf + Statement)
            Sales / [Customer_Name] / ([Invoice_No].pdf + Statement)
            Exchanges / [Customer_Name] / ([Exchange_No].pdf)
    """
    store_info = _get_store_header(db, store_id)
    archive_root = base_dir / "Archived_PDFs"

    for g_sub in ["GST", "Without_GST"]:
        for cat in ["Sales", "Purchases", "Exchanges"]:
            (archive_root / g_sub / cat).mkdir(parents=True, exist_ok=True)

    counts = {
        "sales_invoices": 0,
        "exchanges": 0,
        "customer_statements": 0,
        "purchases": 0,
        "supplier_statements": 0,
        "total_files": 0,
    }

    from app.services.invoice_pdf_service import InvoicePDFService
    from app.services.luxury_pdf_service import (
        generate_luxury_bill_html,
        generate_luxury_statement_html,
        render_html_to_pdf,
    )
    from app.services.gst_pdf_template import generate_gst_tax_invoice_html
    from app.models.purchase import PurchaseStatus
    from app.models.invoice import InvoiceStatus
    from app.models.company import Company

    sellers = db.query(Seller).filter(Seller.store_id == store_id).all()
    seller_map = {s.id: s for s in sellers}
    customers = db.query(Customer).filter(Customer.store_id == store_id).all()
    cust_map = {c.id: c for c in customers}
    comp_map = {c.id: c for c in db.query(Company).all()}

    prev_stmt_state = _load_statement_state(archive_root)
    next_stmt_state = dict(prev_stmt_state)

    # Build HTML strings & pending render jobs on the main thread (SQLAlchemy Session is not thread-safe).
    render_jobs: List[Dict[str, Any]] = []
    mirror_items: List[tuple[Path, Path]] = []
    active_seller_dirs = set()
    active_customer_dirs = set()

    # 1. PROCESS PURCHASES
    all_purchases = db.query(Purchase).filter(
        Purchase.store_id == store_id,
        Purchase.status != PurchaseStatus.CANCELLED,
        Purchase.status != "CANCELLED",
    ).all()

    for pur in all_purchases:
        s_obj = seller_map.get(pur.seller_id) if pur.seller_id else None
        folder_name = _sanitize_name(s_obj.name, default=f"Supplier_{pur.seller_id}") if s_obj else "Suppliers"
        is_gst = (
            (pur.company_id == 2)
            or bool(str(getattr(pur, "purchase_number", "")).startswith(("SJ/P", "PG/P", "SJ_", "PG_")))
            or ("/P/" in str(getattr(pur, "purchase_number", "")))
        )
        gst_folder = "GST" if is_gst else "Without_GST"
        active_seller_dirs.add((gst_folder, folder_name))

        target_dir = archive_root / gst_folder / "Purchases" / folder_name
        target_dir.mkdir(parents=True, exist_ok=True)
        p_no = _sanitize_name(getattr(pur, "purchase_number", None) or f"PUR-{pur.id}")
        pur_pdf = target_dir / f"{p_no}.pdf"
        rel_path = Path(gst_folder) / "Purchases" / folder_name / f"{p_no}.pdf"

        pur_key = f"pur:{pur.id}"
        pur_sig = (
            f"{p_no}|{float(getattr(pur, 'grand_total', 0.0) or 0.0):.2f}"
            f"|{float(getattr(pur, 'cash_paid', 0.0) or 0.0):.2f}"
            f"|{float(getattr(pur, 'metal_given_value', 0.0) or 0.0):.2f}"
            f"|{float(getattr(pur, 'balance_amount', 0.0) or 0.0):.2f}"
            f"|{float(getattr(pur, 'gold_balance_metal_weight', 0.0) or 0.0):.3f}"
            f"|{float(getattr(pur, 'silver_balance_metal_weight', 0.0) or 0.0):.3f}"
            f"|{getattr(pur, 'status', '')}|{folder_name}|{gst_folder}"
        )
        if _bill_needs_refresh(prev_stmt_state, next_stmt_state, pur_key, pur_sig, pur_pdf, force_refresh):
            try:
                p_data = InvoicePDFService.get_purchase_pdf_data(pur.id, db)
                p_html = generate_gst_tax_invoice_html(p_data) if is_gst else generate_luxury_bill_html(p_data)
                render_jobs.append({
                    "html": p_html,
                    "primary_pdf": pur_pdf,
                    "extra_copies": [],
                    "mirror_pairs": [(pur_pdf, rel_path)],
                    "count_key": "purchases",
                    "state_key": pur_key,
                    "fallback": lambda p=pur, path=pur_pdf: generate_purchase_pdf(p, store_info, path),
                    "label": p_no,
                })
            except Exception as e:
                try:
                    generate_purchase_pdf(pur, store_info, pur_pdf)
                    counts["purchases"] += 1
                    mirror_items.append((pur_pdf, rel_path))
                except Exception as e2:
                    print(f"[Archive] Error generating purchase PDF {p_no}: {e} / {e2}")
        else:
            counts["purchases"] += 1
            mirror_items.append((pur_pdf, rel_path))

    # 2. PROCESS SUPPLIER STATEMENTS (render HTML once per supplier, copy to active folders)
    for s in sellers:
        folder_name = _sanitize_name(s.name, default=f"Supplier_{s.id}")
        try:
            ledgers = db.query(SupplierLedger).filter(SupplierLedger.seller_id == s.id).order_by(SupplierLedger.date.asc()).all()
            target_gsubs = _collect_statement_targets(archive_root, "Purchases", folder_name, active_seller_dirs, bool(ledgers))
            if not target_gsubs:
                continue

            stmt_name = f"Statement_{_sanitize_name(s.name)}.pdf"
            target_pdfs = [
                (archive_root / g_sub / "Purchases" / folder_name / stmt_name, Path(g_sub) / "Purchases" / folder_name / stmt_name)
                for g_sub in target_gsubs
            ]
            cash_val = float(getattr(s, "outstanding_balance", 0.0) or getattr(s, "current_balance", 0.0) or 0.0)
            gold_val = float(getattr(s, "fine_gold_balance", 0.0) or 0.0)
            silver_val = float(getattr(s, "fine_silver_balance", 0.0) or 0.0)
            max_lid = max((int(getattr(l, "id", 0) or 0) for l in ledgers), default=0)
            sum_d = sum(float(getattr(l, "debit", 0.0) or 0.0) for l in ledgers)
            sum_c = sum(float(getattr(l, "credit", 0.0) or 0.0) for l in ledgers)
            sum_gd = sum(float(getattr(l, "gold_debit", 0.0) or 0.0) for l in ledgers)
            sum_gc = sum(float(getattr(l, "gold_credit", 0.0) or 0.0) for l in ledgers)
            stmt_key = f"sup:{s.id}"
            stmt_sig = (
                f"{s.name}|{s.mobile or ''}|{cash_val:.2f}|{gold_val:.3f}|{silver_val:.3f}"
                f"|{len(ledgers)}|{max_lid}|{sum_d:.2f}|{sum_c:.2f}|{sum_gd:.3f}|{sum_gc:.3f}|{','.join(sorted(target_gsubs))}"
            )

            missing_file = any(not p.exists() for p, _ in target_pdfs)
            sig_changed = refresh_statements and (prev_stmt_state.get(stmt_key) != stmt_sig)
            needs_render = force_refresh or missing_file or sig_changed
            next_stmt_state[stmt_key] = stmt_sig
            if not needs_render:
                counts["supplier_statements"] += len(target_pdfs)
                mirror_items.extend(target_pdfs)
                continue

            entries = [{
                "date": (l.date.strftime("%d-%b-%Y") if getattr(l, "date", None) else ""),
                "type": l.voucher_type or "Ledger",
                "number": l.voucher_number or "-",
                "description": l.description or "-",
                "debit": float(l.debit or 0.0),
                "credit": float(l.credit or 0.0),
                "balance": float(l.balance or 0.0),
                "gold_debit": float(getattr(l, "gold_debit", 0.0) or 0.0),
                "gold_credit": float(getattr(l, "gold_credit", 0.0) or 0.0),
            } for l in ledgers]
            s_html = generate_luxury_statement_html(
                s.name,
                s.mobile or "",
                "Supplier",
                entries,
                store_info,
                float(getattr(s, "outstanding_balance", 0.0) or getattr(s, "current_balance", 0.0) or 0.0),
                float(getattr(s, "fine_gold_balance", 0.0) or 0.0),
                float(getattr(s, "fine_silver_balance", 0.0) or 0.0),
            )
            primary_pdf, _ = target_pdfs[0]
            primary_pdf.parent.mkdir(parents=True, exist_ok=True)
            render_jobs.append({
                "html": s_html,
                "primary_pdf": primary_pdf,
                "extra_copies": [p for p, _ in target_pdfs[1:]],
                "mirror_pairs": target_pdfs,
                "count_key": "supplier_statements",
                "fallback": lambda sel=s, path=primary_pdf: generate_supplier_statement_pdf(sel, db, store_info, path),
                "label": stmt_name,
            })
        except Exception as e:
            print(f"[Archive] Error preparing supplier statement for {s.name}: {e}")

    # 3. PROCESS SALES INVOICES
    all_invoices = db.query(Invoice).filter(
        Invoice.store_id == store_id,
        Invoice.status != InvoiceStatus.CANCELLED,
        Invoice.status != "Cancelled",
    ).all()

    for inv in all_invoices:
        c_obj = cust_map.get(inv.customer_id) if inv.customer_id else None
        if c_obj:
            c_full = f"{c_obj.first_name} {c_obj.last_name or ''}".strip()
            folder_name = _sanitize_name(c_full, default=f"Customer_{inv.customer_id}")
        else:
            b_name = getattr(inv, "buyer_name", None) or "Walkin_Customer"
            folder_name = _sanitize_name(b_name, default="Walkin_Customer")

        co_obj = comp_map.get(inv.company_id)
        if co_obj is not None:
            is_gst = bool(co_obj.gst_enabled)
        else:
            is_gst = (
                (inv.company_id == 2)
                or bool(str(getattr(inv, "invoice_number", "")).startswith(("SJ/S", "PG/S", "SJ_", "PG_")))
                or ("/S/" in str(getattr(inv, "invoice_number", "")))
            )
        gst_folder = "GST" if is_gst else "Without_GST"
        active_customer_dirs.add((gst_folder, folder_name))

        target_dir = archive_root / gst_folder / "Sales" / folder_name
        target_dir.mkdir(parents=True, exist_ok=True)
        inv_no = _sanitize_name(inv.invoice_number or f"INV-{inv.id}")
        inv_pdf = target_dir / f"{inv_no}.pdf"
        rel_path = Path(gst_folder) / "Sales" / folder_name / f"{inv_no}.pdf"

        co_sig = f"{co_obj.name}|{co_obj.gstin}|{co_obj.address}|{co_obj.phone}" if co_obj else ""
        inv_key = f"inv:{inv.id}"
        inv_sig = (
            f"{inv_no}|{float(getattr(inv, 'grand_total', 0.0) or 0.0):.2f}"
            f"|{float(getattr(inv, 'cash_received', 0.0) or 0.0):.2f}"
            f"|{float(getattr(inv, 'metal_received_value', 0.0) or 0.0):.2f}"
            f"|{float(getattr(inv, 'balance_amount', 0.0) or 0.0):.2f}"
            f"|{float(getattr(inv, 'gold_balance_metal_weight', 0.0) or 0.0):.3f}"
            f"|{float(getattr(inv, 'silver_balance_metal_weight', 0.0) or 0.0):.3f}"
            f"|{getattr(inv, 'status', '')}|{folder_name}|{gst_folder}|{co_sig}"
        )
        if _bill_needs_refresh(prev_stmt_state, next_stmt_state, inv_key, inv_sig, inv_pdf, force_refresh):
            try:
                inv_data = InvoicePDFService.get_invoice_pdf_data(inv.id, db)
                inv_html = generate_gst_tax_invoice_html(inv_data) if is_gst else generate_luxury_bill_html(inv_data)
                render_jobs.append({
                    "html": inv_html,
                    "primary_pdf": inv_pdf,
                    "extra_copies": [],
                    "mirror_pairs": [(inv_pdf, rel_path)],
                    "count_key": "sales_invoices",
                    "state_key": inv_key,
                    "fallback": lambda i=inv, path=inv_pdf: generate_invoice_pdf(i, store_info, path),
                    "label": inv_no,
                })
            except Exception as e:
                try:
                    generate_invoice_pdf(inv, store_info, inv_pdf)
                    counts["sales_invoices"] += 1
                    mirror_items.append((inv_pdf, rel_path))
                except Exception as e2:
                    print(f"[Archive] Error generating invoice PDF {inv_no}: {e} / {e2}")
        else:
            counts["sales_invoices"] += 1
            mirror_items.append((inv_pdf, rel_path))

    # 4. PROCESS EXCHANGES
    all_exchanges = db.query(Exchange).filter(
        Exchange.store_id == store_id,
        getattr(Exchange, "status", None) != "Cancelled",
    ).all()

    for exc in all_exchanges:
        c_obj = cust_map.get(exc.customer_id) if exc.customer_id else None
        if c_obj:
            c_full = f"{c_obj.first_name} {c_obj.last_name or ''}".strip()
            folder_name = _sanitize_name(c_full, default=f"Customer_{exc.customer_id}")
        else:
            folder_name = "Walkin_Customer"

        is_gst = (
            (exc.company_id == 2)
            or bool(str(getattr(exc, "exchange_number", "")).startswith(("SJ/E", "PG/E", "SJ_", "PG_")))
            or ("/E/" in str(getattr(exc, "exchange_number", "")))
        )
        gst_folder = "GST" if is_gst else "Without_GST"

        target_dir = archive_root / gst_folder / "Exchanges" / folder_name
        target_dir.mkdir(parents=True, exist_ok=True)
        exc_no = _sanitize_name(getattr(exc, "exchange_number", None) or f"EXC-{exc.id}")
        exc_pdf = target_dir / f"{exc_no}.pdf"
        rel_path = Path(gst_folder) / "Exchanges" / folder_name / f"{exc_no}.pdf"

        exc_key = f"exc:{exc.id}"
        exc_sig = (
            f"{exc_no}|{float(getattr(exc, 'grand_total', 0.0) or 0.0):.2f}"
            f"|{float(getattr(exc, 'difference_amount', 0.0) or 0.0):.2f}"
            f"|{float(getattr(exc, 'amount_paid', 0.0) or 0.0):.2f}"
            f"|{float(getattr(exc, 'balance_amount', 0.0) or 0.0):.2f}"
            f"|{float(getattr(exc, 'gold_balance_metal_weight', 0.0) or 0.0):.3f}"
            f"|{float(getattr(exc, 'silver_balance_metal_weight', 0.0) or 0.0):.3f}"
            f"|{getattr(exc, 'status', '')}|{folder_name}|{gst_folder}"
        )
        if _bill_needs_refresh(prev_stmt_state, next_stmt_state, exc_key, exc_sig, exc_pdf, force_refresh):
            try:
                exc_data = InvoicePDFService.get_exchange_pdf_data(exc.id, db)
                exc_html = generate_luxury_bill_html(exc_data)
                render_jobs.append({
                    "html": exc_html,
                    "primary_pdf": exc_pdf,
                    "extra_copies": [],
                    "mirror_pairs": [(exc_pdf, rel_path)],
                    "count_key": "exchanges",
                    "state_key": exc_key,
                    "fallback": lambda x=exc, path=exc_pdf: generate_exchange_pdf(x, store_info, path),
                    "label": exc_no,
                })
            except Exception as e:
                try:
                    generate_exchange_pdf(exc, store_info, exc_pdf)
                    counts["exchanges"] += 1
                    mirror_items.append((exc_pdf, rel_path))
                except Exception as e2:
                    print(f"[Archive] Error generating exchange PDF {exc_no}: {e} / {e2}")
        else:
            counts["exchanges"] += 1
            mirror_items.append((exc_pdf, rel_path))

    # 5. PROCESS CUSTOMER STATEMENTS (render HTML once per customer, copy to active folders)
    for c in customers:
        c_full = f"{c.first_name} {c.last_name or ''}".strip()
        folder_name = _sanitize_name(c_full, default=f"Customer_{c.id}")
        try:
            ledgers = db.query(CustomerLedger).filter(CustomerLedger.customer_id == c.id).order_by(CustomerLedger.date.asc()).all()
            target_gsubs = _collect_statement_targets(archive_root, "Sales", folder_name, active_customer_dirs, bool(ledgers))
            if not target_gsubs:
                continue

            stmt_name = f"Statement_{_sanitize_name(c_full)}.pdf"
            target_pdfs = [
                (archive_root / g_sub / "Sales" / folder_name / stmt_name, Path(g_sub) / "Sales" / folder_name / stmt_name)
                for g_sub in target_gsubs
            ]
            cash_val = float(c.outstanding_balance or 0.0)
            gold_val = float(c.fine_gold_balance or 0.0)
            silver_val = float(c.fine_silver_balance or 0.0)
            max_lid = max((int(getattr(l, "id", 0) or 0) for l in ledgers), default=0)
            sum_d = sum(float(getattr(l, "debit", 0.0) or 0.0) for l in ledgers)
            sum_c = sum(float(getattr(l, "credit", 0.0) or 0.0) for l in ledgers)
            sum_gd = sum(float(getattr(l, "gold_debit", 0.0) or 0.0) for l in ledgers)
            sum_gc = sum(float(getattr(l, "gold_credit", 0.0) or 0.0) for l in ledgers)
            stmt_key = f"cust:{c.id}"
            stmt_sig = (
                f"{c_full}|{c.phone_number or ''}|{cash_val:.2f}|{gold_val:.3f}|{silver_val:.3f}"
                f"|{len(ledgers)}|{max_lid}|{sum_d:.2f}|{sum_c:.2f}|{sum_gd:.3f}|{sum_gc:.3f}|{','.join(sorted(target_gsubs))}"
            )

            missing_file = any(not p.exists() for p, _ in target_pdfs)
            sig_changed = refresh_statements and (prev_stmt_state.get(stmt_key) != stmt_sig)
            needs_render = force_refresh or missing_file or sig_changed
            next_stmt_state[stmt_key] = stmt_sig
            if not needs_render:
                counts["customer_statements"] += len(target_pdfs)
                mirror_items.extend(target_pdfs)
                continue

            entries = [{
                "date": (l.date.strftime("%d-%b-%Y") if getattr(l, "date", None) else ""),
                "type": l.voucher_type or "Ledger",
                "number": l.voucher_number or "-",
                "description": l.description or "-",
                "debit": float(l.debit or 0.0),
                "credit": float(l.credit or 0.0),
                "balance": float(l.balance or 0.0),
                "gold_debit": float(l.gold_debit or 0.0),
                "gold_credit": float(l.gold_credit or 0.0),
            } for l in ledgers]
            c_html = generate_luxury_statement_html(
                c_full,
                c.phone_number or "",
                "Customer",
                entries,
                store_info,
                float(c.outstanding_balance or 0.0),
                float(c.fine_gold_balance or 0.0),
                float(c.fine_silver_balance or 0.0),
            )
            primary_pdf, _ = target_pdfs[0]
            primary_pdf.parent.mkdir(parents=True, exist_ok=True)
            render_jobs.append({
                "html": c_html,
                "primary_pdf": primary_pdf,
                "extra_copies": [p for p, _ in target_pdfs[1:]],
                "mirror_pairs": target_pdfs,
                "count_key": "customer_statements",
                "fallback": lambda cust=c, path=primary_pdf: generate_customer_statement_pdf(cust, db, store_info, path),
                "label": stmt_name,
            })
        except Exception as e:
            print(f"[Archive] Error preparing customer statement for {c_full}: {e}")

    # 6. RUN CONCURRENT EDGE RENDERS (up to 4 isolated headless profiles in parallel)
    if render_jobs:
        workers = min(4, len(render_jobs))
        with ThreadPoolExecutor(max_workers=workers) as executor:
            future_map = {
                executor.submit(render_html_to_pdf, job["html"], job["primary_pdf"]): job
                for job in render_jobs
            }
            for future in as_completed(future_map):
                job = future_map[future]
                rendered_ok = False
                try:
                    rendered_ok = bool(future.result())
                except Exception as e:
                    print(f"[Archive] Parallel render failed for {job['label']}: {e}")

                if not rendered_ok and job["fallback"]:
                    try:
                        job["fallback"]()
                        rendered_ok = job["primary_pdf"].exists()
                    except Exception as e2:
                        print(f"[Archive] Fallback render failed for {job['label']}: {e2}")

                if rendered_ok:
                    for extra_path in job["extra_copies"]:
                        try:
                            extra_path.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(job["primary_pdf"], extra_path)
                        except Exception as copy_err:
                            print(f"[Archive] Copy error for {extra_path}: {copy_err}")
                    counts[job["count_key"]] += len(job["mirror_pairs"])
                    mirror_items.extend(job["mirror_pairs"])

    _cleanup_legacy_duplicates(archive_root)

    # Persist updated party statement signatures so subsequent backups skip unchanged parties cleanly
    if render_jobs or force_refresh or next_stmt_state != prev_stmt_state:
        _save_statement_state(archive_root, next_stmt_state)

    # 7. MIRROR TO EXTERNAL ROOTS (Downloads backup + USB + custom folders, skipping unchanged files)
    roots = get_all_archive_roots()
    for src_pdf, rel_path in mirror_items:
        _save_pdf_to_roots(src_pdf, rel_path, roots=roots)

    counts["total_files"] = (
        counts["sales_invoices"]
        + counts["exchanges"]
        + counts["customer_statements"]
        + counts["purchases"]
        + counts["supplier_statements"]
    )

    return {
        "status": "success",
        "counts": counts,
        "archive_dir": str(archive_root),
    }

def get_all_archive_roots() -> List[Path]:
    """Return all target roots for archiving (PC local storage, Downloads/custom backups, and any connected pendrive)."""
    from app.core.config import DATA_DIR

    roots = [DATA_DIR]
    seen = {str(DATA_DIR).lower()}

    def _add_root(candidate: Path):
        try:
            key = str(candidate).lower()
            if key not in seen:
                roots.append(candidate)
                seen.add(key)
        except Exception:
            pass

    # Mirror to Downloads backup vault if Downloads\JewelleryERP_Backups exists
    downloads_backup_parent = Path.home() / "Downloads" / "JewelleryERP_Backups"
    if downloads_backup_parent.exists():
        _add_root(downloads_backup_parent / "JewelleryERP_Data")

    # Mirror to any user-chosen backup folders saved by Electron in storage_config.json
    cfg_path = DATA_DIR / "storage_config.json"
    if cfg_path.exists():
        try:
            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
            for custom_dir in cfg.get("customBackupDirs", []) or []:
                c_path = Path(custom_dir)
                if c_path.exists():
                    target = c_path if c_path.name.lower() == "jewelleryerp_data" else (c_path / "JewelleryERP_Data")
                    _add_root(target)
        except Exception:
            pass

    for letter in string.ascii_uppercase:
        p = Path(f"{letter}:/JewelleryERP_Data")
        if p.exists():
            _add_root(p)

    return roots


def _save_pdf_to_roots(source_pdf: Path, relative_dest_path: Path, roots: Optional[List[Path]] = None):
    """Mirror a generated PDF to all archive roots (PC, custom backups, and USB)."""
    if not source_pdf.exists():
        return

    target_roots = roots if roots is not None else get_all_archive_roots()
    try:
        src_stat = source_pdf.stat()
        src_resolved = source_pdf.resolve()
    except Exception:
        return

    for root in target_roots:
        dest = root / "Archived_PDFs" / relative_dest_path
        try:
            if src_resolved == dest.resolve():
                continue
            if dest.exists():
                d_stat = dest.stat()
                if d_stat.st_size == src_stat.st_size and abs(d_stat.st_mtime - src_stat.st_mtime) <= 2:
                    continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            for attempt in range(2):
                try:
                    shutil.copy2(source_pdf, dest)
                    break
                except PermissionError:
                    if attempt == 0:
                        time.sleep(0.15)
                    else:
                        raise
        except Exception as e:
            print(f"[Archive Mirror] Error copying to {dest}: {e}")

def archive_single_invoice(invoice_id: int, db: Session = None):
    close_db = False
    if db is None:
        from app.db.database import SessionLocal
        db = SessionLocal()
        close_db = True
    try:
        from app.services.invoice_pdf_service import InvoicePDFService
        from app.services.luxury_pdf_service import generate_luxury_bill_html, render_html_to_pdf
        from app.core.config import DATA_DIR
        inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not inv:
            return
        store_info = _get_store_header(db, inv.store_id or 1)
        c_obj = db.query(Customer).filter(Customer.id == inv.customer_id).first() if inv.customer_id else None
        if c_obj:
            c_full = f"{c_obj.first_name} {c_obj.last_name or ''}".strip()
            folder_name = _sanitize_name(c_full, default=f"Customer_{inv.customer_id}")
        else:
            b_name = getattr(inv, 'buyer_name', None) or "Walkin_Customer"
            folder_name = _sanitize_name(b_name, default="Walkin_Customers")

        inv_data = InvoicePDFService.get_invoice_pdf_data(inv.id, db)
        is_gst = bool(inv_data.get("company", {}).get("gst_enabled"))
        gst_folder = "GST" if is_gst else "Without_GST"

        inv_no = _sanitize_name(inv.invoice_number or f"INV-{inv.id}")
        file_name = f"{inv_no}.pdf"
        rel_path = Path(gst_folder) / "Sales" / folder_name / file_name

        primary_pdf = DATA_DIR / "Archived_PDFs" / rel_path
        primary_pdf.parent.mkdir(parents=True, exist_ok=True)
        if is_gst:
            from app.services.gst_pdf_template import generate_gst_tax_invoice_html
            inv_html = generate_gst_tax_invoice_html(inv_data)
        else:
            inv_html = generate_luxury_bill_html(inv_data)

        if not render_html_to_pdf(inv_html, primary_pdf):
            generate_invoice_pdf(inv, store_info, primary_pdf)

        _save_pdf_to_roots(primary_pdf, rel_path)

        if inv.customer_id:
            archive_single_customer_statement(inv.customer_id, db)
    except Exception as e:
        print(f"[Archive Single Invoice Error] {e}")
    finally:
        if close_db:
            db.close()

def archive_single_exchange(exchange_id: int, db: Session = None):
    close_db = False
    if db is None:
        from app.db.database import SessionLocal
        db = SessionLocal()
        close_db = True
    try:
        from app.services.invoice_pdf_service import InvoicePDFService
        from app.services.luxury_pdf_service import generate_luxury_bill_html, render_html_to_pdf
        from app.core.config import DATA_DIR
        exc = db.query(Exchange).filter(Exchange.id == exchange_id).first()
        if not exc:
            return
        store_info = _get_store_header(db, exc.store_id or 1)
        c_obj = db.query(Customer).filter(Customer.id == exc.customer_id).first() if exc.customer_id else None
        if c_obj:
            c_full = f"{c_obj.first_name} {c_obj.last_name or ''}".strip()
            folder_name = _sanitize_name(c_full, default=f"Customer_{exc.customer_id}")
        else:
            folder_name = "Walkin_Customers"

        is_gst = (exc.company_id == 2) or bool(str(getattr(exc, 'exchange_number', '')).startswith(('SJ/E', 'PG/E', 'SJ_', 'PG_'))) or ('/E/' in str(getattr(exc, 'exchange_number', '')))
        gst_folder = "GST" if is_gst else "Without_GST"

        exc_no = _sanitize_name(getattr(exc, 'exchange_number', None) or f"EXC-{exc.id}")
        file_name = f"{exc_no}.pdf"
        rel_path = Path(gst_folder) / "Exchanges" / folder_name / file_name

        primary_pdf = DATA_DIR / "Archived_PDFs" / rel_path
        primary_pdf.parent.mkdir(parents=True, exist_ok=True)

        exc_data = InvoicePDFService.get_exchange_pdf_data(exc.id, db)
        exc_html = generate_luxury_bill_html(exc_data)
        if not render_html_to_pdf(exc_html, primary_pdf):
            generate_exchange_pdf(exc, store_info, primary_pdf)

        _save_pdf_to_roots(primary_pdf, rel_path)

        if exc.customer_id:
            archive_single_customer_statement(exc.customer_id, db)
    except Exception as e:
        print(f"[Archive Single Exchange Error] {e}")
    finally:
        if close_db:
            db.close()

def archive_single_purchase(purchase_id: int, db: Session = None):
    close_db = False
    if db is None:
        from app.db.database import SessionLocal
        db = SessionLocal()
        close_db = True
    try:
        from app.services.invoice_pdf_service import InvoicePDFService
        from app.services.luxury_pdf_service import generate_luxury_bill_html, render_html_to_pdf
        from app.core.config import DATA_DIR
        pur = db.query(Purchase).filter(Purchase.id == purchase_id).first()
        if not pur:
            return
        store_info = _get_store_header(db, pur.store_id or 1)
        s_obj = db.query(Seller).filter(Seller.id == pur.seller_id).first() if pur.seller_id else None
        if s_obj:
            folder_name = _sanitize_name(s_obj.name, default=f"Supplier_{pur.seller_id}")
        else:
            folder_name = "Suppliers"

        is_gst = (pur.company_id == 2) or bool(str(getattr(pur, 'purchase_number', '')).startswith(('SJ/P', 'PG/P', 'SJ_', 'PG_'))) or ('/P/' in str(getattr(pur, 'purchase_number', '')))
        gst_folder = "GST" if is_gst else "Without_GST"

        p_no = _sanitize_name(getattr(pur, 'purchase_number', None) or f"PUR-{pur.id}")
        file_name = f"{p_no}.pdf"
        rel_path = Path(gst_folder) / "Purchases" / folder_name / file_name

        primary_pdf = DATA_DIR / "Archived_PDFs" / rel_path
        primary_pdf.parent.mkdir(parents=True, exist_ok=True)

        pur_data = InvoicePDFService.get_purchase_pdf_data(pur.id, db)
        if is_gst:
            from app.services.gst_pdf_template import generate_gst_tax_invoice_html
            pur_html = generate_gst_tax_invoice_html(pur_data)
        else:
            pur_html = generate_luxury_bill_html(pur_data)
        if not render_html_to_pdf(pur_html, primary_pdf):
            generate_purchase_pdf(pur, store_info, primary_pdf)

        _save_pdf_to_roots(primary_pdf, rel_path)

        if pur.seller_id:
            archive_single_supplier_statement(pur.seller_id, db)
    except Exception as e:
        print(f"[Archive Single Purchase Error] {e}")
    finally:
        if close_db:
            db.close()

def archive_single_customer_statement(customer_id: int, db: Session = None):
    close_db = False
    if db is None:
        from app.db.database import SessionLocal
        db = SessionLocal()
        close_db = True
    try:
        from app.services.luxury_pdf_service import generate_luxury_statement_html, render_html_to_pdf
        from app.core.config import DATA_DIR
        c = db.query(Customer).filter(Customer.id == customer_id).first()
        if not c:
            return
        store_info = _get_store_header(db, c.store_id or 1)
        c_full = f"{c.first_name} {c.last_name or ''}".strip()
        folder_name = _sanitize_name(c_full, default=f"Customer_{c.id}")

        entries = []
        ledgers = db.query(CustomerLedger).filter(CustomerLedger.customer_id == c.id).order_by(CustomerLedger.date.asc()).all()
        for l in ledgers:
            entries.append({
                "date": (l.date.strftime("%d-%b-%Y") if getattr(l, "date", None) else ""),
                "type": l.voucher_type or "Ledger",
                "number": l.voucher_number or "-",
                "description": l.description or "-",
                "debit": float(l.debit or 0.0),
                "credit": float(l.credit or 0.0),
                "balance": float(l.balance or 0.0),
                "gold_debit": float(l.gold_debit or 0.0),
                "gold_credit": float(l.gold_credit or 0.0),
            })

        c_html = generate_luxury_statement_html(
            c_full, c.phone_number or "", "Customer", entries, store_info,
            float(c.outstanding_balance or 0.0), float(c.fine_gold_balance or 0.0), float(c.fine_silver_balance or 0.0)
        )

        for g_sub in ["GST", "Without_GST"]:
            rel_path = Path(g_sub) / "Sales" / folder_name / f"Statement_{_sanitize_name(c_full)}.pdf"
            primary_pdf = DATA_DIR / "Archived_PDFs" / rel_path
            primary_pdf.parent.mkdir(parents=True, exist_ok=True)
            if not render_html_to_pdf(c_html, primary_pdf):
                generate_customer_statement_pdf(c, db, store_info, primary_pdf)
            _save_pdf_to_roots(primary_pdf, rel_path)

    except Exception as e:
        print(f"[Archive Customer Statement Error] {e}")
    finally:
        if close_db:
            db.close()

def archive_single_supplier_statement(seller_id: int, db: Session = None):
    close_db = False
    if db is None:
        from app.db.database import SessionLocal
        db = SessionLocal()
        close_db = True
    try:
        from app.services.luxury_pdf_service import generate_luxury_statement_html, render_html_to_pdf
        from app.core.config import DATA_DIR
        s = db.query(Seller).filter(Seller.id == seller_id).first()
        if not s:
            return
        store_info = _get_store_header(db, s.store_id or 1)
        folder_name = _sanitize_name(s.name, default=f"Supplier_{s.id}")

        entries = []
        ledgers = db.query(SupplierLedger).filter(SupplierLedger.seller_id == s.id).order_by(SupplierLedger.date.asc()).all()
        for l in ledgers:
            entries.append({
                "date": (l.date.strftime("%d-%b-%Y") if getattr(l, "date", None) else ""),
                "type": l.voucher_type or "Ledger",
                "number": l.voucher_number or "-",
                "description": l.description or "-",
                "debit": float(l.debit or 0.0),
                "credit": float(l.credit or 0.0),
                "balance": float(l.balance or 0.0),
                "gold_debit": float(getattr(l, "gold_debit", 0.0) or 0.0),
                "gold_credit": float(getattr(l, "gold_credit", 0.0) or 0.0),
            })

        s_html = generate_luxury_statement_html(
            s.name, s.mobile or "", "Supplier", entries, store_info,
            float(getattr(s, "outstanding_balance", 0.0) or getattr(s, "current_balance", 0.0) or 0.0), float(getattr(s, "fine_gold_balance", 0.0) or 0.0), float(getattr(s, "fine_silver_balance", 0.0) or 0.0)
        )

        for g_sub in ["GST", "Without_GST"]:
            rel_path = Path(g_sub) / "Purchases" / folder_name / f"Statement_{_sanitize_name(s.name)}.pdf"
            primary_pdf = DATA_DIR / "Archived_PDFs" / rel_path
            primary_pdf.parent.mkdir(parents=True, exist_ok=True)
            if not render_html_to_pdf(s_html, primary_pdf):
                generate_supplier_statement_pdf(s, db, store_info, primary_pdf)
            _save_pdf_to_roots(primary_pdf, rel_path)

    except Exception as e:
        print(f"[Archive Supplier Statement Error] {e}")
    finally:
        if close_db:
            db.close()

def dispatch_async_archive(fn, *args):

    """Run an archive function in a background worker thread."""

    def worker():

        try:

            fn(*args)

        except Exception as e:

            print(f"[Async Archive Worker Error] {e}")

    threading.Thread(target=worker, daemon=True).start()

