import os

repo_root = r"C:\Users\YASH SONI\Desktop\jeweller-app"

# 1. Fix invoicePdfUtils.ts
pdf_utils_path = os.path.join(repo_root, "frontend", "src", "utils", "invoicePdfUtils.ts")
with open(pdf_utils_path, "r", encoding="utf-8") as f:
    pdf_content = f.read()

# Fix data.seller -> entity?.name in generatePaymentReceiptPDF
old_seller_line = "const supplierFolder = data.seller?.name || data.customer?.name || 'Suppliers';"
new_seller_line = "const supplierFolder = entity?.name || 'Suppliers';"
if old_seller_line in pdf_content:
    pdf_content = pdf_content.replace(old_seller_line, new_seller_line)
    print("Fixed supplierFolder in invoicePdfUtils.ts")

# Add silent save in generateLedgerStatementPDF
old_stmt_save = """    await html2pdf().set(opt).from(targetElement || renderContainer).save();
    document.body.removeChild(renderContainer);"""

new_stmt_save = """    const electronAPIStmt = (window as any).electronAPI;
    if (electronAPIStmt?.saveVaultPdf) {
      try {
        const worker = html2pdf().set(opt).from(targetElement || renderContainer);
        const pdfBase64 = await worker.outputPdf('datauristring');
        const cleanBase64 = pdfBase64.includes(',') ? pdfBase64.split(',')[1] : pdfBase64;
        const customerFolder = data.customerName || 'Ledgers';
        await electronAPIStmt.saveVaultPdf({
          category: 'Statements',
          folderName: customerFolder,
          fileName: cleanFileName,
          base64Data: cleanBase64
        });
      } catch (vaultErr) {
        console.warn('Silent statement vault save fallback:', vaultErr);
        await html2pdf().set(opt).from(targetElement || renderContainer).save();
      }
    } else {
      await html2pdf().set(opt).from(targetElement || renderContainer).save();
    }
    document.body.removeChild(renderContainer);"""

if old_stmt_save in pdf_content:
    pdf_content = pdf_content.replace(old_stmt_save, new_stmt_save)
    print("Added silent save to generateLedgerStatementPDF in invoicePdfUtils.ts")

with open(pdf_utils_path, "w", encoding="utf-8") as f:
    f.write(pdf_content)

# 2. Fix ExchangeCheckoutModal.tsx (line 415: handleGenerate() -> handleGenerate(false))
exch_modal_path = os.path.join(repo_root, "frontend", "src", "pages", "exchange", "ExchangeCheckoutModal.tsx")
with open(exch_modal_path, "r", encoding="utf-8") as f:
    exch_content = f.read()

old_exch_call = "handleGenerate();"
new_exch_call = "handleGenerate(false);"
if old_exch_call in exch_content:
    exch_content = exch_content.replace(old_exch_call, new_exch_call)
    print("Fixed handleGenerate(false) in ExchangeCheckoutModal.tsx")

with open(exch_modal_path, "w", encoding="utf-8") as f:
    f.write(exch_content)

# 3. Fix PurchaseCheckoutModal.tsx (line 785: handleGenerate() -> handleGenerate(false))
pur_modal_path = os.path.join(repo_root, "frontend", "src", "pages", "purchase", "PurchaseCheckoutModal.tsx")
with open(pur_modal_path, "r", encoding="utf-8") as f:
    pur_content = f.read()

if old_exch_call in pur_content:
    pur_content = pur_content.replace(old_exch_call, new_exch_call)
    print("Fixed handleGenerate(false) in PurchaseCheckoutModal.tsx")

with open(pur_modal_path, "w", encoding="utf-8") as f:
    f.write(pur_content)

# 4. Wire MetalCalculator.tsx
metal_calc_path = os.path.join(repo_root, "frontend", "src", "pages", "billing", "MetalCalculator.tsx")
with open(metal_calc_path, "r", encoding="utf-8") as f:
    mc_content = f.read()

target_mc_div = '<div className="bg-[#111115] border border-gray-800 rounded-2xl p-4 shadow-[0_4px_20px_rgba(0,0,0,0.5)] flex flex-col h-full">'
replacement_mc_div = '''<div 
      data-enter-container="true"
      onKeyDown={(e) => handleEnterKeyNavigation(e, '[data-enter-container]', () => {
        if (isDiamond) handleDiamondAdd();
        else if (isGold) handleGoldAdd();
        else handleSilverAdd();
      })}
      className="bg-[#111115] border border-gray-800 rounded-2xl p-4 shadow-[0_4px_20px_rgba(0,0,0,0.5)] flex flex-col h-full">'''

if target_mc_div in mc_content:
    mc_content = mc_content.replace(target_mc_div, replacement_mc_div)
    print("Wired handleEnterKeyNavigation in MetalCalculator.tsx")
else:
    print("Target div not found in MetalCalculator.tsx")

with open(metal_calc_path, "w", encoding="utf-8") as f:
    f.write(mc_content)

# 5. Wire CheckoutModal.tsx
chk_modal_path = os.path.join(repo_root, "frontend", "src", "pages", "billing", "CheckoutModal.tsx")
with open(chk_modal_path, "r", encoding="utf-8") as f:
    chk_content = f.read()

target_chk_div = '<div className="bg-surface border border-gray-700 rounded-2xl shadow-2xl w-full max-w-3xl max-h-[92vh] flex flex-col overflow-hidden my-auto">'
replacement_chk_div = '''<div 
        data-enter-container="true"
        onKeyDown={(e) => handleEnterKeyNavigation(e, '[data-enter-container]', () => {
          if (!loading && (isFullySettled || selectedCustomer)) {
            handleGenerate(false);
          }
        })}
        className="bg-surface border border-gray-700 rounded-2xl shadow-2xl w-full max-w-3xl max-h-[92vh] flex flex-col overflow-hidden my-auto">'''

if target_chk_div in chk_content:
    chk_content = chk_content.replace(target_chk_div, replacement_chk_div)
    print("Wired handleEnterKeyNavigation in CheckoutModal.tsx")
else:
    print("Target div not found in CheckoutModal.tsx")

with open(chk_modal_path, "w", encoding="utf-8") as f:
    f.write(chk_content)

# 6. Wire PurchaseMetalForm.tsx
pur_form_path = os.path.join(repo_root, "frontend", "src", "pages", "purchase", "PurchaseMetalForm.tsx")
with open(pur_form_path, "r", encoding="utf-8") as f:
    pf_content = f.read()

target_pf_div = '<div className="bg-[#111115] border border-gray-800 rounded-2xl p-4 shadow-[0_4px_20px_rgba(0,0,0,0.5)] flex flex-col h-full">'
replacement_pf_div = '''<div 
      data-enter-container="true"
      onKeyDown={(e) => handleEnterKeyNavigation(e, '[data-enter-container]', () => {
        if (isDiamond) handleDiamondAdd();
        else if (isGold) handleGoldAdd();
        else handleSilverAdd();
      })}
      className="bg-[#111115] border border-gray-800 rounded-2xl p-4 shadow-[0_4px_20px_rgba(0,0,0,0.5)] flex flex-col h-full">'''

if target_pf_div in pf_content:
    pf_content = pf_content.replace(target_pf_div, replacement_pf_div)
    print("Wired handleEnterKeyNavigation in PurchaseMetalForm.tsx")
else:
    print("Target div not found in PurchaseMetalForm.tsx")

# Add focus next item in handleGoldAdd, handleSilverAdd, handleDiamondAdd
auto_focus_code = """
    setTimeout(() => {
      const firstInput = document.querySelector<HTMLInputElement>('[data-enter-container] input:not([disabled])');
      firstInput?.focus();
      firstInput?.select();
    }, 50);"""

if "toast.success('Gold added to purchase list');\n    resetForms();" in pf_content:
    pf_content = pf_content.replace("toast.success('Gold added to purchase list');\n    resetForms();",
                                    f"toast.success('Gold added to purchase list');{auto_focus_code}\n    resetForms();")
if "toast.success('Silver added to purchase list');\n    resetForms();" in pf_content:
    pf_content = pf_content.replace("toast.success('Silver added to purchase list');\n    resetForms();",
                                    f"toast.success('Silver added to purchase list');{auto_focus_code}\n    resetForms();")
if "toast.success('Diamond added to purchase list');\n    resetForms();" in pf_content:
    pf_content = pf_content.replace("toast.success('Diamond added to purchase list');\n    resetForms();",
                                    f"toast.success('Diamond added to purchase list');{auto_focus_code}\n    resetForms();")

with open(pur_form_path, "w", encoding="utf-8") as f:
    f.write(pf_content)

# 7. Wire OldItemsForm.tsx
old_form_path = os.path.join(repo_root, "frontend", "src", "pages", "exchange", "OldItemsForm.tsx")
with open(old_form_path, "r", encoding="utf-8") as f:
    of_content = f.read()

target_of_form = '<form onSubmit={handleAdd} className="space-y-4">'
replacement_of_form = '''<form 
        data-enter-container="true"
        onKeyDown={(e) => handleEnterKeyNavigation(e, '[data-enter-container]', () => {
          handleAdd(e as any);
        })}
        onSubmit={handleAdd} 
        className="space-y-4">'''

if target_of_form in of_content:
    of_content = of_content.replace(target_of_form, replacement_of_form)
    print("Wired handleEnterKeyNavigation in OldItemsForm.tsx")
else:
    print("Target form not found in OldItemsForm.tsx")

with open(old_form_path, "w", encoding="utf-8") as f:
    f.write(of_content)

print("All fixes applied successfully!")
