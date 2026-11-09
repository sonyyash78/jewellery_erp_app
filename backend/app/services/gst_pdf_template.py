"""
Saideep Jewellers GST Tax Invoice Template
===================================
Pixel-accurate layout matching GST reference tax invoice (Sales_PG_S_1944_26-27).
Strictly used ONLY when company.gst_enabled = True.
"""
from typing import Dict, Any, List
from datetime import datetime
from decimal import Decimal


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

    co_name = company.get("name", "SAIDEEP JEWELLERS")
    co_addr = company.get("address", "167, Ward No. 3, Khedawas, Takhatgarh, Pali (Raj.)-306912")
    co_gstin = company.get("gstin", "08BNUPK1610E1Z3")
    co_pan = company.get("pan", "BNUPK1610E")
    co_state = company.get("state", "Rajasthan")
    co_state_code = company.get("state_code", "08")
    co_phone = company.get("phone", "+91-9460820878")
    co_email = company.get("email", "saideepjewellers78@gmail.com")
    co_jurisdiction = company.get("jurisdiction_city", "PALI")
    co_declaration = company.get("declaration", "We declare that this invoice shows the actual price of the goods described and that all particulars are true and correct.")

    buyer_name = (buyer.get("name") or buyer.get("first_name") or "Walk-in Customer").strip()
    if buyer.get("last_name"):
        buyer_name += f" {buyer['last_name']}"
    buyer_addr = buyer.get("address", "")
    buyer_gstin = buyer.get("gstin") or buyer.get("gst_number") or ""
    buyer_pan = buyer.get("pan") or buyer.get("aadhaar_pan") or ""
    buyer_state = buyer.get("state", "Rajasthan")
    buyer_state_code = buyer.get("state_code", "08")
    place_of_supply = buyer.get("place_of_supply") or buyer_state
    buyer_contact_person = buyer.get("contact_person", "")
    buyer_phone = buyer.get("phone") or buyer.get("mobile") or ""
    buyer_email = buyer.get("email", "")

    # Totals
    subtotal = float(gst_calc.get("total_taxable_amount", inv.get("subtotal", 0.0)))
    cgst_tot = float(gst_calc.get("total_cgst_amount", 0.0))
    sgst_tot = float(gst_calc.get("total_sgst_amount", 0.0))
    igst_tot = float(gst_calc.get("total_igst_amount", 0.0))
    total_tax = float(gst_calc.get("total_tax_amount", inv.get("tax_amount", 0.0)))
    round_off = float(gst_calc.get("round_off", 0.0))
    grand_total = float(gst_calc.get("grand_total", inv.get("grand_total", 0.0)))
    is_intra = gst_calc.get("is_intra_state", True)

    words_total = gst_calc.get("amount_chargeable_words", "")
    words_tax = gst_calc.get("tax_amount_words", "")

    # Calculate total quantity
    tot_qty = sum(float(it.get("quantity", it.get("net_weight", it.get("gross_weight", 0.0)))) for it in items)
    default_unit = items[0].get("unit", "Gms") if items else "Gms"

    # Item rows
    item_rows = []
    for idx, it in enumerate(items, 1):
        desc = it.get("description", it.get("item_name", "SILVER BAR"))
        hsn = it.get("hsn_code", it.get("hsn", "71069120"))
        qty = float(it.get("quantity", it.get("net_weight", it.get("gross_weight", 1.0))))
        unit = it.get("unit", "Gms")
        rate = float(it.get("rate", it.get("rate_per_gram", 0.0)))
        amt = float(it.get("amount", it.get("taxable_amount", qty * rate)))
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
    hsn_table = gst_calc.get("hsn_tax_table", [])
    tax_rows = []
    for row_data in hsn_table:
        h = row_data.get("hsn_code", "71069120")
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
    <div class="header-title">TAX INVOICE</div>
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
          <div style="font-size: 7.5pt; color: #555;">Buyer (Bill to)</div>
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
          <div style="font-size: 7pt; font-weight: bold; text-decoration: underline; margin-bottom: 2px;">Declaration:</div>
          <div style="font-size: 7pt; color: #333;">{co_declaration}</div>
        </div>
      </div>

      <div class="footer-right">
        <div style="font-size: 8pt; font-weight: bold;">for {co_name}</div>
        <div class="stamp-box">
          <div style="font-size: 6pt;">★ {co_name.upper()} ★</div>
          <div style="font-size: 5.5pt;">{(co_jurisdiction or "PALI").upper()}</div>
        </div>
        <div style="font-size: 7.5pt; font-weight: bold; margin-top: 6px;">Authorised Signatory</div>
      </div>
    </div>

    <div class="jurisdiction-bar">
      SUBJECT TO {co_jurisdiction or "PALI"} JURISDICTION
    </div>
  </div>
</body>
</html>
"""
