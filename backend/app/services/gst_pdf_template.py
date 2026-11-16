"""
GST Tax Invoice Template
========================
Pixel-accurate layout matching GST reference tax invoice.
Strictly used ONLY when company.gst_enabled = True.
"""
from typing import Dict, Any, List
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
import re


def _round_cur(val: Decimal) -> Decimal:
    return Decimal(str(val)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _resolve_item_hsn(it: Dict[str, Any]) -> str:
    explicit = it.get("hsn_code") or it.get("hsn")
    if explicit and str(explicit).strip():
        return str(explicit).strip()
    m_type = str(it.get("metal_type") or it.get("item_type") or "").upper()
    desc = str(it.get("description") or it.get("item_name") or "").upper()
    is_bullion = bool(re.search(r"\b(BAR|BULLION)\b", desc) or re.search(r"\b(BAR|BULLION)\b", m_type))
    if "SILVER" in m_type or (not m_type and "SILVER" in desc):
        return "71069120" if is_bullion else "711311"
    if "DIAMOND" in m_type or (not m_type and "DIAMOND" in desc):
        return "71049120"
    return "71081200" if is_bullion else "711319"


def generate_gst_tax_invoice_html(data: Dict[str, Any]) -> str:
    company = data.get("company", {})
    inv = data.get("invoice", data)
    buyer = data.get("buyer", data.get("customer", {}))
    items = data.get("items", [])
    gst_calc = data.get("gst_calculation", {})
    einvoice = data.get("einvoice", {})

    inv_num = inv.get("invoice_number", "")
    inv_date = inv.get("invoice_date", datetime.now().strftime("%Y-%m-%d"))
    try:
        if isinstance(inv_date, str):
            dt_obj = datetime.strptime(inv_date[:10], "%Y-%m-%d")
        else:
            dt_obj = inv_date
        formatted_date = dt_obj.strftime("%d-%b-%y")
    except Exception:
        formatted_date = str(inv_date)

    co_name = company.get("name") or "Jewellery Store"
    co_addr = company.get("address") or ""
    co_gstin = company.get("gstin") or ""
    co_pan = company.get("pan") or ""
    co_state = company.get("state") or ""
    co_state_code = company.get("state_code") or ""
    co_phone = company.get("phone") or ""
    co_email = company.get("email") or ""
    co_jurisdiction = company.get("jurisdiction_city") or company.get("city") or ""
    co_declaration = company.get("declaration") or "We declare that this invoice shows the actual price of the goods described and that all particulars are true and correct."
    co_bank_name = company.get("bank_name") or ""
    co_bank_acc = company.get("bank_account_no") or ""
    co_bank_ifsc = company.get("bank_ifsc") or ""
    co_bank_branch = company.get("bank_branch") or ""
    co_footer_note = company.get("computer_generated_note") or ""

    bank_line_parts = [p for p in [co_bank_name, f"A/c: {co_bank_acc}" if co_bank_acc else "", f"IFSC: {co_bank_ifsc}" if co_bank_ifsc else "", co_bank_branch] if p]
    bank_html = f'<div style="font-size: 7pt; margin-bottom: 3px;"><b>Bank Details:</b> {" | ".join(bank_line_parts)}</div>' if bank_line_parts else ""

    is_purchase = (data.get("type") == "purchase") or str(inv_num).startswith(("PUR-", "SJ_P", "PG_P", "SJ/P"))
    
    if is_purchase:
        header_title = "TAX INVOICE (PURCHASE VOUCHER)"
        party_box_label = "Supplier / Vendor (Billed from)"
        party = data.get("seller") or data.get("supplier") or data.get("customer") or {}
        buyer_name = (party.get("name") or party.get("first_name") or "Supplier / Vendor").strip()
        if party.get("last_name"):
            buyer_name += f" {party['last_name']}"
        buyer_addr = party.get("address", "")
        buyer_gstin = party.get("gstin") or party.get("gst_number") or ""
        buyer_pan = party.get("pan") or party.get("aadhaar_pan") or ""
        buyer_state = party.get("state", "Rajasthan")
        buyer_state_code = str(party.get("state_code", "08")).zfill(2)
        place_of_supply = party.get("place_of_supply") or buyer_state
        buyer_contact_person = party.get("contact_person") or buyer_name
        buyer_phone = party.get("phone") or party.get("mobile") or ""
        buyer_email = party.get("email", "")
    else:
        header_title = "TAX INVOICE"
        party_box_label = "Buyer (Bill to)"
        buyer_name = (buyer.get("name") or buyer.get("first_name") or "Walk-in Customer").strip()
        if buyer.get("last_name"):
            buyer_name += f" {buyer['last_name']}"
        buyer_addr = buyer.get("address", "")
        buyer_gstin = buyer.get("gstin") or buyer.get("gst_number") or ""
        buyer_pan = buyer.get("pan") or buyer.get("aadhaar_pan") or ""
        buyer_state = buyer.get("state", "Rajasthan")
        buyer_state_code = str(buyer.get("state_code", "08")).zfill(2)
        place_of_supply = buyer.get("place_of_supply") or buyer_state
        buyer_contact_person = buyer.get("contact_person", "")
        buyer_phone = buyer.get("phone") or buyer.get("mobile") or ""
        buyer_email = buyer.get("email", "")

    # Totals
    seller_sc = str(co_state_code or "08").strip().zfill(2)
    buyer_sc = str(buyer_state_code or seller_sc or "08").strip().zfill(2)
    is_intra = gst_calc.get("is_intra_state", seller_sc == buyer_sc)
    subtotal = float(gst_calc.get("total_taxable_amount") or inv.get("subtotal") or inv.get("total_taxable") or 0.0)
    total_tax = float(gst_calc.get("total_tax_amount") or inv.get("tax_amount") or (float(inv.get("cgst", 0.0)) + float(inv.get("sgst", 0.0)) + float(inv.get("igst", 0.0))) or 0.0)
    cgst_tot = float(gst_calc.get("total_cgst_amount") or inv.get("cgst") or 0.0)
    sgst_tot = float(gst_calc.get("total_sgst_amount") or inv.get("sgst") or 0.0)
    igst_tot = float(gst_calc.get("total_igst_amount") or inv.get("igst") or 0.0)
    if cgst_tot == 0.0 and total_tax > 0 and is_intra:
        cgst_tot = round(total_tax / 2, 2)
        sgst_tot = round(total_tax - cgst_tot, 2)
    grand_total = float(gst_calc.get("grand_total") or inv.get("grand_total") or (subtotal + total_tax))
    round_off = float(gst_calc.get("round_off") or round(grand_total - (subtotal + total_tax), 2))

    def _number_to_indian_words(num):
        units = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten',
                 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen']
        tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']
        def two_digits(n):
            if n < 20: return units[n]
            return tens[n // 10] + (' ' + units[n % 10] if n % 10 else '')
        def three_digits(n):
            if n < 100: return two_digits(n)
            return units[n // 100] + ' Hundred' + (' and ' + two_digits(n % 100) if n % 100 else '')
        n = int(round(num))
        if n == 0: return 'Zero Rupees Only'
        crore = n // 10000000
        n %= 10000000
        lakh = n // 100000
        n %= 100000
        thousand = n // 1000
        n %= 1000
        parts = []
        if crore: parts.append(three_digits(crore) + ' Crore')
        if lakh: parts.append(two_digits(lakh) + ' Lakh')
        if thousand: parts.append(two_digits(thousand) + ' Thousand')
        if n: parts.append(three_digits(n))
        return 'Indian Rupees ' + ' '.join(parts) + ' Only'

    # Calculate total quantity
    tot_qty = sum(float(it.get("quantity") or it.get("net_weight") or it.get("gross_weight") or 0.0) for it in items)
    default_unit = items[0].get("unit", "Gms") if items else "Gms"

    # Item rows
    item_rows = []
    for idx, it in enumerate(items, 1):
        desc = it.get("description") or it.get("item_name") or "Jewellery Item"
        hsn = _resolve_item_hsn(it)
        qty = float(it.get("quantity") or it.get("net_weight") or it.get("gross_weight") or 1.0)
        unit = it.get("unit", "Gms")
        amt = float(it.get("amount") or it.get("taxable_amount") or it.get("final_price") or it.get("metal_value") or 0.0)
        rate = float(it.get("rate") or it.get("applied_rate") or it.get("metal_rate") or (amt / qty if qty > 0 else 0.0))
        row = f"""
        <tr class="item-row">
          <td class="col-sr">{idx}</td>
          <td class="col-desc"><b>{desc}</b></td>
          <td class="col-hsn">{hsn}</td>
          <td class="col-qty"><b>{qty:,.4f} {unit}</b></td>
          <td class="col-rate">{rate:,.2f}</td>
          <td class="col-per">{unit}</td>
          <td class="col-amt"><b>{amt:,.2f}</b></td>
        </tr>
        """
        item_rows.append(row)

    item_rows_html = "".join(item_rows)

    # Tax summary table
    hsn_table = list(gst_calc.get("hsn_tax_table", []))
    if not hsn_table and subtotal > 0:
        hsn_map: Dict[str, Dict[str, Any]] = {}
        for it in items:
            h_c = _resolve_item_hsn(it)
            a_v = Decimal(str(it.get("amount") or it.get("taxable_amount") or it.get("final_price") or it.get("metal_value") or 0.0))
            g_rate = Decimal(str(it.get("gst_rate") or "3.00"))
            if h_c not in hsn_map:
                hsn_map[h_c] = {"taxable": Decimal("0.00"), "gst_rate": g_rate}
            hsn_map[h_c]["taxable"] += a_v
        if not hsn_map:
            hsn_map["711319"] = {"taxable": Decimal(str(subtotal)), "gst_rate": Decimal("3.00")}
        for h_code, h_info in hsn_map.items():
            h_taxable = _round_cur(h_info["taxable"])
            g_rate = h_info["gst_rate"]
            if is_intra:
                half_rate = g_rate / Decimal("2")
                h_cgst = _round_cur(h_taxable * (half_rate / Decimal("100")))
                h_sgst = _round_cur(h_taxable * (half_rate / Decimal("100")))
                h_igst_rate = Decimal("0.00")
                h_igst = Decimal("0.00")
                h_tax = _round_cur(h_cgst + h_sgst)
            else:
                half_rate = Decimal("0.00")
                h_cgst = Decimal("0.00")
                h_sgst = Decimal("0.00")
                h_igst_rate = g_rate
                h_igst = _round_cur(h_taxable * (g_rate / Decimal("100")))
                h_tax = h_igst
            hsn_table.append({
                "hsn_code": h_code,
                "taxable_amount": float(h_taxable),
                "cgst_rate": float(half_rate),
                "cgst_amount": float(h_cgst),
                "sgst_rate": float(half_rate),
                "sgst_amount": float(h_sgst),
                "igst_rate": float(h_igst_rate),
                "igst_amount": float(h_igst),
                "total_tax_amount": float(h_tax),
            })
        if hsn_table and not gst_calc:
            subtotal = float(_round_cur(sum(Decimal(str(r["taxable_amount"])) for r in hsn_table)))
            cgst_tot = float(_round_cur(sum(Decimal(str(r["cgst_amount"])) for r in hsn_table)))
            sgst_tot = float(_round_cur(sum(Decimal(str(r["sgst_amount"])) for r in hsn_table)))
            igst_tot = float(_round_cur(sum(Decimal(str(r["igst_amount"])) for r in hsn_table)))
            total_tax = float(_round_cur(Decimal(str(cgst_tot)) + Decimal(str(sgst_tot)) + Decimal(str(igst_tot))))
            if not inv.get("grand_total"):
                grand_total = float(round(subtotal + total_tax))
            round_off = round(grand_total - (subtotal + total_tax), 2)
    words_total = gst_calc.get("amount_chargeable_words") or _number_to_indian_words(grand_total)
    words_tax = gst_calc.get("tax_amount_words") or _number_to_indian_words(total_tax)
    tax_rows = []
    for row_data in hsn_table:
        h = row_data.get("hsn_code", "711319")
        tx = float(row_data.get("taxable_amount", 0.0))
        cr = float(row_data.get("cgst_rate", 1.5))
        ca = float(row_data.get("cgst_amount", 0.0))
        sr = float(row_data.get("sgst_rate", 1.5))
        sa = float(row_data.get("sgst_amount", 0.0))
        ir = float(row_data.get("igst_rate", 3.0))
        ia = float(row_data.get("igst_amount", 0.0))
        tt = float(row_data.get("total_tax_amount", ca + sa + ia))
        if is_intra:
            r = f"""
            <tr>
              <td style="border: 1px solid #000; padding: 3px; text-align: left;">{h}</td>
              <td style="border: 1px solid #000; text-align: right; padding: 3px;">{tx:,.2f}</td>
              <td style="border: 1px solid #000; text-align: right; padding: 3px;">{cr:.2f}%</td>
              <td style="border: 1px solid #000; text-align: right; padding: 3px;">{ca:,.2f}</td>
              <td style="border: 1px solid #000; text-align: right; padding: 3px;">{sr:.2f}%</td>
              <td style="border: 1px solid #000; text-align: right; padding: 3px;">{sa:,.2f}</td>
              <td style="border: 1px solid #000; text-align: right; padding: 3px;">{tt:,.2f}</td>
            </tr>
            """
        else:
            r = f"""
            <tr>
              <td style="border: 1px solid #000; padding: 3px; text-align: left;">{h}</td>
              <td style="border: 1px solid #000; text-align: right; padding: 3px;">{tx:,.2f}</td>
              <td style="border: 1px solid #000; text-align: right; padding: 3px;">{ir:.2f}%</td>
              <td style="border: 1px solid #000; text-align: right; padding: 3px;">{ia:,.2f}</td>
              <td style="border: 1px solid #000; text-align: right; padding: 3px;">{tt:,.2f}</td>
            </tr>
            """
        tax_rows.append(r)

    tax_rows_html = "".join(tax_rows)

    if is_intra:
        tax_header_html = """
        <tr>
          <th rowspan="2" style="border: 1px solid #000; padding: 3px; width: 18%;">HSN/SAC</th>
          <th rowspan="2" style="border: 1px solid #000; padding: 3px; width: 22%;">Taxable Value</th>
          <th colspan="2" style="border: 1px solid #000; padding: 3px;">CGST</th>
          <th colspan="2" style="border: 1px solid #000; padding: 3px;">SGST/UTGST</th>
          <th rowspan="2" style="border: 1px solid #000; padding: 3px; width: 18%;">Total Tax Amount</th>
        </tr>
        <tr>
          <th style="border: 1px solid #000; padding: 2px;">Rate</th>
          <th style="border: 1px solid #000; padding: 2px;">Amount</th>
          <th style="border: 1px solid #000; padding: 2px;">Rate</th>
          <th style="border: 1px solid #000; padding: 2px;">Amount</th>
        </tr>
        """
        cgst_rate_val = hsn_table[0].get("cgst_rate", 1.5) if hsn_table else 1.5
        sgst_rate_val = hsn_table[0].get("sgst_rate", 1.5) if hsn_table else 1.5
        nested_tax_rows = f"""
        <tr class="calc-row">
          <td></td>
          <td style="text-align: right; padding-right: 15px;"><b>{cgst_rate_val:.2f}% Output CGST</b></td>
          <td></td><td></td><td></td><td></td>
          <td class="col-amt"><b>{cgst_tot:,.2f}</b></td>
        </tr>
        <tr class="calc-row">
          <td></td>
          <td style="text-align: right; padding-right: 15px;"><b>{sgst_rate_val:.2f}% Output SGST</b></td>
          <td></td><td></td><td></td><td></td>
          <td class="col-amt"><b>{sgst_tot:,.2f}</b></td>
        </tr>
        """
        summary_totals = f'<td colspan="2" style="border: 1px solid #000; text-align: right; padding: 3px;"><b>{cgst_tot:,.2f}</b></td><td colspan="2" style="border: 1px solid #000; text-align: right; padding: 3px;"><b>{sgst_tot:,.2f}</b></td>'
    else:
        tax_header_html = """
        <tr>
          <th rowspan="2" style="border: 1px solid #000; padding: 3px; width: 25%;">HSN/SAC</th>
          <th rowspan="2" style="border: 1px solid #000; padding: 3px; width: 25%;">Taxable Value</th>
          <th colspan="2" style="border: 1px solid #000; padding: 3px;">Integrated Tax</th>
          <th rowspan="2" style="border: 1px solid #000; padding: 3px; width: 25%;">Total Tax Amount</th>
        </tr>
        <tr>
          <th style="border: 1px solid #000; padding: 2px;">Rate</th>
          <th style="border: 1px solid #000; padding: 2px;">Amount</th>
        </tr>
        """
        igst_rate_val = hsn_table[0].get("igst_rate", 3.0) if hsn_table else 3.0
        nested_tax_rows = f"""
        <tr class="calc-row">
          <td></td>
          <td style="text-align: right; padding-right: 15px;"><b>{igst_rate_val:.2f}% Output IGST</b></td>
          <td></td><td></td><td></td><td></td>
          <td class="col-amt"><b>{igst_tot:,.2f}</b></td>
        </tr>
        """
        summary_totals = f'<td colspan="2" style="border: 1px solid #000; text-align: right; padding: 3px;"><b>{igst_tot:,.2f}</b></td>'

    round_off_row = ""
    if round_off != 0:
        round_off_row = f"""
        <tr class="calc-row">
          <td></td>
          <td style="text-align: right; padding-right: 15px;"><b>Round Off</b></td>
          <td></td><td></td><td></td><td></td>
          <td class="col-amt"><b>{round_off:,.2f}</b></td>
        </tr>
        """

    irn_block = ""
    irn = einvoice.get("irn") or inv.get("irn")
    if irn:
        ack_no = einvoice.get("ack_no") or inv.get("ack_no", "")
        ack_date = einvoice.get("ack_date") or inv.get("ack_date", "")
        qr_src = einvoice.get("qr_image") or einvoice.get("qr_data", "")
        qr_img_tag = f'<img src="{qr_src}" style="width: 80px; height: 80px;" alt="QR"/>' if qr_src else '<div style="width: 80px; height: 80px; border: 1px dashed #999; margin: 0 auto; display: flex; align-items: center; justify-content: center; font-size: 6pt;">QR CODE</div>'
        irn_block = f"""
        <div style="display: flex; justify-content: space-between; border-top: 1px solid #000; padding: 4px 6px; font-size: 7.5pt;">
          <div style="flex: 1; padding-right: 10px;">
            <table style="width: 100%;">
              <tr><td style="width: 60px; font-weight: bold;">IRN</td><td>: {irn}</td></tr>
              <tr><td style="font-weight: bold;">Ack No.</td><td>: {ack_no}</td></tr>
              <tr><td style="font-weight: bold;">Ack Date</td><td>: {ack_date}</td></tr>
            </table>
          </div>
          <div style="text-align: center; width: 90px;">
            <div style="font-size: 7pt; font-weight: bold;">e-Invoice</div>
            {qr_img_tag}
          </div>
        </div>
        """

    pan_row = f'<tr><td>Party Pan No.</td><td>: <b>{buyer_pan}</b></td></tr>' if buyer_pan else ''
    gstin_row = f'<tr><td>GSTIN/UIN</td><td>: <b>{buyer_gstin}</b></td></tr>' if buyer_gstin else ''
    contact_person_row = f'<tr><td>Contact person</td><td>: {buyer_contact_person}</td></tr>' if buyer_contact_person else ''
    contact_row = f'<tr><td>Contact</td><td>: {buyer_phone}</td></tr>' if buyer_phone else ''
    email_row = f'<tr><td>E-Mail</td><td>: {buyer_email}</td></tr>' if buyer_email else ''

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Tax Invoice - {inv_num}</title>
  <style>
    @page {{ size: A4 portrait; margin: 8mm; }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: Arial, Helvetica, sans-serif; font-size: 8pt; color: #000; line-height: 1.25; }}
    body {{ background: #fff; padding: 4px; }}
    .invoice-container {{ width: 100%; border: 1px solid #000; margin: 0 auto; }}
    .header-title {{ text-align: center; font-size: 11pt; font-weight: bold; padding: 4px; letter-spacing: 0.5px; }}
    .main-grid {{ display: grid; grid-template-columns: 1fr 1fr; border-top: 1px solid #000; }}
    .party-col {{ border-right: 1px solid #000; display: flex; flex-direction: column; }}
    .seller-box {{ padding: 5px 6px; border-bottom: 1px solid #000; }}
    .buyer-box {{ padding: 5px 6px; flex: 1; }}
    .company-title {{ font-size: 9.5pt; font-weight: bold; text-transform: uppercase; margin-bottom: 2px; }}
    .meta-col {{ display: flex; flex-direction: column; }}
    .meta-grid {{ display: grid; grid-template-columns: 1fr 1fr; height: 100%; }}
    .meta-cell {{ border-bottom: 1px solid #000; padding: 3px 5px; min-height: 28px; }}
    .meta-cell:nth-child(odd) {{ border-right: 1px solid #000; }}
    .meta-cell.full-width {{ grid-column: span 2; }}
    .meta-label {{ font-size: 7pt; color: #333; }}
    .meta-value {{ font-size: 8pt; font-weight: bold; }}

    table.items-table {{ width: 100%; border-collapse: collapse; border-top: 1px solid #000; border-bottom: 1px solid #000; }}
    table.items-table th, table.items-table td {{ border-right: 1px solid #000; padding: 4px 5px; font-size: 8pt; }}
    table.items-table th:last-child, table.items-table td:last-child {{ border-right: none; }}
    table.items-table th {{ border-bottom: 1px solid #000; background: #f5f5f5; font-weight: bold; text-align: center; }}
    .col-sr {{ width: 5%; text-align: center; }}
    .col-desc {{ width: 45%; text-align: left; }}
    .col-hsn {{ width: 12%; text-align: center; }}
    .col-qty {{ width: 14%; text-align: right; }}
    .col-rate {{ width: 11%; text-align: right; }}
    .col-per {{ width: 6%; text-align: center; }}
    .col-amt {{ width: 17%; text-align: right; }}

    .item-row td {{ vertical-align: top; border-bottom: none; }}
    .calc-row td {{ border-top: none; border-bottom: none; font-style: italic; }}
    .total-row {{ border-top: 1px solid #000 !important; border-bottom: 1px solid #000 !important; font-weight: bold; }}
    .total-row td {{ padding: 5px; }}

    .words-box {{ padding: 4px 6px; border-bottom: 1px solid #000; display: flex; justify-content: space-between; }}
    .tax-summary-table {{ width: 100%; border-collapse: collapse; border-bottom: 1px solid #000; }}
    .tax-summary-table th, .tax-summary-table td {{ border-right: 1px solid #000; border-bottom: 1px solid #000; padding: 3px 4px; font-size: 7.5pt; text-align: right; }}
    .tax-summary-table th {{ background: #f5f5f5; font-weight: bold; text-align: center; }}
    .tax-summary-table th:last-child, .tax-summary-table td:last-child {{ border-right: none; }}

    .footer-grid {{ display: grid; grid-template-columns: 1.2fr 1fr; border-bottom: 1px solid #000; }}
    .footer-left {{ padding: 6px; border-right: 1px solid #000; display: flex; flex-direction: column; justify-content: space-between; }}
    .footer-right {{ padding: 6px; display: flex; flex-direction: column; justify-content: space-between; text-align: right; min-height: 85px; }}
    .jurisdiction-bar {{ text-align: center; font-weight: bold; font-size: 7.5pt; padding: 3px; }}
    .stamp-box {{ width: 75px; height: 75px; border-radius: 50%; border: 2px solid #1e40af; color: #1e40af; font-size: 7pt; font-weight: bold; display: flex; flex-direction: column; align-items: center; justify-content: center; margin-left: auto; margin-top: 5px; transform: rotate(-5deg); text-align: center; opacity: 0.85; }}
  </style>
</head>
<body>
  <div class="invoice-container">
    <div class="header-title">{header_title}</div>
    {irn_block}
    
    <div class="main-grid">
      <!-- LEFT: Seller & Buyer Details -->
      <div class="party-col">
        <div class="seller-box">
          <div class="company-title">{co_name}</div>
          <div>{co_addr}</div>
          <table style="width: 100%; margin-top: 3px;">
            <tr><td style="width: 85px;">GSTIN/UIN</td><td>: <b>{co_gstin}</b></td></tr>
            <tr><td>State Name</td><td>: {co_state}, Code : <b>{co_state_code}</b></td></tr>
            <tr><td>Contact</td><td>: {co_phone}</td></tr>
            <tr><td>E-Mail</td><td>: {co_email}</td></tr>
          </table>
        </div>

        <div class="buyer-box">
          <div style="font-size: 7.5pt; color: #555;">{party_box_label}</div>
          <div class="company-title" style="font-size: 8.5pt;">{buyer_name}</div>
          <div>{buyer_addr}</div>
          <table style="width: 100%; margin-top: 3px;">
            {pan_row}
            {gstin_row}
            <tr><td>State Name</td><td>: {buyer_state}, Code : <b>{buyer_state_code}</b></td></tr>
            <tr><td>Place of Supply</td><td>: <b>{place_of_supply}</b></td></tr>
            {contact_person_row}
            {contact_row}
            {email_row}
          </table>
        </div>
      </div>

      <!-- RIGHT: Document Meta Grid -->
      <div class="meta-col">
        <div class="meta-grid">
          <div class="meta-cell">
            <div class="meta-label">Invoice No.</div>
            <div class="meta-value">{inv_num}</div>
          </div>
          <div class="meta-cell">
            <div class="meta-label">Dated</div>
            <div class="meta-value">{formatted_date}</div>
          </div>

          <div class="meta-cell">
            <div class="meta-label">Delivery Note</div>
            <div class="meta-value">{inv.get('delivery_note', '')}</div>
          </div>
          <div class="meta-cell">
            <div class="meta-label">Mode/Terms of Payment</div>
            <div class="meta-value">{inv.get('mode_terms_payment', '')}</div>
          </div>

          <div class="meta-cell">
            <div class="meta-label">Reference No. &amp; Date.</div>
            <div class="meta-value">{inv.get('reference_no_date', '')}</div>
          </div>
          <div class="meta-cell">
            <div class="meta-label">Other References</div>
            <div class="meta-value">{inv.get('other_references', '')}</div>
          </div>

          <div class="meta-cell">
            <div class="meta-label">Buyer's Order No.</div>
            <div class="meta-value">{inv.get('buyers_order_no', '')}</div>
          </div>
          <div class="meta-cell">
            <div class="meta-label">Dated</div>
            <div class="meta-value">{inv.get('order_date', '')}</div>
          </div>

          <div class="meta-cell">
            <div class="meta-label">Dispatch Doc No.</div>
            <div class="meta-value">{inv.get('dispatch_doc_no', '')}</div>
          </div>
          <div class="meta-cell">
            <div class="meta-label">Delivery Note Date</div>
            <div class="meta-value">{inv.get('delivery_note_date', '')}</div>
          </div>

          <div class="meta-cell">
            <div class="meta-label">Dispatched through</div>
            <div class="meta-value">{inv.get('dispatched_through', '')}</div>
          </div>
          <div class="meta-cell">
            <div class="meta-label">Destination</div>
            <div class="meta-value">{inv.get('destination', '')}</div>
          </div>

          <div class="meta-cell full-width" style="border-bottom: none;">
            <div class="meta-label">Terms of Delivery</div>
            <div class="meta-value" style="font-weight: normal; min-height: 20px;">{inv.get('terms_of_delivery', '')}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Line Items Table -->
    <table class="items-table">
      <thead>
        <tr>
          <th class="col-sr">Sl<br/>No.</th>
          <th class="col-desc">Description of Goods</th>
          <th class="col-hsn">HSN/SAC</th>
          <th class="col-qty">Quantity</th>
          <th class="col-rate">Rate</th>
          <th class="col-per">per</th>
          <th class="col-amt">Amount</th>
        </tr>
      </thead>
      <tbody>
        {item_rows_html}
        {nested_tax_rows}
        {round_off_row}

        <!-- Total Row -->
        <tr class="total-row">
          <td></td>
          <td style="text-align: right; padding-right: 15px;"><b>Total</b></td>
          <td></td>
          <td class="col-qty"><b>{tot_qty:,.4f} {default_unit}</b></td>
          <td></td><td></td>
          <td class="col-amt" style="font-size: 9pt;"><b>Rs {grand_total:,.2f}</b></td>
        </tr>
      </tbody>
    </table>

    <!-- Amount in words -->
    <div class="words-box">
      <div>
        <div style="font-size: 7pt; color: #555;">Amount Chargeable (in words)</div>
        <div style="font-size: 8pt; font-weight: bold;">{words_total}</div>
      </div>
      <div style="font-size: 7.5pt; font-style: italic; color: #555;">E. &amp; O.E</div>
    </div>

    <!-- HSN Summary Table -->
    <table class="tax-summary-table">
      <thead>{tax_header_html}</thead>
      <tbody>
        {tax_rows_html}
        <tr style="font-weight: bold; background: #fafafa;">
          <td style="border: 1px solid #000; padding: 3px; text-align: left;">Total</td>
          <td style="border: 1px solid #000; text-align: right; padding: 3px;">{subtotal:,.2f}</td>
          {summary_totals}
          <td style="border: 1px solid #000; text-align: right; padding: 3px;">{total_tax:,.2f}</td>
        </tr>
      </tbody>
    </table>

    <div style="padding: 4px 6px; border-bottom: 1px solid #000; font-size: 7.5pt;">
      <span style="color: #555;">Tax Amount (in words): </span>
      <b>{words_tax}</b>
    </div>

    <!-- Declaration & Signatory -->
    <div class="footer-grid">
      <div class="footer-left">
        <div>
          <div style="font-size: 7.5pt; margin-bottom: 4px;">Company's PAN : <b>{co_pan}</b></div>
          {bank_html}
          <div style="font-size: 7pt; font-weight: bold; text-decoration: underline; margin-bottom: 2px;">Declaration:</div>
          <div style="font-size: 7pt; color: #333;">{co_declaration}</div>
        </div>
      </div>

      <div class="footer-right">
        <div style="font-size: 8pt; font-weight: bold;">for {co_name}</div>
        <div class="stamp-box">
          <div style="font-size: 6pt;">★ {co_name.upper()} ★</div>
          <div style="font-size: 5.5pt;">{(co_jurisdiction or "").upper()}</div>
        </div>
        <div style="font-size: 7.5pt; font-weight: bold; margin-top: 6px;">Authorised Signatory</div>
      </div>
    </div>

    <div class="jurisdiction-bar">
      {f"SUBJECT TO {co_jurisdiction.upper()} JURISDICTION" if co_jurisdiction else ""}
      {f'<div style="font-size: 6.5pt; font-weight: normal; color: #555; margin-top: 2px;">{co_footer_note}</div>' if co_footer_note else ""}
    </div>
  </div>
</body>
</html>
"""
