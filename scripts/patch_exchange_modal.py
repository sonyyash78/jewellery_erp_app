import re

exchange_path = r'c:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\pages\exchange\ExchangeCheckoutModal.tsx'
with open(exchange_path, 'r', encoding='utf-8') as f:
    e_text = f.read()

# 1. Import useRef
e_text = e_text.replace(
    "import { useState, useEffect, useMemo } from 'react';",
    "import { useState, useEffect, useMemo, useRef } from 'react';"
)

# 2. cashReceived initial + ref
e_old_cash = "  const [cashReceived, setCashReceived] = useState<number>(0);"
e_new_cash = """  const [cashReceived, setCashReceived] = useState<number>(() => {
    return Math.round((payload?.net_amount_due || payload?.grand_total || grandTotal || 0) * 100) / 100;
  });
  const cashInputRef = useRef<HTMLInputElement>(null);
  useEffect(() => {
    const timer = setTimeout(() => {
      if (cashInputRef.current) {
        cashInputRef.current.focus();
        cashInputRef.current.select();
      }
    }, 100);
    return () => clearTimeout(timer);
  }, []);"""
if e_old_cash in e_text:
    e_text = e_text.replace(e_old_cash, e_new_cash, 1)

# 3. In handleGenerate: remove blocking check and resolve effectiveCustomerId
e_old_gen_guard = re.search(r'  const handleGenerate = async \(shouldPrint: boolean\) => \{\r?\n\s+if \(!isFullySettled && !selectedCustomer\) \{.*?\r?\n\s+setLoading\(true\);', e_text, re.DOTALL)
if e_old_gen_guard:
    e_new_gen_guard = """  const handleGenerate = async (shouldPrint: boolean) => {
    if (cashReceived < 0 || goldDeposited < 0 || silverDeposited < 0) {
      toast.error('Deposits cannot be negative.');
      return;
    }
    setLoading(true);

    let effectiveCustomerId = selectedCustomer || null;
    if (!effectiveCustomerId && customers && customers.length > 0) {
      effectiveCustomerId = customers[0].id;
    }"""
    e_text = e_text.replace(e_old_gen_guard.group(0), e_new_gen_guard, 1)

# replace customer_id: selectedCustomer || null
if 'customer_id: selectedCustomer || null,' in e_text:
    e_text = e_text.replace('customer_id: selectedCustomer || null,', 'customer_id: effectiveCustomerId,', 1)

# 4. Add window keydown listener after handleSaveNewCustomer
target_save_cust = "  const handleSaveNewCustomer = async () => {\n    if (!newCustomer.first_name || (newCustomer.phone.length !== 10 && newCustomer.phone.length !== 12)) { toast.error('First name and 10 or 12-digit phone number are required'); return; }\n    setLoading(true);\n    try {\n      const res = await axiosClient.post('/customers/', { first_name: newCustomer.first_name, last_name: newCustomer.last_name, phone_number: newCustomer.phone, email: null, address: '', city: newCustomer.city });\n      setCustomers([...customers, res.data]); setSelectedCustomer(res.data.id); setMode('checkout'); toast.success('Customer added');\n    } catch (e: any) { toast.error(getErrorMessage(e, 'Failed to save customer')); } finally { setLoading(false); }\n  };"
target_save_cust_crlf = target_save_cust.replace('\n', '\r\n')

e_new_keys = """

  useEffect(() => {
    const handleModalKeys = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.preventDefault();
        if (mode === 'new_customer') {
          setMode('checkout');
        } else {
          onClose();
        }
        return;
      }

      if (e.key === 'F12') {
        e.preventDefault();
        if (!loading) {
          handleGenerate(true);
        }
        return;
      }

      if (e.key === 'Enter') {
        const target = e.target as HTMLElement;
        if (target?.tagName === 'TEXTAREA' && !e.ctrlKey) return;
        if (target?.tagName === 'BUTTON' && target.getAttribute('data-save-only') !== 'true') return;
        if (target?.getAttribute('data-counter-metal') === 'true') return;

        e.preventDefault();
        if (!loading) {
          handleGenerate(false);
        }
      }
    };

    window.addEventListener('keydown', handleModalKeys);
    return () => window.removeEventListener('keydown', handleModalKeys);
  }, [mode, onClose, loading, isFullySettled, selectedCustomer, cashReceived, goldDeposited, silverDeposited, customers, currentCompanyId]);"""

if target_save_cust in e_text and 'handleModalKeys' not in e_text:
    e_text = e_text.replace(target_save_cust, target_save_cust + e_new_keys, 1)
elif target_save_cust_crlf in e_text and 'handleModalKeys' not in e_text:
    e_text = e_text.replace(target_save_cust_crlf, target_save_cust_crlf + e_new_keys, 1)

# 5. Container enter callback
e_old_container = re.search(r'        onKeyDown=\{\(e\) => handleEnterKeyNavigation\(e, \'\[data-enter-container\]\', \(\) => \{\r?\n\s+if \(!loading && \(isFullySettled \|\| selectedCustomer\)\) \{\r?\n\s+handleGenerate\(false\);\r?\n\s+\}\r?\n\s+\}\)\}', e_text)
if e_old_container:
    e_new_container = """        onKeyDown={(e) => handleEnterKeyNavigation(e, '[data-enter-container]', () => {
          if (!loading) {
            handleGenerate(false);
          }
        })}"""
    e_text = e_text.replace(e_old_container.group(0), e_new_container, 1)

# 6. cashReceived input
e_old_cash_input = re.search(r'<input type="number" min="0" value=\{cashReceived === 0 \? \'\' : cashReceived\} onChange=\{e => setCashReceived\(Number\(e\.target\.value\)\)\} placeholder="0" className="[^"]*" />', e_text)
if e_old_cash_input:
    e_new_cash_input = """<input 
                        ref={cashInputRef}
                        type="number" 
                        min="0" 
                        value={cashReceived === 0 ? '' : cashReceived} 
                        onChange={e => setCashReceived(Number(e.target.value))} 
                        onKeyDown={e => {
                          if (e.key === 'Enter' && !e.shiftKey) {
                            e.preventDefault();
                            e.stopPropagation();
                            if (!loading) handleGenerate(false);
                          }
                        }}
                        placeholder="0" 
                        className="w-full bg-background border border-green-900 rounded p-2 text-lg font-mono text-green-400 outline-none focus:border-green-500" 
                      />"""
    e_text = e_text.replace(e_old_cash_input.group(0), e_new_cash_input, 1)

# 7. Buttons disabled attribute
e_old_save_btn = re.search(r'<button data-nav-button="true" onClick=\{\(\) => handleGenerate\(false\)\} disabled=\{loading \|\| \(!isFullySettled && !selectedCustomer\)\} className="[^"]*">\r?\n\s+\{loading \? \'Saving\.\.\.\' : \'SAVE ONLY\'\}\r?\n\s+</button>', e_text)
assert e_old_save_btn, 'e_old_save_btn not found'
e_new_save_btn = """<button data-nav-button="true" data-save-only="true" onClick={() => handleGenerate(false)} disabled={loading} className="py-2.5 sm:py-3 px-4 bg-emerald-700 text-white font-bold rounded-lg hover:bg-emerald-600 disabled:opacity-50 transition-all order-2 sm:order-2 sm:flex-1 text-xs sm:text-sm cursor-pointer">
                  {loading ? 'Saving...' : '💾 SAVE ONLY (Enter)'}
                </button>"""
e_text = e_text.replace(e_old_save_btn.group(0), e_new_save_btn, 1)

e_old_print_btn = re.search(r'<button data-nav-button="true" onClick=\{\(\) => handleGenerate\(true\)\} disabled=\{loading \|\| \(!isFullySettled && !selectedCustomer\)\} className="([^"]*)">\r?\n\s+\{loading \? \'Processing\.\.\.\' : <><Check size=\{18\} className="mr-2" /> SAVE &amp; PRINT</>\}\r?\n\s+</button>', e_text)
assert e_old_print_btn, 'e_old_print_btn not found'
e_new_print_btn = """<button data-nav-button="true" onClick={() => handleGenerate(true)} disabled={loading} className="py-2.5 sm:py-3 px-4 bg-primary text-black font-black rounded-lg hover:bg-primary-dark disabled:opacity-50 flex justify-center items-center shadow-[0_0_15px_rgba(212,175,55,0.3)] transition-all order-1 sm:order-3 sm:flex-1 text-xs sm:text-sm cursor-pointer">
                  {loading ? 'Processing...' : <><Check size={18} className="mr-2" /> SAVE &amp; PRINT (F12)</>}
                </button>"""
e_text = e_text.replace(e_old_print_btn.group(0), e_new_print_btn, 1)

with open(exchange_path, 'w', encoding='utf-8') as f:
    f.write(e_text)

print("ExchangeCheckoutModal.tsx successfully patched!")
