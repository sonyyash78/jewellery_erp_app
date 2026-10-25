import QRCode from 'qrcode';
import { BACKEND_BASE_URL } from '../config/api';

export interface InvoicePDFData {
  type?: string;
  invoice: any;
  customer: any;
  items: Array<any>;
  old_items?: Array<any>;
  company: any;
  settings?: any;
  totals: any;
}

export const normalizeMetal = (metalType: string | undefined): string => {
  if (!metalType) return '';
  const m = metalType.toLowerCase();
  if (m.includes('gold')) return 'Gold';
  if (m.includes('silver')) return 'Silver';
  return metalType;
};

export const generateInvoiceHtml = async (data: InvoicePDFData): Promise<string> => {
  try {
    // @ts-ignore
    const premiumComponents = await import('./premiumInvoiceHtml');
    
    // Fallback data mapping if missing
    let settings: any = { ...(data.company || {}), ...(data.settings || {}) };
    
    // Fetch live user profile if needed
    let defaultStoreName = 'JEWELLERY STORE';
    try {
      const { useAuthStore } = await import('../store/authStore');
      const u = useAuthStore.getState().user;
      if (u?.store_name) defaultStoreName = u.store_name;
    } catch {}

    const company = { 
      name: settings.business_name || settings.store_name || settings.name || data.company?.name || defaultStoreName, 
      address: settings.address || settings.store_address || data.company?.address || '', 
      phone: settings.phone || settings.store_phone || data.company?.phone || '', 
      email: settings.email || settings.store_email || data.company?.email || '', 
      gstin: settings.gstin || settings.store_gstin || data.company?.gstin || '',
      tagline: settings.tagline || data.company?.tagline || 'TIMELESS BEAUTY. TRUSTED FOREVER.',
      ...settings
    };
    const customer = data.customer || { name: 'Cash Customer', phone: '', address: '', email: '', gstin: '', pan: '' };
    const invoice = data.invoice || { invoice_number: 'INV-001', invoice_date: new Date().toISOString(), status: 'paid', subtotal: 0, tax_amount: 0, discount_amount: 0, grand_total: 0, amount_paid: 0, balance_due: 0 };
    const allItems = data.items || [];
    const isOldOrDeposit = (item: any) => {
      const name = (item.item_name || '').toLowerCase();
      // Ensure we only match whole words so "gold" doesn't falsely trigger "old"
      return /\b(old|deposit|metal given)\b/i.test(name);
    };

    const items = allItems.filter((i: any) => !isOldOrDeposit(i));
    const oldItems = [...(data.old_items || []), ...allItems.filter((i: any) => isOldOrDeposit(i))];

    try {
      const { axiosClient } = await import('../api/axiosClient');
      const res = await axiosClient.get('/settings/');
      Object.assign(settings, res.data || {});
      if (settings.business_name || settings.store_name) company.name = settings.business_name || settings.store_name;
      if (settings.address || settings.store_address) company.address = settings.address || settings.store_address;
      if (settings.phone || settings.store_phone) company.phone = settings.phone || settings.store_phone;
      if (settings.email || settings.store_email) company.email = settings.email || settings.store_email;
      if (settings.gstin || settings.store_gstin) company.gstin = settings.gstin || settings.store_gstin;
      if (settings.logo_url) company.logo_url = settings.logo_url;
      if (settings.tagline) company.tagline = settings.tagline;
    } catch (e) {
      console.warn('Failed to fetch settings', e);
    }

    let qrDataUrl = '';
    try {
      const upiId = settings?.upi_id || '';
      const upiName = settings?.upi_name || settings?.business_name || company?.name || defaultStoreName;
      const isCustomAmount = settings?.qr_amount_type === 'custom';
      
      // Calculate true payable / due amount (e.g. 4038.55 for EXC-16, not 138656.75)
      let payableAmount = 0;
      if (invoice.balance_due != null && Number(invoice.balance_due) > 0) {
        payableAmount = Number(invoice.balance_due);
      } else if (invoice.balance_amount != null && Number(invoice.balance_amount) > 0) {
        payableAmount = Number(invoice.balance_amount);
      } else if (invoice.difference_amount != null && Number(invoice.difference_amount) > 0) {
        payableAmount = Number(invoice.difference_amount);
      } else {
        const grand = Number(invoice.grand_total || 0);
        const settled = Number(invoice.cash_received || invoice.amount_paid || 0) + Number(invoice.metal_received_value || invoice.total_old_value || 0);
        payableAmount = Math.max(0, grand - settled);
        if (payableAmount === 0 && grand > 0 && settled === 0) {
          payableAmount = grand;
        }
      }

      if (upiId) {
        let upiDeepLink = `upi://pay?pa=${encodeURIComponent(upiId)}&pn=${encodeURIComponent(upiName)}`;
        if (!isCustomAmount && payableAmount > 0) {
          upiDeepLink += `&am=${payableAmount.toFixed(2)}`;
        }
        upiDeepLink += `&cu=INR&tn=${encodeURIComponent(invoice.invoice_number || 'Tax Invoice')}`;
        qrDataUrl = await QRCode.toDataURL(upiDeepLink, { width: 120, margin: 0 });
      }
    } catch (e) {
      console.warn('Failed to generate QR', e);
    }

    let logoDataUrl = '';
    const logoPath = settings?.logo_url || data.company?.logo_url;
    if (logoPath) {
      try {
        const backendBase = BACKEND_BASE_URL;
        const logoUrl = logoPath.startsWith('http') ? logoPath : `${backendBase}${logoPath.startsWith('/') ? '' : '/'}${logoPath}`;
        const response = await fetch(`${logoUrl}?v=` + Date.now(), { cache: 'no-store' });
        if (response.ok) {
          const blob = await response.blob();
          logoDataUrl = await new Promise((resolve) => {
            const reader = new FileReader();
            reader.onloadend = () => resolve(reader.result as string);
            reader.readAsDataURL(blob);
          });
        }
      } catch (e) {
        console.warn('Failed to fetch logo', e);
      }
    }
    if (!logoDataUrl) {
      logoDataUrl = data.company?.logo_data_url || '';
    }

    // Calculations
    let goldBilled = { fineBilled: 0, fineReceived: 0, billedValue: 0, receivedValue: 0, appliedRate: 0, metalValueSettled: 0, balanceMetalWeight: 0 };
    let silverBilled = { fineBilled: 0, fineReceived: 0, billedValue: 0, receivedValue: 0, appliedRate: 0, metalValueSettled: 0, balanceMetalWeight: 0 };
    let totals = { totalGoldAmount: 0, totalSilverAmount: 0, totalMakingCharges: 0, totalOtherCharges: 0 };
    const detectedMetals = new Set<string>();

    const getItemFineWeight = (item: any): number => {
      const directFine = Number(
        item.gold_calculation?.fine_weight ||
        item.silver_calculation?.pure_weight ||
        item.silver_calculation?.fine_weight ||
        item.fine_weight ||
        item.pure_weight ||
        0
      );
      if (directFine > 0) return directFine;

      const netWt = Number(item.net_weight || item.gross_weight || item.gold_calculation?.net_weight || item.silver_calculation?.net_weight || 0);
      const purity = Number(
        item.touch_purity ||
        item.tanch_percentage ||
        item.touch ||
        item.purity ||
        item.gold_calculation?.touch_purity ||
        item.silver_calculation?.tanch_percentage ||
        0
      );
      if (netWt > 0 && purity > 0) {
        return Math.round(netWt * purity * 10) / 1000;
      }
      return netWt;
    };

    items.forEach((item) => {
      const isGold = item.item_type === 'Gold' || normalizeMetal(item.metal_type) === 'Gold';
      if (isGold) detectedMetals.add('Gold');
      else detectedMetals.add('Silver');

      const making = item.making_charges || 0;
      const other = (item.other_charges || 0) + (item.hallmark_charges || 0);
      let val = item.metal_value || item.final_price || 0;
      
      // Fallback for previously corrupted silver data where metal_value was inflated by 1000x
      if (val > (item.final_price || 0) * 10 && item.final_price > 0) {
        val = item.final_price - making - other + (item.discount || 0);
      }

      const fineWt = getItemFineWeight(item);

      if (isGold) {
        goldBilled.fineBilled += fineWt;
        goldBilled.billedValue += val;
        totals.totalGoldAmount += val + making + other;
        // Capture rate from first gold item
        if (!goldBilled.appliedRate) goldBilled.appliedRate = item.applied_rate || item.gold_calculation?.applied_rate || 0;
      } else {
        silverBilled.fineBilled += fineWt;
        silverBilled.billedValue += val;
        totals.totalSilverAmount += val + making + other;
        // Silver rate is stored per kg
        if (!silverBilled.appliedRate) silverBilled.appliedRate = item.applied_rate || item.silver_calculation?.applied_rate || 0;
      }
      totals.totalMakingCharges += making;
      totals.totalOtherCharges += other;
    });

    oldItems.forEach((item) => {
      const isGold = item.item_type === 'Gold' || normalizeMetal(item.metal_type) === 'Gold';
      const fine = getItemFineWeight(item);
      let itemVal = Number(item.metal_value || item.gold_calculation?.total_gold_value || item.silver_calculation?.total_silver_value || item.total_gold_value || item.total_silver_value || item.final_price || 0);
      
      if (isGold) {
        if (!goldBilled.appliedRate) goldBilled.appliedRate = item.applied_rate || item.metal_rate || item.gold_calculation?.applied_rate || 0;
        if (goldBilled.appliedRate > 0 && goldBilled.appliedRate < 15000) goldBilled.appliedRate = goldBilled.appliedRate * 10;
        if (itemVal === 0 && fine > 0 && goldBilled.appliedRate > 0) {
          itemVal = fine * (goldBilled.appliedRate / 10);
        }
        goldBilled.fineReceived += fine;
        goldBilled.receivedValue += itemVal;
        goldBilled.metalValueSettled += itemVal;
      } else {
        if (!silverBilled.appliedRate) silverBilled.appliedRate = item.applied_rate || item.metal_rate || item.silver_calculation?.applied_rate || 0;
        if (silverBilled.appliedRate > 0 && silverBilled.appliedRate < 1000) silverBilled.appliedRate = silverBilled.appliedRate * 1000;
        if (itemVal === 0 && fine > 0 && silverBilled.appliedRate > 0) {
          itemVal = fine * (silverBilled.appliedRate / 1000);
        }
        silverBilled.fineReceived += fine;
        silverBilled.receivedValue += itemVal;
        silverBilled.metalValueSettled += itemVal;
      }
    });

    if (goldBilled.appliedRate > 0 && goldBilled.appliedRate < 15000) goldBilled.appliedRate = goldBilled.appliedRate * 10;
    if (silverBilled.appliedRate > 0 && silverBilled.appliedRate < 1000) silverBilled.appliedRate = silverBilled.appliedRate * 1000;

    const metalsArray = Array.from(detectedMetals);
    if (oldItems.length > 0 && metalsArray.length === 0) {
       // if only depositing old items
       if (goldBilled.fineReceived > 0) metalsArray.push('Gold');
       if (silverBilled.fineReceived > 0) metalsArray.push('Silver');
    }


    // DOM Measurement Engine (Isolated to prevent CSS bleed and ensure accurate font/style measurements)
    const measureIframe = document.createElement('iframe');
    measureIframe.style.position = 'fixed';
    measureIframe.style.top = '0';
    measureIframe.style.left = '-9999px';
    measureIframe.style.width = '210mm';
    measureIframe.style.visibility = 'hidden';
    document.body.appendChild(measureIframe);

    const idoc = measureIframe.contentWindow?.document;
    if (idoc) {
      idoc.open();
      idoc.write(`
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
          ${premiumComponents.getCommonStyles()}
        </head>
        <body>
          <div id="page-measure" class="invoice-wrapper">
             <div class="content">
                <div id="footer-measure" style="text-align: center; margin-top: auto; padding-bottom: 60px; font-family: 'Cinzel', serif; font-size: 11px; font-weight: 700; color: var(--gold); letter-spacing: 1px;">
                  Purity You Trust, Elegance You Deserve.
                  <div style="font-size: 9px; margin-top: 4px; font-family: 'Inter', sans-serif;">Page 1 of 1</div>
                </div>
             </div>
          </div>
          <div id="measure-box" class="invoice-wrapper" style="height: auto; min-height: 0; max-height: none; padding: 0; border: none; overflow: visible;"></div>
        </body>
        </html>
      `);
      idoc.close();
    }





    // We build the full final HTML structure inside <div class="pdf-container">
    let finalHtml = `<!DOCTYPE html><html><head><meta charset="utf-8">`;
    finalHtml += `<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">`;
    finalHtml += premiumComponents.getCommonStyles();
    
    // PERMANENT 1-PAGE FIX: Auto-scale script injected into the print window
    finalHtml += `<script>
      window.onload = function() {
        const wrapper = document.querySelector('.invoice-wrapper');
        const content = document.querySelector('.content');
        if (wrapper && content) {
          const maxH = wrapper.clientHeight; // 297mm
          const contentH = content.scrollHeight;
          if (contentH > maxH) {
             const scale = maxH / contentH;
             content.style.transformOrigin = 'top center';
             content.style.transform = 'scale(' + scale + ')';
             content.style.height = contentH + 'px';
          }
        }
      };
    </script>`;
    
    finalHtml += `</head><body><div class="pdf-container">`;

    // Always use exactly one page
    finalHtml += premiumComponents.getPageWrapperStart(company);

    // Header & Info
    finalHtml += premiumComponents.renderHeader(company, invoice, logoDataUrl) + premiumComponents.renderCardsRow(customer, qrDataUrl, settings, invoice);

    // Items
    finalHtml += premiumComponents.renderTableHeader();
        if (items.length === 0) {
        finalHtml += premiumComponents.renderTableRow({ item_name: 'No New Items', final_price: 0 }, 0, true);
      } else {
        items.forEach((item, index) => {
          const isGold = item.item_type === 'Gold' || normalizeMetal(item.metal_type) === 'Gold';
          finalHtml += premiumComponents.renderTableRow(item, index, isGold);
        });
      }

      // Add Old Items if they exist
      const explicitOldItems = oldItems.filter((i: any) => i.item_name && !i.item_name.includes('Metal Given Now'));
      if (explicitOldItems.length > 0) {
        const isPurchase = (invoice.invoice_number || '').startsWith('PUR-') || data.type === 'purchase';
        const sectionTitle = isPurchase ? 'PURCHASED METAL' : 'OLD ITEMS DEPOSITED';
        finalHtml += `<tr><td colspan="9" style="background: #FFFBEB; text-align: center; font-weight: 800; color: #92400E; padding: 6px; font-size: 10px; letter-spacing: 1px;">${sectionTitle}</td></tr>`;
        explicitOldItems.forEach((item, index) => {
          const isGold = item.item_type === 'Gold' || normalizeMetal(item.metal_type) === 'Gold';
          finalHtml += premiumComponents.renderTableRow(item, index + items.length, isGold);
        });
      }

      finalHtml += premiumComponents.renderTableEnd();
    
    // Settlement (Show for Hybrid, Metal, or if any counter metal was deposited / trade-in was received, or balance metal is owed to ledger)
    const hasBalanceMetal = (Number(invoice.gold_balance_metal_weight || 0) > 0.001) || (Number(invoice.silver_balance_metal_weight || 0) > 0.001) || (Number(invoice.balance_metal_weight || 0) > 0.001);
    const hasCounterMetal = (goldBilled.fineReceived > 0.001) || (silverBilled.fineReceived > 0.001) || (explicitOldItems.length > 0);
    const isMetalBillType = (invoice.bill_type && invoice.bill_type !== 'Cash') || (invoice.settlement_type === 'Metal');
    const hasMetalInBill = (goldBilled.fineBilled > 0.001) || (silverBilled.fineBilled > 0.001);
    const hasMetalActivity = isMetalBillType || hasCounterMetal || hasBalanceMetal || hasMetalInBill;
    if (hasMetalActivity) {
      const settlementHtml = premiumComponents.renderSettlements(metalsArray, goldBilled, silverBilled, invoice);
      if (settlementHtml) finalHtml += settlementHtml;
    }

    // Bottom Summary
    finalHtml += premiumComponents.renderBottomRow(metalsArray, invoice, totals, settings, goldBilled, silverBilled);

    // Footer
    finalHtml += premiumComponents.getPageWrapperEnd(company, 1, 1);
    
    finalHtml += `</div></body></html>`;

    // Cleanup measurement div (we don't even use it anymore because we force 1 page!)
    document.body.removeChild(measureIframe);

    // Inject an auto-scale script directly into the HTML so native browser Print Previews
    // automatically shrink the content to fit perfectly within the 296.5mm A4 boundary.
    const scriptHtml = `
      <script>
        setTimeout(function() {
          var wrapper = document.querySelector('.invoice-wrapper');
          var content = document.querySelector('.content');
          if (wrapper && content) {
            var maxH = wrapper.clientHeight || 1120;
            var contentH = content.scrollHeight;
            if (contentH > maxH) {
               var scale = Math.max(0.1, maxH / contentH);
               content.style.transform = 'scale(' + scale + ')';
               content.style.transformOrigin = 'top center';
               content.style.height = contentH + 'px';
            }
          }
        }, 100);
      </script>
    `;

    return finalHtml + scriptHtml;
  } catch (error) {
    console.error('Error generating HTML:', error);
    throw error;
  }
};

export const generateInvoicePDF = async (data: InvoicePDFData) => {
  try {
    // @ts-ignore
    const html2pdf = (await import('html2pdf.js')).default;
    const finalRenderedHtml = await generateInvoiceHtml(data);
    
    // We MUST render this into the DOM first, because passing a string to html2pdf
    // breaks absolute positioned elements (like the watermark) across pages.
    const renderContainer = document.createElement('div');
    renderContainer.style.position = 'fixed';
    renderContainer.style.top = '0';
    renderContainer.style.left = '-3000px'; // Safely offscreen, avoids browser paint culling that happens at -99999px
    renderContainer.style.width = '210mm'; 
    renderContainer.innerHTML = finalRenderedHtml;
    document.body.appendChild(renderContainer);

    // Wait for fonts and layouts to resolve in the DOM
    await new Promise(resolve => setTimeout(resolve, 800));

    const targetElement = renderContainer.querySelector('.pdf-container') as HTMLElement;
    const invoiceWrapper = renderContainer.querySelector('.invoice-wrapper') as HTMLElement;
    const content = renderContainer.querySelector('.content') as HTMLElement;
    
    if (invoiceWrapper && content) {
      const maxH = invoiceWrapper.clientHeight || 1122; 
      const contentH = content.scrollHeight || 1;
      
      if (contentH > maxH) {
         // Scale down to fit one page precisely
         const scale = Math.max(0.1, maxH / contentH);
         content.style.transform = `scale(${scale})`;
         content.style.transformOrigin = 'top center';
         // Adjust height so the wrapper knows the scaled content fits
         content.style.height = `${contentH}px`;
      }
    }
    
    const opt: any = {
      margin:       0,
      filename:     `${data.invoice?.invoice_number || 'INVOICE'}.pdf`,
      image:        { type: 'jpeg', quality: 1.0 },
      html2canvas:  { scale: 3, useCORS: true, letterRendering: true, windowWidth: 794 }, // Explicit window width ensures correct scaling
      jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' }
    };

    await html2pdf().set(opt).from(targetElement).save();

    // Cleanup
    document.body.removeChild(renderContainer);
  } catch (error) {
    console.error('Error generating PDF:', error);
    throw error;
  }
};

export const printInvoiceDirect = async (data: InvoicePDFData): Promise<void> => {
  try {
    const finalRenderedHtml = await generateInvoiceHtml(data);

    // Create an invisible iframe for native print triggering
    const printFrame = document.createElement('iframe');
    printFrame.style.position = 'fixed';
    printFrame.style.top = '0';
    printFrame.style.left = '-9999px';
    printFrame.style.width = '210mm';
    printFrame.style.height = '297mm';
    printFrame.style.border = 'none';
    printFrame.style.visibility = 'hidden';
    document.body.appendChild(printFrame);

    const frameDoc = printFrame.contentWindow?.document;
    if (!frameDoc) {
      throw new Error('Failed to access print iframe document');
    }

    frameDoc.open();
    frameDoc.write(finalRenderedHtml);
    frameDoc.close();

    // Allow time for images, barcode, QR, fonts to render inside the iframe
    await new Promise(resolve => setTimeout(resolve, 600));

    try {
      printFrame.contentWindow?.focus();
      printFrame.contentWindow?.print();
    } catch (printErr) {
      console.warn('iframe print failed, falling back to popup window', printErr);
      const printWin = window.open('', '_blank');
      if (printWin) {
        printWin.document.open();
        printWin.document.write(finalRenderedHtml);
        printWin.document.close();
        printWin.focus();
        setTimeout(() => {
          try {
            printWin.print();
          } catch {}
        }, 500);
      }
    } finally {
      // Remove iframe after print dialog completes or closes
      setTimeout(() => {
        if (document.body.contains(printFrame)) {
          document.body.removeChild(printFrame);
        }
      }, 60000);
    }
  } catch (error) {
    console.error('Error in printInvoiceDirect, falling back to PDF download:', error);
    await generateInvoicePDF(data);
  }
};

export const generatePaymentReceiptPDF = async (row: any, entity: any) => {
  try {
    let settings: any = {};
    let storeName = 'JEWELLERY STORE';
    try {
      const { axiosClient } = await import('../api/axiosClient');
      const res = await axiosClient.get('/settings/');
      settings = res.data || {};
    } catch {}

    try {
      const { useAuthStore } = await import('../store/authStore');
      const u = useAuthStore.getState().user;
      if (u?.store_name) storeName = u.store_name;
    } catch {}

    const companyName = settings.business_name || settings.store_name || storeName;
    const companyAddress = settings.address || settings.store_address || '';
    const companyPhone = settings.phone || settings.store_phone || '';
    const companyGstin = settings.gstin || settings.store_gstin || '';

    // Fetch store logo if available
    let logoDataUrl = '';
    const logoPath = settings?.logo_url;
    if (logoPath) {
      try {
        const backendBase = BACKEND_BASE_URL;
        const logoUrl = logoPath.startsWith('http') ? logoPath : `${backendBase}${logoPath.startsWith('/') ? '' : '/'}${logoPath}`;
        const response = await fetch(`${logoUrl}?v=` + Date.now(), { cache: 'no-store' });
        if (response.ok) {
          const blob = await response.blob();
          logoDataUrl = await new Promise((resolve) => {
            const reader = new FileReader();
            reader.onloadend = () => resolve(reader.result as string);
            reader.readAsDataURL(blob);
          });
        }
      } catch (e) {
        console.warn('Failed to load logo for receipt', e);
      }
    }

    const partyName = entity?.name || `${entity?.first_name || ''} ${entity?.last_name || ''}`.trim() || 'Valued Party';
    const partyPhone = entity?.phone_number || entity?.mobile || '';
    const partyAddress = entity?.address ? `${entity.address}${entity.city ? ', ' + entity.city : ''}` : (entity?.city || '');
    const voucherNo = row.bill_no && row.bill_no !== '-' ? row.bill_no : `REC-${row.id || Date.now().toString().slice(-6)}`;
    const formattedDate = row.date ? new Date(row.date).toLocaleString('en-IN') : new Date().toLocaleString('en-IN');

    const amount = Number(row.credit || 0) > 0 ? Number(row.credit) : Number(row.debit || 0);
    const isCredit = Number(row.credit || 0) > 0;
    const goldChange = Number(row.gold_change || 0);
    const silverChange = Number(row.silver_change || 0);

    // Final Remaining Ledger Balances after this transaction
    const closingCashBalance = row.balance != null ? Number(row.balance) : Number(entity?.outstanding_balance || 0);
    const closingGoldBalance = row.gold_balance != null ? Number(row.gold_balance) : Number(entity?.fine_gold_balance || 0);
    const closingSilverBalance = row.silver_balance != null ? Number(row.silver_balance) : Number(entity?.fine_silver_balance || 0);

    const receiptHtml = `
      <div class="receipt-pdf-page" style="width: 210mm; min-height: 297mm; padding: 20mm; box-sizing: border-box; background: #ffffff; color: #1e293b; font-family: 'Inter', -apple-system, sans-serif;">
        <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
        
        <div style="border: 2px solid #b45309; border-radius: 12px; padding: 24px; position: relative; background: #ffffff;">
          
          <!-- Watermark -->
          <div style="position: absolute; top: 48%; left: 50%; transform: translate(-50%, -50%) rotate(-25deg); font-family: 'Cinzel', serif; font-size: 72px; font-weight: 800; color: rgba(212, 175, 55, 0.05); pointer-events: none; text-transform: uppercase; white-space: nowrap;">
            SETTLEMENT VOUCHER
          </div>

          <!-- Header -->
          <div style="text-align: center; border-bottom: 2px dashed #cbd5e1; padding-bottom: 16px; margin-bottom: 18px;">
            ${logoDataUrl ? `
              <div style="margin-bottom: 8px;">
                <img src="${logoDataUrl}" style="height: 48px; max-width: 140px; object-fit: contain;" />
              </div>` : ''}
            <div style="font-family: 'Cinzel', serif; font-size: 22px; font-weight: 800; color: #996515; letter-spacing: 1px;">
              ${companyName.toUpperCase()}
            </div>
            ${companyAddress ? `<div style="font-size: 11px; color: #64748b; margin-top: 3px;">${companyAddress}</div>` : ''}
            <div style="font-size: 11px; color: #64748b; margin-top: 2px;">
              ${companyPhone ? `<span>Ph: ${companyPhone}</span>` : ''}
              ${companyGstin ? `<span style="margin-left: 12px;">GSTIN: ${companyGstin}</span>` : ''}
            </div>
            <div style="display: inline-block; background: #fef3c7; border: 1px solid #f59e0b; color: #92400e; font-size: 11px; font-weight: 800; letter-spacing: 1px; padding: 3px 14px; border-radius: 20px; margin-top: 10px; text-transform: uppercase;">
              Payment &amp; Settlement Receipt
            </div>
          </div>

          <!-- Metadata -->
          <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 16px; line-height: 1.6;">
            <div>
              <div style="color: #64748b; font-size: 10px; text-transform: uppercase; font-weight: 700;">Party Details:</div>
              <div style="font-weight: 700; font-size: 14px; color: #0f172a;">${partyName}</div>
              ${partyPhone ? `<div>Contact: ${partyPhone}</div>` : ''}
              ${partyAddress ? `<div>Address: ${partyAddress}</div>` : ''}
            </div>
            <div style="text-align: right;">
              <div><strong style="color: #64748b;">Receipt No:</strong> <span style="font-family: monospace; font-weight: 700; color: #0f172a;">${voucherNo}</span></div>
              <div><strong style="color: #64748b;">Date:</strong> ${formattedDate}</div>
              <div><strong style="color: #64748b;">Type:</strong> <span style="background: #e0e7ff; color: #3730a3; padding: 1px 6px; border-radius: 4px; font-size: 10px; font-weight: 700;">${row.type || 'PAYMENT'}</span></div>
            </div>
          </div>

          <!-- Settlement Summary Card -->
          <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; margin-bottom: 18px;">
            <div style="font-size: 11px; font-weight: 700; color: #475569; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px;">Transaction Particulars</div>
            <div style="font-size: 13px; color: #1e293b; margin-bottom: 12px; font-style: italic; font-weight: 500;">
              ${row.summary && row.summary !== '-' ? row.summary : 'Ledger settlement voucher / transaction acknowledged'}
            </div>
            
            <table style="width: 100%; border-collapse: collapse; font-size: 12px;">
              <thead>
                <tr style="background: #f1f5f9; border-bottom: 2px solid #cbd5e1;">
                  <th style="text-align: left; padding: 8px 10px; font-weight: 700; color: #334155;">Particulars</th>
                  <th style="text-align: right; padding: 8px 10px; font-weight: 700; color: #334155;">Effect / Weight</th>
                </tr>
              </thead>
              <tbody style="line-height: 1.8;">
                ${amount > 0 ? `
                  <tr style="border-bottom: 1px solid #f1f5f9;">
                    <td style="padding: 8px 10px;">Cash / Bank Amount (${isCredit ? 'Received / Credit' : 'Paid / Debit'})</td>
                    <td style="text-align: right; padding: 8px 10px; font-weight: 800; color: ${isCredit ? '#15803d' : '#b91c1c'}; font-family: monospace; font-size: 14px;">
                      &#8377; ${amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                    </td>
                  </tr>` : (goldChange !== 0 || silverChange !== 0 ? `
                  <tr style="border-bottom: 1px solid #f1f5f9;">
                    <td style="padding: 8px 10px;">Cash / Bank Transaction</td>
                    <td style="text-align: right; padding: 8px 10px; font-weight: 700; color: #64748b; font-family: monospace;">
                      &#8377; 0.00 (Metal Settlement)
                    </td>
                  </tr>` : '')}
                ${goldChange !== 0 ? `
                  <tr style="border-bottom: 1px solid #f1f5f9;">
                    <td style="padding: 8px 10px;">Fine Gold Weight (24K Pure)</td>
                    <td style="text-align: right; padding: 8px 10px; font-weight: 800; color: #b45309; font-family: monospace; font-size: 13px;">
                      ${goldChange > 0 ? '+' : ''}${goldChange.toFixed(3)} gm <span style="font-size: 10px; font-weight: 600; color: #64748b;">(${goldChange < 0 ? 'Received by Store / Deposit' : 'Issued by Store / Debit'})</span>
                    </td>
                  </tr>` : ''}
                ${silverChange !== 0 ? `
                  <tr style="border-bottom: 1px solid #f1f5f9;">
                    <td style="padding: 8px 10px;">Fine Silver Weight (Pure)</td>
                    <td style="text-align: right; padding: 8px 10px; font-weight: 800; color: #475569; font-family: monospace; font-size: 13px;">
                      ${silverChange > 0 ? '+' : ''}${silverChange.toFixed(3)} gm <span style="font-size: 10px; font-weight: 600; color: #64748b;">(${silverChange < 0 ? 'Received by Store / Deposit' : 'Issued by Store / Debit'})</span>
                    </td>
                  </tr>` : ''}

                <!-- Final Remaining Ledger Balances -->
                <tr style="background: #f1f5f9; border-top: 2px solid #cbd5e1;">
                  <td colspan="2" style="padding: 8px 10px; font-weight: 800; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; color: #334155; background: #e2e8f0;">
                    Final Remaining Ledger Balances (After Transaction)
                  </td>
                </tr>
                <tr style="background: #fefce8; border-top: 1px solid #fde047;">
                  <td style="padding: 8px 10px; color: #713f12; font-weight: 700; font-size: 12px;">Remaining Cash / Amount Balance</td>
                  <td style="text-align: right; padding: 8px 10px; color: #713f12; font-weight: 800; font-family: monospace; font-size: 13px;">
                    &#8377; ${Math.abs(closingCashBalance).toLocaleString('en-IN', { minimumFractionDigits: 2 })} ${closingCashBalance > 0 ? '(Dr - Due)' : (closingCashBalance < 0 ? '(Cr - Advance)' : '(Settled - Nil)')}
                  </td>
                </tr>
                <tr style="background: #fffbeb; border-top: 1px solid #fef3c7;">
                  <td style="padding: 8px 10px; color: #92400e; font-weight: 700; font-size: 12px;">Remaining Pure Gold Balance (24K)</td>
                  <td style="text-align: right; padding: 8px 10px; color: #b45309; font-weight: 800; font-family: monospace; font-size: 13px;">
                    ${Math.abs(closingGoldBalance).toFixed(3)} gm ${closingGoldBalance > 0 ? '(Dr - Due)' : (closingGoldBalance < 0 ? '(Cr - Advance)' : '(Nil)')}
                  </td>
                </tr>
                <tr style="background: #f8fafc; border-top: 1px solid #e2e8f0;">
                  <td style="padding: 8px 10px; color: #475569; font-weight: 700; font-size: 12px;">Remaining Pure Silver Balance (99.9%)</td>
                  <td style="text-align: right; padding: 8px 10px; color: #475569; font-weight: 800; font-family: monospace; font-size: 13px;">
                    ${Math.abs(closingSilverBalance).toFixed(3)} gm ${closingSilverBalance > 0 ? '(Dr - Due)' : (closingSilverBalance < 0 ? '(Cr - Advance)' : '(Nil)')}
                  </td>
                </tr>
              </tbody>
            </table>

            <!-- Visual 3-Stat Metric Cards for Closing Balances -->
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin-top: 16px;">
              <div style="background: #fefce8; border: 1px solid #fde047; border-radius: 8px; padding: 10px; text-align: center;">
                <div style="font-size: 9px; font-weight: 700; color: #854d0e; text-transform: uppercase; letter-spacing: 0.5px;">Remaining Amount</div>
                <div style="font-size: 14px; font-weight: 800; color: #713f12; font-family: monospace; margin-top: 4px;">
                  &#8377; ${Math.abs(closingCashBalance).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </div>
                <div style="font-size: 9px; font-weight: 600; color: #a16207; margin-top: 2px;">
                  ${closingCashBalance > 0 ? 'Dr (Payable)' : (closingCashBalance < 0 ? 'Cr (Advance)' : 'Settled (Nil)')}
                </div>
              </div>

              <div style="background: #fffbeb; border: 1px solid #fef3c7; border-radius: 8px; padding: 10px; text-align: center;">
                <div style="font-size: 9px; font-weight: 700; color: #92400e; text-transform: uppercase; letter-spacing: 0.5px;">Remaining Gold</div>
                <div style="font-size: 14px; font-weight: 800; color: #b45309; font-family: monospace; margin-top: 4px;">
                  ${Math.abs(closingGoldBalance).toFixed(3)} gm
                </div>
                <div style="font-size: 9px; font-weight: 600; color: #b45309; margin-top: 2px;">
                  ${closingGoldBalance > 0 ? 'Dr (Due to Store)' : (closingGoldBalance < 0 ? 'Cr (Advance)' : 'Nil')}
                </div>
              </div>

              <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px; text-align: center;">
                <div style="font-size: 9px; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.5px;">Remaining Silver</div>
                <div style="font-size: 14px; font-weight: 800; color: #334155; font-family: monospace; margin-top: 4px;">
                  ${Math.abs(closingSilverBalance).toFixed(3)} gm
                </div>
                <div style="font-size: 9px; font-weight: 600; color: #64748b; margin-top: 2px;">
                  ${closingSilverBalance > 0 ? 'Dr (Due to Store)' : (closingSilverBalance < 0 ? 'Cr (Advance)' : 'Nil')}
                </div>
              </div>
            </div>
          </div>

          <!-- Signatures -->
          <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-top: 40px; padding-top: 20px;">
            <div style="text-align: center; border-top: 1px solid #94a3b8; width: 170px; padding-top: 6px; font-size: 11px; color: #64748b; font-weight: 600;">
              Party Signature
            </div>
            <div style="text-align: center; border-top: 1px solid #94a3b8; width: 190px; padding-top: 6px; font-size: 11px; color: #64748b; font-weight: 600;">
              For ${companyName}
            </div>
          </div>
          
          <div style="text-align: center; font-size: 9px; color: #94a3b8; margin-top: 20px; font-style: italic;">
            This is a computer-generated transaction settlement voucher.
          </div>
        </div>
      </div>
    `;

    // Render container - placed offscreen safely at -3000px with explicit A4 width
    const renderContainer = document.createElement('div');
    renderContainer.style.position = 'fixed';
    renderContainer.style.top = '0';
    renderContainer.style.left = '-3000px';
    renderContainer.style.width = '210mm';
    renderContainer.style.background = '#ffffff';
    renderContainer.innerHTML = receiptHtml;
    document.body.appendChild(renderContainer);

    // Wait for web fonts and layout engine to paint
    await new Promise(resolve => setTimeout(resolve, 800));

    const targetElement = renderContainer.querySelector('.receipt-pdf-page') as HTMLElement;

    // @ts-ignore
    const html2pdf = (await import('html2pdf.js')).default;
    const opt: any = {
      margin:       0,
      filename:     `Receipt_${voucherNo}.pdf`,
      image:        { type: 'jpeg', quality: 1.0 },
      html2canvas:  { scale: 2, useCORS: true, letterRendering: true, windowWidth: 794 },
      jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' }
    };

    await html2pdf().set(opt).from(targetElement || renderContainer).save();
    document.body.removeChild(renderContainer);
  } catch (err) {
    console.error('Failed to generate receipt PDF:', err);
    throw err;
  }
};

export interface StatementPDFData {
  entity: any;
  isSupplier?: boolean;
  bills: any[];
  dateRangeLabel?: string;
  balances?: {
    outstanding_balance?: number;
    fine_gold_balance?: number;
    fine_silver_balance?: number;
    current_gold_rate?: number;
    current_silver_rate?: number;
  };
}

export const generateLedgerStatementPDF = async (data: StatementPDFData) => {
  const { entity, isSupplier = false, bills = [], dateRangeLabel = 'All Transactions', balances = {} } = data;
  try {
    let settings: any = {};
    let storeName = 'JEWELLERY STORE';
    try {
      const { axiosClient } = await import('../api/axiosClient');
      const res = await axiosClient.get('/settings/');
      settings = res.data || {};
    } catch {}

    try {
      const { useAuthStore } = await import('../store/authStore');
      const u = useAuthStore.getState().user;
      if (u?.store_name) storeName = u.store_name;
    } catch {}

    const companyName = settings.business_name || settings.store_name || storeName;
    const companyAddress = settings.address || settings.store_address || '';
    const companyPhone = settings.phone || settings.store_phone || '';
    const companyGstin = settings.gstin || settings.store_gstin || '';

    let logoDataUrl = '';
    const logoPath = settings?.logo_url;
    if (logoPath) {
      try {
        const backendBase = BACKEND_BASE_URL;
        const logoUrl = logoPath.startsWith('http') ? logoPath : `${backendBase}${logoPath.startsWith('/') ? '' : '/'}${logoPath}`;
        const response = await fetch(`${logoUrl}?v=` + Date.now(), { cache: 'no-store' });
        if (response.ok) {
          const blob = await response.blob();
          logoDataUrl = await new Promise((resolve) => {
            const reader = new FileReader();
            reader.onloadend = () => resolve(reader.result as string);
            reader.readAsDataURL(blob);
          });
        }
      } catch (e) {
        console.warn('Failed to load logo for statement', e);
      }
    }

    const partyName = entity?.name || `${entity?.first_name || ''} ${entity?.last_name || ''}`.trim() || (isSupplier ? 'Supplier' : 'Customer');
    const partyPhone = entity?.phone_number || entity?.mobile || '';
    const partyAddress = entity?.address ? `${entity.address}${entity.city ? ', ' + entity.city : ''}` : (entity?.city || '');
    const partyGstin = entity?.gst_number || '';
    const partyPan = entity?.pan_card || entity?.aadhaar_pan || '';

    const closingCash = Number(balances.outstanding_balance ?? entity?.outstanding_balance ?? 0);
    const closingGold = Number(balances.fine_gold_balance ?? entity?.fine_gold_balance ?? 0);
    const closingSilver = Number(balances.fine_silver_balance ?? entity?.fine_silver_balance ?? 0);

    const totalDebit = bills.reduce((acc, r) => acc + (Number(r.debit) || 0), 0);
    const totalCredit = bills.reduce((acc, r) => acc + (Number(r.credit) || 0), 0);
    const totalGoldChange = bills.reduce((acc, r) => acc + (Number(r.gold_change) || 0), 0);
    const totalSilverChange = bills.reduce((acc, r) => acc + (Number(r.silver_change) || 0), 0);

    const printDate = new Date().toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' });

    const rowsHtml = bills.map((b: any, index: number) => {
      const dStr = b.date ? new Date(b.date).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }) : '-';
      const deb = Number(b.debit || 0);
      const cred = Number(b.credit || 0);
      const gChg = Number(b.gold_change || 0);
      const sChg = Number(b.silver_change || 0);
      const bal = Number(b.balance || 0);
      const bg = index % 2 === 0 ? '#ffffff' : '#f8fafc';

      return `
        <tr style="background: ${bg}; border-bottom: 1px solid #e2e8f0; font-size: 10px; page-break-inside: avoid;">
          <td style="padding: 6px 8px; color: #475569; font-weight: 500;">${dStr}</td>
          <td style="padding: 6px 8px; font-weight: 700; color: #1e293b;"><span style="background: #e2e8f0; padding: 1.5px 5px; border-radius: 3px; font-size: 9px;">${b.type || 'TXN'}</span></td>
          <td style="padding: 6px 8px; font-family: monospace; font-weight: 700; color: #0284c7;">${b.bill_no && b.bill_no !== '-' ? b.bill_no : '-'}</td>
          <td style="padding: 6px 8px; color: #334155; max-width: 160px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${b.summary || '-'}</td>
          <td style="padding: 6px 8px; text-align: right; font-family: monospace; font-weight: 700; color: ${gChg > 0 ? '#b45309' : gChg < 0 ? '#15803d' : '#94a3b8'};">
            ${gChg !== 0 ? `${gChg > 0 ? '+' : ''}${gChg.toFixed(3)}g` : '-'}
          </td>
          <td style="padding: 6px 8px; text-align: right; font-family: monospace; font-weight: 700; color: ${sChg !== 0 ? '#475569' : '#94a3b8'};">
            ${sChg !== 0 ? `${sChg > 0 ? '+' : ''}${sChg.toFixed(3)}g` : '-'}
          </td>
          <td style="padding: 6px 8px; text-align: right; font-family: monospace; font-weight: 700; color: ${deb > 0 ? '#dc2626' : '#94a3b8'};">
            ${deb > 0 ? `&#8377;${deb.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : '-'}
          </td>
          <td style="padding: 6px 8px; text-align: right; font-family: monospace; font-weight: 700; color: ${cred > 0 ? '#16a34a' : '#94a3b8'};">
            ${cred > 0 ? `&#8377;${cred.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : '-'}
          </td>
          <td style="padding: 6px 8px; text-align: right; font-family: monospace; font-weight: 800; color: #0f172a;">
            &#8377;${Math.abs(bal).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ${bal > 0 ? (isSupplier ? 'Cr' : 'Dr') : bal < 0 ? (isSupplier ? 'Dr' : 'Cr') : ''}
          </td>
        </tr>
      `;
    }).join('');

    const statementHtml = `
      <div class="statement-pdf-page" style="width: 210mm; min-height: 297mm; padding: 12mm 15mm; box-sizing: border-box; background: #ffffff; color: #1e293b; font-family: 'Inter', -apple-system, sans-serif;">
        <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
        
        <!-- Header -->
        <div style="border-bottom: 2px solid #b45309; padding-bottom: 12px; margin-bottom: 14px; display: flex; justify-content: space-between; align-items: flex-start;">
          <div>
            ${logoDataUrl ? `<img src="${logoDataUrl}" style="height: 42px; max-width: 130px; object-fit: contain; margin-bottom: 4px;" />` : ''}
            <div style="font-family: 'Cinzel', serif; font-size: 20px; font-weight: 800; color: #996515; letter-spacing: 0.8px;">
              ${companyName.toUpperCase()}
            </div>
            ${companyAddress ? `<div style="font-size: 10px; color: #64748b; margin-top: 2px;">${companyAddress}</div>` : ''}
            <div style="font-size: 10px; color: #64748b; margin-top: 2px;">
              ${companyPhone ? `<span>Ph: ${companyPhone}</span>` : ''}
              ${companyGstin ? `<span style="margin-left: 10px;">GSTIN: ${companyGstin}</span>` : ''}
            </div>
          </div>
          <div style="text-align: right;">
            <div style="background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%); border: 1.5px solid #D4AF37; color: #78350F; font-size: 12px; font-weight: 800; letter-spacing: 1px; padding: 4px 14px; border-radius: 6px; display: inline-block; text-transform: uppercase;">
              ${isSupplier ? 'SUPPLIER LEDGER STATEMENT' : 'CUSTOMER ACCOUNT STATEMENT'}
            </div>
            <div style="font-size: 10px; color: #475569; margin-top: 6px; font-weight: 600;">
              Period: <span style="color: #0f172a; font-weight: 700;">${dateRangeLabel}</span>
            </div>
            <div style="font-size: 9px; color: #94a3b8; margin-top: 2px;">Generated on: ${printDate}</div>
          </div>
        </div>

        <!-- Party Information Box -->
        <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 8px; padding: 10px 14px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center; font-size: 11px;">
          <div>
            <div style="color: #64748b; font-size: 9px; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px;">Account Name:</div>
            <div style="font-size: 15px; font-weight: 800; color: #0f172a; margin-top: 1px;">${partyName}</div>
            ${partyAddress ? `<div style="color: #475569; font-size: 10px; margin-top: 2px;">${partyAddress}</div>` : ''}
          </div>
          <div style="text-align: right; line-height: 1.5;">
            ${partyPhone ? `<div><strong style="color: #64748b;">Phone:</strong> <span style="font-weight: 700;">${partyPhone}</span></div>` : ''}
            ${partyGstin ? `<div><strong style="color: #64748b;">GSTIN:</strong> <span style="font-family: monospace; font-weight: 700;">${partyGstin}</span></div>` : ''}
            ${partyPan ? `<div><strong style="color: #64748b;">PAN/Aadhar:</strong> <span style="font-family: monospace; font-weight: 700;">${partyPan}</span></div>` : ''}
          </div>
        </div>

        <!-- Key Financial Summary Cards -->
        <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; margin-bottom: 14px;">
          <div style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 6px; padding: 6px 8px; text-align: center;">
            <div style="font-size: 8.5px; font-weight: 700; color: #64748b; text-transform: uppercase;">Total Debit</div>
            <div style="font-size: 12px; font-weight: 800; color: #dc2626; font-family: monospace; margin-top: 2px;">
              &#8377;${totalDebit.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </div>
          </div>
          <div style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 6px; padding: 6px 8px; text-align: center;">
            <div style="font-size: 8.5px; font-weight: 700; color: #64748b; text-transform: uppercase;">Total Credit</div>
            <div style="font-size: 12px; font-weight: 800; color: #16a34a; font-family: monospace; margin-top: 2px;">
              &#8377;${totalCredit.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </div>
          </div>
          <div style="background: #fefce8; border: 1.5px solid #fde047; border-radius: 6px; padding: 6px 8px; text-align: center;">
            <div style="font-size: 8.5px; font-weight: 700; color: #854d0e; text-transform: uppercase;">Cash Balance</div>
            <div style="font-size: 12px; font-weight: 800; color: #713f12; font-family: monospace; margin-top: 2px;">
              &#8377;${Math.abs(closingCash).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ${closingCash > 0 ? (isSupplier ? 'Cr' : 'Dr') : closingCash < 0 ? (isSupplier ? 'Dr' : 'Cr') : 'Nil'}
            </div>
          </div>
          <div style="background: #fffbeb; border: 1.5px solid #fcd34d; border-radius: 6px; padding: 6px 8px; text-align: center;">
            <div style="font-size: 8.5px; font-weight: 700; color: #92400e; text-transform: uppercase;">Gold Balance</div>
            <div style="font-size: 12px; font-weight: 800; color: #b45309; font-family: monospace; margin-top: 2px;">
              ${Math.abs(closingGold).toFixed(3)}g ${closingGold > 0 ? 'Due' : closingGold < 0 ? 'Surplus' : 'Nil'}
            </div>
          </div>
          <div style="background: #f8fafc; border: 1.5px solid #cbd5e1; border-radius: 6px; padding: 6px 8px; text-align: center;">
            <div style="font-size: 8.5px; font-weight: 700; color: #475569; text-transform: uppercase;">Silver Balance</div>
            <div style="font-size: 12px; font-weight: 800; color: #334155; font-family: monospace; margin-top: 2px;">
              ${Math.abs(closingSilver).toFixed(3)}g ${closingSilver > 0 ? 'Due' : closingSilver < 0 ? 'Surplus' : 'Nil'}
            </div>
          </div>
        </div>

        <!-- Ledger Table -->
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 14px;">
          <thead>
            <tr style="background: #0f172a; color: #f8fafc; font-size: 9.5px; text-transform: uppercase; letter-spacing: 0.5px;">
              <th style="padding: 7px 8px; text-align: left; border: 1px solid #334155;">Date</th>
              <th style="padding: 7px 8px; text-align: left; border: 1px solid #334155;">Type</th>
              <th style="padding: 7px 8px; text-align: left; border: 1px solid #334155;">Ref No</th>
              <th style="padding: 7px 8px; text-align: left; border: 1px solid #334155;">Details</th>
              <th style="padding: 7px 8px; text-align: right; border: 1px solid #334155; color: #fbbf24;">Gold (g)</th>
              <th style="padding: 7px 8px; text-align: right; border: 1px solid #334155; color: #cbd5e1;">Silver (g)</th>
              <th style="padding: 7px 8px; text-align: right; border: 1px solid #334155;">Debit (₹)</th>
              <th style="padding: 7px 8px; text-align: right; border: 1px solid #334155;">Credit (₹)</th>
              <th style="padding: 7px 8px; text-align: right; border: 1px solid #334155;">Balance (₹)</th>
            </tr>
          </thead>
          <tbody>
            ${rowsHtml || `<tr><td colspan="9" style="text-align: center; padding: 20px; color: #94a3b8; font-size: 12px;">No transactions recorded in this period.</td></tr>`}
          </tbody>
          <tfoot>
            <tr style="background: #e2e8f0; font-weight: 800; font-size: 10.5px; border-top: 2px solid #0f172a;">
              <td colspan="4" style="padding: 7px 8px; text-transform: uppercase; color: #0f172a;">Period Totals:</td>
              <td style="padding: 7px 8px; text-align: right; font-family: monospace; color: #b45309;">
                ${totalGoldChange !== 0 ? `${totalGoldChange > 0 ? '+' : ''}${totalGoldChange.toFixed(3)}g` : '-'}
              </td>
              <td style="padding: 7px 8px; text-align: right; font-family: monospace; color: #334155;">
                ${totalSilverChange !== 0 ? `${totalSilverChange > 0 ? '+' : ''}${totalSilverChange.toFixed(3)}g` : '-'}
              </td>
              <td style="padding: 7px 8px; text-align: right; font-family: monospace; color: #dc2626;">
                &#8377;${totalDebit.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </td>
              <td style="padding: 7px 8px; text-align: right; font-family: monospace; color: #16a34a;">
                &#8377;${totalCredit.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </td>
              <td style="padding: 7px 8px; text-align: right; font-family: monospace; color: #0f172a;">
                &#8377;${Math.abs(closingCash).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ${closingCash > 0 ? (isSupplier ? 'Cr' : 'Dr') : closingCash < 0 ? (isSupplier ? 'Dr' : 'Cr') : ''}
              </td>
            </tr>
          </tfoot>
        </table>

        <!-- Signatures & Disclaimer -->
        <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-top: 30px; padding-top: 15px; page-break-inside: avoid;">
          <div style="text-align: center; border-top: 1px solid #94a3b8; width: 170px; padding-top: 4px; font-size: 10px; color: #64748b; font-weight: 600;">
            Party Signature
          </div>
          <div style="text-align: center; border-top: 1px solid #94a3b8; width: 190px; padding-top: 4px; font-size: 10px; color: #64748b; font-weight: 600;">
            For ${companyName}
          </div>
        </div>
        
        <div style="text-align: center; font-size: 8.5px; color: #94a3b8; margin-top: 16px; font-style: italic;">
          This is an official computer-generated account ledger statement. Please notify any discrepancy within 7 days.
        </div>
      </div>
    `;

    const renderContainer = document.createElement('div');
    renderContainer.style.position = 'fixed';
    renderContainer.style.top = '0';
    renderContainer.style.left = '-3000px';
    renderContainer.style.width = '210mm';
    renderContainer.style.background = '#ffffff';
    renderContainer.innerHTML = statementHtml;
    document.body.appendChild(renderContainer);

    await new Promise(resolve => setTimeout(resolve, 800));

    const targetElement = renderContainer.querySelector('.statement-pdf-page') as HTMLElement;
    // @ts-ignore
    const html2pdf = (await import('html2pdf.js')).default;
    const cleanFileName = `${isSupplier ? 'Supplier' : 'Customer'}_${partyName.replace(/[^a-zA-Z0-9]/g, '_')}_Statement.pdf`;
    const opt: any = {
      margin:       5,
      filename:     cleanFileName,
      image:        { type: 'jpeg', quality: 0.98 },
      html2canvas:  { scale: 2, useCORS: true, letterRendering: true, windowWidth: 794 },
      jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' },
      pagebreak:    { mode: ['css', 'legacy'] }
    };

    await html2pdf().set(opt).from(targetElement || renderContainer).save();
    document.body.removeChild(renderContainer);
  } catch (err) {
    console.error('Failed to generate statement PDF:', err);
    throw err;
  }
};
