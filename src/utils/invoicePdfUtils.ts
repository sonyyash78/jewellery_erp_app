import * as premiumComponents from './premiumInvoiceHtml';

export const normalizeMetal = (metalType: string | undefined): string => {
  if (!metalType) return '';
  const m = metalType.toLowerCase();
  if (m.includes('gold')) return 'Gold';
  if (m.includes('silver')) return 'Silver';
  return metalType;
};

export const generateInvoiceHtml = (data: any): string => {
  const company = data.company || { name: 'SAIDEEP JEWELLERS', address: '123 Jewellery Lane, City, Country', phone: '+91 98765 43210', email: 'contact@saideep.com', gstin: '22AAAAA0000A1Z5' };
  const customer = data.customer || { name: 'Cash Customer', phone: '', address: '', email: '', gstin: '', pan: '' };
  const invoice = data.invoice || { invoice_number: 'INV-001', invoice_date: new Date().toISOString(), status: 'paid', subtotal: 0, tax_amount: 0, discount_amount: 0, grand_total: 0, amount_paid: 0, balance_due: 0 };
  const items = data.items || [];
  const oldItems = data.old_items || [];
  const totals = data.totals || {};
  const settings = {};

  const metalsArray: string[] = [];
  const goldBilled = { required: 0, fineReceived: 0, valueSettled: 0, balanceLedger: 0, price: invoice.gold_balance_metal_weight > 0 ? (totals.metal_received_value / totals.cash_received || 72500) : 72500 };
  const silverBilled = { required: 0, fineReceived: 0, valueSettled: 0, balanceLedger: 0, price: invoice.silver_balance_metal_weight > 0 ? 90000 : 90000 };

  items.forEach((item: any) => {
    const metal = normalizeMetal(item.metal_type || item.item_type);
    if (metal === 'Gold' && !metalsArray.includes('Gold')) metalsArray.push('Gold');
    if (metal === 'Silver' && !metalsArray.includes('Silver')) metalsArray.push('Silver');
    
    if (metal === 'Gold') goldBilled.required += (item.gold_calculation?.fine_weight || item.net_weight || 0);
    if (metal === 'Silver') silverBilled.required += (item.silver_calculation?.pure_weight || item.net_weight || 0);
  });

  oldItems.forEach((item: any) => {
    const metal = normalizeMetal(item.metal_type || item.item_type);
    if (metal === 'Gold') goldBilled.fineReceived += (item.gold_calculation?.fine_weight || item.net_weight || 0);
    if (metal === 'Silver') silverBilled.fineReceived += (item.silver_calculation?.pure_weight || item.net_weight || 0);
  });

  if (invoice.gold_balance_metal_weight > 0) goldBilled.balanceLedger = invoice.gold_balance_metal_weight;
  if (invoice.silver_balance_metal_weight > 0) silverBilled.balanceLedger = invoice.silver_balance_metal_weight;

  let finalHtml = `<!DOCTYPE html><html><head><meta charset="utf-8">`;
  finalHtml += `<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">`;
  finalHtml += premiumComponents.getCommonStyles();
  finalHtml += `</head><body><div class="pdf-container">`;
  finalHtml += premiumComponents.getPageWrapperStart();

  finalHtml += premiumComponents.renderHeader(company, invoice, '');
  finalHtml += premiumComponents.renderCardsRow(customer, '');

  finalHtml += premiumComponents.renderTableHeader();
  if (items.length === 0) {
    finalHtml += premiumComponents.renderTableRow({ item_name: 'No New Items', final_price: 0 }, 0, true);
  } else {
    items.forEach((item: any, index: number) => {
      const isGold = item.item_type === 'Gold' || normalizeMetal(item.metal_type) === 'Gold';
      finalHtml += premiumComponents.renderTableRow(item, index, isGold);
    });
  }

  const explicitOldItems = oldItems.filter((i: any) => i.item_name && !i.item_name.includes('Metal Given Now'));
  if (explicitOldItems.length > 0) {
    finalHtml += `<tr><td colspan="9" style="background: #FFFBEB; text-align: center; font-weight: 800; color: #92400E; padding: 6px; font-size: 10px; letter-spacing: 1px;">OLD ITEMS DEPOSITED</td></tr>`;
    explicitOldItems.forEach((item: any, index: number) => {
      const isGold = item.item_type === 'Gold' || normalizeMetal(item.metal_type) === 'Gold';
      finalHtml += premiumComponents.renderTableRow(item, index + items.length, isGold);
    });
  }
  finalHtml += premiumComponents.renderTableEnd();

  if (invoice.bill_type !== 'Cash') {
    const settlementHtml = premiumComponents.renderSettlements(metalsArray, goldBilled, silverBilled);
    if (settlementHtml) finalHtml += settlementHtml;
  }

  finalHtml += premiumComponents.renderBottomRow(metalsArray, invoice, totals, settings, goldBilled, silverBilled);
  finalHtml += premiumComponents.getPageWrapperEnd(company, 1, 1);
  finalHtml += `</div></body></html>`;

  return finalHtml;
};
