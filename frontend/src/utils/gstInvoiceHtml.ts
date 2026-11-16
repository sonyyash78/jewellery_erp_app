/**

 * GST Tax Invoice HTML Generator

 * ==============================

 * Pixel-accurate layout matching GST reference tax invoice.

 * Strictly used ONLY when company.gst_enabled = true.

 */

import QRCode from 'qrcode';



export interface GSTInvoiceData {

  invoice: {

    invoice_number: string;

    invoice_date: string;

    delivery_note?: string;

    mode_terms_payment?: string;

    reference_no_date?: string;

    other_references?: string;

    buyers_order_no?: string;

    order_date?: string;

    dispatch_doc_no?: string;

    delivery_note_date?: string;

    dispatched_through?: string;

    destination?: string;

    terms_of_delivery?: string;

    grand_total: number;

    subtotal?: number;

    round_off?: number;

  };

  seller: {

    name: string;

    address: string;

    city?: string;

    state: string;

    state_code: string;

    gstin: string;

    pan: string;

    phone: string;

    email: string;

    jurisdiction_city?: string;

    declaration?: string;

    bank_name?: string;

    bank_account_no?: string;

    bank_ifsc?: string;

    bank_branch?: string;

    upi_id?: string;

    upi_name?: string;

    computer_generated_note?: string;

    stamp_url?: string;

    signature_url?: string;

  };

  buyer: {

    name: string;

    address: string;

    pan?: string;

    gstin?: string;

    state: string;

    state_code: string;

    place_of_supply: string;

    contact_person?: string;

    phone?: string;

    email?: string;

  };

  items: Array<{

    description: string;

    hsn_code: string;

    quantity: number;

    unit?: string;

    rate: number;

    taxable_amount: number;

    cgst_rate?: number;

    cgst_amount?: number;

    sgst_rate?: number;

    sgst_amount?: number;

    igst_rate?: number;

    igst_amount?: number;

    total_tax?: number;

  }>;

  gst_summary: {

    is_intra_state: boolean;

    total_taxable_amount: number;

    total_cgst_amount: number;

    total_sgst_amount: number;

    total_igst_amount: number;

    total_tax_amount: number;

    round_off: number;

    grand_total: number;

    amount_chargeable_words: string;

    tax_amount_words: string;

    hsn_table: Array<{

      hsn_code: string;

      taxable_amount: number;

      cgst_rate: number;

      cgst_amount: number;

      sgst_rate: number;

      sgst_amount: number;

      igst_rate: number;

      igst_amount: number;

      total_tax_amount: number;

    }>;

  };

  einvoice?: {

    irn?: string;

    ack_no?: string;

    ack_date?: string;

    qr_data?: string;

  };

}



export function toIndianWords(amount: number): string {

  const ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten',

    'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen'];

  const tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety'];



  const numToWords = (n: number): string => {

    if (n === 0) return '';

    if (n < 20) return ones[n] + ' ';

    if (n < 100) return tens[Math.floor(n / 10)] + ' ' + (n % 10 !== 0 ? ones[n % 10] + ' ' : '');

    if (n < 1000) return ones[Math.floor(n / 100)] + ' Hundred ' + numToWords(n % 100);

    if (n < 100000) return numToWords(Math.floor(n / 1000)) + 'Thousand ' + numToWords(n % 1000);

    if (n < 10000000) return numToWords(Math.floor(n / 100000)) + 'Lakh ' + numToWords(n % 100000);

    return numToWords(Math.floor(n / 10000000)) + 'Crore ' + numToWords(n % 10000000);

  };



  const rounded = Math.round(amount * 100) / 100;

  const rupees = Math.floor(rounded);

  const paise = Math.round((rounded - rupees) * 100);



  let result = 'Indian Rupees ' + (rupees === 0 ? 'Zero ' : numToWords(rupees));

  if (paise > 0) {

    result += 'and ' + numToWords(paise) + 'paise ';

  }

  return result.trim().replace(/\s+/g, ' ') + ' Only';

}



export const generateGSTInvoiceHtml = async (data: GSTInvoiceData): Promise<string> => {

  const seller = data.seller;

  const buyer = data.buyer;

  const inv = data.invoice;

  const summary = data.gst_summary;

  const einv = data.einvoice;



  const amountWords = (summary.amount_chargeable_words && !summary.amount_chargeable_words.includes('NaN'))

    ? summary.amount_chargeable_words

    : toIndianWords(summary.grand_total);

  const taxWords = (summary.tax_amount_words && !summary.tax_amount_words.includes('NaN'))

    ? summary.tax_amount_words

    : toIndianWords(summary.total_tax_amount);



  let qrDataUrl = '';

  if (einv?.qr_data) {

    try {

      qrDataUrl = await QRCode.toDataURL(einv.qr_data, { width: 120, margin: 1 });

    } catch {

      qrDataUrl = '';

    }

  }



  // Format dates

  const formatDate = (dateStr: string) => {

    if (!dateStr) return '';

    try {

      const d = new Date(dateStr);

      return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: '2-digit' }).replace(/ /g, '-');

    } catch {

      return dateStr;

    }

  };



  const invoiceDateStr = formatDate(inv.invoice_date);



  // Currency formatter

  const cur = (num: number | undefined) => {

    if (num === undefined || num === null) return '0.00';

    return Number(num).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

  };



  // Quantity formatter

  const qtyFormat = (q: number) => {

    return Number(q).toLocaleString('en-IN', { minimumFractionDigits: 4, maximumFractionDigits: 4 });

  };



  return `

<!DOCTYPE html>

<html lang="en">

<head>

  <meta charset="UTF-8">

  <title>Tax Invoice - ${inv.invoice_number}</title>

  <style>

    @page {

      size: A4 portrait;

      margin: 10mm;

    }

    * {

      box-sizing: border-box;

      margin: 0;

      padding: 0;

      font-family: Arial, Helvetica, sans-serif;

      font-size: 8pt;

      color: #000;

      line-height: 1.25;

    }

    body {

      background: #fff;

      color: #000;

      padding: 5px;

    }

    .invoice-container {

      width: 100%;

      background: #fff;

      color: #000;

      border: 1px solid #000;

      margin: 0 auto;

    }

    .header-title {

      text-align: center;

      font-size: 11pt;

      font-weight: bold;

      padding: 4px;

      letter-spacing: 0.5px;

    }

    .e-invoice-block {

      display: flex;

      justify-content: space-between;

      border-top: 1px solid #000;

      padding: 4px 6px;

      font-size: 7.5pt;

    }

    .e-inv-left {

      flex: 1;

      padding-right: 10px;

    }

    .e-inv-right {

      text-align: center;

      width: 110px;

    }

    .e-inv-right img {

      width: 85px;

      height: 85px;

    }

    .main-grid {

      display: grid;

      grid-template-columns: 1fr 1fr;

      border-top: 1px solid #000;

    }

    .party-col {

      border-right: 1px solid #000;

      display: flex;

      flex-direction: column;

    }

    .seller-box {

      padding: 5px 6px;

      border-bottom: 1px solid #000;

    }

    .buyer-box {

      padding: 5px 6px;

      flex: 1;

    }

    .company-title {

      font-size: 9.5pt;

      font-weight: bold;

      text-transform: uppercase;

      margin-bottom: 2px;

    }

    .meta-col {

      display: flex;

      flex-direction: column;

    }

    .meta-grid {

      display: grid;

      grid-template-columns: 1fr 1fr;

      height: 100%;

    }

    .meta-cell {

      border-bottom: 1px solid #000;

      padding: 3px 5px;

      min-height: 28px;

    }

    .meta-cell:nth-child(odd) {

      border-right: 1px solid #000;

    }

    .meta-cell.full-width {

      grid-column: span 2;

    }

    .meta-label {

      font-size: 7pt;

      color: #333;

    }

    .meta-value {

      font-size: 8pt;

      font-weight: bold;

    }

    table.items-table {

      width: 100%;

      border-collapse: collapse;

      border-top: 1px solid #000;

      border-bottom: 1px solid #000;

    }

    table.items-table th, table.items-table td {

      border-right: 1px solid #000;

      padding: 4px 5px;

      font-size: 8pt;

    }

    table.items-table th:last-child, table.items-table td:last-child {

      border-right: none;

    }

    table.items-table th {

      border-bottom: 1px solid #000;

      background: #f5f5f5;

      font-weight: bold;

      text-align: center;

    }

    .col-sr { width: 5%; text-align: center; }

    .col-desc { width: 45%; text-align: left; }

    .col-hsn { width: 12%; text-align: center; }

    .col-qty { width: 14%; text-align: right; }

    .col-rate { width: 11%; text-align: right; }

    .col-per { width: 6%; text-align: center; }

    .col-amt { width: 17%; text-align: right; }



    .item-row td {

      vertical-align: top;

      border-bottom: none;

    }

    .calc-row td {

      border-top: none;

      border-bottom: none;

      font-style: italic;

    }

    .total-row {

      border-top: 1px solid #000 !important;

      border-bottom: 1px solid #000 !important;

      font-weight: bold;

    }

    .total-row td {

      padding: 5px;

    }

    .words-box {

      padding: 4px 6px;

      border-bottom: 1px solid #000;

      display: flex;

      justify-content: space-between;

    }

    .tax-summary-table {

      width: 100%;

      border-collapse: collapse;

      border-bottom: 1px solid #000;

    }

    .tax-summary-table th, .tax-summary-table td {

      border-right: 1px solid #000;

      border-bottom: 1px solid #000;

      padding: 3px 4px;

      font-size: 7.5pt;

      text-align: right;

    }

    .tax-summary-table th {

      background: #f5f5f5;

      font-weight: bold;

      text-align: center;

    }

    .tax-summary-table th:last-child, .tax-summary-table td:last-child {

      border-right: none;

    }

    .footer-grid {

      display: grid;

      grid-template-columns: 1.2fr 1fr;

      border-bottom: 1px solid #000;

    }

    .footer-left {

      padding: 6px;

      border-right: 1px solid #000;

      display: flex;

      flex-direction: column;

      justify-content: space-between;

    }

    .footer-right {

      padding: 6px;

      display: flex;

      flex-direction: column;

      justify-content: space-between;

      text-align: right;

    }

    .jurisdiction-bar {

      text-align: center;

      font-weight: bold;

      font-size: 7.5pt;

      padding: 3px;

    }

  </style>

</head>

<body>

  <div class="invoice-container">

    <div class="header-title">TAX INVOICE</div>



    ${einv?.irn ? `

    <div class="e-invoice-block">

      <div class="e-inv-left">

        <table style="width: 100%;">

          <tr><td style="width: 80px; font-weight: bold;">IRN</td><td>: ${einv.irn}</td></tr>

          <tr><td style="font-weight: bold;">Ack No.</td><td>: ${einv.ack_no || ''}</td></tr>

          <tr><td style="font-weight: bold;">Ack Date</td><td>: ${einv.ack_date || ''}</td></tr>

        </table>

      </div>

      <div class="e-inv-right">

        <div style="font-size: 7pt; font-weight: bold;">e-Invoice</div>

        ${qrDataUrl ? `<img src="${qrDataUrl}" alt="e-Invoice QR" />` : ''}

      </div>

    </div>

    ` : ''}



    <div class="main-grid">

      <!-- LEFT: Seller & Buyer Details -->

      <div class="party-col">

        <div class="seller-box">

          <div class="company-title">${seller.name}</div>

          <div>${seller.address}</div>

          ${seller.address?.includes('India') ? '' : `<div>${seller.state || 'Rajasthan'}, India</div>`}

          <table style="width: 100%; margin-top: 3px;">

            <tr><td style="width: 90px;">GSTIN/UIN</td><td>: <b>${seller.gstin}</b></td></tr>

            <tr><td>State Name</td><td>: ${seller.state}, Code : <b>${seller.state_code}</b></td></tr>

            <tr><td>Contact</td><td>: ${seller.phone}</td></tr>

            <tr><td>E-Mail</td><td>: ${seller.email}</td></tr>

          </table>

        </div>



        <div class="buyer-box">

          <div style="font-size: 7.5pt; color: #555;">Buyer (Bill to)</div>

          <div class="company-title" style="font-size: 8.5pt;">${buyer.name}</div>

          <div>${buyer.address}${buyer.pan && !buyer.address?.includes('Party Pan') ? `, Party Pan No. ${buyer.pan}` : ''}</div>

          ${buyer.state ? `<div>${buyer.state}, India</div>` : ''}

          <table style="width: 100%; margin-top: 3px;">

            <tr><td style="width: 90px;">GSTIN/UIN</td><td>: <b>${buyer.gstin || 'Unregistered'}</b></td></tr>

            <tr><td>State Name</td><td>: ${buyer.state}, Code : <b>${buyer.state_code}</b></td></tr>

            <tr><td>Place of Supply</td><td>: <b>${buyer.place_of_supply}</b></td></tr>

            ${buyer.contact_person ? `<tr><td>Contact person</td><td>: ${buyer.contact_person}</td></tr>` : ''}

            ${buyer.phone ? `<tr><td>Contact</td><td>: ${buyer.phone}</td></tr>` : ''}

            ${buyer.email ? `<tr><td>E-Mail</td><td>: ${buyer.email}</td></tr>` : ''}

          </table>

        </div>

      </div>



      <!-- RIGHT: Document Meta Grid -->

      <div class="meta-col">

        <div class="meta-grid">

          <div class="meta-cell">

            <div class="meta-label">Invoice No.</div>

            <div class="meta-value">${inv.invoice_number}</div>

          </div>

          <div class="meta-cell">

            <div class="meta-label">Dated</div>

            <div class="meta-value">${invoiceDateStr}</div>

          </div>



          <div class="meta-cell">

            <div class="meta-label">Delivery Note</div>

            <div class="meta-value">${inv.delivery_note || ''}</div>

          </div>

          <div class="meta-cell">

            <div class="meta-label">Mode/Terms of Payment</div>

            <div class="meta-value">${inv.mode_terms_payment || ''}</div>

          </div>



          <div class="meta-cell">

            <div class="meta-label">Reference No. & Date.</div>

            <div class="meta-value">${inv.reference_no_date || ''}</div>

          </div>

          <div class="meta-cell">

            <div class="meta-label">Other References</div>

            <div class="meta-value">${inv.other_references || ''}</div>

          </div>



          <div class="meta-cell">

            <div class="meta-label">Buyer's Order No.</div>

            <div class="meta-value">${inv.buyers_order_no || ''}</div>

          </div>

          <div class="meta-cell">

            <div class="meta-label">Dated</div>

            <div class="meta-value">${inv.order_date || ''}</div>

          </div>



          <div class="meta-cell">

            <div class="meta-label">Dispatch Doc No.</div>

            <div class="meta-value">${inv.dispatch_doc_no || ''}</div>

          </div>

          <div class="meta-cell">

            <div class="meta-label">Delivery Note Date</div>

            <div class="meta-value">${inv.delivery_note_date || ''}</div>

          </div>



          <div class="meta-cell">

            <div class="meta-label">Dispatched through</div>

            <div class="meta-value">${inv.dispatched_through || ''}</div>

          </div>

          <div class="meta-cell">

            <div class="meta-label">Destination</div>

            <div class="meta-value">${inv.destination || ''}</div>

          </div>



          <div class="meta-cell full-width" style="border-bottom: none;">

            <div class="meta-label">Terms of Delivery</div>

            <div class="meta-value" style="font-weight: normal; min-height: 20px;">${inv.terms_of_delivery || ''}</div>

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

        ${data.items.map((it, idx) => `

        <tr class="item-row">

          <td class="col-sr">${idx + 1}</td>

          <td class="col-desc"><b>${it.description}</b></td>

          <td class="col-hsn">${it.hsn_code}</td>

          <td class="col-qty"><b>${qtyFormat(it.quantity)} ${it.unit || 'Gms'}</b></td>

          <td class="col-rate">${cur(it.rate)}</td>

          <td class="col-per">${it.unit || 'Gms'}</td>

          <td class="col-amt"><b>${cur(it.taxable_amount)}</b></td>

        </tr>

        `).join('')}



        <!-- Tax breakdown sub-lines inside item table -->

        ${summary.is_intra_state ? `

        <tr class="calc-row">

          <td></td>

          <td style="text-align: right; padding-right: 15px;"><b>${cur(summary.hsn_table[0]?.cgst_rate || 1.5)}% Output CGST</b></td>

          <td></td><td></td><td></td><td></td>

          <td class="col-amt"><b>${cur(summary.total_cgst_amount)}</b></td>

        </tr>

        <tr class="calc-row">

          <td></td>

          <td style="text-align: right; padding-right: 15px;"><b>${cur(summary.hsn_table[0]?.sgst_rate || 1.5)}% Output SGST</b></td>

          <td></td><td></td><td></td><td></td>

          <td class="col-amt"><b>${cur(summary.total_sgst_amount)}</b></td>

        </tr>

        ` : `

        <tr class="calc-row">

          <td></td>

          <td style="text-align: right; padding-right: 15px;"><b>${cur(summary.hsn_table[0]?.igst_rate || 3.0)}% Output IGST</b></td>

          <td></td><td></td><td></td><td></td>

          <td class="col-amt"><b>${cur(summary.total_igst_amount)}</b></td>

        </tr>

        `}

        ${summary.round_off !== 0 ? `

        <tr class="calc-row">

          <td></td>

          <td style="text-align: right; padding-right: 15px;"><b>Round Off</b></td>

          <td></td><td></td><td></td><td></td>

          <td class="col-amt"><b>${cur(summary.round_off)}</b></td>

        </tr>

        ` : ''}



        <!-- Total Row -->

        <tr class="total-row">

          <td></td>

          <td style="text-align: right;"><b>Total</b></td>

          <td></td>

          <td class="col-qty"><b>${qtyFormat(data.items.reduce((acc, i) => acc + i.quantity, 0))} Gms</b></td>

          <td></td>

          <td></td>

          <td class="col-amt"><b>₹ ${cur(summary.grand_total)}</b></td>

        </tr>

      </tbody>

    </table>



    <!-- Amount Chargeable in words -->

    <div class="words-box">

      <div>

        <div style="font-size: 7pt; color: #555;">Amount Chargeable (in words)</div>

        <div style="font-weight: bold; font-size: 8.5pt;">${amountWords}</div>

      </div>

      <div style="font-style: italic; font-size: 7.5pt; align-self: flex-end;">E. & O.E</div>

    </div>



    <!-- HSN / Tax Summary Table -->

    <table class="tax-summary-table">

      <thead>

        <tr>

          <th rowspan="2" style="width: 18%;">HSN/SAC</th>

          <th rowspan="2" style="width: 22%;">Taxable<br/>Value</th>

          ${summary.is_intra_state ? `

          <th colspan="2" style="width: 25%;">CGST</th>

          <th colspan="2" style="width: 25%;">SGST/UTGST</th>

          ` : `

          <th colspan="2" style="width: 50%;">IGST</th>

          `}

          <th rowspan="2" style="width: 10%;">Total<br/>Tax Amount</th>

        </tr>

        <tr>

          ${summary.is_intra_state ? `

          <th style="width: 8%;">Rate</th>

          <th style="width: 17%;">Amount</th>

          <th style="width: 8%;">Rate</th>

          <th style="width: 17%;">Amount</th>

          ` : `

          <th style="width: 15%;">Rate</th>

          <th style="width: 35%;">Amount</th>

          `}

        </tr>

      </thead>

      <tbody>

        ${summary.hsn_table.map((row) => `

        <tr>

          <td style="text-align: center;">${row.hsn_code}</td>

          <td>${cur(row.taxable_amount)}</td>

          ${summary.is_intra_state ? `

          <td style="text-align: center;">${row.cgst_rate.toFixed(2)}%</td>

          <td>${cur(row.cgst_amount)}</td>

          <td style="text-align: center;">${row.sgst_rate.toFixed(2)}%</td>

          <td>${cur(row.sgst_amount)}</td>

          ` : `

          <td style="text-align: center;">${row.igst_rate.toFixed(2)}%</td>

          <td>${cur(row.igst_amount)}</td>

          `}

          <td><b>${cur(row.total_tax_amount)}</b></td>

        </tr>

        `).join('')}

        <tr style="font-weight: bold; background: #fafafa;">

          <td style="text-align: right;">Total:</td>

          <td>${cur(summary.total_taxable_amount)}</td>

          ${summary.is_intra_state ? `

          <td></td>

          <td>${cur(summary.total_cgst_amount)}</td>

          <td></td>

          <td>${cur(summary.total_sgst_amount)}</td>

          ` : `

          <td></td>

          <td>${cur(summary.total_igst_amount)}</td>

          `}

          <td><b>${cur(summary.total_tax_amount)}</b></td>

        </tr>

      </tbody>

    </table>



    <div style="padding: 4px 6px; border-bottom: 1px solid #000; font-size: 7.5pt;">

      <span style="color: #555;">Tax Amount (in words) : </span>

      <b>${taxWords}</b>

    </div>



    <!-- Footer: PAN, Declaration, Signatory -->

    <div class="footer-grid">

      <div class="footer-left">

        <div style="margin-bottom: 4px;">

          <span>Company's PAN : </span><b>${seller.pan}</b>

        </div>

        ${(seller.bank_name || seller.bank_account_no) ? `
        <div style="font-size: 7pt; margin-bottom: 4px;">
          <b>Bank Details:</b> ${[seller.bank_name, seller.bank_account_no ? `A/c: ${seller.bank_account_no}` : '', seller.bank_ifsc ? `IFSC: ${seller.bank_ifsc}` : '', seller.bank_branch].filter(Boolean).join(' | ')}
        </div>
        ` : ''}

        <div>

          <div style="font-weight: bold; text-decoration: underline; font-size: 7pt; margin-bottom: 2px;">Declaration</div>

          <div style="font-size: 7pt; line-height: 1.2;">

            ${seller.declaration || 'We declare that this invoice shows the actual price of the goods described and that all particulars are true and correct.'}

          </div>

        </div>

      </div>



      <div class="footer-right">

        <div style="font-weight: bold; font-size: 7.5pt;">for ${seller.name}</div>

        <div style="height: 52px; display: flex; align-items: center; justify-content: flex-end;">

          ${seller.stamp_url ? `<img src="${seller.stamp_url}" alt="Stamp" style="max-height: 45px; margin-right: 10px;" />` : `

          <div style="width: 52px; height: 52px; border-radius: 50%; border: 1.5px solid #2563eb; color: #2563eb; font-size: 5pt; font-weight: bold; display: flex; flex-direction: column; align-items: center; justify-content: center; margin-right: 15px; transform: rotate(-5deg); opacity: 0.85; line-height: 1.1; text-align: center;">

            <div>★ ${seller.name.toUpperCase()} ★</div>

            <div style="font-size: 4.5pt; margin-top: 1px;">${(seller.city || seller.jurisdiction_city || seller.state || "").toUpperCase()}</div>

          </div>

          `}

          ${seller.signature_url ? `<img src="${seller.signature_url}" alt="Sign" style="max-height: 40px;" />` : ''}

        </div>

        <div style="font-size: 7.5pt;">Authorised Signatory</div>

      </div>

    </div>



    <div class="jurisdiction-bar">

      ${(seller.jurisdiction_city || seller.city) ? `SUBJECT TO ${(seller.jurisdiction_city || seller.city || '').toUpperCase()} JURISDICTION` : ''}

      ${seller.computer_generated_note ? `<div style="font-size: 6.5pt; font-weight: normal; color: #555; margin-top: 2px;">${seller.computer_generated_note}</div>` : ''}

    </div>

  </div>

</body>

</html>

  `;

};

