import os
import re

print("Starting complete fix application...")

base_dir = r"C:\Users\YASH SONI\Desktop\jeweller-app"

# ----------------------------------------------------
# 1. Update frontend/src/components/layout/AdminLayout.tsx
# ----------------------------------------------------
admin_layout_path = os.path.join(base_dir, "frontend", "src", "components", "layout", "AdminLayout.tsx")
with open(admin_layout_path, "r", encoding="utf-8") as f:
    admin_content = f.read()

# Replace handleGlobalKeyDown block
old_key_pattern = r"const handleGlobalKeyDown = \(e: KeyboardEvent\) => \{.*?\n    \};\n\n    window\.addEventListener\('keydown', handleGlobalKeyDown\);"
new_key_block = """const handleGlobalKeyDown = (e: KeyboardEvent) => {
      // 1. Alt + 1 or Alt + 2: Company switching anywhere
      const isAlt1 = e.altKey && (e.key === '1' || e.code === 'Digit1' || e.code === 'Numpad1');
      const isAlt2 = e.altKey && (e.key === '2' || e.code === 'Digit2' || e.code === 'Numpad2');
      if (isAlt1 || isAlt2) {
        e.preventDefault();
        const cid = isAlt1 ? 1 : 2;
        const comp = companies.find(c => c.id === cid);
        if (comp) {
          selectCompany(cid);
          toast.success(`Switched to ${comp.name} (${comp.gst_enabled ? 'GST' : 'Normal'})`, { id: 'comp-switch' });
        }
        return;
      }

      // 2. F1, F2, F3: Switch Metal Tabs (Gold, Silver, Diamond)
      if (e.key === 'F1' || (e.altKey && (e.key === 'g' || e.key === 'G'))) {
        e.preventDefault();
        if (location.pathname !== '/' && location.pathname !== '/billing') {
          navigate('/billing');
          setTimeout(() => window.dispatchEvent(new CustomEvent('switch-metal', { detail: 'Gold' })), 100);
        } else {
          window.dispatchEvent(new CustomEvent('switch-metal', { detail: 'Gold' }));
        }
        return;
      }
      if (e.key === 'F2' || (e.altKey && (e.key === 's' || e.key === 'S'))) {
        e.preventDefault();
        if (location.pathname !== '/' && location.pathname !== '/billing') {
          navigate('/billing');
          setTimeout(() => window.dispatchEvent(new CustomEvent('switch-metal', { detail: 'Silver' })), 100);
        } else {
          window.dispatchEvent(new CustomEvent('switch-metal', { detail: 'Silver' }));
        }
        return;
      }
      if (e.key === 'F3' || (e.altKey && (e.key === 'd' || e.key === 'D'))) {
        e.preventDefault();
        if (location.pathname !== '/' && location.pathname !== '/billing') {
          navigate('/billing');
          setTimeout(() => window.dispatchEvent(new CustomEvent('switch-metal', { detail: 'Diamond' })), 100);
        } else {
          window.dispatchEvent(new CustomEvent('switch-metal', { detail: 'Diamond' }));
        }
        return;
      }

      // 3. F12 or Ctrl+Enter: Quick Checkout trigger
      if (e.key === 'F12' || (e.key === 'Enter' && (e.ctrlKey || e.metaKey))) {
        e.preventDefault();
        window.dispatchEvent(new CustomEvent('trigger-quick-checkout'));
        return;
      }

      // 4. Global Navigation with Function Keys
      if (e.key === 'F4' || (e.altKey && (e.key === 'b' || e.key === 'B'))) {
        e.preventDefault();
        navigate('/billing');
      } else if (e.key === 'F5' || (e.altKey && (e.key === 'p' || e.key === 'P'))) {
        e.preventDefault();
        navigate('/purchases');
      } else if (e.key === 'F6' || (e.altKey && (e.key === 'e' || e.key === 'E'))) {
        e.preventDefault();
        navigate('/exchange');
      } else if (e.key === 'F7' || e.key === 'F8' || (e.altKey && (e.key === 'i' || e.key === 'I'))) {
        e.preventDefault();
        navigate('/invoices');
      } else if (e.key === 'F9' || (e.altKey && (e.key === 'c' || e.key === 'C'))) {
        e.preventDefault();
        navigate('/customers');
      } else if (e.key === 'F10' || (e.altKey && (e.key === 'r' || e.key === 'R'))) {
        e.preventDefault();
        navigate('/reports');
      } else if (e.key === 'F11' || (e.altKey && (e.key === 's' || e.key === 'S'))) {
        e.preventDefault();
        navigate('/settings');
      } else if (e.altKey && (e.key === 'h' || e.key === 'H')) {
        e.preventDefault();
        navigate('/');
      }
    };

    window.addEventListener('keydown', handleGlobalKeyDown);"""

admin_content = re.sub(old_key_pattern, new_key_block, admin_content, flags=re.DOTALL)

# Add pb-20 to main tag so shortcut bar doesn't overlap content
admin_content = admin_content.replace(
    '<main className="flex-1 overflow-auto p-2 sm:p-4 md:p-6">',
    '<main className="flex-1 overflow-auto p-2 sm:p-4 md:p-6 pb-20 sm:pb-24">'
)

with open(admin_layout_path, "w", encoding="utf-8") as f:
    f.write(admin_content)
print("1. AdminLayout.tsx updated successfully!")

# ----------------------------------------------------
# 2. Update frontend/src/components/common/ShortcutBar.tsx
# ----------------------------------------------------
shortcut_bar_path = os.path.join(base_dir, "frontend", "src", "components", "common", "ShortcutBar.tsx")
with open(shortcut_bar_path, "r", encoding="utf-8") as f:
    sc_content = f.read()

# Replace flex-wrap with overflow-x-auto whitespace-nowrap in shortcut bar
sc_content = sc_content.replace(
    '<div className="flex items-center gap-2 sm:gap-3 flex-wrap">',
    '<div className="flex items-center gap-2 sm:gap-3 overflow-x-auto whitespace-nowrap scrollbar-none">'
)

# Replace billing keys to also show F8 Invoices and Alt+1/2
old_billing_keys = """              {isBilling && (
                <>
                  <div className="flex items-center gap-1">
                    <kbd className="px-1.5 py-0.5 bg-gray-800 border border-gray-700 rounded text-amber-400 font-mono font-bold">F1</kbd>
                    <span className="text-gray-400">Gold</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <kbd className="px-1.5 py-0.5 bg-gray-800 border border-gray-700 rounded text-cyan-400 font-mono font-bold">F2</kbd>
                    <span className="text-gray-400">Silver</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <kbd className="px-1.5 py-0.5 bg-gray-800 border border-gray-700 rounded text-purple-400 font-mono font-bold">F3</kbd>
                    <span className="text-gray-400">Diamond</span>
                  </div>
                  <div className="h-3 w-px bg-gray-800" />
                  <div className="flex items-center gap-1">
                    <kbd className="px-1.5 py-0.5 bg-gray-800 border border-gray-700 rounded text-emerald-400 font-mono font-bold">Enter / ↓</kbd>
                    <span className="text-gray-400">Next Field</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <kbd className="px-1.5 py-0.5 bg-gray-800 border border-gray-700 rounded text-gray-400 font-mono font-bold">↑</kbd>
                    <span className="text-gray-400">Prev</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <kbd className="px-1.5 py-0.5 bg-primary/20 border border-primary/40 rounded text-primary font-mono font-bold">F12</kbd>
                    <span className="text-gray-300 font-semibold">Checkout</span>
                  </div>
                </>
              )}"""

new_billing_keys = """              {isBilling && (
                <>
                  <div className="flex items-center gap-1">
                    <kbd className="px-1.5 py-0.5 bg-amber-500/20 border border-amber-500/40 rounded text-amber-300 font-mono font-bold">F1</kbd>
                    <span className="text-gray-300">Gold</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <kbd className="px-1.5 py-0.5 bg-cyan-500/20 border border-cyan-500/40 rounded text-cyan-300 font-mono font-bold">F2</kbd>
                    <span className="text-gray-300">Silver</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <kbd className="px-1.5 py-0.5 bg-purple-500/20 border border-purple-500/40 rounded text-purple-300 font-mono font-bold">F3</kbd>
                    <span className="text-gray-300">Diamond</span>
                  </div>
                  <div className="h-3 w-px bg-gray-800" />
                  <div className="flex items-center gap-1">
                    <kbd className="px-1.5 py-0.5 bg-gray-800 border border-gray-700 rounded text-emerald-400 font-mono font-bold">Enter / ↓</kbd>
                    <span className="text-gray-400">Next Field</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <kbd className="px-1.5 py-0.5 bg-primary/20 border border-primary/40 rounded text-primary font-mono font-bold">F12</kbd>
                    <span className="text-gray-300 font-semibold">Checkout</span>
                  </div>
                  <div className="h-3 w-px bg-gray-800" />
                  <div className="flex items-center gap-1">
                    <kbd className="px-1.5 py-0.5 bg-gray-800 border border-gray-700 rounded text-cyan-400 font-mono font-bold">F8</kbd>
                    <span className="text-gray-400">Invoices</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <kbd className="px-1.5 py-0.5 bg-gray-800 border border-gray-700 rounded text-amber-400 font-mono font-bold">Alt+1/2</kbd>
                    <span className="text-gray-400">Co.</span>
                  </div>
                </>
              )}"""

sc_content = sc_content.replace(old_billing_keys, new_billing_keys)

with open(shortcut_bar_path, "w", encoding="utf-8") as f:
    f.write(sc_content)
print("2. ShortcutBar.tsx updated successfully!")

# ----------------------------------------------------
# 3. Update frontend/src/pages/invoices/InvoiceHistory.tsx
# ----------------------------------------------------
inv_history_path = os.path.join(base_dir, "frontend", "src", "pages", "invoices", "InvoiceHistory.tsx")
with open(inv_history_path, "r", encoding="utf-8") as f:
    inv_content = f.read()

# Update getPdfEndpoint and handleDelete to recognize tab and invoice series
old_pdf_ep = """  const getPdfEndpoint = (invoice: Invoice) => {
    if (invoice.invoice_number.startsWith('PUR-')) return `/purchases/${invoice.id}/pdf-data`;
    if (invoice.invoice_number.startsWith('EXC-')) return `/exchanges/${invoice.id}/pdf-data`;
    return `/invoices/${invoice.id}/pdf-data`;
  };"""

new_pdf_ep = """  const getPdfEndpoint = (invoice: Invoice) => {
    const isPur = tab === 'purchases' || invoice.invoice_number.startsWith('PUR-') || invoice.invoice_number.includes('/P/');
    const isExc = tab === 'exchange' || invoice.invoice_number.startsWith('EXC-') || invoice.invoice_number.includes('/E/');
    if (isPur) return `/purchases/${invoice.id}/pdf-data`;
    if (isExc) return `/exchanges/${invoice.id}/pdf-data`;
    return `/invoices/${invoice.id}/pdf-data`;
  };"""

inv_content = inv_content.replace(old_pdf_ep, new_pdf_ep)

# Update handleDelete checks
old_del_check = """  const handleDelete = async (invoice: Invoice) => {
    const isExchange = invoice.invoice_number.startsWith('EXC-');
    const isPurchase = invoice.invoice_number.startsWith('PUR-');"""

new_del_check = """  const handleDelete = async (invoice: Invoice) => {
    const isPurchase = tab === 'purchases' || invoice.invoice_number.startsWith('PUR-') || invoice.invoice_number.includes('/P/');
    const isExchange = tab === 'exchange' || invoice.invoice_number.startsWith('EXC-') || invoice.invoice_number.includes('/E/');"""

inv_content = inv_content.replace(old_del_check, new_del_check)

# Update handlePrint checks
old_print_check = """  const handlePrint = (invoice: Invoice) => {
    const isEx = invoice.invoice_number.startsWith('EXC-');
    const isPur = invoice.invoice_number.startsWith('PUR-');"""

new_print_check = """  const handlePrint = (invoice: Invoice) => {
    const isPur = tab === 'purchases' || invoice.invoice_number.startsWith('PUR-') || invoice.invoice_number.includes('/P/');
    const isEx = tab === 'exchange' || invoice.invoice_number.startsWith('EXC-') || invoice.invoice_number.includes('/E/');"""

inv_content = inv_content.replace(old_print_check, new_print_check)

# Update subtitle so it never says Pride Gold
inv_content = inv_content.replace(
    "GST Tax Invoices for Pride Gold",
    "GST Tax Invoices for Saideep Jewellers"
)

with open(inv_history_path, "w", encoding="utf-8") as f:
    f.write(inv_content)
print("3. InvoiceHistory.tsx updated successfully!")

# ----------------------------------------------------
# 4. Update frontend/src/utils/invoicePdfUtils.ts
# ----------------------------------------------------
pdf_utils_path = os.path.join(base_dir, "frontend", "src", "utils", "invoicePdfUtils.ts")
with open(pdf_utils_path, "r", encoding="utf-8") as f:
    pdf_content = f.read()

# Replace isGstCompany resolution
old_is_gst = """    const isGstCompany = Boolean(
      company.gst_enabled === true ||
      data.company?.gst_enabled === true ||
      data.company?.id === 2 ||
      (data as any).company_id === 2 ||
      String(data.invoice?.invoice_number || '').startsWith('SJ/S/') ||
      String(data.invoice?.invoice_number || '').startsWith('PUR-') && company.gst_enabled === true
    );"""

new_is_gst = """    const resolvedCompanyId = Number(data.company_id || data.company?.id || (data.invoice as any)?.company_id || 1);
    const isGstCompany = Boolean(
      resolvedCompanyId === 2 ||
      company.gst_enabled === true ||
      company.gst_enabled === 1 ||
      data.company?.gst_enabled === true ||
      data.company?.gst_enabled === 1 ||
      String(data.invoice?.invoice_number || '').startsWith('SJ/') ||
      String(data.invoice?.invoice_number || '').startsWith('PG/') ||
      ((data as any).type === 'purchase' && (resolvedCompanyId === 2 || company.gst_enabled))
    );"""

pdf_content = pdf_content.replace(old_is_gst, new_is_gst)

# Ensure fallback invoice number does not use PG
pdf_content = pdf_content.replace(
    "invoice_number: data.invoice?.invoice_number || 'PG/S/1944/26-27'",
    "invoice_number: data.invoice?.invoice_number || 'SJ/S/1945/26-27'"
)

with open(pdf_utils_path, "w", encoding="utf-8") as f:
    f.write(pdf_content)
print("4. invoicePdfUtils.ts updated successfully!")

# ----------------------------------------------------
# 5. Update frontend/src/pages/settings/index.tsx
# ----------------------------------------------------
settings_path = os.path.join(base_dir, "frontend", "src", "pages", "settings", "index.tsx")
with open(settings_path, "r", encoding="utf-8") as f:
    sett_content = f.read()

sett_content = sett_content.replace(
    'placeholder="e.g. 1st Floor, Near Koira Ji ka Bera, Ghodo ka Chowk, Sojati Gate, Jodhpur (Raj.)- 342001"',
    'placeholder="e.g. 167, Ward No. 3, Khedawas, Takhatgarh, Pali (Raj.)-306912"'
)

with open(settings_path, "w", encoding="utf-8") as f:
    f.write(sett_content)
print("5. settings/index.tsx updated successfully!")

print("\nALL FIXES APPLIED SUCCESSFULLY!")
