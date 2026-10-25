
export const getCommonStyles = () => `
  <style>
    :root {
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
    }
    
    * { box-sizing: border-box; margin: 0; padding: 0; }
    
    body {
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      color: var(--text);
      background: white;
      -webkit-font-smoothing: antialiased;
      line-height: 1.5;
    }
    
    @page { size: A4 portrait; margin: 0; }
    
    @media print {
      body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    }

    .pdf-container {
      width: 100%;
      background: #e0e0e0;
      display: flex;
      flex-direction: column;
      align-items: center;
    }

    .invoice-wrapper {
      width: 210mm;
      height: 296.5mm;
      background: white;
      position: relative;
      padding: 4mm 5mm 5mm 5mm;
      box-sizing: border-box;
      overflow: hidden;
    }

    .watermark { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-family: 'Cinzel', serif; font-size: 350px; color: var(--gold); opacity: 0.03; z-index: 0; pointer-events: none; }
    .content { position: relative; z-index: 1; min-height: 100%; height: max-content; display: flex; flex-direction: column; transform-origin: top center; }
    
    .header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 2px; }
    .logo-section { display: flex; align-items: center; gap: 15px; }
    .logo-circle { width: 64px; height: 64px; border-radius: 50%; border: 2px solid var(--gold); display: flex; align-items: center; justify-content: center; font-family: 'Cinzel', serif; font-size: 32px; color: var(--gold); position: relative; background: radial-gradient(circle, #FFFDF7 0%, #FAF6EA 100%); }
    .logo-circle::after { content: ''; position: absolute; width: 54px; height: 54px; border-radius: 50%; border: 1px solid rgba(212, 175, 55, 0.4); }
    .logo-img { max-width: 64px; max-height: 64px; object-fit: contain; }
    .company-info h1 { font-family: 'Cinzel', serif; font-size: 26px; font-weight: 700; color: var(--navy); line-height: 1.15; letter-spacing: 2px; margin-bottom: 3px; }
    .tagline { font-family: 'Inter', sans-serif; font-size: 9px; font-weight: 700; color: var(--gold-dark); letter-spacing: 2.5px; text-transform: uppercase; }
    
    .tax-invoice-badge { background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); color: var(--gold); border: 1.5px solid rgba(212, 175, 55, 0.6); padding: 5px 18px; border-radius: 6px; font-family: 'Cinzel', serif; font-size: 13.5px; font-weight: 700; letter-spacing: 1.5px; display: inline-flex; align-items: center; gap: 8px; margin-bottom: 3px; box-shadow: 0 2px 8px rgba(15, 23, 42, 0.12); }
    .tax-invoice-badge svg { width: 15px; height: 15px; fill: var(--gold); }
    .meta-table { margin-top: 3px; font-size: 9.5px; font-weight: 600; color: var(--navy); }
    .meta-table td { padding: 1.5px 8px 1.5px 0; }
    .meta-table td:first-child { width: 90px; color: var(--text-muted); font-size: 9px; }
    
    .diamond-divider { display: flex; align-items: center; margin: 3px 0 6px; }
    .diamond-divider::before, .diamond-divider::after { content: ''; flex: 1; height: 1px; background: linear-gradient(90deg, rgba(212,175,55,0.1), rgba(212,175,55,0.6), rgba(212,175,55,0.1)); }
    .diamond { width: 5px; height: 5px; background: var(--gold); transform: rotate(45deg); margin: 0 10px; }
    
    .cards-row { display: flex; gap: 10px; margin-bottom: 4px; }
    .info-card { flex: 1; border: 1px solid var(--card-border); border-radius: 8px; padding: 6px 10px; background: var(--card-bg); position: relative; box-shadow: 0 1px 3px rgba(0,0,0,0.02); }
    .card-header { display: flex; align-items: center; gap: 7px; margin-bottom: 5px; border-bottom: 1px solid var(--card-border); padding-bottom: 4px; }
    .card-icon { background: linear-gradient(135deg, #0F172A, #1E293B); color: var(--gold); width: 22px; height: 22px; border-radius: 4px; border: 1px solid rgba(212,175,55,0.3); display: flex; align-items: center; justify-content: center; }
    .card-icon svg { width: 12px; height: 12px; fill: currentColor; }
    .card-title { font-family: 'Cinzel', serif; font-size: 10.5px; font-weight: 800; color: #0F172A; letter-spacing: 1.2px; }
    .info-card h3 { font-size: 14px; font-weight: 700; color: var(--navy); margin-bottom: 4px; }
    .info-line { display: flex; align-items: flex-start; gap: 7px; font-size: 10px; color: var(--text); margin-bottom: 3px; }
    .info-line svg { width: 12px; height: 12px; fill: var(--text-muted); margin-top: 2px; flex-shrink: 0; }
    
    .items-table { width: 100%; border-collapse: separate; border-spacing: 0 2px; margin-top: 2px; font-variant-numeric: tabular-nums; }
    .items-table th { background: linear-gradient(180deg, #0F172A 0%, #162036 100%); color: #D4AF37; padding: 4.5px 4px; font-size: 9px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; border-bottom: 2px solid #D4AF37; }
    .items-table th:first-child { border-radius: 4px 0 0 0; }
    .items-table th:last-child { border-radius: 0 4px 0 0; }
    .items-table tbody td { background: #FFFFFF; padding: 3.5px 4px; font-size: 10px; border-top: 1px solid #ECE7DB; border-bottom: 1px solid #ECE7DB; text-align: center; color: #1E293B; }
    .items-table tbody tr:hover td, .items-table tbody tr:nth-child(even) td { background: #FAF8F2; }
    .items-table th:nth-child(2), .items-table td:nth-child(2) { text-align: left; }
    
    .grand-total-box { margin-top: 10px; background: linear-gradient(135deg, var(--gold-light), var(--gold), var(--gold-dark)); border-radius: 8px; padding: 8px 16px; text-align: center; color: var(--navy); box-shadow: 0 4px 15px rgba(212, 175, 55, 0.25); position: relative; }
    .grand-total-box::after { content: ''; position: absolute; bottom: -5px; left: 50%; transform: translateX(-50%) rotate(45deg); width: 10px; height: 10px; background: var(--gold-dark); border-radius: 50%; }
  </style>
`;

export const getPageWrapperStart = (company?: any) => {
  const name = company?.name || 'Jewellers';
  const initials = name.split(' ').map((w: string) => w[0]).filter(Boolean).slice(0, 2).join('').toUpperCase() || 'J';
  return `
<div class="invoice-wrapper">
  <div class="watermark">${initials}</div>
  <div class="content">
`;
};

export const getPageWrapperEnd = (company: any, pageNum: any, totalPages: any) => `
    <div style="text-align: center; margin-top: auto; padding-bottom: 46px; font-family: 'Cinzel', serif; font-size: 10px; font-weight: 700; color: var(--gold); letter-spacing: 1px;">
      Purity You Trust, Elegance You Deserve.
      <div style="font-size: 8px; margin-top: 3px; font-family: 'Inter', sans-serif;">Page ${pageNum} of ${totalPages}</div>
    </div>

    <!-- Thank You Badge Overlapping -->
    <div style="position: absolute; bottom: 2mm; right: 20px; z-index: 10; width: 62px; height: 62px; border-radius: 50%; background: #0B132B; border: 2px solid var(--gold); display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: 0 2px 8px rgba(0,0,0,0.18);">
      <svg viewBox="0 0 24 24" style="width: 13px; height: 13px; fill: var(--gold); margin-bottom: 1px;"><path d="M12 2l-5.5 9h11z"/><path d="M12 22l5.5-9h-11z"/></svg>
      <div style="font-family: 'Cinzel', serif; font-size: 9px; font-weight: 700; color: var(--gold); line-height: 1.1; text-align: center;">THANK<br>YOU</div>
      <div style="font-family: 'Inter', sans-serif; font-size: 5.5px; color: var(--gold); margin-top: 1px; text-transform: uppercase; letter-spacing: 0.8px;">For Your Visit</div>
    </div>

    <!-- Navy Strip Footer -->
    <div style="position: absolute; bottom: 4mm; left: 5mm; right: 5mm; height: 36px; border-radius: 6px; background: #0B132B; display: flex; align-items: center; padding: 0 95px 0 20px; justify-content: space-between; color: white; font-size: 9px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">
      <div style="display: flex; align-items: center; gap: 6px;">
        <svg viewBox="0 0 24 24" style="width: 12px; height: 12px; fill: var(--gold); flex-shrink: 0;"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>
        <span style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 190px;">${(company?.address || '').split(',')[0] || ''}, ${(company?.address || '').split(',')[1] || ''}</span>
      </div>
      <div style="display: flex; flex-direction: column; gap: 1px;">
        <div style="display: flex; align-items: center; gap: 6px;">
          <svg viewBox="0 0 24 24" style="width: 11px; height: 11px; fill: var(--gold); flex-shrink: 0;"><path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/></svg>
          <span>${company?.phone || ''}</span>
        </div>
        <div style="display: flex; align-items: center; gap: 6px;">
          <svg viewBox="0 0 24 24" style="width: 11px; height: 11px; fill: var(--gold); flex-shrink: 0;"><path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 14H4V8l-8 5-8-5v10h16zm-8-7L4 6h16l-8 5z"/></svg>
          <span style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 180px;">${company?.email || ''}</span>
        </div>
      </div>
      <div style="display: flex; align-items: center; gap: 6px;">
        <svg viewBox="0 0 24 24" style="width: 12px; height: 12px; fill: var(--gold); flex-shrink: 0;"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/></svg>
        <span style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 160px;">${company?.website || (company?.email && company.email.includes('@') ? 'www.' + company.email.split('@')[1] : '')}</span>
      </div>
    </div>
  </div>
</div>
`;

export const renderHeader = (company: any, invoice: any, logoDataUrl?: string) => {
  const formatDate = (dateString?: string) => {
    if (!dateString) return '';
    try {
      return new Date(dateString).toLocaleDateString('en-GB', { day: '2-digit', month: 'long', year: 'numeric' }).toUpperCase();
    } catch { return dateString; }
  };
  const storeName = company?.name || 'Jewellers';
  const initials = storeName.split(' ').map((w: string) => w[0]).filter(Boolean).slice(0, 2).join('').toUpperCase() || 'J';
  return `
    <div class="header" style="margin-bottom: 2px;">
      <div class="logo-section">
        ${logoDataUrl ? `<img src="${logoDataUrl}" class="logo-img" />` : `<div class="logo-circle">${initials}</div>`}
        <div class="company-info">
          <h1>${storeName.replace(' ', '<br>')}</h1>
          <div class="tagline">${company?.tagline || 'TIMELESS BEAUTY. TRUSTED FOREVER.'}</div>
        </div>
      </div>
      <div style="text-align: right; display: flex; flex-direction: column; align-items: flex-end;">
        <div class="tax-invoice-badge">
          <svg viewBox="0 0 24 24"><path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2h12c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/></svg>
          TAX INVOICE
        </div>
        <table class="meta-table" style="margin-left: auto;">
          <tr><td>INVOICE NO.</td><td>:</td><td style="color: var(--navy);">${invoice.invoice_number}</td></tr>
          <tr><td>DATE</td><td>:</td><td style="color: var(--navy);">${formatDate(invoice.invoice_date)}</td></tr>
          <tr><td>PLACE</td><td>:</td><td style="color: var(--navy);">${company.address.split(',')[0] || '-'}</td></tr>
          <tr><td>GSTIN</td><td>:</td><td style="color: var(--navy);">${company.gstin || '-'}</td></tr>
        </table>
      </div>
    </div>
    <div class="diamond-divider"><div class="diamond"></div></div>
  `;
};

export const renderCardsRow = (customer: any, qrDataUrl: string, settings?: any, invoice?: any) => {
  const upiId = settings?.upi_id || '';
  const upiName = settings?.upi_name || settings?.business_name || settings?.store_name || 'Jewellery Store';
  const isCustomAmount = settings?.qr_amount_type === 'custom';
  
  // Calculate true payable / due amount (e.g. 4038.55 for EXC-16, not 138656.75)
  let payableAmount = 0;
  if (invoice?.balance_due != null && Number(invoice.balance_due) > 0) {
    payableAmount = Number(invoice.balance_due);
  } else if (invoice?.balance_amount != null && Number(invoice.balance_amount) > 0) {
    payableAmount = Number(invoice.balance_amount);
  } else if (invoice?.difference_amount != null && Number(invoice.difference_amount) > 0) {
    payableAmount = Number(invoice.difference_amount);
  } else {
    const grand = Number(invoice?.grand_total || 0);
    const settled = Number(invoice?.cash_received || invoice?.amount_paid || 0) + Number(invoice?.metal_received_value || invoice?.total_old_value || 0);
    payableAmount = Math.max(0, grand - settled);
    if (payableAmount === 0 && grand > 0 && settled === 0) {
      payableAmount = grand;
    }
  }
  
  let upiDeepLink = upiId ? `upi://pay?pa=${encodeURIComponent(upiId)}&pn=${encodeURIComponent(upiName)}` : '';
  if (upiDeepLink && !isCustomAmount && payableAmount > 0) {
    upiDeepLink += `&am=${payableAmount.toFixed(2)}`;
  }
  if (upiDeepLink) {
    upiDeepLink += `&cu=INR&tn=${encodeURIComponent(invoice?.invoice_number || 'Tax Invoice')}`;
  }
  
  const qrUrl = qrDataUrl || `https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=${encodeURIComponent(upiDeepLink)}`;

  return `
    <div class="cards-row">
      <div class="info-card">
        <div class="card-header">
          <div class="card-icon"><svg viewBox="0 0 24 24" style="width: 16px; height: 16px; fill: currentColor;"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg></div>
          <div class="card-title">BILL TO</div>
        </div>
        <h3>${customer.name}</h3>
        <div class="info-line"><svg viewBox="0 0 24 24" style="width: 14px; height: 14px; fill: currentColor; flex-shrink: 0;"><path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/></svg><span>${customer.phone || '-'}</span></div>
        <div class="info-line"><svg viewBox="0 0 24 24" style="width: 14px; height: 14px; fill: currentColor; flex-shrink: 0;"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg><span>${customer.address || '-'}</span></div>
        <div class="info-line" style="margin-top: 5px; font-weight: 600;"><svg viewBox="0 0 24 24" style="width: 14px; height: 14px; fill: currentColor; flex-shrink: 0;"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/></svg><span>GSTIN: ${customer.gstin || '-'}</span></div>
      </div>
      <div class="info-card" style="display: flex; flex-direction: column;">
        <div class="card-header">
          <div class="card-icon"><svg viewBox="0 0 24 24" style="width: 16px; height: 16px; fill: currentColor;"><path d="M20 4H4c-1.11 0-1.99.89-1.99 2L2 18c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V6c0-1.11-.89-2-2-2zm0 14H4v-6h16v6zm0-10H4V6h16v2z"/></svg></div>
          <div class="card-title">PAYMENT INFO</div>
        </div>
        <div style="display: flex; justify-content: space-between; margin-top: 5px; flex: 1;">
          <table style="font-size: 11px; font-weight: 600; color: #16213E;">
            <tr><td style="padding-bottom: 4px; width: 60px;">MODE</td><td style="padding-bottom: 4px;">:</td><td style="padding-bottom: 4px; padding-left: 10px;">NEFT / UPI / CASH</td></tr>
            <tr><td style="padding-bottom: 4px;">UPI ID</td><td style="padding-bottom: 4px;">:</td><td style="padding-bottom: 4px; padding-left: 10px; font-family: monospace;">${upiId}</td></tr>
            ${settings?.bank_account_no ? `<tr><td style="padding-bottom: 4px;">A/C NO</td><td style="padding-bottom: 4px;">:</td><td style="padding-bottom: 4px; padding-left: 10px; font-family: monospace;">${settings.bank_account_no}</td></tr>` : ''}
            ${settings?.bank_ifsc ? `<tr><td style="padding-bottom: 4px;">IFSC</td><td style="padding-bottom: 4px;">:</td><td style="padding-bottom: 4px; padding-left: 10px; font-family: monospace;">${settings.bank_ifsc}</td></tr>` : ''}
            <tr><td colspan="3" style="padding-top: 6px; font-size: 10px; color: #7f8c8d; font-weight: 700;">SCAN TO PAY</td></tr>
          </table>
          <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; width: 72px;">
            <img src="${qrUrl}" style="width: 52px; height: 52px; object-fit: contain; margin-bottom: 3px; border-radius: 4px;" />
            <div style="background: var(--navy); color: white; border-radius: 4px; padding: 2px 6px; font-size: 8px; font-weight: 700; text-align: center; width: 100%;">SCAN TO PAY</div>
          </div>
        </div>
      </div>
    </div>
  `;
};

export const renderTableHeader = () => `
  <div style="min-height: 20px; width: 100%; margin-bottom: 5px;">
    <table class="items-table">
      <thead>
        <tr>
          <th>S.NO.</th><th>DESCRIPTION</th><th>METAL</th><th>TANCH<br>+WAST</th><th>WEIGHT<br>(gm)</th><th>RATE<br>(&#8377;)</th><th>MAKING<br>(&#8377;)</th><th>OTHER<br>(&#8377;)</th><th>AMOUNT<br>(&#8377;)</th>
        </tr>
      </thead>
      <tbody>
`;

export const formatCurrency = (amount?: number) => {
  if (amount === undefined || amount === null) return '0.00';
  return amount.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
};

export const renderTableRow = (item: any, index: number, isGold: boolean) => {
  const isZeroPrice = !item.final_price || item.final_price === 0;
  const gross = Number(item.gross_weight || 0);
  const stone = Number(item.stone_weight || 0);
  const netWt = Number(item.net_weight) > 0
    ? Number(item.net_weight)
    : (gross - stone > 0 ? (gross - stone) : Number(item.pure_weight || item.fine_weight || gross || 0));
  
  let displayRate = Number(item.applied_rate || 0);
  if (isGold && displayRate > 0 && displayRate < 15000) {
    displayRate = displayRate * 10;
  } else if (!isGold && displayRate > 0 && displayRate < 1000) {
    displayRate = displayRate * 1000;
  }

  return `
        <tr>
          <td>${index + 1}</td>
          <td style="text-align: left; font-weight: 600;">
            <div style="font-size: 14px; color: #16213E; font-weight: 700;">${item.item_name}</div>
            <div style="font-size: 11px; color: #7f8c8d; font-weight: 400; margin-top: 2px;">Gross: ${gross}g</div>
          </td>
          <td>${item.metal_type || '-'}</td>
          <td>${(item.tanch_percentage || item.touch_purity) ? (item.tanch_percentage || item.touch_purity) + '%' : '-'}${item.wastage ? ` + ${item.wastage}%` : ''}</td>
          <td>${netWt.toFixed(3)}</td>
          <td>${formatCurrency(displayRate)}<div style="font-size: 9px; color: #7f8c8d; margin-top: 1px;">${!isGold ? 'per kg' : 'per 10g'}</div></td>
          <td>${isZeroPrice ? '-' : formatCurrency(item.making_charges || 0)}</td>
          <td>${isZeroPrice ? '-' : formatCurrency((item.other_charges || 0) + (item.hallmark_charges || 0))}</td>
          <td style="font-weight: 700;">${isZeroPrice ? '-' : `&#8377; ${formatCurrency(item.final_price)}`}</td>
        </tr>
  `;
};

export const renderTableEnd = () => `
      </tbody>
    </table>
  </div>
`;

export const renderSettlements = (metals: string[], goldSettlement: any, silverSettlement: any, _invoice?: any) => {
  const hasGold = metals.includes('Gold');
  const hasSilver = metals.includes('Silver');
  if (!hasGold && !hasSilver) return '';

  const generateBox = (metal: 'GOLD' | 'SILVER', data: any, fullWidth: boolean) => {
    const { fineBilled = 0, fineReceived = 0, appliedRate = 0, metalValueSettled = 0 } = data || {};
    let fineBalance = Math.max(0, fineBilled - fineReceived);
    if (_invoice) {
      if (metal === 'GOLD' && _invoice.gold_balance_metal_weight !== undefined && _invoice.gold_balance_metal_weight !== null) {
        fineBalance = Number(_invoice.gold_balance_metal_weight);
      } else if (metal === 'SILVER' && _invoice.silver_balance_metal_weight !== undefined && _invoice.silver_balance_metal_weight !== null) {
        fineBalance = Number(_invoice.silver_balance_metal_weight);
      }
      if (_invoice.settlement_type === 'Cash' || (_invoice.bill_type === 'Cash' && !_invoice.gold_balance_metal_weight && !_invoice.silver_balance_metal_weight)) {
        fineBalance = 0;
      }
    }
    let boxRate = appliedRate;
    if (metal === 'GOLD' && boxRate > 0 && boxRate < 15000) boxRate = boxRate * 10;
    if (metal === 'SILVER' && boxRate > 0 && boxRate < 1000) boxRate = boxRate * 1000;
    const isFixed = boxRate > 0;
    
    const color = metal === 'GOLD' ? '#8F6614' : '#334155';
    const border = metal === 'GOLD' ? '1px solid #E2D3B8' : '1px solid #E2E8F0';
    const bg = metal === 'GOLD' ? 'linear-gradient(180deg, #FDFAF4 0%, #F8F4E8 100%)' : 'linear-gradient(180deg, #F8FAFC 0%, #F1F5F9 100%)';
    const titleColor = metal === 'GOLD' ? '#D4AF37' : '#94A3B8';

    const explicitSurplus = metal === 'GOLD'
      ? (Number(_invoice?.gold_balance_metal_weight || 0) < -0.001 ? Math.abs(Number(_invoice.gold_balance_metal_weight)) : 0)
      : (Number(_invoice?.silver_balance_metal_weight || 0) < -0.001 ? Math.abs(Number(_invoice.silver_balance_metal_weight)) : 0);
    const calculatedSurplus = Math.max(0, (fineReceived || 0) - (fineBilled || 0));
    const surplus = Math.max(calculatedSurplus, explicitSurplus);
    const physicalDiff = Math.max(0, fineBilled - fineReceived);
    let balanceLabel = '';
    let balanceColor = '#10B981';

    if (fineBalance > 0.001) {
      balanceColor = '#DC2626';
      balanceLabel = `+ ${fineBalance.toFixed(3)} gm Balance Due`;
    } else if (surplus > 0.001) {
      balanceColor = '#10B981';
      balanceLabel = `- ${surplus.toFixed(3)} gm Surplus`;
    } else if (physicalDiff > 0.001) {
      balanceColor = '#2563EB';
      balanceLabel = `0.000 gm (Settled in Cash)`;
    } else {
      balanceColor = '#10B981';
      balanceLabel = `0.000 gm (Settled)`;
    }

    return `
      <div style="flex: 1; border: ${border}; border-radius: 8px; background: ${bg}; display: flex; flex-direction: column; box-shadow: 0 1px 4px rgba(0,0,0,0.02); ${fullWidth ? 'width: 100%;' : ''}">
        <div style="padding: 5px 9px; flex: 1;">
          <div style="font-family: 'Cinzel', serif; font-size: 11px; font-weight: 800; color: ${color}; display: flex; align-items: center; gap: 6px; margin-bottom: 4px; border-bottom: ${border}; padding-bottom: 4px;">
            <svg viewBox="0 0 24 24" style="width: 12px; height: 12px; fill: ${titleColor};"><path d="M12 2L4 6v2h16V6l-8-4zm0 2.5l5.5 2.75h-11L12 4.5zM4 10v9h16v-9H4zm14 7H6v-5h12v5z"/></svg>
            ${metal} SETTLEMENT ${metal === 'GOLD' ? '(22K)' : '(92.5)'}
          </div>
          <table style="width: 100%; font-size: 10px; font-weight: 600; color: #16213E; margin-bottom: 4px; line-height: 1.4; font-variant-numeric: tabular-nums;">
            <tr><td>Total ${metal === 'GOLD' ? 'Gold' : 'Silver'} Required</td><td style="text-align: right; width: 5%;">:</td><td style="text-align: right;">${fineBilled.toFixed(3)} gm</td></tr>
            <tr><td>${metal === 'GOLD' ? 'Gold' : 'Silver'} Received</td><td style="text-align: right;">:</td><td style="text-align: right;">${fineReceived.toFixed(3)} gm</td></tr>
            <tr><td colspan="3"><hr style="border: none; border-top: 1px dashed rgba(0,0,0,0.1); margin: 4px 0;"></td></tr>
            ${isFixed ? `
            <tr><td>Rate</td><td style="text-align: right;">:</td><td style="text-align: right;">&#8377; ${boxRate.toLocaleString('en-IN')}${metal === 'SILVER' ? '/kg' : '/10g'}</td></tr>
            <tr><td>Value Settled (Metal)</td><td style="text-align: right;">:</td><td style="text-align: right; color: #10B981; font-weight: 800;">&#8377; ${metalValueSettled.toLocaleString('en-IN', {minimumFractionDigits:2, maximumFractionDigits:2})}</td></tr>
            <tr><td>Balance Due</td><td style="text-align: right;">:</td><td style="text-align: right; color: ${balanceColor}; font-weight: 800;">${balanceLabel}</td></tr>
            ` : `
            <tr><td>Balance Due</td><td style="text-align: right;">:</td><td style="text-align: right; color: ${balanceColor}; font-weight: 800;">${balanceLabel}</td></tr>
            `}
          </table>
        </div>
      </div>`;
  };

  const showGold = hasGold && (goldSettlement.fineBilled > 0 || goldSettlement.fineReceived > 0);
  const showSilver = hasSilver && (silverSettlement.fineBilled > 0 || silverSettlement.fineReceived > 0);

  if (!showGold && !showSilver) return '';

  const fullWidth = (showGold && !showSilver) || (!showGold && showSilver);

  // Settlement Option Banner Badge
  const st = (_invoice?.settlement_type || '').toLowerCase();
  const rawGoldBal = Number(_invoice?.gold_balance_metal_weight || 0);
  const rawSilverBal = Number(_invoice?.silver_balance_metal_weight || 0);
  const goldBal = Math.max(0, rawGoldBal);
  const silverBal = Math.max(0, rawSilverBal);

  const goldSurplusAmt = Math.max(0, (goldSettlement?.fineReceived || 0) - (goldSettlement?.fineBilled || 0), rawGoldBal < -0.001 ? Math.abs(rawGoldBal) : 0);
  const silverSurplusAmt = Math.max(0, (silverSettlement?.fineReceived || 0) - (silverSettlement?.fineBilled || 0), rawSilverBal < -0.001 ? Math.abs(rawSilverBal) : 0);
  const hasMetalSurplusTotal = goldSurplusAmt > 0.001 || silverSurplusAmt > 0.001;
  const isPureCashSettlement = st === 'cash' || _invoice?.bill_type === 'Cash';

  const hasGoldDue = !isPureCashSettlement && (goldBal > 0.001 || ((goldSettlement?.fineBilled || 0) > (goldSettlement?.fineReceived || 0) + 0.001 && rawGoldBal >= 0));
  const hasSilverDue = !isPureCashSettlement && (silverBal > 0.001 || ((silverSettlement?.fineBilled || 0) > (silverSettlement?.fineReceived || 0) + 0.001 && rawSilverBal >= 0));

  let settlementBadge = '';
  if (hasGoldDue && hasSilverDue) {
    settlementBadge = `<div style="text-align: center; margin-bottom: 3px;"><span style="background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%); border: 1px solid #93C5FD; color: #1E40AF; padding: 2.5px 12px; border-radius: 12px; font-size: 8.5px; font-weight: 800; letter-spacing: 0.6px; box-shadow: 0 1px 3px rgba(30,64,175,0.08);">OPTION 4: BOTH METALS DUE (Gold &amp; Silver Balance Due | Charges in Cash)</span></div>`;
  } else if (hasGoldDue) {
    settlementBadge = `<div style="text-align: center; margin-bottom: 3px;"><span style="background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%); border: 1px solid #D4AF37; color: #78350F; padding: 2.5px 12px; border-radius: 12px; font-size: 8.5px; font-weight: 800; letter-spacing: 0.6px; box-shadow: 0 1px 3px rgba(212,175,55,0.12);">OPTION 2: GOLD DUE (Remaining Gold Balance Due | Silver &amp; Charges in Cash)</span></div>`;
  } else if (hasSilverDue) {
    settlementBadge = `<div style="text-align: center; margin-bottom: 3px;"><span style="background: linear-gradient(135deg, #F8FAFC 0%, #E2E8F0 100%); border: 1px solid #CBD5E1; color: #334155; padding: 2.5px 12px; border-radius: 12px; font-size: 8.5px; font-weight: 800; letter-spacing: 0.6px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">OPTION 3: SILVER DUE (Remaining Silver Balance Due | Gold &amp; Charges in Cash)</span></div>`;
  } else if (hasMetalSurplusTotal) {
    const surplusSummaryParts = [
      goldSurplusAmt > 0.001 ? `${goldSurplusAmt.toFixed(3)}g Gold Surplus` : '',
      silverSurplusAmt > 0.001 ? `${silverSurplusAmt.toFixed(3)}g Silver Surplus` : ''
    ].filter(Boolean).join(' & ');
    settlementBadge = `<div style="text-align: center; margin-bottom: 3px;"><span style="background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%); border: 1px solid #10B981; color: #065F46; padding: 2.5px 12px; border-radius: 12px; font-size: 8.5px; font-weight: 800; letter-spacing: 0.6px; box-shadow: 0 1px 3px rgba(16,185,129,0.12);">METAL ADVANCE / SURPLUS (${surplusSummaryParts} Deposited | Credited to Customer Advance)</span></div>`;
  } else if (st === 'cash' || _invoice?.bill_type === 'Cash' || (_invoice && goldBal <= 0.001 && silverBal <= 0.001 && (goldSettlement.fineBilled > 0 || silverSettlement.fineBilled > 0))) {
    settlementBadge = `<div style="text-align: center; margin-bottom: 3px;"><span style="background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%); border: 1px solid #6EE7B7; color: #065F46; padding: 2.5px 12px; border-radius: 12px; font-size: 8.5px; font-weight: 800; letter-spacing: 0.6px; box-shadow: 0 1px 3px rgba(5,150,105,0.08);">OPTION 1: CASH SETTLEMENT (All Metal &amp; Bill Dues Settled in Cash)</span></div>`;
  }

  return `
    <div style="margin-top: 3px;">
      <div style="display: flex; align-items: center; justify-content: center; margin: 5px 0 3px; position: relative;">
        <div style="position: absolute; left: 0; right: 0; height: 1px; background: linear-gradient(90deg, transparent, #E2D3B8 20%, #E2D3B8 80%, transparent); z-index: 1;"></div>
        <span style="position: relative; z-index: 2; background: #FFFFFF; border: 1.5px solid #D4AF37; padding: 2px 16px; border-radius: 12px; color: #8F6614; font-family: 'Cinzel', serif; font-weight: 800; font-size: 10.5px; letter-spacing: 1.2px; display: inline-flex; align-items: center; gap: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
          <svg viewBox="0 0 24 24" style="width: 12px; height: 12px; fill: #D4AF37;"><path d="M12 2L4 6v2h16V6l-8-4zm0 2.5l5.5 2.75h-11L12 4.5zM4 10v9h16v-9H4zm14 7H6v-5h12v5z"/></svg>
          METAL SETTLEMENT
        </span>
      </div>
      ${settlementBadge}
      <div style="display: flex; gap: 8px;">
          ${showGold ? generateBox('GOLD', goldSettlement, fullWidth) : ''}
          ${showSilver ? generateBox('SILVER', silverSettlement, fullWidth) : ''}
      </div>
      <div style="text-align: center; font-size: 8px; color: #7f8c8d; margin-top: 2px;">
          ${hasMetalSurplusTotal ? 'Surplus metal is credited as advance metal deposit in customer account.' : 'If fine balance is 0.000 gm, metal balance is fully settled for this invoice.'}
      </div>
    </div>
  `;
};




export const renderBottomRow = (metals: string[], invoice: any, totals: any, settings: any, goldBilled?: any, silverBilled?: any) => {
  const isExchange = invoice.bill_type === 'Exchange' || (invoice.invoice_number || '').startsWith('EXC-') || invoice.type === 'exchange';
  const taxableAmount  = Number(invoice.subtotal || totals.subtotal || 0);
  const gstAmount      = Number(invoice.tax_amount || totals.tax_amount || 0);
  const totalBillWithTax = taxableAmount + gstAmount;

  const oldItemsValue  = Number(invoice.total_old_value || 0);
  const discountAmount = isExchange ? 0 : Number(invoice.discount_amount || totals.discount_amount || 0);

  // Net difference due before payments or ledger conversions
  const netDueBeforeSettlement = Math.max(0, totalBillWithTax - oldItemsValue - discountAmount);

  const cashPaid       = Number(invoice.amount_paid || invoice.cash_paid || invoice.cash_received || 0);
  const rawBalanceDue  = Number(invoice.balance_due ?? invoice.balance_amount ?? 0);
  const nonMetalCharges = (Number(totals.totalMakingCharges || 0)) + (Number(totals.totalOtherCharges || 0)) + gstAmount;

  // Non-metal charges (GST, Making Charges, Other Expenses) can NEVER be settled in metal.
  // When settling in metal or hybrid, any unpaid non-metal charges MUST be due in cash!
  let balanceDue = rawBalanceDue;
  if (isExchange && balanceDue < (nonMetalCharges - cashPaid) - 0.01) {
    balanceDue = Math.max(0, nonMetalCharges - cashPaid);
  }

  const metalRecStr    = invoice.metal_received_str || '';
  const metalValue     = Number(invoice.metal_received_value || invoice.metal_given_value || 0);

  // Metal / Ledger settled:
  // Any portion of netDueBeforeSettlement that was settled via metal ledger conversion or physical metal deposit
  const ledgerSettledValue = Math.max(0, netDueBeforeSettlement - cashPaid - Math.max(0, balanceDue));

  // Round off calculation
  const explicitRoundOff = Number(invoice.round_off || 0);
  const calcRoundOff = (Number(invoice.grand_total || 0) > 0 && !isExchange) 
    ? Number(invoice.grand_total) - (taxableAmount + gstAmount - discountAmount) 
    : explicitRoundOff;
  const showRoundOff = Math.abs(calcRoundOff) > 0.01;

  // Determine physical metal due for THIS bill only
  let pendingGoldGrams   = Math.max(0, (goldBilled?.fineBilled || 0) - (goldBilled?.fineReceived || 0));
  let pendingSilverGrams = Math.max(0, (silverBilled?.fineBilled || 0) - (silverBilled?.fineReceived || 0));

  // If this invoice has explicit settled metal balance weights (e.g. from exchange settlement with cash payment)
  if (invoice.gold_balance_metal_weight !== undefined && invoice.gold_balance_metal_weight !== null && (invoice.settlement_type || isExchange)) {
    pendingGoldGrams = Number(invoice.gold_balance_metal_weight);
  }
  if (invoice.silver_balance_metal_weight !== undefined && invoice.silver_balance_metal_weight !== null && (invoice.settlement_type || isExchange)) {
    pendingSilverGrams = Number(invoice.silver_balance_metal_weight);
  }

  // If settlement type is pure 'Cash', no metal is due to ledger
  if (invoice.settlement_type === 'Cash' || (invoice.bill_type === 'Cash' && !invoice.gold_balance_metal_weight && !invoice.silver_balance_metal_weight)) {
    pendingGoldGrams = 0;
    pendingSilverGrams = 0;
  }

  // In the bill, ONLY this bill's actual pending metal is displayed (no external ledger totals)
  const effectiveGoldDue   = Math.max(0, pendingGoldGrams);
  const effectiveSilverDue = Math.max(0, pendingSilverGrams);

  // Physical metal surplus deposited for THIS bill (Received > Billed or explicit negative balance)
  const explicitGoldSurplus = Number(invoice.gold_balance_metal_weight || 0) < -0.001 ? Math.abs(Number(invoice.gold_balance_metal_weight)) : 0;
  const explicitSilverSurplus = Number(invoice.silver_balance_metal_weight || 0) < -0.001 ? Math.abs(Number(invoice.silver_balance_metal_weight)) : 0;
  const goldSurplus   = Math.max(0, (goldBilled?.fineReceived || 0) - (goldBilled?.fineBilled || 0), explicitGoldSurplus);
  const silverSurplus = Math.max(0, (silverBilled?.fineReceived || 0) - (silverBilled?.fineBilled || 0), explicitSilverSurplus);

  const hasGold   = metals.includes('Gold');
  const hasSilver = metals.includes('Silver');

  const formatDate = (dateString?: string) => {
    if (!dateString) return '';
    try { return new Date(dateString).toLocaleDateString('en-GB', { day: '2-digit', month: 'long', year: 'numeric' }).toUpperCase(); } catch { return dateString; }
  };

  // ─── Build Payment Received cards ──────────────────────────────────────────
  let paymentCards = '';

  // Cash paid card (only if cash was actually paid)
  if (cashPaid > 0) {
    paymentCards += `
      <div style="background: #ECFDF5; border: 1px solid #A7F3D0; border-radius: 8px; padding: 6px 8px; display: flex; align-items: center; gap: 8px;">
        <div style="width: 36px; height: 36px; border-radius: 50%; background: #10B981; color: white; display: flex; align-items: center; justify-content: center; flex-shrink: 0; box-shadow: 0 2px 4px rgba(16,185,129,0.2);">
          <svg viewBox="0 0 24 24" style="width: 20px; height: 20px; fill: white;"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>
        </div>
        <div>
          <div style="color: #065F46; font-size: 9px; font-weight: 700; letter-spacing: 1px;">CASH RECEIVED</div>
          <div style="color: #064E3B; font-size: 18px; font-weight: 800;">&#8377; ${formatCurrency(cashPaid)}</div>
          <div style="color: #065F46; font-size: 9px;">Thank you!</div>
        </div>
      </div>`;
  }

  // Metal received card (only if metal was deposited)
  if (metalValue > 0 && metalRecStr) {
    paymentCards += `
      <div style="background: #FFFBEB; border: 1px solid #FDE68A; border-radius: 8px; padding: 6px 8px; display: flex; align-items: center; gap: 8px;">
        <div style="width: 36px; height: 36px; border-radius: 50%; background: #F59E0B; color: white; display: flex; align-items: center; justify-content: center; flex-shrink: 0; box-shadow: 0 2px 4px rgba(245,158,11,0.2);">
          <svg viewBox="0 0 24 24" style="width: 18px; height: 18px; fill: currentColor;"><path d="M12 2L4 6v2h16V6l-8-4zm0 2.5l5.5 2.75h-11L12 4.5zM4 10v9h16v-9H4zm14 7H6v-5h12v5z"/></svg>
        </div>
        <div>
          <div style="color: #92400E; font-size: 9px; font-weight: 700; letter-spacing: 1px;">METAL RECEIVED</div>
          <div style="color: #78350F; font-size: 13px; font-weight: 800;">${metalRecStr}</div>
          <div style="color: #92400E; font-size: 9px;">Value: &#8377; ${formatCurrency(metalValue)}</div>
        </div>
      </div>`;
  }

  // If nothing paid at all, show a "No payment yet" info card
  if (cashPaid === 0 && metalValue === 0) {
    paymentCards += `
      <div style="background: #F8F9FA; border: 1px solid #CED4DA; border-radius: 8px; padding: 6px 8px; display: flex; align-items: center; gap: 8px;">
        <div style="width: 36px; height: 36px; border-radius: 50%; background: #6C757D; color: white; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
          <svg viewBox="0 0 24 24" style="width: 18px; height: 18px; fill: white;"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>
        </div>
        <div>
          <div style="color: #495057; font-size: 9px; font-weight: 700; letter-spacing: 1px;">PAYMENT PENDING</div>
          <div style="color: #212529; font-size: 13px; font-weight: 700;">No payment received yet</div>
        </div>
      </div>`;
  }

  // 🔹🔹🔹 Build Final Settlement card 🔹🔹🔹
  let settlementContent = '';

  const hasMetalToLedger = effectiveGoldDue > 0.001 || effectiveSilverDue > 0.001;
  const hasMetalSurplus  = goldSurplus > 0.001 || silverSurplus > 0.001;
  const isCashCleared    = balanceDue <= 0.01 && balanceDue >= -0.01;

  if (isCashCleared && !hasMetalToLedger && !hasMetalSurplus) {
    settlementContent = `
      <div style="background: #ECFDF5; border: 1px solid #A7F3D0; border-radius: 8px; padding: 6px 8px; display: flex; align-items: center; gap: 8px;">
        <div style="width: 24px; height: 24px; border-radius: 50%; background: #10B981; color: white; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
          <svg viewBox="0 0 24 24" style="width: 14px; height: 14px; fill: white;"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>
        </div>
        <div>
          <div style="color: #065F46; font-size: 9px; font-weight: 700; letter-spacing: 1px;">FINAL SETTLEMENT</div>
          <div style="color: #064E3B; font-size: 16px; font-weight: 800;">FULLY PAID &#10003;</div>
          <div style="color: #065F46; font-size: 8px; margin-top: 1px;">All dues cleared for this bill.</div>
        </div>
      </div>`;
  } else {
    let dueBlocks = '';
    if (balanceDue > 0.01) {
      dueBlocks += `
        <div style="background: #FFFFFF; border: 1px solid #FCA5A5; border-radius: 4px; padding: 3px 6px; display: flex; justify-content: space-between; align-items: center;">
          <span style="color: #7F1D1D; font-size: 9px; font-weight: 800;">CASH DUE:</span>
          <span style="color: #991B1B; font-size: 12px; font-weight: 900;">&#8377; ${formatCurrency(balanceDue)}</span>
        </div>`;
    }
    if (balanceDue < -0.01) {
      dueBlocks += `
        <div style="background: #ECFDF5; border: 1px solid #A7F3D0; border-radius: 4px; padding: 3px 6px; display: flex; justify-content: space-between; align-items: center;">
          <span style="color: #065F46; font-size: 9px; font-weight: 800;">REFUND:</span>
          <span style="color: #064E3B; font-size: 12px; font-weight: 900;">&#8377; ${formatCurrency(Math.abs(balanceDue))}</span>
        </div>`;
    }
    if (effectiveGoldDue > 0.001) {
      dueBlocks += `
        <div style="background: #FFFDF5; border: 1px solid #FDE68A; border-radius: 4px; padding: 3px 6px; display: flex; justify-content: space-between; align-items: center;">
          <span style="color: #92400E; font-size: 9px; font-weight: 800;">GOLD DUE:</span>
          <span style="color: #B45309; font-size: 12px; font-weight: 900;">+${effectiveGoldDue.toFixed(3)} gm</span>
        </div>`;
    }
    if (goldSurplus > 0.001) {
      dueBlocks += `
        <div style="background: #ECFDF5; border: 1px solid #A7F3D0; border-radius: 4px; padding: 3px 6px; display: flex; justify-content: space-between; align-items: center;">
          <span style="color: #065F46; font-size: 9px; font-weight: 800;">GOLD SURPLUS:</span>
          <span style="color: #047857; font-size: 12px; font-weight: 900;">-${goldSurplus.toFixed(3)} gm</span>
        </div>`;
    }
    if (effectiveSilverDue > 0.001) {
      dueBlocks += `
        <div style="background: #F9FAFB; border: 1px solid #D1D5DB; border-radius: 4px; padding: 3px 6px; display: flex; justify-content: space-between; align-items: center;">
          <span style="color: #374151; font-size: 9px; font-weight: 800;">SILVER DUE:</span>
          <span style="color: #1F2937; font-size: 12px; font-weight: 900;">+${effectiveSilverDue.toFixed(3)} gm</span>
        </div>`;
    }
    if (silverSurplus > 0.001) {
      dueBlocks += `
        <div style="background: #ECFDF5; border: 1px solid #A7F3D0; border-radius: 4px; padding: 3px 6px; display: flex; justify-content: space-between; align-items: center;">
          <span style="color: #065F46; font-size: 9px; font-weight: 800;">SILVER SURPLUS:</span>
          <span style="color: #047857; font-size: 12px; font-weight: 900;">-${silverSurplus.toFixed(3)} gm</span>
        </div>`;
    }

    const hasOnlyMetalDue = isCashCleared && hasMetalToLedger && !hasMetalSurplus;
    const hasOnlySurplus   = isCashCleared && !hasMetalToLedger && hasMetalSurplus;
    const headerBg        = hasOnlySurplus ? '#ECFDF5' : hasOnlyMetalDue ? '#FFFBEB' : '#FEF2F2';
    const headerBorder    = hasOnlySurplus ? '#A7F3D0' : hasOnlyMetalDue ? '#FDE68A' : '#FCA5A5';
    const headerTextColor = hasOnlySurplus ? '#065F46' : hasOnlyMetalDue ? '#92400E' : '#991B1B';
    const badgeText       = hasOnlySurplus ? 'SURPLUS' : (hasOnlyMetalDue || hasMetalToLedger) ? 'METAL DUE' : 'DUE';
    const badgeBg         = hasOnlySurplus ? '#D1FAE5' : (hasOnlyMetalDue || hasMetalToLedger) ? '#FEF3C7' : '#FEE2E2';
    const iconBg          = hasOnlySurplus ? '#10B981' : (hasOnlyMetalDue || hasMetalToLedger) ? '#F59E0B' : '#EF4444';
    const iconContent     = hasOnlySurplus ? '&#10003;' : '!';

    settlementContent = `
      <div style="background: ${headerBg}; border: 1.5px solid ${headerBorder}; border-radius: 8px; padding: 6px 8px; width: 100%; box-sizing: border-box;">
        <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px dashed ${headerBorder}; padding-bottom: 4px; margin-bottom: 4px;">
          <div style="display: flex; align-items: center; gap: 6px;">
            <div style="width: 18px; height: 18px; border-radius: 50%; background: ${iconBg}; color: white; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
              <span style="font-size: 10px; font-weight: bold;">${iconContent}</span>
            </div>
            <span style="color: ${headerTextColor}; font-family: 'Cinzel', serif; font-size: 10px; font-weight: 800; letter-spacing: 0.5px;">FINAL SETTLEMENT</span>
          </div>
          <span style="background: ${badgeBg}; color: ${headerTextColor}; font-size: 8px; font-weight: 700; padding: 1px 6px; border-radius: 3px;">${badgeText}</span>
        </div>
        <div style="display: flex; flex-direction: column; gap: 4px;">
          ${dueBlocks}
        </div>
        <div style="color: ${headerTextColor}; font-size: 7.5px; text-align: center; font-style: italic; margin-top: 4px;">This bill due only.</div>
      </div>`;
  }

  // ─── Payment Details table ──────────────────────────────────────────
  const paymentDetailsRows = `
    ${cashPaid > 0 ? `<tr><td style="width:45%;">Cash Paid</td><td style="text-align:right;width:5%;">:</td><td style="text-align:right;">&#8377; ${formatCurrency(cashPaid)}</td></tr>` : ''}
    ${metalValue > 0 ? `<tr><td>Metal Value Settled</td><td style="text-align:right;">:</td><td style="text-align:right;">&#8377; ${formatCurrency(metalValue)}</td></tr>` : ''}
    <tr><td>Date</td><td style="text-align:right;">:</td><td style="text-align:right;">${formatDate(invoice.invoice_date)}</td></tr>
    <tr><td>Mode</td><td style="text-align:right;">:</td><td style="text-align:right;">${cashPaid > 0 ? (invoice.payment_method || 'CASH') : (metalValue > 0 || ledgerSettledValue > 0) ? 'METAL' : '-'}</td></tr>
    ${invoice.transaction_id && invoice.transaction_id !== '-' ? `<tr><td>Transaction ID</td><td style="text-align:right;">:</td><td style="text-align:right;">${invoice.transaction_id}</td></tr>` : ''}
    ${metalRecStr ? `<tr><td>Metal Deposited</td><td style="text-align:right;">:</td><td style="text-align:right;">${metalRecStr}</td></tr>` : ''}
    ${effectiveGoldDue > 0.001 ? `<tr><td style="color:#B45309;font-weight:700;">Gold Balance Due</td><td style="text-align:right;">:</td><td style="text-align:right;color:#B45309;font-weight:700;">+${effectiveGoldDue.toFixed(3)} gm</td></tr>` : ''}
    ${goldSurplus > 0.001 ? `<tr><td style="color:#047857;font-weight:700;">Gold Surplus (Advance)</td><td style="text-align:right;">:</td><td style="text-align:right;color:#047857;font-weight:700;">-${goldSurplus.toFixed(3)} gm</td></tr>` : ''}
    ${effectiveSilverDue > 0.001 ? `<tr><td style="color:#1F2937;font-weight:700;">Silver Balance Due</td><td style="text-align:right;">:</td><td style="text-align:right;color:#1F2937;font-weight:700;">+${effectiveSilverDue.toFixed(3)} gm</td></tr>` : ''}
    ${silverSurplus > 0.001 ? `<tr><td style="color:#047857;font-weight:700;">Silver Surplus (Advance)</td><td style="text-align:right;">:</td><td style="text-align:right;color:#047857;font-weight:700;">-${silverSurplus.toFixed(3)} gm</td></tr>` : ''}
    ${balanceDue > 0.01 ? `<tr><td style="color:var(--red);font-weight:700;">Cash Due</td><td style="text-align:right;">:</td><td style="text-align:right;color:var(--red);font-weight:700;">&#8377; ${formatCurrency(balanceDue)}</td></tr>` : ''}
  `;

  return `
    <div style="display: flex; gap: 5px; margin-top: 4px;">

      ${invoice.bill_type !== 'Metal' ? `
      <!-- AMOUNT SUMMARY -->
      <div style="flex: 1; border: 1px solid var(--card-border); border-radius: 8px; background: var(--card-bg); display: flex; flex-direction: column; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
        <div style="padding: 5px 9px; flex: 1;">
          <div style="font-family: 'Cinzel', serif; font-size: 11px; font-weight: 800; color: #0F172A; display: flex; align-items: center; gap: 6px; margin-bottom: 4px; border-bottom: 1px solid var(--card-border); padding-bottom: 4px;">
            <div style="width: 18px; height: 18px; border-radius: 4px; background: #0F172A; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
              <svg viewBox="0 0 24 24" style="width: 11px; height: 11px; fill: #D4AF37;"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/></svg>
            </div>
            AMOUNT SUMMARY
          </div>
          <table style="width: 100%; font-size: 10px; font-weight: 600; color: #16213E; margin-bottom: 4px; line-height: 1.4; font-variant-numeric: tabular-nums;">
            ${hasGold && totals.totalGoldAmount > 0 ? `<tr><td>Total Gold Amount</td><td style="text-align:right;">:</td><td style="text-align:right;">&#8377; ${formatCurrency(totals.totalGoldAmount)}</td></tr>` : ''}
            ${hasSilver && totals.totalSilverAmount > 0 ? `<tr><td>Total Silver Amount</td><td style="text-align:right;">:</td><td style="text-align:right;">&#8377; ${formatCurrency(totals.totalSilverAmount)}</td></tr>` : ''}
            ${totals.totalMakingCharges > 0 ? `<tr><td>Making Charges</td><td style="text-align:right;">:</td><td style="text-align:right;">&#8377; ${formatCurrency(totals.totalMakingCharges)}</td></tr>` : ''}
            ${totals.totalOtherCharges > 0 ? `<tr><td>Other Charges</td><td style="text-align:right;">:</td><td style="text-align:right;">&#8377; ${formatCurrency(totals.totalOtherCharges)}</td></tr>` : ''}
            <tr><td colspan="3"><hr style="border: none; border-top: 1px dashed var(--card-border); margin: 4px 0;"></td></tr>
            <tr><td>Taxable Amount</td><td style="text-align:right;">:</td><td style="text-align:right;">&#8377; ${formatCurrency(taxableAmount)}</td></tr>
            <tr><td>GST</td><td style="text-align:right;">:</td><td style="text-align:right;">&#8377; ${formatCurrency(gstAmount)}</td></tr>
            ${oldItemsValue > 0 ? `
            <tr><td>Total Bill Amount</td><td style="text-align:right;">:</td><td style="text-align:right;">&#8377; ${formatCurrency(totalBillWithTax)}</td></tr>
            <tr><td>Old Items Deposited</td><td style="text-align:right;">:</td><td style="text-align:right; color: var(--red);">- &#8377; ${formatCurrency(oldItemsValue)}</td></tr>
            <tr><td colspan="3"><hr style="border: none; border-top: 1px dashed var(--card-border); margin: 3px 0;"></td></tr>
            <tr><td>Net Difference Due</td><td style="text-align:right;">:</td><td style="text-align:right; font-weight: 700;">&#8377; ${formatCurrency(netDueBeforeSettlement)}</td></tr>
            ` : ''}
            ${discountAmount > 0 ? `<tr><td>Discount</td><td style="text-align:right;">:</td><td style="text-align:right; color: var(--red);">- &#8377; ${formatCurrency(discountAmount)}</td></tr>` : ''}
            ${showRoundOff ? `<tr><td>Round Off</td><td style="text-align:right;">:</td><td style="text-align:right;">${calcRoundOff > 0 ? '+' : ''}&#8377; ${formatCurrency(calcRoundOff)}</td></tr>` : ''}
            ${cashPaid > 0 ? `<tr><td>Cash Paid</td><td style="text-align:right;">:</td><td style="text-align:right; color: #10B981;">- &#8377; ${formatCurrency(cashPaid)}</td></tr>` : ''}
            ${ledgerSettledValue > 0.01 ? `
            <tr>
              <td>Metal Deposited Value</td>
              <td style="text-align:right;">:</td>
              <td style="text-align:right; color: var(--red); font-weight: 700;">- &#8377; ${formatCurrency(ledgerSettledValue)}</td>
            </tr>
            ${(effectiveGoldDue > 0.001 || effectiveSilverDue > 0.001 || goldSurplus > 0.001 || silverSurplus > 0.001) ? `<tr><td colspan="3" style="text-align:right; font-size:8px; color:#7f8c8d;">(${[effectiveGoldDue > 0.001 ? `Gold: +${effectiveGoldDue.toFixed(3)}g Due` : (goldSurplus > 0.001 ? `Gold: -${goldSurplus.toFixed(3)}g Surplus` : ''), effectiveSilverDue > 0.001 ? `Silver: +${effectiveSilverDue.toFixed(3)}g Due` : (silverSurplus > 0.001 ? `Silver: -${silverSurplus.toFixed(3)}g Surplus` : '')].filter(Boolean).join(' | ')})</td></tr>` : (metalRecStr ? `<tr><td colspan="3" style="text-align:right; font-size:8px; color:#7f8c8d;">(${metalRecStr})</td></tr>` : '')}
            ` : ''}
          </table>
        </div>
        <div style="background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); border-top: 1.5px solid #D4AF37; border-radius: 0 0 8px 8px; padding: 5px; text-align: center; color: #D4AF37;">
          <div style="font-family: 'Cinzel', serif; font-size: 10px; font-weight: 700; margin-bottom: 2px; letter-spacing: 0.5px;">
            ${balanceDue > 0.01 ? 'CASH BALANCE DUE' : (hasMetalToLedger ? 'CASH BALANCE (PAID ✓)' : (hasMetalSurplus ? 'CASH BALANCE (PAID ✓)' : (cashPaid > 0 ? 'BALANCE (PAID ✓)' : 'PAYABLE AMOUNT')))}
          </div>
          <div style="font-size: 15px; font-weight: 800; color: #FFFFFF;">&#8377; ${formatCurrency(Math.max(0, balanceDue))}</div>
        </div>
      </div>
      ` : ''}

      <!-- PAYMENT STATUS COLUMN -->
      <div style="flex: 1; display: flex; flex-direction: column; gap: 5px;">
        ${paymentCards}
        ${settlementContent}
      </div>

      <!-- PAYMENT DETAILS + OTHER DETAILS -->
      <div style="flex: 1; display: flex; flex-direction: column; gap: 5px;">

        <!-- Payment Details -->
        <div style="border: 1px solid var(--card-border); border-radius: 8px; background: var(--card-bg); padding: 5px 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
          <div style="font-family: 'Cinzel', serif; font-size: 11px; font-weight: 800; color: #0F172A; display: flex; align-items: center; gap: 6px; margin-bottom: 4px; border-bottom: 1px solid var(--card-border); padding-bottom: 4px;">
            <div style="width: 18px; height: 18px; border-radius: 4px; background: #0F172A; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
              <svg viewBox="0 0 24 24" style="width: 11px; height: 11px; fill: #D4AF37;"><path d="M21 4H3c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h18c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 14H3V6h18v12zm-9-2h9v-2h-9v2z"/></svg>
            </div>
            PAYMENT DETAILS
          </div>
          <table style="width: 100%; font-size: 10px; font-weight: 600; color: #16213E; line-height: 1.4; font-variant-numeric: tabular-nums;">
            ${paymentDetailsRows}
          </table>
        </div>

        <!-- Other Details -->
        <div style="border: 1px solid var(--card-border); border-radius: 8px; background: var(--card-bg); padding: 5px 8px; flex: 1; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
          <div style="font-family: 'Cinzel', serif; font-size: 11px; font-weight: 800; color: #0F172A; display: flex; align-items: center; gap: 6px; margin-bottom: 4px; border-bottom: 1px solid var(--card-border); padding-bottom: 4px;">
            <div style="width: 18px; height: 18px; border-radius: 4px; background: #0F172A; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
              <svg viewBox="0 0 24 24" style="width: 11px; height: 11px; fill: #D4AF37;"><path d="M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.06-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.56-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.73 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.05.3-.09.63-.09.94s.02.64.06.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .43-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.49-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/></svg>
            </div>
            OTHER DETAILS
          </div>
          <table style="width: 100%; font-size: 10px; font-weight: 600; color: #16213E; line-height: 1.5;">
            <tr><td style="vertical-align:top;width:40%;">Hallmark</td><td style="text-align:right;vertical-align:top;width:10%;">:</td><td style="text-align:right;vertical-align:top;white-space:pre-wrap;">${settings.print_hallmark || 'BIS 916 (Gold)\nBIS 925 (Silver)'}</td></tr>
            <tr><td style="vertical-align:top;">Wastage</td><td style="text-align:right;vertical-align:top;">:</td><td style="text-align:right;vertical-align:top;white-space:pre-wrap;">${settings.print_wastage || '0.00%'}</td></tr>
            <tr><td style="vertical-align:top;">Making Charges</td><td style="text-align:right;vertical-align:top;">:</td><td style="text-align:right;vertical-align:top;white-space:pre-wrap;">${settings.print_making_charges || 'Gold &#8377; 1,000.00/gm\nSilver &#8377; 20.00/gm'}</td></tr>
            <tr><td style="vertical-align:top;">Remarks</td><td style="text-align:right;vertical-align:top;">:</td><td style="text-align:right;vertical-align:top;white-space:pre-wrap;">${settings.print_remarks || '-'}</td></tr>
          </table>
        </div>
      </div>
    </div>
  `;
};

