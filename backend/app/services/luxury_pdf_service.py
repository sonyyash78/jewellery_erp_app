"""
Luxury PDF Generator Service
Generates 100% pixel-perfect original bills (Invoices, Exchanges, Purchases, Statements)
matching the application's premium UI design with gold accents, Cinzel typography,
QR codes, metal settlements, and converts them to high-resolution vector PDFs.
"""
import os
import io
import json
import base64
import shutil
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

import qrcode


def _find_browser_binary() -> Optional[str]:
    """Find Microsoft Edge or Google Chrome executable on the system."""
    candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        shutil.which("msedge"),
        shutil.which("chrome"),
        shutil.which("chromium"),
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return None


def _format_currency(val: Any) -> str:
    try:
        f = float(val or 0)
        return f"{f:,.2f}"
    except (ValueError, TypeError):
        return "0.00"


def _format_weight(val: Any) -> str:
    try:
        f = float(val or 0)
        return f"{f:.3f}"
    except (ValueError, TypeError):
        return "0.000"


def _format_date(val: Any) -> str:
    if not val:
        return ""
    if isinstance(val, (datetime, )):
        return val.strftime("%d %B %Y").upper()
    try:
        dt = datetime.fromisoformat(str(val).split("T")[0])
        return dt.strftime("%d %B %Y").upper()
    except Exception:
        return str(val).upper()


def _generate_qr_data_url(upi_id: str, upi_name: str, amount: float, note: str) -> str:
    """Generate base64 PNG data URL for UPI QR code."""
    if not upi_id:
        return ""
    try:
        link = f"upi://pay?pa={upi_id}&pn={upi_name}"
        if amount > 0:
            link += f"&am={amount:.2f}"
        link += f"&cu=INR&tn={note}"

        qr = qrcode.QRCode(box_size=4, border=1)
        qr.add_data(link)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{b64}"
    except Exception as e:
        print(f"[LuxuryPDF] QR code generation error: {e}")
        return ""


def render_html_to_pdf(html_content: str, output_path: Path) -> bool:
    """Render full HTML string into a PDF using headless Chromium (Edge/Chrome)."""
    browser_exe = _find_browser_binary()
    if not browser_exe:
        print("[LuxuryPDF] No Chromium browser binary found for headless rendering.")
        return False

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as tf:
        tf.write(html_content)
        temp_html = tf.name

    temp_pdf = temp_html.replace(".html", ".pdf")

    try:
        cmd = [
            browser_exe,
            "--headless",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={temp_pdf}",
            temp_html
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20)
        temp_pdf_path = Path(temp_pdf)
        if temp_pdf_path.exists() and temp_pdf_path.stat().st_size > 500:
            try:
                shutil.copy2(temp_pdf, str(output_path))
                return True
            except PermissionError:
                # If target PDF is currently locked open in user's browser, write with a fresh copy
                print(f"[LuxuryPDF] Target file {output_path.name} is locked in user viewer. Retrying via safe write.")
                try:
                    alt_path = output_path.parent / f"{output_path.stem}_new{output_path.suffix}"
                    shutil.copy2(temp_pdf, str(alt_path))
                except Exception:
                    pass
                return True
        else:
            print(f"[LuxuryPDF] Headless browser failed or produced empty file: {res.stderr.decode('utf-8', errors='ignore')}")
            return False
    except Exception as e:
        print(f"[LuxuryPDF] Execution error rendering HTML to PDF: {e}")
        return False
    finally:
        try:
            if os.path.exists(temp_html):
                os.remove(temp_html)
            if os.path.exists(temp_pdf):
                os.remove(temp_pdf)
        except Exception:
            pass


def generate_luxury_bill_html(data: Dict[str, Any]) -> str:
    """
    Generate 100% pixel-perfect luxury bill HTML matching the frontend design.
    Handles Sales Invoices, Exchanges, and Purchases with full styling and calculations.
    """
    doc_type = data.get("type", "sale")
    invoice = data.get("invoice", {})
    customer = data.get("customer", {})
    company = data.get("company", {})
    items = data.get("items", [])
    old_items = data.get("old_items", [])
    totals = data.get("totals", {})

    company_name = company.get("name") or "SAIDEEP JEWELLERS"
    initials = "".join([w[0] for w in company_name.split() if w])[:2].upper() or "SJ"
    tagline = company.get("tagline") or "PURITY & TRUST SINCE INCEPTION"
    address = company.get("address") or "Takhatgarh, Rajasthan"
    phone = company.get("phone") or "9876543210"
    email = company.get("email") or "info@saideepjewellers.com"
    gstin = company.get("gstin") or ""
    website = company.get("website") or (f"www.{email.split('@')[1]}" if "@" in email else "")

    logo_data_url = company.get("logo_data_url", "")
    upi_id = company.get("upi_id", "")
    upi_name = company.get("upi_name") or company_name
    bank_acc = company.get("bank_account_no", "")
    bank_ifsc = company.get("bank_ifsc", "")

    # Customer / Supplier info
    cust_name = customer.get("name") or "Walk-in Customer"
    cust_phone = customer.get("phone") or "-"
    cust_address = customer.get("address") or "-"
    cust_gstin = customer.get("gstin") or "-"

    # Invoice / Voucher info
    inv_number = invoice.get("invoice_number") or "BILL-001"
    inv_date = _format_date(invoice.get("invoice_date"))

    is_exchange = doc_type == "exchange" or inv_number.startswith("EXC-") or invoice.get("bill_type") == "Exchange"
    is_purchase = doc_type == "purchase" or inv_number.startswith("PUR-")

    if is_exchange:
        badge_title = "EXCHANGE VOUCHER"
        badge_icon = '<path d="M6.99 11L3 15l3.99 4v-3H14v-2H6.99v-3zM21 9l-3.99-4v3H10v2h7.01v3L21 9z"/>'
        bill_to_label = "EXCHANGED WITH"
    elif is_purchase:
        badge_title = "PURCHASE VOUCHER"
        badge_icon = '<path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>'
        bill_to_label = "SUPPLIER / KARIGAR"
    else:
        badge_title = "TAX INVOICE"
        badge_icon = '<path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2h12c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/>'
        bill_to_label = "BILL TO"

    # Financial totals
    subtotal = float(invoice.get("subtotal") or totals.get("subtotal") or 0.0)
    tax_amount = float(invoice.get("tax_amount") or totals.get("tax_amount") or 0.0)
    discount_amount = float(invoice.get("discount_amount") or totals.get("discount_amount") or 0.0)
    grand_total = float(invoice.get("grand_total") or totals.get("grand_total") or (subtotal + tax_amount - discount_amount))

    total_old_val = float(invoice.get("total_old_value") or 0.0)
    diff_amount = float(invoice.get("difference_amount") or (grand_total - total_old_val if is_exchange else grand_total))

    amount_paid = float(invoice.get("amount_paid") or invoice.get("cash_paid") or invoice.get("cash_received") or 0.0)
    balance_due = float(invoice.get("balance_due") if invoice.get("balance_due") is not None else invoice.get("balance_amount") or (diff_amount - amount_paid))

    gold_bal_metal = float(invoice.get("gold_balance_metal_weight") or 0.0)
    silver_bal_metal = float(invoice.get("silver_balance_metal_weight") or 0.0)
    settlement_type = invoice.get("settlement_type") or "Cash"

    # QR Code Generation
    payable_qr = balance_due if balance_due > 0 else (diff_amount if diff_amount > 0 else grand_total)
    qr_data_url = _generate_qr_data_url(upi_id, upi_name, payable_qr, inv_number) if upi_id else ""

    # Metal sums
    gold_fine_billed = 0.0
    gold_fine_received = 0.0
    gold_applied_rate = 0.0
    silver_fine_billed = 0.0
    silver_fine_received = 0.0
    silver_applied_rate = 0.0

    # Build items rows
    new_rows_html = []
    for idx, item in enumerate(items):
        item_name = item.get("item_name") or "Jewellery Item"
        metal = (item.get("metal_type") or item.get("metal") or "Gold").capitalize()
        gross = float(item.get("gross_weight") or 0.0)
        stone = float(item.get("stone_weight") or 0.0)
        net_wt = float(item.get("net_weight") or (gross - stone if gross - stone > 0 else gross))
        touch = float(item.get("touch_purity") or item.get("tanch_percentage") or 91.6)
        wastage = float(item.get("wastage") or 0.0)
        fine_wt = float(item.get("fine_weight") or (net_wt * (touch + wastage) / 100.0))

        rate = float(item.get("applied_rate") or 0.0)
        making = float(item.get("making_charges") or 0.0)
        other = float(item.get("other_charges") or 0.0) + float(item.get("hallmark_charges") or 0.0)
        final_price = float(item.get("final_price") or item.get("metal_value") or 0.0)

        is_gold = "gold" in metal.lower()
        if is_gold:
            gold_fine_billed += fine_wt
            if not gold_applied_rate:
                gold_applied_rate = rate
        else:
            silver_fine_billed += fine_wt
            if not silver_applied_rate:
                silver_applied_rate = rate

        tanch_str = f"{touch:.1f}%"
        if wastage > 0:
            tanch_str += f" + {wastage:.1f}%"

        rate_unit = "per 10g" if is_gold else "per kg"
        price_display = f"&#8377; {_format_currency(final_price)}" if final_price > 0 else "-"

        new_rows_html.append(f"""
        <tr>
          <td>{idx + 1}</td>
          <td style="text-align: left; font-weight: 600;">
            <div style="font-size: 11px; color: #16213E; font-weight: 700;">{item_name}</div>
            <div style="font-size: 9px; color: #7f8c8d; font-weight: 400; margin-top: 1px;">Gross: {gross:.3f}g | Fine: {fine_wt:.3f}g</div>
          </td>
          <td>{metal}</td>
          <td>{tanch_str}</td>
          <td><b>{net_wt:.3f}</b></td>
          <td>&#8377; {_format_currency(rate)}<div style="font-size: 8px; color: #7f8c8d;">{rate_unit}</div></td>
          <td>{_format_currency(making) if making > 0 else '-'}</td>
          <td>{_format_currency(other) if other > 0 else '-'}</td>
          <td style="font-weight: 800; color: #0F172A;">{price_display}</td>
        </tr>
        """)

    # Build old items / return items rows
    old_rows_html = []
    for idx, oi in enumerate(old_items):
        item_name = oi.get("item_name") or "Old Metal Deposited"
        metal = (oi.get("metal_type") or oi.get("metal") or "Gold").capitalize()
        gross = float(oi.get("gross_weight") or 0.0)
        stone = float(oi.get("stone_weight") or 0.0)
        net_wt = float(oi.get("net_weight") or (gross - stone if gross - stone > 0 else gross))
        touch = float(oi.get("tanch_percentage") or oi.get("touch") or 91.6)
        wastage = float(oi.get("wastage") or 0.0)
        fine_wt = float(oi.get("fine_weight") or (net_wt * (touch + wastage) / 100.0))

        rate = float(oi.get("applied_rate") or oi.get("rate_applied") or 0.0)
        charges = float(oi.get("labour_charge") or 0.0) + float(oi.get("testing_melting_charge") or 0.0) + float(oi.get("hallmark_charge") or 0.0)
        val = float(oi.get("final_price") or oi.get("calculated_value") or 0.0)

        is_gold = "gold" in metal.lower()
        if is_gold:
            gold_fine_received += fine_wt
            if not gold_applied_rate:
                gold_applied_rate = rate
        else:
            silver_fine_received += fine_wt
            if not silver_applied_rate:
                silver_applied_rate = rate

        tanch_str = f"{touch:.1f}%"
        if wastage > 0:
            tanch_str += f" + {wastage:.1f}%"

        rate_unit = "per 10g" if is_gold else "per kg"
        val_display = f"&#8377; {_format_currency(val)}" if val > 0 else "-"

        old_rows_html.append(f"""
        <tr style="background: #FFFDF7;">
          <td>{len(items) + idx + 1}</td>
          <td style="text-align: left; font-weight: 600;">
            <div style="font-size: 11px; color: #8F6614; font-weight: 700;">{item_name}</div>
            <div style="font-size: 9px; color: #7f8c8d; font-weight: 400; margin-top: 1px;">Gross: {gross:.3f}g | Return Metal</div>
          </td>
          <td>{metal}</td>
          <td>{tanch_str}</td>
          <td><b>{net_wt:.3f}</b></td>
          <td>&#8377; {_format_currency(rate)}<div style="font-size: 8px; color: #7f8c8d;">{rate_unit}</div></td>
          <td>-</td>
          <td>{_format_currency(charges) if charges > 0 else '-'}</td>
          <td style="font-weight: 800; color: #B45309;">{val_display}</td>
        </tr>
        """)

    # Combine tables
    table_rows_combined = "".join(new_rows_html)
    if old_rows_html:
        section_title = "PURCHASED METAL" if is_purchase else "OLD ITEMS DEPOSITED (RETURN / EXCHANGE)"
        table_rows_combined += f"""
        <tr>
          <td colspan="9" style="background: #FEF3C7; text-align: center; font-weight: 800; color: #92400E; padding: 4px; font-size: 9.5px; letter-spacing: 1px;">
            {section_title}
          </td>
        </tr>
        """ + "".join(old_rows_html)

    # Metal Settlement Section
    has_gold = gold_fine_billed > 0 or gold_fine_received > 0 or gold_bal_metal != 0
    has_silver = silver_fine_billed > 0 or silver_fine_received > 0 or silver_bal_metal != 0
    has_metal_settlement = is_exchange or settlement_type in ("Metal", "Hybrid") or has_gold or has_silver

    settlement_boxes_html = ""
    if has_metal_settlement and (has_gold or has_silver):
        boxes = []
        if has_gold:
            bal_label = f"+ {gold_bal_metal:.3f} gm Balance Due" if gold_bal_metal > 0.001 else ("0.000 gm (Settled)" if gold_bal_metal == 0 else f"- {abs(gold_bal_metal):.3f} gm Surplus")
            bal_color = "#DC2626" if gold_bal_metal > 0.001 else "#10B981"
            boxes.append(f"""
            <div style="flex: 1; border: 1px solid #E2D3B8; border-radius: 6px; background: linear-gradient(180deg, #FDFAF4 0%, #F8F4E8 100%); padding: 5px 8px;">
              <div style="font-family: 'Cinzel', serif; font-size: 10px; font-weight: 800; color: #8F6614; border-bottom: 1px solid #E2D3B8; padding-bottom: 3px; margin-bottom: 3px;">
                GOLD SETTLEMENT (22K)
              </div>
              <table style="width: 100%; font-size: 9px; font-weight: 600; color: #16213E;">
                <tr><td>Gold Required (New Items)</td><td style="text-align: right;">{gold_fine_billed:.3f} gm</td></tr>
                <tr><td>Gold Received (Old Items)</td><td style="text-align: right;">{gold_fine_received:.3f} gm</td></tr>
                <tr><td colspan="2"><hr style="border: none; border-top: 1px dashed #D4AF37; margin: 3px 0;"></td></tr>
                <tr><td>Rate Applied</td><td style="text-align: right;">&#8377; {_format_currency(gold_applied_rate)}/10g</td></tr>
                <tr><td><b>Gold Balance Due</b></td><td style="text-align: right; color: {bal_color}; font-weight: 800;">{bal_label}</td></tr>
              </table>
            </div>
            """)

        if has_silver:
            bal_label = f"+ {silver_bal_metal:.3f} gm Balance Due" if silver_bal_metal > 0.001 else ("0.000 gm (Settled)" if silver_bal_metal == 0 else f"- {abs(silver_bal_metal):.3f} gm Surplus")
            bal_color = "#DC2626" if silver_bal_metal > 0.001 else "#10B981"
            boxes.append(f"""
            <div style="flex: 1; border: 1px solid #E2E8F0; border-radius: 6px; background: linear-gradient(180deg, #F8FAFC 0%, #F1F5F9 100%); padding: 5px 8px;">
              <div style="font-family: 'Cinzel', serif; font-size: 10px; font-weight: 800; color: #334155; border-bottom: 1px solid #CBD5E1; padding-bottom: 3px; margin-bottom: 3px;">
                SILVER SETTLEMENT (92.5)
              </div>
              <table style="width: 100%; font-size: 9px; font-weight: 600; color: #16213E;">
                <tr><td>Silver Required (New Items)</td><td style="text-align: right;">{silver_fine_billed:.3f} gm</td></tr>
                <tr><td>Silver Received (Old Items)</td><td style="text-align: right;">{silver_fine_received:.3f} gm</td></tr>
                <tr><td colspan="2"><hr style="border: none; border-top: 1px dashed #94A3B8; margin: 3px 0;"></td></tr>
                <tr><td>Rate Applied</td><td style="text-align: right;">&#8377; {_format_currency(silver_applied_rate)}/kg</td></tr>
                <tr><td><b>Silver Balance Due</b></td><td style="text-align: right; color: {bal_color}; font-weight: 800;">{bal_label}</td></tr>
              </table>
            </div>
            """)

        option_badge = ""
        if gold_bal_metal > 0.001 and silver_bal_metal > 0.001:
            option_badge = '<div style="text-align: center; margin-bottom: 3px;"><span style="background: #EFF6FF; border: 1px solid #93C5FD; color: #1E40AF; padding: 2px 10px; border-radius: 10px; font-size: 8px; font-weight: 800;">OPTION 4: BOTH METALS DUE (Gold &amp; Silver Balance Due)</span></div>'
        elif gold_bal_metal > 0.001:
            option_badge = f'<div style="text-align: center; margin-bottom: 3px;"><span style="background: #FEF3C7; border: 1px solid #D4AF37; color: #78350F; padding: 2px 10px; border-radius: 10px; font-size: 8px; font-weight: 800;">OPTION 2: GOLD DUE (+{gold_bal_metal:.3f} gm Gold Balance Due)</span></div>'
        elif silver_bal_metal > 0.001:
            option_badge = f'<div style="text-align: center; margin-bottom: 3px;"><span style="background: #F8FAFC; border: 1px solid #CBD5E1; color: #334155; padding: 2px 10px; border-radius: 10px; font-size: 8px; font-weight: 800;">OPTION 3: SILVER DUE (+{silver_bal_metal:.3f} gm Silver Balance Due)</span></div>'
        elif settlement_type == "Cash" or balance_due == 0:
            option_badge = '<div style="text-align: center; margin-bottom: 3px;"><span style="background: #ECFDF5; border: 1px solid #6EE7B7; color: #065F46; padding: 2px 10px; border-radius: 10px; font-size: 8px; font-weight: 800;">OPTION 1: CASH SETTLEMENT (All Metal Dues Cleared)</span></div>'

        settlement_boxes_html = f"""
        <div style="margin-top: 4px;">
          <div style="display: flex; align-items: center; justify-content: center; margin: 4px 0 2px; position: relative;">
            <div style="position: absolute; left: 0; right: 0; height: 1px; background: linear-gradient(90deg, transparent, #E2D3B8 20%, #E2D3B8 80%, transparent); z-index: 1;"></div>
            <span style="position: relative; z-index: 2; background: #FFFFFF; border: 1px solid #D4AF37; padding: 1px 12px; border-radius: 10px; color: #8F6614; font-family: 'Cinzel', serif; font-weight: 800; font-size: 9.5px; letter-spacing: 1px;">
              METAL SETTLEMENT &amp; PURITY SUMMARY
            </span>
          </div>
          {option_badge}
          <div style="display: flex; gap: 8px;">
            {''.join(boxes)}
          </div>
        </div>
        """

    # Bottom summary: Left column (Cash received / Final settlement), Right column (Calculations)
    left_cards = []
    if amount_paid > 0:
        left_cards.append(f"""
        <div style="background: #ECFDF5; border: 1px solid #A7F3D0; border-radius: 6px; padding: 5px 8px; display: flex; align-items: center; gap: 8px;">
          <div style="width: 28px; height: 28px; border-radius: 50%; background: #10B981; color: white; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 14px;">&#10003;</div>
          <div>
            <div style="color: #065F46; font-size: 8px; font-weight: 800; letter-spacing: 0.5px;">CASH RECEIVED</div>
            <div style="color: #064E3B; font-size: 14px; font-weight: 800;">&#8377; {_format_currency(amount_paid)}</div>
          </div>
        </div>
        """)
    else:
        left_cards.append("""
        <div style="background: #F8F9FA; border: 1px solid #CED4DA; border-radius: 6px; padding: 5px 8px; display: flex; align-items: center; gap: 8px;">
          <div style="width: 28px; height: 28px; border-radius: 50%; background: #6C757D; color: white; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 12px;">!</div>
          <div>
            <div style="color: #495057; font-size: 8px; font-weight: 800; letter-spacing: 0.5px;">PAYMENT STATUS</div>
            <div style="color: #212529; font-size: 11px; font-weight: 700;">No Cash Payment Received</div>
          </div>
        </div>
        """)

    # Final settlement badge
    is_cash_cleared = balance_due <= 0.01 and balance_due >= -0.01
    has_metal_due = gold_bal_metal > 0.001 or silver_bal_metal > 0.001
    if is_cash_cleared and not has_metal_due:
        left_cards.append("""
        <div style="background: #ECFDF5; border: 1px solid #A7F3D0; border-radius: 6px; padding: 5px 8px; display: flex; align-items: center; gap: 8px; margin-top: 4px;">
          <div style="width: 24px; height: 24px; border-radius: 50%; background: #10B981; color: white; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 800;">&#10003;</div>
          <div>
            <div style="color: #065F46; font-size: 8px; font-weight: 800;">FINAL SETTLEMENT</div>
            <div style="color: #064E3B; font-size: 13px; font-weight: 800;">FULLY PAID &#10003;</div>
          </div>
        </div>
        """)
    elif has_metal_due:
        metal_due_desc = []
        if gold_bal_metal > 0.001:
            metal_due_desc.append(f"{gold_bal_metal:.3f}g Gold")
        if silver_bal_metal > 0.001:
            metal_due_desc.append(f"{silver_bal_metal:.3f}g Silver")
        left_cards.append(f"""
        <div style="background: #FEF3C7; border: 1px solid #FDE68A; border-radius: 6px; padding: 5px 8px; display: flex; align-items: center; gap: 8px; margin-top: 4px;">
          <div style="width: 24px; height: 24px; border-radius: 50%; background: #D97706; color: white; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 800;">&#9878;</div>
          <div>
            <div style="color: #92400E; font-size: 8px; font-weight: 800;">METAL DUE TO LEDGER</div>
            <div style="color: #78350F; font-size: 12px; font-weight: 800;">{' &amp; '.join(metal_due_desc)} Due</div>
          </div>
        </div>
        """)
    else:
        left_cards.append(f"""
        <div style="background: #FEF2F2; border: 1px solid #FECACA; border-radius: 6px; padding: 5px 8px; display: flex; align-items: center; gap: 8px; margin-top: 4px;">
          <div style="width: 24px; height: 24px; border-radius: 50%; background: #DC2626; color: white; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 800;">&#9888;</div>
          <div>
            <div style="color: #991B1B; font-size: 8px; font-weight: 800;">BALANCE DUE</div>
            <div style="color: #7F1D1D; font-size: 13px; font-weight: 800;">&#8377; {_format_currency(balance_due)}</div>
          </div>
        </div>
        """)

    # Right column totals
    right_totals_rows = [
        f"<tr><td>Taxable Subtotal</td><td style='text-align: right;'>:</td><td style='text-align: right;'>&#8377; {_format_currency(subtotal)}</td></tr>"
    ]
    if is_exchange and total_old_val > 0:
        right_totals_rows.append(f"<tr><td style='color: #B45309;'>Less Old Jewellery Traded</td><td style='text-align: right;'>:</td><td style='text-align: right; color: #B45309; font-weight: 700;'>- &#8377; {_format_currency(total_old_val)}</td></tr>")
    if tax_amount > 0:
        right_totals_rows.append(f"<tr><td>GST Tax (3%)</td><td style='text-align: right;'>:</td><td style='text-align: right;'>&#8377; {_format_currency(tax_amount)}</td></tr>")
    if discount_amount > 0 and not is_exchange:
        right_totals_rows.append(f"<tr><td style='color: #059669;'>Discount Allowed</td><td style='text-align: right;'>:</td><td style='text-align: right; color: #059669;'>- &#8377; {_format_currency(discount_amount)}</td></tr>")

    net_label = "Net Difference Due" if is_exchange else "Grand Total"
    right_totals_rows.append(f"""
    <tr><td colspan='3'><hr style='border: none; border-top: 1px solid #D4AF37; margin: 3px 0;'></td></tr>
    <tr style='font-size: 11.5px; font-weight: 800; color: #0F172A;'>
      <td>{net_label}</td><td style='text-align: right;'>:</td><td style='text-align: right;'>&#8377; {_format_currency(diff_amount if is_exchange else grand_total)}</td>
    </tr>
    """)
    if amount_paid > 0:
        right_totals_rows.append(f"<tr style='color: #059669; font-weight: 700;'><td>Cash Paid</td><td style='text-align: right;'>:</td><td style='text-align: right;'>- &#8377; {_format_currency(amount_paid)}</td></tr>")

    bal_color = "#DC2626" if balance_due > 0.01 else "#059669"
    right_totals_rows.append(f"""
    <tr style='font-size: 11.5px; font-weight: 800; color: {bal_color};'>
      <td>Balance Cash Due</td><td style='text-align: right;'>:</td><td style='text-align: right;'>&#8377; {_format_currency(balance_due)}</td>
    </tr>
    """)

    # Logo HTML
    if logo_data_url:
        logo_html = f'<img src="{logo_data_url}" style="max-width: 64px; max-height: 64px; object-fit: contain;" />'
    else:
        logo_html = f'<div style="width: 58px; height: 58px; border-radius: 50%; border: 2px solid #D4AF37; display: flex; align-items: center; justify-content: center; font-family: \'Cinzel\', serif; font-size: 26px; color: #D4AF37; background: #FFFDF7;">{initials}</div>'

    # QR Code HTML
    qr_img_html = f'<img src="{qr_data_url}" style="width: 52px; height: 52px; object-fit: contain; margin-bottom: 2px; border-radius: 4px;" />' if qr_data_url else '<div style="width: 52px; height: 52px; border: 1px dashed #CBD5E1; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 8px; color: #94A3B8;">NO QR</div>'

    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>{badge_title} - {inv_number}</title>
  <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --navy: #0F172A;
      --navy-light: #1E293B;
      --gold: #D4AF37;
      --gold-dark: #996515;
      --text: #1E293B;
      --border: #E2E8F0;
      --card-bg: #FDFAF5;
      --card-border: #EAE3D2;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      color: var(--text);
      background: white;
      -webkit-font-smoothing: antialiased;
      line-height: 1.4;
      font-size: 10px;
    }}
    @page {{
      size: A4 portrait;
      margin: 0;
    }}
    @media print {{
      body {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
    }}
    .invoice-wrapper {{
      width: 210mm;
      height: 296.5mm;
      background: white;
      position: relative;
      padding: 5mm 6mm 6mm 6mm;
      box-sizing: border-box;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }}
    .watermark {{
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      font-family: 'Cinzel', serif;
      font-size: 320px;
      color: var(--gold);
      opacity: 0.03;
      z-index: 0;
      pointer-events: none;
    }}
    .content {{
      position: relative;
      z-index: 1;
      height: 100%;
      display: flex;
      flex-direction: column;
    }}
    .header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 2px;
    }}
    .logo-section {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .company-info h1 {{
      font-family: 'Cinzel', serif;
      font-size: 24px;
      font-weight: 800;
      color: var(--navy);
      line-height: 1.1;
      letter-spacing: 1.5px;
      margin-bottom: 2px;
    }}
    .tagline {{
      font-family: 'Inter', sans-serif;
      font-size: 8.5px;
      font-weight: 700;
      color: var(--gold-dark);
      letter-spacing: 2px;
      text-transform: uppercase;
    }}
    .tax-invoice-badge {{
      background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
      color: var(--gold);
      border: 1.5px solid rgba(212, 175, 55, 0.6);
      padding: 4px 16px;
      border-radius: 6px;
      font-family: 'Cinzel', serif;
      font-size: 13px;
      font-weight: 800;
      letter-spacing: 1.2px;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      margin-bottom: 3px;
      box-shadow: 0 2px 6px rgba(15, 23, 42, 0.12);
    }}
    .tax-invoice-badge svg {{
      width: 14px;
      height: 14px;
      fill: var(--gold);
    }}
    .meta-table {{
      margin-top: 2px;
      font-size: 9px;
      font-weight: 600;
      color: var(--navy);
      margin-left: auto;
    }}
    .meta-table td {{
      padding: 1px 4px;
    }}
    .meta-table td:first-child {{
      color: #64748B;
      font-size: 8.5px;
    }}
    .diamond-divider {{
      display: flex;
      align-items: center;
      margin: 4px 0 6px;
    }}
    .diamond-divider::before, .diamond-divider::after {{
      content: '';
      flex: 1;
      height: 1px;
      background: linear-gradient(90deg, rgba(212,175,55,0.1), rgba(212,175,55,0.6), rgba(212,175,55,0.1));
    }}
    .diamond {{
      width: 5px;
      height: 5px;
      background: var(--gold);
      transform: rotate(45deg);
      margin: 0 8px;
    }}
    .cards-row {{
      display: flex;
      gap: 10px;
      margin-bottom: 4px;
    }}
    .info-card {{
      flex: 1;
      border: 1px solid var(--card-border);
      border-radius: 6px;
      padding: 5px 8px;
      background: var(--card-bg);
      box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }}
    .card-header {{
      display: flex;
      align-items: center;
      gap: 6px;
      margin-bottom: 3px;
      border-bottom: 1px solid var(--card-border);
      padding-bottom: 3px;
    }}
    .card-title {{
      font-family: 'Cinzel', serif;
      font-size: 9.5px;
      font-weight: 800;
      color: #0F172A;
      letter-spacing: 1px;
    }}
    .items-table {{
      width: 100%;
      border-collapse: separate;
      border-spacing: 0 1px;
      margin-top: 2px;
      font-variant-numeric: tabular-nums;
    }}
    .items-table th {{
      background: linear-gradient(180deg, #0F172A 0%, #162036 100%);
      color: #D4AF37;
      padding: 3.5px 4px;
      font-size: 8.5px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.6px;
      border-bottom: 2px solid #D4AF37;
      text-align: center;
    }}
    .items-table tbody td {{
      background: #FFFFFF;
      padding: 3px 4px;
      font-size: 9px;
      border-top: 1px solid #ECE7DB;
      border-bottom: 1px solid #ECE7DB;
      text-align: center;
      color: #1E293B;
    }}
    .items-table tbody tr:nth-child(even) td {{
      background: #FAF8F2;
    }}
  </style>
</head>
<body>
  <div class="invoice-wrapper">
    <div class="watermark">{initials}</div>
    <div class="content">

      <!-- Header -->
      <div class="header">
        <div class="logo-section">
          {logo_html}
          <div class="company-info">
            <h1>{company_name}</h1>
            <div class="tagline">{tagline}</div>
          </div>
        </div>
        <div style="text-align: right; display: flex; flex-direction: column; align-items: flex-end;">
          <div class="tax-invoice-badge">
            <svg viewBox="0 0 24 24">{badge_icon}</svg>
            {badge_title}
          </div>
          <table class="meta-table">
            <tr><td>VOUCHER NO.</td><td>:</td><td style="color: var(--navy); font-weight: 800;">{inv_number}</td></tr>
            <tr><td>DATE</td><td>:</td><td style="color: var(--navy);">{inv_date}</td></tr>
            <tr><td>PLACE</td><td>:</td><td style="color: var(--navy);">{address.split(',')[0]}</td></tr>
            <tr><td>GSTIN</td><td>:</td><td style="color: var(--navy); font-weight: 700;">{gstin or 'N/A'}</td></tr>
          </table>
        </div>
      </div>

      <div class="diamond-divider"><div class="diamond"></div></div>

      <!-- Bill To & Payment Info Cards -->
      <div class="cards-row">
        <div class="info-card">
          <div class="card-header">
            <div class="card-title">{bill_to_label}</div>
          </div>
          <div style="font-size: 13px; font-weight: 800; color: #0F172A; margin-bottom: 2px;">{cust_name}</div>
          <div style="font-size: 9.5px; color: #334155;"><b>Phone:</b> {cust_phone}</div>
          <div style="font-size: 9.5px; color: #334155;"><b>Address:</b> {cust_address}</div>
          {f'<div style="font-size: 9.5px; color: #334155; margin-top: 1px;"><b>GSTIN/PAN:</b> {cust_gstin}</div>' if cust_gstin and cust_gstin != '-' else ''}
        </div>

        <div class="info-card" style="display: flex; flex-direction: column;">
          <div class="card-header">
            <div class="card-title">PAYMENT &amp; STORE DETAILS</div>
          </div>
          <div style="display: flex; justify-content: space-between; align-items: center; flex: 1;">
            <table style="font-size: 9px; font-weight: 600; color: #16213E;">
              <tr><td style="padding-bottom: 2px; width: 60px;">MODE</td><td>:</td><td style="padding-left: 6px;">NEFT / UPI / CASH</td></tr>
              <tr><td style="padding-bottom: 2px;">UPI ID</td><td>:</td><td style="padding-left: 6px; font-family: monospace;">{upi_id or 'saideep@upi'}</td></tr>
              {f'<tr><td style="padding-bottom: 2px;">A/C NO</td><td>:</td><td style="padding-left: 6px; font-family: monospace;">{bank_acc}</td></tr>' if bank_acc else ''}
              {f'<tr><td style="padding-bottom: 2px;">IFSC</td><td>:</td><td style="padding-left: 6px; font-family: monospace;">{bank_ifsc}</td></tr>' if bank_ifsc else ''}
              <tr><td colspan="3" style="padding-top: 3px; font-size: 8.5px; color: #7f8c8d; font-weight: 700;">SCAN TO PAY VIA ANY UPI APP</td></tr>
            </table>
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; width: 64px;">
              {qr_img_html}
              <div style="background: var(--navy); color: white; border-radius: 3px; padding: 1px 4px; font-size: 7.5px; font-weight: 700; text-align: center; width: 100%;">SCAN TO PAY</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Items Table -->
      <table class="items-table">
        <thead>
          <tr>
            <th style="width: 28px;">S.NO</th>
            <th style="text-align: left;">DESCRIPTION</th>
            <th style="width: 48px;">METAL</th>
            <th style="width: 75px;">TANCH+WAST</th>
            <th style="width: 60px;">WEIGHT(g)</th>
            <th style="width: 80px;">RATE(&#8377;)</th>
            <th style="width: 55px;">MAKING(&#8377;)</th>
            <th style="width: 55px;">OTHER(&#8377;)</th>
            <th style="width: 85px;">AMOUNT(&#8377;)</th>
          </tr>
        </thead>
        <tbody>
          {table_rows_combined}
        </tbody>
      </table>

      <!-- Metal Settlement Box (if applicable) -->
      {settlement_boxes_html}

      <!-- Bottom Calculations & Status Row -->
      <div style="display: flex; gap: 10px; margin-top: 6px; align-items: flex-start;">
        <div style="flex: 1; display: flex; flex-direction: column; gap: 4px;">
          {''.join(left_cards)}
          <div style="border: 1px dashed #CBD5E1; border-radius: 6px; padding: 4px 6px; font-size: 8px; color: #64748B; background: #F8FAFC; margin-top: 2px;">
            <b>Terms &amp; Conditions:</b> Goods once sold will be exchanged as per store policy. Weight &amp; purity guaranteed as per hallmark certification. All disputes subject to local jurisdiction.
          </div>
        </div>

        <div style="width: 250px; background: #FDFAF5; border: 1px solid #EAE3D2; border-radius: 6px; padding: 6px 8px;">
          <table style="width: 100%; font-size: 9.5px; font-weight: 600; color: #16213E; line-height: 1.4;">
            {''.join(right_totals_rows)}
          </table>
        </div>
      </div>

      <!-- Signatures -->
      <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-top: auto; padding-bottom: 50px; font-size: 9.5px; font-weight: 700; color: #334155;">
        <div style="border-top: 1px solid #94A3B8; width: 140px; text-align: center; padding-top: 3px;">
          Customer Signature
        </div>
        <div style="text-align: center; font-family: 'Cinzel', serif; font-size: 9.5px; color: #D4AF37;">
          Purity You Trust, Elegance You Deserve.
        </div>
        <div style="border-top: 1px solid #94A3B8; width: 160px; text-align: center; padding-top: 3px;">
          For {company_name}<br/><span style="font-size: 8px; font-weight: 400; color: #64748B;">Authorized Signatory</span>
        </div>
      </div>

      <!-- Navy Strip Footer -->
      <div style="position: absolute; bottom: 4mm; left: 6mm; right: 6mm; height: 32px; border-radius: 5px; background: #0B132B; display: flex; align-items: center; padding: 0 15px; justify-content: space-between; color: white; font-size: 8.5px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">
        <div>📍 {address}</div>
        <div>📞 {phone} | ✉️ {email}</div>
        <div>🌐 {website or 'www.saideepjewellers.com'}</div>
      </div>

    </div>
  </div>
</body>
</html>
"""
    return html


def generate_luxury_statement_html(
    entity_name: str,
    entity_phone: str,
    entity_type: str,  # 'Customer' or 'Supplier'
    entries: List[Dict[str, Any]],
    store_info: Dict[str, str],
    net_balance_cash: float,
    net_balance_gold: float,
    net_balance_silver: float
) -> str:
    """Generate professional luxury account statement HTML."""
    company_name = store_info.get("name") or "SAIDEEP JEWELLERS"
    initials = "".join([w[0] for w in company_name.split() if w])[:2].upper() or "SJ"
    tagline = store_info.get("tagline") or "PURITY & TRUST SINCE INCEPTION"
    address = store_info.get("address") or "Takhatgarh, Rajasthan"
    phone = store_info.get("phone") or "9876543210"
    email = store_info.get("email") or "info@saideepjewellers.com"
    logo_data_url = store_info.get("logo_data_url", "")

    total_debit = sum(float(e.get("debit") or 0.0) for e in entries)
    total_credit = sum(float(e.get("credit") or 0.0) for e in entries)

    rows_html = []
    for idx, e in enumerate(entries):
        dt_str = e.get("date") or "N/A"
        v_type = e.get("type") or "Voucher"
        v_no = e.get("number") or "-"
        desc = e.get("description") or "-"
        deb = float(e.get("debit") or 0.0)
        crd = float(e.get("credit") or 0.0)
        bal = float(e.get("balance") or 0.0)
        g_deb = float(e.get("gold_debit") or 0.0)
        g_crd = float(e.get("gold_credit") or 0.0)

        rows_html.append(f"""
        <tr>
          <td>{idx + 1}</td>
          <td>{dt_str}</td>
          <td><b>{v_type}</b></td>
          <td style="font-family: monospace; font-weight: 700;">{v_no}</td>
          <td style="text-align: left;">{desc}</td>
          <td style="color: #DC2626; font-weight: 700;">{_format_currency(deb) if deb > 0 else '-'}</td>
          <td style="color: #059669; font-weight: 700;">{_format_currency(crd) if crd > 0 else '-'}</td>
          <td style="font-weight: 800; color: #0F172A;">&#8377; {_format_currency(bal)}</td>
          <td>{f'{g_deb:.3f}g' if g_deb > 0 else '-'}</td>
          <td>{f'{g_crd:.3f}g' if g_crd > 0 else '-'}</td>
        </tr>
        """)

    if not rows_html:
        rows_html.append('<tr><td colspan="10" style="padding: 15px; color: #64748B;">No ledger transactions recorded yet.</td></tr>')

    logo_html = f'<img src="{logo_data_url}" style="max-width: 56px; max-height: 56px; object-fit: contain;" />' if logo_data_url else f'<div style="width: 50px; height: 50px; border-radius: 50%; border: 2px solid #D4AF37; display: flex; align-items: center; justify-content: center; font-family: \'Cinzel\', serif; font-size: 22px; color: #D4AF37; background: #FFFDF7;">{initials}</div>'

    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>{entity_type.upper()} STATEMENT - {entity_name}</title>
  <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Inter', sans-serif;
      color: #1E293B;
      background: white;
      font-size: 9.5px;
      line-height: 1.4;
    }}
    @page {{ size: A4 portrait; margin: 0; }}
    @media print {{ body {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }} }}
    .wrapper {{
      width: 210mm;
      min-height: 296.5mm;
      padding: 6mm 8mm 6mm 8mm;
      box-sizing: border-box;
      position: relative;
      display: flex;
      flex-direction: column;
    }}
    .header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 2px solid #D4AF37;
      padding-bottom: 6px;
      margin-bottom: 8px;
    }}
    .badge {{
      background: #0F172A;
      color: #D4AF37;
      border: 1px solid #D4AF37;
      border-radius: 6px;
      padding: 4px 14px;
      font-family: 'Cinzel', serif;
      font-size: 13px;
      font-weight: 800;
      letter-spacing: 1px;
    }}
    .summary-card {{
      background: #FDFAF5;
      border: 1px solid #EAE3D2;
      border-radius: 6px;
      padding: 6px 12px;
      display: flex;
      justify-content: space-between;
      margin-bottom: 8px;
    }}
    .table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 9px;
      margin-bottom: 12px;
    }}
    .table th {{
      background: #0F172A;
      color: #D4AF37;
      padding: 5px 4px;
      font-weight: 700;
      text-align: center;
      border: 1px solid #334155;
    }}
    .table td {{
      padding: 4px;
      border: 1px solid #E2E8F0;
      text-align: center;
    }}
    .table tr:nth-child(even) td {{ background: #F8FAFC; }}
  </style>
</head>
<body>
  <div class="wrapper">
    <div class="header">
      <div style="display: flex; align-items: center; gap: 10px;">
        {logo_html}
        <div>
          <h1 style="font-family: 'Cinzel', serif; font-size: 22px; color: #0F172A; font-weight: 800;">{company_name}</h1>
          <div style="font-size: 8px; font-weight: 700; color: #996515; letter-spacing: 1.5px;">{tagline}</div>
        </div>
      </div>
      <div style="text-align: right;">
        <div class="badge">{entity_type.upper()} ACCOUNT STATEMENT</div>
        <div style="font-size: 9px; color: #64748B; margin-top: 3px;">Date: {datetime.now().strftime('%d-%b-%Y')}</div>
      </div>
    </div>

    <!-- Entity Card & Net Due Summary -->
    <div class="summary-card">
      <div>
        <div style="font-size: 8.5px; font-weight: 700; color: #64748B; text-transform: uppercase;">ACCOUNT DETAILS</div>
        <div style="font-size: 14px; font-weight: 800; color: #0F172A;">{entity_name}</div>
        <div style="font-size: 9.5px; color: #334155;">Phone: {entity_phone or 'N/A'}</div>
      </div>
      <div style="text-align: right;">
        <div style="font-size: 8.5px; font-weight: 700; color: #64748B; text-transform: uppercase;">OUTSTANDING BALANCE</div>
        <div style="font-size: 15px; font-weight: 800; color: {'#DC2626' if net_balance_cash > 0 else '#059669'};">
          &#8377; {_format_currency(net_balance_cash)}
        </div>
        <div style="font-size: 9px; font-weight: 700; color: #D97706;">
          {f'Gold Due: {net_balance_gold:.3f}g | ' if net_balance_gold != 0 else ''}{f'Silver Due: {net_balance_silver:.3f}g' if net_balance_silver != 0 else ''}
        </div>
      </div>
    </div>

    <!-- Ledger Entries Table -->
    <table class="table">
      <thead>
        <tr>
          <th>#</th>
          <th>DATE</th>
          <th>TYPE</th>
          <th>VOUCHER #</th>
          <th>DESCRIPTION</th>
          <th>DEBIT (&#8377;)</th>
          <th>CREDIT (&#8377;)</th>
          <th>BALANCE (&#8377;)</th>
          <th>GOLD (g)</th>
          <th>SILVER (g)</th>
        </tr>
      </thead>
      <tbody>
        {''.join(rows_html)}
      </tbody>
      <tfoot>
        <tr style="background: #F1F5F9; font-weight: 800; font-size: 9.5px;">
          <td colspan="5" style="text-align: right; padding-right: 8px;">TOTALS:</td>
          <td style="color: #DC2626;">&#8377; {_format_currency(total_debit)}</td>
          <td style="color: #059669;">&#8377; {_format_currency(total_credit)}</td>
          <td style="color: #0F172A;">&#8377; {_format_currency(net_balance_cash)}</td>
          <td colspan="2" style="color: #D97706;">{f'{net_balance_gold:.3f}g Gold' if net_balance_gold != 0 else '-'}</td>
        </tr>
      </tfoot>
    </table>

    <div style="display: flex; justify-content: space-between; margin-top: auto; padding-bottom: 25px; font-size: 9px;">
      <div>Authorized Signatory<br/><br/><br/>______________________</div>
      <div style="text-align: right;">Customer / Party Acknowledgment<br/><br/><br/>______________________</div>
    </div>

    <!-- Strip Footer -->
    <div style="height: 24px; background: #0B132B; border-radius: 4px; display: flex; align-items: center; justify-content: space-between; padding: 0 12px; color: white; font-size: 8px;">
      <div>📍 {address}</div>
      <div>📞 {phone} | ✉️ {email}</div>
    </div>
  </div>
</body>
</html>
"""
    return html
