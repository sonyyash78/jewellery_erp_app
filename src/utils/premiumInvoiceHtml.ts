export const getCommonStyles = () => `
  <style>
    :root {
      --navy: #0B132B;
      --navy-light: #16213E;
      --gold: #C8A045;
      --gold-light: #DFB967;
      --gold-dark: #B18835;
      --text: #333333;
      --border: #E5E7EB;
      --green: #15803D;
      --green-bg: #F0FDF4;
      --red: #B91C1C;
      --red-bg: #FEF2F2;
    }
    
    * { box-sizing: border-box; margin: 0; padding: 0; }
    
    body {
      font-family: 'Inter', sans-serif;
      color: var(--text);
      background: white;
      -webkit-font-smoothing: antialiased;
      line-height: 1.4;
    }
    
    @page {
      size: A4 portrait;
      margin: 6mm 5mm 6mm 5mm;
    }
    
    @media print {
      body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
      .invoice-wrapper {
        box-shadow: none !important;
        margin: 0 !important;
        padding: 0 !important;
        width: 100% !important;
      }
      tr {
        page-break-inside: avoid !important;
      }
      .bottom-row, .signatures-block, .settlement-box, .cards-row {
        page-break-inside: avoid !important;
      }
    }

    .pdf-container {
      width: 100%;
      background: white;
      display: flex;
      flex-direction: column;
      align-items: center;
    }

    .invoice-wrapper {
      width: 100%;
      max-width: 210mm;
      min-height: 285mm;
      background: white;
      position: relative;
      padding: 6mm 4mm;
      box-sizing: border-box;
      display: flex;
      flex-direction: column;
    }

    .watermark {
      position: absolute;
      top: 40%;
      left: 50%;
      transform: translate(-50%, -50%);
      font-family: 'Cinzel', serif;
      font-size: 300px;
      color: var(--gold);
      opacity: 0.03;
      z-index: 0;
      pointer-events: none;
    }

    .content {
      position: relative;
      z-index: 1;
      display: flex;
      flex-direction: column;
      flex: 1;
    }
    
    .header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 4px; }
    .logo-section { display: flex; align-items: center; gap: 12px; }
    .logo-circle { width: 56px; height: 56px; border-radius: 50%; border: 2px solid var(--gold); display: flex; align-items: center; justify-content: center; font-family: 'Cinzel', serif; font-size: 28px; color: var(--gold); position: relative; }
    .logo-circle::after { content: ''; position: absolute; width: 48px; height: 48px; border-radius: 50%; border: 1px solid rgba(200, 160, 69, 0.4); }
    .logo-img { max-width: 56px; max-height: 56px; object-fit: contain; }
    .company-info h1 { font-family: 'Cinzel', serif; font-size: 24px; font-weight: 700; color: var(--navy); line-height: 1.2; letter-spacing: 1.5px; margin-bottom: 2px; }
    .tagline { font-family: 'Inter', sans-serif; font-size: 9px; font-weight: 700; color: var(--gold); letter-spacing: 2px; text-transform: uppercase; }
    
    .tax-invoice-badge { background: var(--navy); color: var(--gold); padding: 8px 18px; border-radius: 6px 0 0 6px; font-family: 'Cinzel', serif; font-size: 15px; font-weight: 600; display: flex; align-items: center; gap: 8px; margin-right: -4mm; margin-top: -6mm; }
    .meta-table { margin-top: 10px; font-size: 10px; font-weight: 600; color: var(--navy); }
    .meta-table td { padding: 2px 10px 2px 0; }
    .meta-table td:first-child { width: 90px; }
    
    .cards-row { display: flex; gap: 8px; margin: 8px 0; }
    .card { flex: 1; border: 1px solid var(--border); border-radius: 6px; overflow: hidden; }
    .card-header { background: var(--navy); color: var(--gold); padding: 4px 8px; font-family: 'Cinzel', serif; font-size: 9px; font-weight: 700; letter-spacing: 1px; }
    .card-body { padding: 6px 8px; font-size: 9px; }
    .card-title { font-weight: 700; color: var(--navy); font-size: 11px; margin-bottom: 2px; }
    .card-meta { color: #555; line-height: 1.3; }

    .items-table { width: 100%; border-collapse: collapse; margin-top: 6px; margin-bottom: 6px; font-size: 9px; }
    .items-table thead { display: table-header-group; }
    .items-table th { background: var(--navy); color: var(--gold); padding: 5px 4px; font-weight: 600; font-size: 8.5px; text-transform: uppercase; text-align: right; border-right: 1px solid rgba(255,255,255,0.1); }
    .items-table th:first-child, .items-table th:nth-child(2) { text-align: left; }
    .items-table td { padding: 4px 4px; border-bottom: 1px solid var(--border); text-align: right; }
    .items-table td:first-child, .items-table td:nth-child(2) { text-align: left; }
    .items-table tr:nth-child(even) { background-color: #FAFAFA; }
    
    .bottom-row { display: flex; gap: 8px; margin-top: 8px; font-size: 9px; }
    .bottom-col-left { flex: 1.1; display: flex; flex-direction: column; gap: 6px; }
    .bottom-col-right { flex: 0.9; }

    .totals-table { width: 100%; border-collapse: collapse; font-size: 9.5px; }
    .totals-table td { padding: 3px 6px; }
    .totals-table tr.grand-total { background: var(--navy); color: var(--gold); font-weight: 700; font-size: 11px; }
    .totals-table tr.grand-total td { padding: 5px 6px; }

    .settlement-box { border: 1px solid var(--gold); border-radius: 6px; padding: 6px 8px; background: #FFFCF5; }
    .settlement-title { font-weight: 700; color: var(--navy); font-size: 9px; margin-bottom: 4px; text-transform: uppercase; }

    .footer-note { text-align: center; margin-top: auto; padding-top: 8px; padding-bottom: 8px; font-family: 'Cinzel', serif; font-size: 10px; font-weight: 700; color: var(--gold); letter-spacing: 1px; }
  </style>
`;

export const getPageWrapperStart = () => `
<div class="invoice-wrapper">
  <div class="watermark">SJ</div>
  <div class="content">
`;

export const getPageWrapperEnd = (company: any, pageNum: any, totalPages: any) => `
    <div class="footer-note">
      Purity You Trust, Elegance You Deserve.
    </div>
  </div>
</div>
`;

export const renderHeader = (company: any, invoice: any, logoBase64: string) => `
  <div class="header">
    <div class="logo-section">
      ${logoBase64 ? `<img src="${logoBase64}" class="logo-img"/>` : `<div class="logo-circle">SJ</div>`}
      <div class="company-info">
        <h1>${company.name || 'SAIDEEP JEWELLERS'}</h1>
        <div class="tagline">FINE GOLD & SILVER JEWELLERY</div>
      </div>
    </div>
    <div>
      <div class="tax-invoice-badge">TAX INVOICE</div>
      <table class="meta-table">
        <tr><td>Invoice No</td><td>: <b>${invoice.invoice_number}</b></td></tr>
        <tr><td>Date</td><td>: ${new Date(invoice.invoice_date).toLocaleDateString('en-IN')}</td></tr>
        <tr><td>Place of Supply</td><td>: 24-Gujarat</td></tr>
      </table>
    </div>
  </div>
`;

export const renderCardsRow = (customer: any, company: any) => `
  <div class="cards-row">
    <div class="card">
      <div class="card-header">BILLED TO (BUYER)</div>
      <div class="card-body">
        <div class="card-title">${customer.name || 'Cash Customer'}</div>
        <div class="card-meta">
          Phone: ${customer.phone || '-'}<br>
          GSTIN: ${customer.gstin || 'Unregistered'}<br>
          Address: ${customer.address || '-'}
        </div>
      </div>
    </div>
    <div class="card">
      <div class="card-header">SHOP / SELLER DETAILS</div>
      <div class="card-body">
        <div class="card-title">${company?.name || 'SAIDEEP JEWELLERS'}</div>
        <div class="card-meta">
          Phone: ${company?.phone || '+91 98765 43210'}<br>
          GSTIN: ${company?.gstin || '22AAAAA0000A1Z5'}<br>
          Address: ${company?.address || 'Main Jewellery Market'}
        </div>
      </div>
    </div>
  </div>
`;

export const renderTableHeader = () => `
  <table class="items-table">
    <thead>
      <tr>
        <th style="width: 24px;">#</th>
        <th>Item Description</th>
        <th style="width: 38px;">HSC</th>
        <th style="width: 50px;">Gross (g)</th>
        <th style="width: 46px;">Net (g)</th>
        <th style="width: 42px;">Tanch%</th>
        <th style="width: 48px;">Fine (g)</th>
        <th style="width: 54px;">Rate(₹)</th>
        <th style="width: 65px;">Total(₹)</th>
      </tr>
    </thead>
    <tbody>
`;

export const renderTableRow = (item: any, index: number, isGold: boolean) => {
  const gross = item.gross_weight || item.net_weight || 0;
  const net = item.net_weight || 0;
  const tanch = item.gold_calculation?.purity_percent || item.silver_calculation?.purity_percent || item.touch_purity || 91.6;
  const fine = item.gold_calculation?.fine_weight || item.silver_calculation?.pure_weight || item.fine_weight || 0;
  const rate = item.gold_calculation?.applied_rate || item.silver_calculation?.applied_rate || item.metal_rate || 0;
  const total = item.taxable_amount || item.final_price || item.total_price || item.metal_value || 0;

  return `
    <tr>
      <td style="text-align: center; color: #777;">${index + 1}</td>
      <td style="font-weight: 600;">${item.item_name || 'Jewellery Item'}</td>
      <td>${isGold ? '7113' : '7106'}</td>
      <td>${Number(gross).toFixed(3)}</td>
      <td>${Number(net).toFixed(3)}</td>
      <td>${Number(tanch).toFixed(1)}%</td>
      <td style="font-weight: 600; color: ${isGold ? '#B45309' : '#374151'};">${Number(fine).toFixed(3)}</td>
      <td>${Number(rate).toLocaleString('en-IN')}</td>
      <td style="font-weight: 700;">${Number(total).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</td>
    </tr>
  `;
};

export const renderTableEnd = () => `
    </tbody>
  </table>
`;

export const renderSettlements = (metalsArray: string[], goldBilled: any, silverBilled: any) => {
  if (goldBilled.balanceLedger <= 0 && silverBilled.balanceLedger <= 0) return '';
  return `
    <div class="settlement-box">
      <div class="settlement-title">Metal Settlement Summary</div>
      <div style="font-size: 8.5px; color: #444; line-height: 1.4;">
        ${goldBilled.balanceLedger > 0 ? `• Gold Settled to Ledger: <b>${goldBilled.balanceLedger.toFixed(3)} g</b><br>` : ''}
        ${silverBilled.balanceLedger > 0 ? `• Silver Settled to Ledger: <b>${silverBilled.balanceLedger.toFixed(3)} g</b>` : ''}
      </div>
    </div>
  `;
};

export const renderBottomRow = (
  metalsArray: string[],
  invoice: any,
  totals: any,
  settings: any,
  goldBilled: any,
  silverBilled: any
) => {
  const taxable = Number(invoice.subtotal || totals.taxable_amount || 0);
  const cgst = Number(invoice.cgst || (invoice.tax_amount ? invoice.tax_amount / 2 : taxable * 0.015));
  const sgst = Number(invoice.sgst || (invoice.tax_amount ? invoice.tax_amount / 2 : taxable * 0.015));
  const grand = Number(invoice.grand_total || taxable + cgst + sgst);
  const paid = Number(invoice.amount_paid || invoice.cash_received || 0);
  const due = Number(invoice.balance_due || invoice.balance_amount || 0);

  return `
    <div class="bottom-row">
      <div class="bottom-col-left">
        <div style="border: 1px solid var(--border); border-radius: 6px; padding: 6px 8px; font-size: 8.5px; line-height: 1.3;">
          <b>Terms & Conditions:</b><br>
          1. Goods once sold will not be taken back without original bill.<br>
          2. Subject to local jurisdiction only.<br>
          3. Purity guaranteed as per hallmark standards.
        </div>
      </div>
      <div class="bottom-col-right">
        <table class="totals-table">
          <tr><td>Taxable Amount</td><td style="text-align: right; font-weight: 600;">₹ ${taxable.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</td></tr>
          <tr><td>CGST (1.5%)</td><td style="text-align: right;">₹ ${cgst.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</td></tr>
          <tr><td>SGST (1.5%)</td><td style="text-align: right;">₹ ${sgst.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</td></tr>
          <tr class="grand-total"><td>Grand Total</td><td style="text-align: right;">₹ ${grand.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</td></tr>
          <tr><td>Amount Paid</td><td style="text-align: right; color: var(--green); font-weight: 600;">₹ ${paid.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</td></tr>
          <tr><td>Balance Due</td><td style="text-align: right; color: ${due > 0 ? 'var(--red)' : '#555'}; font-weight: 700;">₹ ${due.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</td></tr>
        </table>
      </div>
    </div>
  `;
};
