export const generateLedgerVoucherHtml = (
  partyType: 'Customer' | 'Supplier',
  party: any,
  bill: any,
  company?: any
): string => {
  const comp = company || {
    name: 'SAIDEEP JEWELLERS',
    address: 'Main Bazaar, Jewellery Market',
    phone: '+91 98765 43210',
    gstin: '22AAAAA0000A1Z5',
  };

  const partyName = (party?.first_name ? `${party.first_name} ${party.last_name || ''}`.trim() : (party?.name || 'Party')).toUpperCase();
  const partyPhone = party?.phone_number || party?.mobile || 'N/A';
  const partyGst = party?.gst_number || 'N/A';
  const partyPan = party?.aadhaar_pan || 'N/A';
  const partyAddress = party?.address || 'N/A';

  const dateFormatted = bill?.date ? new Date(bill.date).toLocaleString('en-IN') : new Date().toLocaleString('en-IN');
  const typeName = bill?.type || 'TRANSACTION';
  const voucherNo = bill?.bill_no || '-';
  const summary = bill?.summary || '-';

  const debit = Number(bill?.debit || 0);
  const credit = Number(bill?.credit || 0);
  const balance = Number(bill?.balance || 0);
  const goldChange = Number(bill?.gold_change || 0);
  const silverChange = Number(bill?.silver_change || 0);

  const isDebit = debit > 0;
  const isCredit = credit > 0;

  return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Voucher - ${voucherNo}</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background: #fff; color: #1f2937; padding: 24px; line-height: 1.5; }
    .voucher-card { border: 2px solid #d4af37; border-radius: 12px; padding: 24px; max-width: 700px; margin: 0 auto; background: #fff; }
    .header { text-align: center; border-bottom: 2px solid #f3f4f6; padding-bottom: 16px; margin-bottom: 20px; }
    .brand-name { font-size: 24px; font-weight: 800; color: #0a0a0a; letter-spacing: 1px; }
    .brand-sub { font-size: 12px; color: #6b7280; margin-top: 4px; }
    .voucher-title { margin-top: 12px; display: inline-block; background: #0a0a0a; color: #d4af37; font-size: 13px; font-weight: 700; padding: 4px 16px; border-radius: 20px; letter-spacing: 0.5px; }
    
    .meta-grid { display: flex; justify-content: space-between; margin-bottom: 20px; font-size: 13px; }
    .meta-col { flex: 1; }
    .meta-col.right { text-align: right; }
    .meta-label { color: #6b7280; font-size: 11px; font-weight: 600; text-transform: uppercase; }
    .meta-val { color: #111827; font-weight: 700; margin-top: 2px; }

    .party-box { background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 14px; margin-bottom: 20px; font-size: 13px; }
    .party-title { font-size: 11px; font-weight: 700; color: #d4af37; text-transform: uppercase; margin-bottom: 6px; letter-spacing: 0.5px; }
    .party-name { font-size: 16px; font-weight: 700; color: #111827; margin-bottom: 4px; }
    .party-details { color: #4b5563; font-size: 12px; line-height: 1.4; }

    .table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
    .table th { background: #f3f4f6; padding: 10px 12px; font-size: 11px; text-transform: uppercase; color: #374151; font-weight: 700; border-bottom: 2px solid #e5e7eb; text-align: left; }
    .table th.right { text-align: right; }
    .table td { padding: 12px; border-bottom: 1px solid #e5e7eb; font-size: 13px; vertical-align: middle; }
    .table td.right { text-align: right; font-weight: 600; }
    
    .badge { display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; background: #e0f2fe; color: #0284c7; }
    .debit-val { color: #dc2626; font-weight: 700; }
    .credit-val { color: #16a34a; font-weight: 700; }
    
    .metal-section { background: #fefce8; border: 1px solid #fef08a; border-radius: 8px; padding: 12px; margin-bottom: 20px; display: flex; justify-content: space-around; font-size: 13px; }
    .metal-box { text-align: center; }
    .metal-lbl { font-size: 11px; color: #854d0e; font-weight: 600; text-transform: uppercase; }
    .metal-num { font-size: 15px; font-weight: 800; color: #713f12; margin-top: 2px; }

    .total-box { background: #111827; color: #fff; border-radius: 8px; padding: 16px; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: center; }
    .total-label { font-size: 13px; color: #9ca3af; text-transform: uppercase; font-weight: 600; }
    .total-val { font-size: 20px; font-weight: 800; color: #d4af37; }

    .signatures { display: flex; justify-content: space-between; margin-top: 40px; padding-top: 20px; border-top: 1px dashed #d1d5db; font-size: 12px; color: #6b7280; }
    .sig-block { text-align: center; width: 180px; }
    .sig-line { border-top: 1px solid #9ca3af; margin-top: 36px; padding-top: 4px; font-weight: 600; }
  </style>
</head>
<body>
  <div class="voucher-card">
    <div class="header">
      <div class="brand-name">${comp.name}</div>
      <div class="brand-sub">${comp.address} | Phone: ${comp.phone} | GSTIN: ${comp.gstin}</div>
      <div class="voucher-title">${typeName} VOUCHER</div>
    </div>

    <div class="meta-grid">
      <div class="meta-col">
        <div class="meta-label">Voucher / Ref No</div>
        <div class="meta-val">${voucherNo}</div>
      </div>
      <div class="meta-col right">
        <div class="meta-label">Date & Time</div>
        <div class="meta-val">${dateFormatted}</div>
      </div>
    </div>

    <div class="party-box">
      <div class="party-title">${partyType.toUpperCase()} DETAILS</div>
      <div class="party-name">${partyName}</div>
      <div class="party-details">
        Contact: ${partyPhone} | GSTIN: ${partyGst} | PAN: ${partyPan}<br>
        Address: ${partyAddress}
      </div>
    </div>

    <table class="table">
      <thead>
        <tr>
          <th>Description</th>
          <th>Type</th>
          <th class="right">Debit (₹)</th>
          <th class="right">Credit (₹)</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>${summary}</td>
          <td><span class="badge">${typeName}</span></td>
          <td class="right debit-val">${isDebit ? `₹ ${debit.toLocaleString('en-IN', { minimumFractionDigits: 2 })}` : '-'}</td>
          <td class="right credit-val">${isCredit ? `₹ ${credit.toLocaleString('en-IN', { minimumFractionDigits: 2 })}` : '-'}</td>
        </tr>
      </tbody>
    </table>

    ${(goldChange !== 0 || silverChange !== 0) ? `
    <div class="metal-section">
      ${goldChange !== 0 ? `
      <div class="metal-box">
        <div class="metal-lbl">Gold Movement</div>
        <div class="metal-num">${goldChange > 0 ? '+' : ''}${goldChange.toFixed(3)} g</div>
      </div>
      ` : ''}
      ${silverChange !== 0 ? `
      <div class="metal-box">
        <div class="metal-lbl">Silver Movement</div>
        <div class="metal-num">${silverChange > 0 ? '+' : ''}${silverChange.toFixed(3)} g</div>
      </div>
      ` : ''}
    </div>
    ` : ''}

    <div class="total-box">
      <div>
        <div class="total-label">Closing Running Balance</div>
        <div style="font-size: 11px; color: #9ca3af; margin-top: 2px;">After this transaction</div>
      </div>
      <div class="total-val">₹ ${Math.abs(balance).toLocaleString('en-IN', { minimumFractionDigits: 2 })} ${balance > 0 ? '(Dr)' : (balance < 0 ? '(Cr)' : '')}</div>
    </div>

    <div class="signatures">
      <div class="sig-block">
        <div class="sig-line">Receiver's Signature</div>
      </div>
      <div class="sig-block">
        <div class="sig-line">Authorized Signatory</div>
      </div>
    </div>
  </div>
</body>
</html>
  `;
};

export const generateLedgerStatementHtml = (
  partyType: 'Customer' | 'Supplier',
  party: any,
  data: any,
  company?: any
): string => {
  const comp = company || {
    name: 'SAIDEEP JEWELLERS',
    address: 'Main Bazaar, Jewellery Market',
    phone: '+91 98765 43210',
    gstin: '22AAAAA0000A1Z5',
  };

  const partyName = (party?.first_name ? `${party.first_name} ${party.last_name || ''}`.trim() : (party?.name || 'Party')).toUpperCase();
  const partyPhone = party?.phone_number || party?.mobile || 'N/A';
  const partyGst = party?.gst_number || 'N/A';
  const partyPan = party?.aadhaar_pan || 'N/A';
  const partyAddress = party?.address || 'N/A';

  const outstanding = Number(data?.outstanding_balance || 0);
  const fineGold = Number(data?.fine_gold_balance || 0);
  const fineSilver = Number(data?.fine_silver_balance || 0);
  const goldRate = Number(data?.current_gold_rate || 7000);
  const silverRate = Number(data?.current_silver_rate || 85);
  const bills: any[] = data?.bills || [];

  const rowsHtml = bills.map((b: any, index: number) => {
    const d = b.date ? new Date(b.date).toLocaleDateString('en-IN') : '-';
    const deb = Number(b.debit || 0);
    const cred = Number(b.credit || 0);
    const bal = Number(b.balance || 0);
    const gChg = Number(b.gold_change || 0);
    const sChg = Number(b.silver_change || 0);

    return `
      <tr>
        <td style="text-align: center; color: #6b7280;">${index + 1}</td>
        <td>${d}</td>
        <td><span class="badge ${b.type?.toLowerCase()}">${b.type || '-'}</span></td>
        <td style="font-weight: 600;">${b.bill_no || '-'}</td>
        <td style="max-width: 200px;">${b.summary || '-'}</td>
        <td style="text-align: right; color: #b45309; font-weight: 600;">${gChg !== 0 ? (gChg > 0 ? '+' : '') + gChg.toFixed(3) : '-'}</td>
        <td style="text-align: right; color: #4b5563; font-weight: 600;">${sChg !== 0 ? (sChg > 0 ? '+' : '') + sChg.toFixed(3) : '-'}</td>
        <td style="text-align: right; color: #dc2626; font-weight: 600;">${deb > 0 ? deb.toLocaleString('en-IN', { minimumFractionDigits: 2 }) : '-'}</td>
        <td style="text-align: right; color: #16a34a; font-weight: 600;">${cred > 0 ? cred.toLocaleString('en-IN', { minimumFractionDigits: 2 }) : '-'}</td>
        <td style="text-align: right; font-weight: 700; color: #111827;">${Math.abs(bal).toLocaleString('en-IN', { minimumFractionDigits: 2 })} ${bal > 0 ? 'Dr' : (bal < 0 ? 'Cr' : '')}</td>
      </tr>
    `;
  }).join('');

  return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>${partyType} Ledger Statement - ${partyName}</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background: #fff; color: #1f2937; padding: 20px; line-height: 1.4; font-size: 12px; }
    .statement-wrapper { max-width: 1000px; margin: 0 auto; }
    
    .header { display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 2px solid #d4af37; padding-bottom: 16px; margin-bottom: 16px; }
    .brand-title { font-size: 24px; font-weight: 800; color: #0a0a0a; letter-spacing: 0.5px; }
    .brand-sub { font-size: 11px; color: #4b5563; margin-top: 3px; }
    .statement-tag { text-align: right; }
    .statement-title { font-size: 18px; font-weight: 800; color: #d4af37; text-transform: uppercase; }
    .statement-date { font-size: 11px; color: #6b7280; margin-top: 2px; }

    .party-and-summary { display: flex; gap: 16px; margin-bottom: 16px; }
    .party-card { flex: 1.2; background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px; }
    .card-title { font-size: 10px; font-weight: 700; color: #d4af37; text-transform: uppercase; margin-bottom: 4px; letter-spacing: 0.5px; }
    .party-name { font-size: 15px; font-weight: 700; color: #111827; }
    .party-meta { color: #4b5563; font-size: 11px; margin-top: 4px; line-height: 1.4; }

    .summary-card { flex: 1.5; background: #0a0a0a; color: #fff; border-radius: 8px; padding: 12px; display: flex; justify-content: space-between; align-items: center; }
    .sum-col { text-align: center; flex: 1; border-right: 1px solid #262626; padding: 0 8px; }
    .sum-col:last-child { border-right: none; }
    .sum-lbl { font-size: 9px; color: #9ca3af; text-transform: uppercase; font-weight: 700; }
    .sum-val { font-size: 14px; font-weight: 800; margin-top: 2px; }
    .sum-sub { font-size: 8px; color: #6b7280; margin-top: 1px; }

    .table { width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 11px; }
    .table th { background: #f3f4f6; color: #374151; padding: 8px 6px; text-transform: uppercase; font-weight: 700; border: 1px solid #e5e7eb; font-size: 10px; }
    .table td { padding: 8px 6px; border: 1px solid #e5e7eb; vertical-align: middle; }
    
    .badge { display: inline-block; padding: 2px 6px; border-radius: 4px; font-size: 9px; font-weight: 700; }
    .badge.invoice { background: #eff6ff; color: #2563eb; }
    .badge.exchange { background: #faf5ff; color: #9333ea; }
    .badge.settlement, .badge.payment, .badge.receipt { background: #f0fdf4; color: #16a34a; }

    .footer { display: flex; justify-content: space-between; align-items: flex-end; margin-top: 30px; padding-top: 16px; border-top: 1px solid #e5e7eb; font-size: 11px; color: #6b7280; }
  </style>
</head>
<body>
  <div class="statement-wrapper">
    <div class="header">
      <div>
        <div class="brand-title">${comp.name}</div>
        <div class="brand-sub">${comp.address} | Phone: ${comp.phone} | GSTIN: ${comp.gstin}</div>
      </div>
      <div class="statement-tag">
        <div class="statement-title">${partyType} Account Statement</div>
        <div class="statement-date">Generated: ${new Date().toLocaleString('en-IN')}</div>
      </div>
    </div>

    <div class="party-and-summary">
      <div class="party-card">
        <div class="card-title">${partyType.toUpperCase()} INFO</div>
        <div class="party-name">${partyName}</div>
        <div class="party-meta">
          Mobile: ${partyPhone} | GSTIN: ${partyGst} | PAN: ${partyPan}<br>
          Address: ${partyAddress}
        </div>
      </div>

      <div class="summary-card">
        <div class="sum-col">
          <div class="sum-lbl">Fine Gold</div>
          <div class="sum-val" style="color: #fbbf24;">${fineGold.toFixed(3)} g</div>
          <div class="sum-sub">@ ₹${goldRate}/g</div>
        </div>
        <div class="sum-col">
          <div class="sum-lbl">Fine Silver</div>
          <div class="sum-val" style="color: #e5e7eb;">${fineSilver.toFixed(3)} g</div>
          <div class="sum-sub">@ ₹${silverRate}/g</div>
        </div>
        <div class="sum-col">
          <div class="sum-lbl">Net Outstanding</div>
          <div class="sum-val" style="color: ${outstanding > 0 ? '#ef4444' : '#10b981'};">
            ₹ ${Math.abs(outstanding).toLocaleString('en-IN', { minimumFractionDigits: 2 })} ${outstanding > 0 ? '(Dr)' : (outstanding < 0 ? '(Cr)' : '')}
          </div>
        </div>
      </div>
    </div>

    <table class="table">
      <thead>
        <tr>
          <th style="width: 30px;">#</th>
          <th>Date</th>
          <th>Type</th>
          <th>Ref No</th>
          <th>Details / Bill</th>
          <th style="text-align: right;">Gold (g)</th>
          <th style="text-align: right;">Silver (g)</th>
          <th style="text-align: right;">Debit (₹)</th>
          <th style="text-align: right;">Credit (₹)</th>
          <th style="text-align: right;">Balance (₹)</th>
        </tr>
      </thead>
      <tbody>
        ${rowsHtml.length > 0 ? rowsHtml : '<tr><td colspan="10" style="text-align: center; padding: 20px; color: #9ca3af;">No transaction records found</td></tr>'}
      </tbody>
    </table>

    <div class="footer">
      <div>This is a computer-generated statement and does not require a physical signature.</div>
      <div style="text-align: right; font-weight: 600;">For ${comp.name}</div>
    </div>
  </div>
</body>
</html>
  `;
};
