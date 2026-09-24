import * as premiumComponents from './premiumInvoiceHtml';

export const normalizeMetal = (metalType: string | undefined): string => {
  if (!metalType) return '';
  const m = metalType.toLowerCase();
  if (m.includes('gold')) return 'Gold';
  if (m.includes('silver')) return 'Silver';
  return metalType;
};

export const generateInvoiceHtml = (data: any): string => {
  const company = data.company || { name: 'SAIDEEP JEWELLERS', address: 'Takhatgarh khedawas', phone: '+91 98765 43210', email: 'contact@saideep.com', gstin: '22AAAAA0000A1Z5' };
  const customer = data.customer || { name: 'Walk-in Customer', phone: '', address: '', email: '', gstin: '', pan: '' };
  const invoice = data.invoice || { invoice_number: 'INV-001', invoice_date: new Date().toISOString(), status: 'paid', subtotal: 0, tax_amount: 0, discount_amount: 0, grand_total: 0, amount_paid: 0, balance_due: 0 };
  
  const allItems = data.items || [];
  const isOldOrDeposit = (item: any) => {
    const name = (item.item_name || '').toLowerCase();
    const cat = (item.category || '').toLowerCase();
    return /\b(old|deposit|metal given)\b/i.test(name) || cat === 'deposit' || cat === 'old';
  };

  const items = allItems.filter((i: any) => !isOldOrDeposit(i));
  const oldItems = [...(data.old_items || []), ...allItems.filter((i: any) => isOldOrDeposit(i))];

  const detectedMetals = new Set<string>();
  const goldBilled = { required: 0, fineBilled: 0, fineReceived: 0, valueSettled: 0, balanceLedger: 0, price: 0 };
  const silverBilled = { required: 0, fineBilled: 0, fineReceived: 0, valueSettled: 0, balanceLedger: 0, price: 0 };
  let totals = {
    totalGoldAmount: 0,
    totalSilverAmount: 0,
    totalMakingCharges: 0,
    totalOtherCharges: 0,
    taxableAmount: invoice.subtotal || 0,
    totalGst: invoice.tax_amount || 0,
    metal_received_value: invoice.metal_given_value || invoice.metal_received_value || 0,
    ...(data.totals || {})
  };
  const settings = data.settings || {};

  items.forEach((item: any) => {
    const isGold = item.item_type === 'Gold' || normalizeMetal(item.metal_type) === 'Gold';
    if (isGold) detectedMetals.add('Gold');
    else detectedMetals.add('Silver');

    const making = Number(item.making_charges || item.labour_charge || 0);
    const other = Number(item.other_charges || 0) + Number(item.hallmark_charges || item.hallmark_charge || 0);
    let val = Number(item.metal_value || item.final_price || item.taxable_amount || 0);

    const fineWt = Number(item.gold_calculation?.fine_weight || item.silver_calculation?.pure_weight || item.fine_weight || item.net_weight || 0);
    const appliedRate = Number(item.applied_rate || item.metal_rate || item.gold_calculation?.applied_rate || item.silver_calculation?.applied_rate || 0);

    if (isGold) {
      goldBilled.required += fineWt;
      goldBilled.fineBilled += fineWt;
      totals.totalGoldAmount += (val > 0 ? val : (fineWt * (appliedRate / 10)));
      if (!goldBilled.price && appliedRate > 0) goldBilled.price = appliedRate;
    } else {
      silverBilled.required += fineWt;
      silverBilled.fineBilled += fineWt;
      totals.totalSilverAmount += (val > 0 ? val : (fineWt * (appliedRate / 1000)));
      if (!silverBilled.price && appliedRate > 0) silverBilled.price = appliedRate;
    }
    totals.totalMakingCharges += making;
    totals.totalOtherCharges += other;
  });

  oldItems.forEach((item: any) => {
    const isGold = item.item_type === 'Gold' || normalizeMetal(item.metal_type) === 'Gold';
    const fineWt = Number(item.gold_calculation?.fine_weight || item.silver_calculation?.pure_weight || item.fine_weight || item.net_weight || 0);
    const appliedRate = Number(item.applied_rate || item.metal_rate || item.gold_calculation?.applied_rate || item.silver_calculation?.applied_rate || (isGold ? goldBilled.price : silverBilled.price) || (isGold ? 72500 : 90000));
    const itemVal = Number(item.final_price || item.calculated_value || item.metal_value || (fineWt * (appliedRate / (isGold ? 10 : 1000))) || 0);

    if (isGold) {
      goldBilled.fineReceived += fineWt;
      goldBilled.valueSettled += itemVal;
      if (!goldBilled.price && appliedRate > 0) goldBilled.price = appliedRate;
    } else {
      silverBilled.fineReceived += fineWt;
      silverBilled.valueSettled += itemVal;
      if (!silverBilled.price && appliedRate > 0) silverBilled.price = appliedRate;
    }
    totals.metal_received_value += itemVal;
  });

  if (invoice.gold_balance_metal_weight > 0) goldBilled.balanceLedger = Number(invoice.gold_balance_metal_weight);
  if (invoice.silver_balance_metal_weight > 0) silverBilled.balanceLedger = Number(invoice.silver_balance_metal_weight);

  const metalsArray = Array.from(detectedMetals);
  if (metalsArray.length === 0) {
    if (goldBilled.required > 0 || goldBilled.fineReceived > 0) metalsArray.push('Gold');
    if (silverBilled.required > 0 || silverBilled.fineReceived > 0) metalsArray.push('Silver');
  }

  const explicitOldItems = oldItems.filter((i: any) => i.item_name && !i.item_name.includes('Metal Given Now'));
  const totalItemCount = Math.max(1, items.length + explicitOldItems.length);

  let finalHtml = `<!DOCTYPE html><html><head><meta charset="utf-8">`;
  finalHtml += `<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">`;
  finalHtml += premiumComponents.getCommonStyles(totalItemCount);
  finalHtml += `</head><body><div class="pdf-container">`;
  finalHtml += premiumComponents.getPageWrapperStart();

  finalHtml += premiumComponents.renderHeader(company, invoice, '');
  finalHtml += premiumComponents.renderCardsRow(customer, '', settings);

  finalHtml += premiumComponents.renderTableHeader();
  if (items.length === 0) {
    finalHtml += premiumComponents.renderTableRow({ item_name: 'No New Items', final_price: 0 }, 0, true);
  } else {
    items.forEach((item: any, index: number) => {
      const isGold = item.item_type === 'Gold' || normalizeMetal(item.metal_type) === 'Gold';
      finalHtml += premiumComponents.renderTableRow(item, index, isGold);
    });
  }

  if (explicitOldItems.length > 0) {
    const isPurchase = (invoice.invoice_number || '').startsWith('PUR-') || data.type === 'purchase';
    const sectionTitle = isPurchase ? 'METAL GIVEN TO SUPPLIER' : 'OLD ITEMS DEPOSITED';
    finalHtml += `<tr><td colspan="9" style="background: #FFFBEB; text-align: center; font-weight: 800; color: #92400E; padding: 4px; font-size: 9px; letter-spacing: 1px;">${sectionTitle}</td></tr>`;
    explicitOldItems.forEach((item: any, index: number) => {
      const isGold = item.item_type === 'Gold' || normalizeMetal(item.metal_type) === 'Gold';
      finalHtml += premiumComponents.renderTableRow(item, index + items.length, isGold);
    });
  }
  finalHtml += premiumComponents.renderTableEnd();

  // Show metal settlement if there is metal requirement or metal given or hybrid/metal bill
  const hasMetalSettlement = goldBilled.fineReceived > 0 || silverBilled.fineReceived > 0 || goldBilled.balanceLedger > 0 || silverBilled.balanceLedger > 0 || invoice.bill_type !== 'Cash';
  if (hasMetalSettlement) {
    const settlementHtml = premiumComponents.renderSettlements(metalsArray, goldBilled, silverBilled);
    if (settlementHtml) finalHtml += settlementHtml;
  }

  finalHtml += premiumComponents.renderBottomRow(metalsArray, invoice, totals, settings, goldBilled, silverBilled, customer);
  finalHtml += premiumComponents.getPageWrapperEnd(company, 1, 1);
  finalHtml += `</div></body></html>`;

  return finalHtml;
};
