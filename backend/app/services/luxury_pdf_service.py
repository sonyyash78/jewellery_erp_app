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
    website = company.get("website") or (f"www.{email.split('@')[1]}" if "@" in email else "www.saideepjewellers.com")

    logo_data_url = company.get("logo_data_url", "")
    upi_id = company.get("upi_id") or "saideep@upi"
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
        number_label = "VOUCHER NO."
    elif is_purchase:
        badge_title = "PURCHASE VOUCHER"
        badge_icon = '<path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>'
        bill_to_label = "SUPPLIER / KARIGAR"
        number_label = "PURCHASE NO."
    else:
        badge_title = "TAX INVOICE"
        badge_icon = '<path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2h12c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/>'
        bill_to_label = "BILL TO"
        number_label = "INVOICE NO."

    # Financial totals
    subtotal = float(invoice.get("subtotal") or totals.get("subtotal") or 0.0)
    tax_amount = float(invoice.get("tax_amount") or totals.get("tax_amount") or 0.0)
    discount_amount = float(invoice.get("discount_amount") or totals.get("discount_amount") or 0.0)
    grand_total = float(invoice.get("grand_total") or totals.get("grand_total") or (subtotal + tax_amount - discount_amount))
    amount_paid = float(invoice.get("amount_paid") or invoice.get("cash_received") or 0.0)
    balance_due = float(invoice.get("balance_due") if invoice.get("balance_due") is not None else invoice.get("balance_amount") or (grand_total - amount_paid))

    total_old_val = float(invoice.get("total_old_value") or 0.0)
    settlement_type = invoice.get("settlement_type") or invoice.get("bill_type") or "Cash"

    # Metal tracking & deposits
    gold_bal_metal = float(invoice.get("gold_balance_metal_weight") or 0.0)
    silver_bal_metal = float(invoice.get("silver_balance_metal_weight") or 0.0)
    if gold_bal_metal == 0 and silver_bal_metal == 0:
        gold_bal_metal = float(invoice.get("balance_metal_weight") or 0.0)

    metal_rec_str = str(invoice.get("metal_received_str") or "").strip()
    metal_value = float(invoice.get("metal_received_value") or invoice.get("metal_given_value") or 0.0)

    # Derive from old_items if not explicitly given
    if not metal_rec_str and old_items:
        g_wt = sum(float(x.get("gross_weight") or x.get("net_weight") or 0.0) for x in old_items if "gold" in str(x.get("metal_type") or "").lower())
        s_wt = sum(float(x.get("gross_weight") or x.get("net_weight") or 0.0) for x in old_items if "silver" in str(x.get("metal_type") or "").lower())
        pts = []
        if g_wt > 0.001: pts.append(f"{g_wt:.3f}g Gold")
        if s_wt > 0.001: pts.append(f"{s_wt:.3f}g Silver")
        metal_rec_str = " + ".join(pts)
        if metal_value == 0:
            metal_value = sum(float(x.get("final_price") or x.get("amount") or 0.0) for x in old_items)

    has_metal_settlement = is_exchange or metal_value > 0 or gold_bal_metal > 0.001 or silver_bal_metal > 0.001

    # QR Code
    qr_data_url = _generate_qr_data_url(upi_id, upi_name, max(0.0, balance_due if balance_due > 0 else grand_total), f"Bill {inv_number}")
    qr_img_html = f'<img src="{qr_data_url}" style="width: 54px; height: 54px;" />' if qr_data_url else '<div style="width: 54px; height: 54px; border: 1px dashed #CBD5E1; display: flex; align-items: center; justify-content: center; font-size: 8px; color: #94A3B8;">NO QR</div>'

    # Build Items Table Rows
    item_rows = []
    has_gold = False
    has_silver = False
    gold_fine_billed = 0.0
    silver_fine_billed = 0.0
    gold_rate_applied = 0.0
    silver_rate_applied = 0.0

    for idx, item in enumerate(items, 1):
        m_type = str(item.get("metal_type") or "Gold").capitalize()
        is_g = "gold" in m_type.lower()
        if is_g:
            has_gold = True
        else:
            has_silver = True

        name = item.get("item_name") or "Jewellery Item"
        gross_w = float(item.get("gross_weight") or 0.0)
        stone_w = float(item.get("stone_weight") or 0.0)
        net_w = float(item.get("net_weight") or (gross_w - stone_w if gross_w > stone_w else gross_w))
        fine_w = float(item.get("fine_weight") or item.get("pure_weight") or net_w)

        if is_g:
            gold_fine_billed += fine_w
        else:
            silver_fine_billed += fine_w

        tanch = float(item.get("tanch_percentage") or item.get("touch_purity") or 100.0)
        wastage = float(item.get("wastage") or 0.0)
        rate = float(item.get("applied_rate") or item.get("rate") or 0.0)
        if is_g and rate > 0 and rate < 15000:
            rate = rate * 10
        elif not is_g and rate > 0 and rate < 1000:
            rate = rate * 1000

        if is_g and rate > 0 and gold_rate_applied == 0:
            gold_rate_applied = rate
        elif not is_g and rate > 0 and silver_rate_applied == 0:
            silver_rate_applied = rate

        making = float(item.get("making_charges") or 0.0)
        other = float(item.get("other_charges") or 0.0) + float(item.get("hallmark_charges") or 0.0)
        final_price = float(item.get("final_price") or item.get("amount") or 0.0)

        tanch_str = f"{tanch:.1f}%" if tanch % 1 else f"{int(tanch)}%"
        if wastage > 0:
            tanch_str += f" + {wastage:.1f}%" if wastage % 1 else f" + {int(wastage)}%"

        rate_unit = "per 10g" if is_g else "per kg"

        item_rows.append(f"""
        <tr>
          <td>{idx}</td>
          <td style="text-align: left; font-weight: 600;">
            <div style="font-size: 13px; color: #16213E; font-weight: 700;">{name}</div>
            <div style="font-size: 10px; color: #7f8c8d; font-weight: 400; margin-top: 1px;">Gross: {_format_weight(gross_w)}g | Fine: {_format_weight(fine_w)}g</div>
          </td>
          <td>{m_type}</td>
          <td>{tanch_str}</td>
          <td>{_format_weight(net_w)}</td>
          <td>&#8377; {_format_currency(rate)}<div style="font-size: 8px; color: #7f8c8d;">{rate_unit}</div></td>
          <td>{"-" if making == 0 else f"&#8377; {_format_currency(making)}"}</td>
          <td>{"-" if other == 0 else f"&#8377; {_format_currency(other)}"}</td>
          <td style="font-weight: 700; color: #0F172A;">&#8377; {_format_currency(final_price)}</td>
        </tr>
        """)

    # Build Old Items Rows
    gold_fine_received = 0.0
    silver_fine_received = 0.0
    old_rows = []

    if old_items:
        old_rows.append("""
        <tr style="background: #F8F4E8;">
          <td colspan="9" style="text-align: center; font-size: 9px; font-weight: 800; color: #8F6614; letter-spacing: 1px; padding: 3px 0;">
            OLD ITEMS DEPOSITED
          </td>
        </tr>
        """)
        for o_idx, o_item in enumerate(old_items, len(items) + 1):
            o_mtype = str(o_item.get("metal_type") or "Gold").capitalize()
            is_og = "gold" in o_mtype.lower()
            if is_og:
                has_gold = True
            else:
                has_silver = True

            o_name = o_item.get("item_name") or ("Gold Deposit" if is_og else "Silver Deposit")
            o_gross = float(o_item.get("gross_weight") or 0.0)
            o_net = float(o_item.get("net_weight") or o_gross)
            o_fine = float(o_item.get("fine_weight") or o_item.get("pure_weight") or o_net)

            if is_og:
                gold_fine_received += o_fine
            else:
                silver_fine_received += o_fine

            o_tanch = float(o_item.get("tanch_percentage") or o_item.get("touch_purity") or 100.0)
            o_rate = float(o_item.get("applied_rate") or o_item.get("rate") or (gold_rate_applied if is_og else silver_rate_applied))
            if is_og and o_rate > 0 and o_rate < 15000:
                o_rate = o_rate * 10
            elif not is_og and o_rate > 0 and o_rate < 1000:
                o_rate = o_rate * 1000

            o_val = float(o_item.get("final_price") or o_item.get("amount") or 0.0)
            o_rate_unit = "per 10g" if is_og else "per kg"

            old_rows.append(f"""
            <tr style="background: #FFFDF8;">
              <td>{o_idx}</td>
              <td style="text-align: left;">
                <div style="font-size: 13px; color: #16213E; font-weight: 700;">{o_name}</div>
                <div style="font-size: 10px; color: #7f8c8d; margin-top: 1px;">Gross: {_format_weight(o_gross)}g | Fine: {_format_weight(o_fine)}g</div>
              </td>
              <td>{o_mtype}</td>
              <td>{o_tanch:.1f}%</td>
              <td>{_format_weight(o_net)}</td>
              <td>&#8377; {_format_currency(o_rate)}<div style="font-size: 8px; color: #7f8c8d;">{o_rate_unit}</div></td>
              <td>-</td>
              <td>-</td>
              <td style="font-weight: 700; color: #0F172A;">{"-" if o_val == 0 else f"&#8377; {_format_currency(o_val)}"}</td>
            </tr>
            """)

    table_rows_combined = "".join(item_rows) + "".join(old_rows)

    # Metal Settlement Section (if applicable)
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
                <tr><td>Rate Applied</td><td style="text-align: right;">&#8377; {_format_currency(gold_rate_applied)}/10g</td></tr>
                <tr><td>Value Settled (Metal)</td><td style="text-align: right; color: #059669; font-weight: 700;">&#8377; {_format_currency(metal_value)}</td></tr>
                <tr style="border-top: 1px solid #E2D3B8; font-weight: 800;"><td style="color: {bal_color};">Gold Balance Due</td><td style="text-align: right; color: {bal_color};">{bal_label}</td></tr>
              </table>
            </div>
            """)

        settlement_boxes_html = f"""
        <div style="margin-top: 6px; border: 1px solid #E8D49E; border-radius: 6px; padding: 5px 8px; background: #FDFAF5;">
          <div style="text-align: center; font-family: 'Cinzel', serif; font-size: 9.5px; font-weight: 800; color: #996515; letter-spacing: 1px; margin-bottom: 4px;">
            &#9670; METAL SETTLEMENT &amp; PURITY SUMMARY &#9670;
            <div style="font-size: 7.5px; font-weight: 700; color: #B45309; text-transform: uppercase; margin-top: 1px;">
              OPTION 2: GOLD DUE (+{gold_bal_metal:.3f} gm Gold Balance Due)
            </div>
          </div>
          <div style="display: flex; gap: 8px;">
            {''.join(boxes)}
          </div>
        </div>
        """

    # --- 3-COLUMN LUXURY BOTTOM SUMMARY ---
    # Col 1: Amount Summary Table
    right_totals_rows = [
        f"<tr><td>Total Gold Amount</td><td style='text-align: right;'>:</td><td style='text-align: right;'>&#8377; {_format_currency(subtotal)}</td></tr>",
        f"<tr><td>Taxable Amount</td><td style='text-align: right;'>:</td><td style='text-align: right;'>&#8377; {_format_currency(subtotal)}</td></tr>",
        f"<tr><td>GST</td><td style='text-align: right;'>:</td><td style='text-align: right;'>&#8377; {_format_currency(tax_amount)}</td></tr>",
        f"<tr><td style='color: #059669; font-weight: 700;'>Metal Deposited Value</td><td style='text-align: right;'>:</td><td style='text-align: right; color: #059669; font-weight: 700;'>- &#8377; {_format_currency(metal_value or subtotal)}<br><span style='font-size: 7px; color: #7f8c8d;'>(Gold +{gold_bal_metal:.3f}g Due)</span></td></tr>"
    ]

    # Col 2: Center Cards (Metal Received + Final Settlement)
    center_cards = []

    # Card A: Metal Received
    if metal_value > 0 or metal_rec_str:
        center_cards.append(f"""
        <div style="background: #FFFBEB; border: 1px solid #FDE68A; border-radius: 8px; padding: 6px 8px; display: flex; align-items: center; gap: 8px;">
          <div style="width: 32px; height: 32px; border-radius: 50%; background: #F59E0B; color: white; display: flex; align-items: center; justify-content: center; flex-shrink: 0; box-shadow: 0 2px 4px rgba(245,158,11,0.2);">
            <svg viewBox="0 0 24 24" style="width: 16px; height: 16px; fill: currentColor;"><path d="M12 2L4 6v2h16V6l-8-4zm0 2.5l5.5 2.75h-11L12 4.5zM4 10v9h16v-9H4zm14 7H6v-5h12v5z"/></svg>
          </div>
          <div>
            <div style="color: #92400E; font-size: 8.5px; font-weight: 700; letter-spacing: 0.8px;">METAL RECEIVED</div>
            <div style="color: #78350F; font-size: 13px; font-weight: 800;">{metal_rec_str or f'{gold_fine_received:.3f}g Gold'}</div>
            <div style="color: #92400E; font-size: 8.5px;">Value: &#8377; {_format_currency(metal_value)}</div>
          </div>
        </div>
        """)
    elif amount_paid > 0:
        center_cards.append(f"""
        <div style="background: #ECFDF5; border: 1px solid #A7F3D0; border-radius: 8px; padding: 6px 8px; display: flex; align-items: center; gap: 8px;">
          <div style="width: 32px; height: 32px; border-radius: 50%; background: #10B981; color: white; display: flex; align-items: center; justify-content: center; flex-shrink: 0; box-shadow: 0 2px 4px rgba(16,185,129,0.2);">
            <svg viewBox="0 0 24 24" style="width: 16px; height: 16px; fill: white;"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>
          </div>
          <div>
            <div style="color: #065F46; font-size: 8.5px; font-weight: 700; letter-spacing: 0.8px;">CASH RECEIVED</div>
            <div style="color: #064E3B; font-size: 14px; font-weight: 800;">&#8377; {_format_currency(amount_paid)}</div>
            <div style="color: #065F46; font-size: 8.5px;">Thank you!</div>
          </div>
        </div>
        """)
    else:
        center_cards.append("""
        <div style="background: #F8F9FA; border: 1px solid #CED4DA; border-radius: 8px; padding: 6px 8px; display: flex; align-items: center; gap: 8px;">
          <div style="width: 32px; height: 32px; border-radius: 50%; background: #6C757D; color: white; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
            <svg viewBox="0 0 24 24" style="width: 16px; height: 16px; fill: white;"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>
          </div>
          <div>
            <div style="color: #495057; font-size: 8.5px; font-weight: 700; letter-spacing: 0.8px;">PAYMENT PENDING</div>
            <div style="color: #212529; font-size: 12px; font-weight: 700;">No payment received yet</div>
          </div>
        </div>
        """)

    # Card B: Final Settlement Card
    is_cash_cleared = balance_due <= 0.01 and balance_due >= -0.01
    has_metal_due = gold_bal_metal > 0.001 or silver_bal_metal > 0.001

    if is_cash_cleared and not has_metal_due:
        center_cards.append("""
        <div style="background: #ECFDF5; border: 1px solid #A7F3D0; border-radius: 8px; padding: 6px 8px; display: flex; align-items: center; gap: 8px;">
          <div style="width: 24px; height: 24px; border-radius: 50%; background: #10B981; color: white; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
            <svg viewBox="0 0 24 24" style="width: 14px; height: 14px; fill: white;"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>
          </div>
          <div>
            <div style="color: #065F46; font-size: 8.5px; font-weight: 700; letter-spacing: 0.8px;">FINAL SETTLEMENT</div>
            <div style="color: #064E3B; font-size: 15px; font-weight: 800;">FULLY PAID &#10003;</div>
            <div style="color: #065F46; font-size: 7.5px; margin-top: 1px;">All dues cleared for this bill.</div>
          </div>
        </div>
        """)
    else:
        due_blocks = []
        if balance_due > 0.01:
            due_blocks.append(f"""
            <div style="background: #FFFFFF; border: 1px solid #FCA5A5; border-radius: 4px; padding: 2.5px 6px; display: flex; justify-content: space-between; align-items: center;">
              <span style="color: #7F1D1D; font-size: 8.5px; font-weight: 800;">CASH DUE:</span>
              <span style="color: #991B1B; font-size: 11px; font-weight: 900;">&#8377; {_format_currency(balance_due)}</span>
            </div>
            """)
        if gold_bal_metal > 0.001:
            due_blocks.append(f"""
            <div style="background: #FFFDF5; border: 1px solid #FDE68A; border-radius: 4px; padding: 2.5px 6px; display: flex; justify-content: space-between; align-items: center;">
              <span style="color: #92400E; font-size: 8.5px; font-weight: 800;">GOLD DUE:</span>
              <span style="color: #B45309; font-size: 11px; font-weight: 900;">+{gold_bal_metal:.3f} gm</span>
            </div>
            """)
        if silver_bal_metal > 0.001:
            due_blocks.append(f"""
            <div style="background: #F9FAFB; border: 1px solid #D1D5DB; border-radius: 4px; padding: 2.5px 6px; display: flex; justify-content: space-between; align-items: center;">
              <span style="color: #374151; font-size: 8.5px; font-weight: 800;">SILVER DUE:</span>
              <span style="color: #1F2937; font-size: 11px; font-weight: 900;">+{silver_bal_metal:.3f} gm</span>
            </div>
            """)

        badge_txt = "METAL DUE" if has_metal_due else "DUE"
        center_cards.append(f"""
        <div style="background: #FFFBEB; border: 1.5px solid #FDE68A; border-radius: 8px; padding: 5px 8px; width: 100%; box-sizing: border-box;">
          <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px dashed #FDE68A; padding-bottom: 3px; margin-bottom: 3px;">
            <div style="display: flex; align-items: center; gap: 5px;">
              <div style="width: 16px; height: 16px; border-radius: 50%; background: #F59E0B; color: white; display: flex; align-items: center; justify-content: center; font-size: 9px; font-weight: 800;">!</div>
              <span style="color: #92400E; font-size: 8px; font-weight: 800; letter-spacing: 0.8px;">FINAL SETTLEMENT</span>
            </div>
            <span style="background: #FEF3C7; color: #92400E; font-size: 7.5px; font-weight: 800; padding: 1px 5px; border-radius: 10px; border: 1px solid #FDE68A;">{badge_txt}</span>
          </div>
          <div style="display: flex; flex-direction: column; gap: 2.5px;">
            {''.join(due_blocks)}
          </div>
          <div style="font-size: 6.5px; color: #92400E; opacity: 0.85; margin-top: 2px; text-align: center; font-style: italic;">*This Bill Due only</div>
        </div>
        """)

    # Col 3: Payment Details & Other Details
    pay_mode_label = "METAL" if (metal_value > 0 and amount_paid == 0) else ("CASH" if amount_paid > 0 else "NEFT / UPI / CASH")
    pay_details_rows = []
    if metal_value > 0:
        pay_details_rows.append(f"<tr><td style='width: 50%;'>Metal Value Settled</td><td style='text-align: right;'>:</td><td style='text-align: right;'>&#8377; {_format_currency(metal_value)}</td></tr>")
    if amount_paid > 0:
        pay_details_rows.append(f"<tr><td style='width: 50%;'>Cash Paid</td><td style='text-align: right;'>:</td><td style='text-align: right;'>&#8377; {_format_currency(amount_paid)}</td></tr>")
    pay_details_rows.append(f"<tr><td>Date</td><td style='text-align: right;'>:</td><td style='text-align: right;'>{inv_date}</td></tr>")
    pay_details_rows.append(f"<tr><td>Mode</td><td style='text-align: right;'>:</td><td style='text-align: right;'>{pay_mode_label}</td></tr>")
    if metal_rec_str:
        pay_details_rows.append(f"<tr><td>Metal Deposited</td><td style='text-align: right;'>:</td><td style='text-align: right;'>{metal_rec_str}</td></tr>")
    if gold_bal_metal > 0.001:
        pay_details_rows.append(f"<tr><td style='color: #B45309; font-weight: 700;'>Gold Balance Due</td><td style='text-align: right;'>:</td><td style='text-align: right; color: #B45309; font-weight: 700;'>+{gold_bal_metal:.3f} gm</td></tr>")
    if balance_due > 0.01:
        pay_details_rows.append(f"<tr><td style='color: #DC2626; font-weight: 700;'>Cash Due</td><td style='text-align: right;'>:</td><td style='text-align: right; color: #DC2626; font-weight: 700;'>&#8377; {_format_currency(balance_due)}</td></tr>")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Invoice {inv_number}</title>
  <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {{
      --navy: #0F172A;
      --navy-light: #1E293B;
      --navy-dark: #0A0F1D;
      --gold: #D4AF37;
      --gold-light: #F6E6B4;
      --gold-dark: #996515;
      --gold-border: #E8D49E;
      --text: #1E293B;
      --text-muted: #64748B;
      --border: #E2E8F0;
      --card-bg: #FDFAF5;
      --card-border: #EAE3D2;
      --green: #059669;
      --green-bg: #ECFDF5;
      --red: #DC2626;
      --red-bg: #FEF2F2;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      color: var(--text);
      background: white;
      -webkit-font-smoothing: antialiased;
      line-height: 1.4;
    }}
    @page {{ size: A4 portrait; margin: 0; }}
    @media print {{
      body {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
    }}
    .pdf-container {{
      width: 100%;
      background: white;
      display: flex;
      flex-direction: column;
      align-items: center;
    }}
    .invoice-wrapper {{
      width: 210mm;
      height: 296.5mm;
      background: white;
      position: relative;
      padding: 4mm 5mm 5mm 5mm;
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
      opacity: 0.035;
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
      gap: 15px;
    }}
    .logo-circle {{
      width: 64px;
      height: 64px;
      border-radius: 50%;
      border: 2px solid var(--gold);
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: 'Cinzel', serif;
      font-size: 32px;
      color: var(--gold);
      background: radial-gradient(circle, #FFFDF7 0%, #FAF6EA 100%);
    }}
    .company-info h1 {{
      font-family: 'Cinzel', serif;
      font-size: 24px;
      font-weight: 700;
      color: var(--navy);
      line-height: 1.15;
      letter-spacing: 2px;
      margin-bottom: 2px;
    }}
    .tagline {{
      font-family: 'Inter', sans-serif;
      font-size: 8.5px;
      font-weight: 700;
      color: var(--gold-dark);
      letter-spacing: 2.2px;
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
      font-weight: 700;
      letter-spacing: 1.2px;
      display: inline-flex;
      align-items: center;
      gap: 7px;
      margin-bottom: 2px;
      box-shadow: 0 2px 8px rgba(15, 23, 42, 0.12);
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
    }}
    .meta-table td {{
      padding: 1px 6px 1px 0;
    }}
    .meta-table td:first-child {{
      width: 85px;
      color: var(--text-muted);
      font-size: 8.5px;
    }}
    .diamond-divider {{
      display: flex;
      align-items: center;
      margin: 2px 0 5px;
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
      margin: 0 10px;
    }}
    .cards-row {{
      display: flex;
      gap: 10px;
      margin-bottom: 3px;
    }}
    .info-card {{
      flex: 1;
      border: 1px solid var(--card-border);
      border-radius: 8px;
      padding: 5px 9px;
      background: var(--card-bg);
      box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }}
    .card-header {{
      display: flex;
      align-items: center;
      gap: 6px;
      margin-bottom: 4px;
      border-bottom: 1px solid var(--card-border);
      padding-bottom: 3px;
    }}
    .card-title {{
      font-family: 'Cinzel', serif;
      font-size: 10px;
      font-weight: 800;
      color: #0F172A;
      letter-spacing: 1px;
    }}
    .items-table {{
      width: 100%;
      border-collapse: separate;
      border-spacing: 0 1.5px;
      margin-top: 2px;
      font-variant-numeric: tabular-nums;
    }}
    .items-table th {{
      background: linear-gradient(180deg, #0F172A 0%, #162036 100%);
      color: #D4AF37;
      padding: 4px 4px;
      font-size: 8.5px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.8px;
      border-bottom: 2px solid #D4AF37;
    }}
    .items-table th:first-child {{ border-radius: 4px 0 0 0; }}
    .items-table th:last-child {{ border-radius: 0 4px 0 0; }}
    .items-table tbody td {{
      background: #FFFFFF;
      padding: 3px 4px;
      font-size: 9.5px;
      border-top: 1px solid #ECE7DB;
      border-bottom: 1px solid #ECE7DB;
      text-align: center;
      color: #1E293B;
    }}
    .items-table tbody tr:nth-child(even) td {{ background: #FAF8F2; }}
    .items-table th:nth-child(2), .items-table td:nth-child(2) {{ text-align: left; }}
  </style>
</head>
<body>
  <div class="pdf-container">
    <div class="invoice-wrapper">
      <div class="watermark">{initials}</div>
      <div class="content">

        <!-- Header -->
        <div class="header">
          <div class="logo-section">
            <div class="logo-circle">{initials}</div>
            <div class="company-info">
              <h1>{company_name.replace(' ', '<br>')}</h1>
              <div class="tagline">{tagline}</div>
            </div>
          </div>
          <div style="text-align: right; display: flex; flex-direction: column; align-items: flex-end;">
            <div class="tax-invoice-badge">
              <svg viewBox="0 0 24 24">{badge_icon}</svg>
              {badge_title}
            </div>
            <table class="meta-table" style="margin-left: auto;">
              <tr><td>{number_label}</td><td>:</td><td style="color: var(--navy); font-weight: 800;">{inv_number}</td></tr>
              <tr><td>DATE</td><td>:</td><td style="color: var(--navy);">{inv_date}</td></tr>
              <tr><td>PLACE</td><td>:</td><td style="color: var(--navy);">{address.split(',')[0]}</td></tr>
              <tr><td>GSTIN</td><td>:</td><td style="color: var(--navy);">{gstin or 'N/A'}</td></tr>
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
                <tr><td style="padding-bottom: 2px; width: 60px;">MODE</td><td>:</td><td style="padding-left: 6px;">{pay_mode_label}</td></tr>
                <tr><td style="padding-bottom: 2px;">UPI ID</td><td>:</td><td style="padding-left: 6px; font-family: monospace;">{upi_id}</td></tr>
                {f'<tr><td style="padding-bottom: 2px;">A/C NO</td><td>:</td><td style="padding-left: 6px; font-family: monospace;">{bank_acc}</td></tr>' if bank_acc else ''}
                {f'<tr><td style="padding-bottom: 2px;">IFSC</td><td>:</td><td style="padding-left: 6px; font-family: monospace;">{bank_ifsc}</td></tr>' if bank_ifsc else ''}
                <tr><td colspan="3" style="padding-top: 3px; font-size: 8px; color: #7f8c8d; font-weight: 700;">SCAN TO PAY VIA ANY UPI APP</td></tr>
              </table>
              <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; width: 60px;">
                {qr_img_html}
                <div style="background: var(--navy); color: white; border-radius: 3px; padding: 1px 3px; font-size: 7px; font-weight: 700; text-align: center; width: 100%;">SCAN TO PAY</div>
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

        <!-- 3-Column Luxury Bottom Summary Row (Matching App Layout) -->
        <div style="display: grid; grid-template-columns: 1.15fr 1fr 1fr; gap: 8px; margin-top: 5px; align-items: stretch;">
          <!-- Col 1: Amount Summary -->
          <div style="background: #FDFAF5; border: 1px solid #EAE3D2; border-radius: 6px; padding: 5px 8px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
              <div style="font-family: 'Cinzel', serif; font-size: 9.5px; font-weight: 800; color: #0F172A; border-bottom: 1px solid #EAE3D2; padding-bottom: 2px; margin-bottom: 3px; display: flex; align-items: center; gap: 4px;">
                <span style="color: #D4AF37;">&#9632;</span> AMOUNT SUMMARY
              </div>
              <table style="width: 100%; font-size: 9px; font-weight: 600; color: #16213E; line-height: 1.4;">
                {''.join(right_totals_rows)}
              </table>
            </div>
            <div style="background: #0F172A; color: white; border-radius: 4px; padding: 4px 8px; margin-top: 5px; text-align: center;">
              <div style="font-size: 7px; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.5px;">CASH BALANCE DUE</div>
              <div style="font-size: 13px; font-weight: 800; color: #F1F5F9; margin-top: 1px;">&#8377; {_format_currency(balance_due)}</div>
            </div>
          </div>

          <!-- Col 2: Center Cards -->
          <div style="display: flex; flex-direction: column; gap: 4px; justify-content: flex-start;">
            {''.join(center_cards)}
            <div style="border: 1px dashed #CBD5E1; border-radius: 5px; padding: 3px 6px; font-size: 7px; color: #64748B; background: #F8FAFC; margin-top: auto;">
              <b>Terms &amp; Conditions:</b> Goods once sold will be exchanged as per store policy. Weight &amp; purity guaranteed as per hallmark certification.
            </div>
          </div>

          <!-- Col 3: Payment Details & Other Details -->
          <div style="display: flex; flex-direction: column; gap: 4px;">
            <div style="background: #FDFAF5; border: 1px solid #EAE3D2; border-radius: 5px; padding: 4px 7px;">
              <div style="font-family: 'Cinzel', serif; font-size: 8.5px; font-weight: 800; color: #0F172A; margin-bottom: 2px; border-bottom: 1px solid #EAE3D2; padding-bottom: 2px;">
                PAYMENT DETAILS
              </div>
              <table style="width: 100%; font-size: 8px; color: #334155; line-height: 1.35;">
                {''.join(pay_details_rows)}
              </table>
            </div>

            <div style="background: #FDFAF5; border: 1px solid #EAE3D2; border-radius: 5px; padding: 4px 7px; flex: 1;">
              <div style="font-family: 'Cinzel', serif; font-size: 8.5px; font-weight: 800; color: #0F172A; margin-bottom: 2px; border-bottom: 1px solid #EAE3D2; padding-bottom: 2px;">
                OTHER DETAILS
              </div>
              <table style="width: 100%; font-size: 7.5px; color: #334155; line-height: 1.35;">
                <tr><td style="width: 45%;">Hallmark</td><td>:</td><td style="text-align: right;">BIS 916 (Gold) / BIS 925 (Silver)</td></tr>
                <tr><td>Wastage</td><td>:</td><td style="text-align: right;">0.00%</td></tr>
                <tr><td>Making Charges</td><td>:</td><td style="text-align: right;">Gold &#8377; 1,000.00/gm<br>Silver &#8377; 20.00/gm</td></tr>
                <tr><td>Remarks</td><td>:</td><td style="text-align: right;">-</td></tr>
              </table>
            </div>
          </div>
        </div>

        <!-- Signatures Row -->
        <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-top: auto; padding-bottom: 42px; font-size: 8.5px; font-weight: 600; color: #334155;">
          <div style="border-top: 1px solid #94A3B8; width: 140px; text-align: center; padding-top: 2px;">
            Customer Signature
          </div>
          <div style="text-align: center; font-family: 'Cinzel', serif; font-size: 9px; font-weight: 700; color: var(--gold); letter-spacing: 1px;">
            PURITY YOU TRUST, ELEGANCE YOU DESERVE.
          </div>
          <div style="border-top: 1px solid #94A3B8; width: 150px; text-align: center; padding-top: 2px;">
            For {company_name}<br/><span style="font-size: 7.5px; font-weight: 400; color: #64748B;">Authorized Signatory</span>
          </div>
        </div>

        <!-- Circular Overlapping Thank You Badge -->
        <div style="position: absolute; bottom: 2mm; right: 18px; z-index: 10; width: 56px; height: 56px; border-radius: 50%; background: #0B132B; border: 2px solid var(--gold); display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: 0 2px 8px rgba(0,0,0,0.2);">
          <svg viewBox="0 0 24 24" style="width: 12px; height: 12px; fill: var(--gold); margin-bottom: 1px;"><path d="M12 2l-5.5 9h11z"/><path d="M12 22l5.5-9h-11z"/></svg>
          <div style="font-family: 'Cinzel', serif; font-size: 8px; font-weight: 800; color: var(--gold); line-height: 1.1; text-align: center;">THANK<br>YOU</div>
          <div style="font-family: 'Inter', sans-serif; font-size: 5px; color: var(--gold); margin-top: 1px; text-transform: uppercase; letter-spacing: 0.6px;">For Your Visit</div>
        </div>

        <!-- Navy Strip Footer -->
        <div style="position: absolute; bottom: 4mm; left: 5mm; right: 5mm; height: 32px; border-radius: 5px; background: #0B132B; display: flex; align-items: center; padding: 0 85px 0 15px; justify-content: space-between; color: white; font-size: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">
          <div>&#128205; {address}</div>
          <div>&#128222; {phone} | &#9993;&#65039; {email}</div>
          <div>&#127760; {website}</div>
        </div>

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

