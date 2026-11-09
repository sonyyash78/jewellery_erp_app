def update_pdf_utils():
    path = r"C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\utils\invoicePdfUtils.ts"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    target_inv = "    await html2pdf().set(opt).from(targetElement).save();"
    replace_inv = """    const electronAPI = (window as any).electronAPI;
    if (electronAPI?.saveVaultPdf) {
      try {
        const worker = html2pdf().set(opt).from(targetElement);
        const pdfBase64 = await worker.outputPdf('datauristring');
        const cleanBase64 = pdfBase64.includes(',') ? pdfBase64.split(',')[1] : pdfBase64;
        const customerFolder = data.customer?.name || 'Walk-in Customer';
        await electronAPI.saveVaultPdf({
          category: 'Sales',
          folderName: customerFolder,
          fileName: `${data.invoice?.invoice_number || 'INVOICE'}.pdf`,
          base64Data: cleanBase64
        });
      } catch (vaultErr) {
        console.warn('Silent vault save fallback:', vaultErr);
        await html2pdf().set(opt).from(targetElement).save();
      }
    } else {
      await html2pdf().set(opt).from(targetElement).save();
    }"""

    target_receipt = "    await html2pdf().set(opt).from(targetElement || renderContainer).save();\n    document.body.removeChild(renderContainer);"
    replace_receipt = """    const electronAPIReceipt = (window as any).electronAPI;
    if (electronAPIReceipt?.saveVaultPdf) {
      try {
        const worker = html2pdf().set(opt).from(targetElement || renderContainer);
        const pdfBase64 = await worker.outputPdf('datauristring');
        const cleanBase64 = pdfBase64.includes(',') ? pdfBase64.split(',')[1] : pdfBase64;
        const supplierFolder = data.seller?.name || data.customer?.name || 'Suppliers';
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
    }
    document.body.removeChild(renderContainer);"""

    c_norm = content.replace("\r\n", "\n")
    t_inv_norm = target_inv.replace("\r\n", "\n")
    r_inv_norm = replace_inv.replace("\r\n", "\n")
    t_rec_norm = target_receipt.replace("\r\n", "\n")
    r_rec_norm = replace_receipt.replace("\r\n", "\n")

    if t_inv_norm in c_norm:
        c_norm = c_norm.replace(t_inv_norm, r_inv_norm, 1)
        print("Updated invoicePdfUtils.ts generateInvoicePDF")
    if t_rec_norm in c_norm:
        c_norm = c_norm.replace(t_rec_norm, r_rec_norm, 1)
        print("Updated invoicePdfUtils.ts generateReceiptPDF")

    with open(path, "w", encoding="utf-8") as f:
        f.write(c_norm.replace("\n", "\r\n"))

if __name__ == "__main__":
    update_pdf_utils()
