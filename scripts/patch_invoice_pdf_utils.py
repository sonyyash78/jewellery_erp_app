from pathlib import Path
import re

pdf_utils_file = Path(r"c:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\utils\invoicePdfUtils.ts")
code = pdf_utils_file.read_text(encoding="utf-8")

old_block = """    const electronAPI = (window as any).electronAPI;

    if (electronAPI?.saveVaultPdf) {

      try {

        const worker = html2pdf().set(opt).from(targetElement);

        const pdfBase64 = await worker.outputPdf('datauristring');

        const cleanBase64 = pdfBase64.includes(',') ? pdfBase64.split(',')[1] : pdfBase64;

        const isPurchase = (data as any).type === 'purchase' || String(data.invoice?.invoice_number || '').startsWith('PUR-') || String(data.invoice?.invoice_number || '').includes('/P/');
        const isExchange = (data as any).type === 'exchange' || String(data.invoice?.invoice_number || '').startsWith('EXC-') || String(data.invoice?.invoice_number || '').includes('/E/');
        const category = isPurchase ? 'Purchases' : isExchange ? 'Exchanges' : 'Sales';
        const partyName = (data.customer?.name || (data as any).seller?.name || (data as any).supplier?.name || (isPurchase ? 'Supplier' : 'Walk-in Customer')).trim();
        await electronAPI.saveVaultPdf({
          category,
          folderName: partyName,
          fileName: `${data.invoice?.invoice_number || (isPurchase ? 'PURCHASE' : isExchange ? 'EXCHANGE' : 'INVOICE')}.pdf`,
          base64Data: cleanBase64
        });

      } catch (vaultErr) {

        console.warn('Silent vault save fallback:', vaultErr);

        await html2pdf().set(opt).from(targetElement).save();

      }

    } else {

      await html2pdf().set(opt).from(targetElement).save();

    }"""

new_block = """    const electronAPI = (window as any).electronAPI;

    try {
      const worker = html2pdf().set(opt).from(targetElement);
      const pdfBase64 = await worker.outputPdf('datauristring');
      const cleanBase64 = pdfBase64.includes(',') ? pdfBase64.split(',')[1] : pdfBase64;

      const rawDocNum = String(data.invoice?.invoice_number || ((data as any).type === 'purchase' ? 'PURCHASE' : (data as any).type === 'exchange' ? 'EXCHANGE' : 'INVOICE')).trim();
      const cleanDocNum = rawDocNum.replace(/[\\\\/*?:"<>|]/g, '_').trim();
      const fileName = `${cleanDocNum}.pdf`;

      const isPurchase = (data as any).type === 'purchase' || rawDocNum.startsWith('PUR-') || rawDocNum.includes('/P/') || rawDocNum.includes('_P_');
      const isExchange = (data as any).type === 'exchange' || rawDocNum.startsWith('EXC-') || rawDocNum.includes('/E/') || rawDocNum.includes('_E_');
      const category = isPurchase ? 'Purchases' : isExchange ? 'Exchanges' : 'Sales';

      const rawParty = (data.customer?.name || (data as any).seller?.name || (data as any).supplier?.name || (isPurchase ? 'Supplier' : 'Walk-in Customer')).trim();
      const cleanPartyName = rawParty.replace(/[\\\\/*?:"<>|]/g, '_').trim() || (isPurchase ? 'Supplier' : 'Customer');

      const isGst = Boolean(
        (data as any).is_gst ||
        data.company?.id === 2 ||
        data.invoice?.is_gst ||
        cleanDocNum.startsWith('SJ_S') || cleanDocNum.startsWith('SJ/S') ||
        cleanDocNum.startsWith('SJ_P') || cleanDocNum.startsWith('SJ/P') ||
        cleanDocNum.startsWith('SJ_E') || cleanDocNum.startsWith('SJ/E') ||
        cleanDocNum.includes('_S_') || cleanDocNum.includes('/S/')
      );
      const companyId = isGst ? 2 : (data.company?.id || 1);

      if (electronAPI?.saveVaultPdf) {
        await electronAPI.saveVaultPdf({
          category,
          folderName: cleanPartyName,
          fileName,
          base64Data: cleanBase64,
          isGst,
          companyId
        });
      }

      // Always sync to backend vault as well
      try {
        const { axiosClient } = await import('../../api/axiosClient');
        await axiosClient.post('/backup/save-vault-pdf', {
          category,
          folder_name: cleanPartyName,
          file_name: fileName,
          pdf_base64: cleanBase64,
          is_gst: isGst,
          company_id: companyId
        });
      } catch (bkErr) {
        console.warn('Backend vault sync warning:', bkErr);
      }

    } catch (vaultErr) {
      console.warn('Silent vault save fallback:', vaultErr);
      await html2pdf().set(opt).from(targetElement).save();
    }"""

code = code.replace(old_block, new_block)

# Also update receipt save block
old_receipt_block = """    const electronAPIReceipt = (window as any).electronAPI;

    if (electronAPIReceipt?.saveVaultPdf) {

      try {

        const worker = html2pdf().set(opt).from(targetElement || renderContainer);

        const pdfBase64 = await worker.outputPdf('datauristring');

        const cleanBase64 = pdfBase64.includes(',') ? pdfBase64.split(',')[1] : pdfBase64;

        const supplierFolder = entity?.name || 'Suppliers';

        await electronAPIReceipt.saveVaultPdf({

          category: 'Purchases',

          folderName: supplierFolder,

          fileName: `Receipt_${voucherNo}.pdf`,

          base64Data: cleanBase64

        });

      } catch (vaultErr) {

        console.warn('Silent receipt vault save fallback:', vaultErr);

        await html2pdf().set(opt).from(targetElement || renderContainer).save();

      }

    } else {

      await html2pdf().set(opt).from(targetElement || renderContainer).save();

    }"""

new_receipt_block = """    const electronAPIReceipt = (window as any).electronAPI;

    try {
      const worker = html2pdf().set(opt).from(targetElement || renderContainer);
      const pdfBase64 = await worker.outputPdf('datauristring');
      const cleanBase64 = pdfBase64.includes(',') ? pdfBase64.split(',')[1] : pdfBase64;

      const rawSupplier = entity?.name || 'Suppliers';
      const cleanSupplierFolder = String(rawSupplier).replace(/[\\\\/*?:"<>|]/g, '_').trim() || 'Suppliers';
      const cleanVouch = String(voucherNo).replace(/[\\\\/*?:"<>|]/g, '_').trim();
      const fileName = `Receipt_${cleanVouch}.pdf`;

      if (electronAPIReceipt?.saveVaultPdf) {
        await electronAPIReceipt.saveVaultPdf({
          category: 'Purchases',
          folderName: cleanSupplierFolder,
          fileName,
          base64Data: cleanBase64,
          isGst: false,
          companyId: 1
        });
      }

      try {
        const { axiosClient } = await import('../../api/axiosClient');
        await axiosClient.post('/backup/save-vault-pdf', {
          category: 'Purchases',
          folder_name: cleanSupplierFolder,
          file_name: fileName,
          pdf_base64: cleanBase64,
          is_gst: false,
          company_id: 1
        });
      } catch (bkErr) {
        console.warn('Backend receipt vault sync warning:', bkErr);
      }
    } catch (vaultErr) {
      console.warn('Silent receipt vault save fallback:', vaultErr);
      await html2pdf().set(opt).from(targetElement || renderContainer).save();
    }"""

code = code.replace(old_receipt_block, new_receipt_block)

pdf_utils_file.write_text(code, encoding="utf-8")
print("invoicePdfUtils.ts updated with full silent vault saving!")
