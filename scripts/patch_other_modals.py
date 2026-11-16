import re

# ==================== PATCH PURCHASE CHECKOUT MODAL ====================
purchase_path = r'c:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\pages\purchase\PurchaseCheckoutModal.tsx'
with open(purchase_path, 'r', encoding='utf-8') as f:
    p_text = f.read()

# 1. Import useRef
p_text = p_text.replace(
    "import { useState, useEffect, useMemo } from 'react';",
    "import { useState, useEffect, useMemo, useRef } from 'react';"
)

# 2. cashPaid initial + ref
p_old_cash = "  const [cashPaid, setCashPaid] = useState<number>(0);"
p_new_cash = """  const [cashPaid, setCashPaid] = useState<number>(() => {
    return Math.round((payload?.grand_total || payload?.total_amount || grandTotal || 0) * 100) / 100;
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
assert p_old_cash in p_text, 'p_old_cash not found'
p_text = p_text.replace(p_old_cash, p_new_cash, 1)

# 3. In handleGenerate: remove blocking check and resolve effectiveSellerId
p_old_gen_guard = re.search(r'  const handleGenerate = async \(shouldPrint: boolean\) => \{\r?\n\s+if \(!isFullySettled && !selectedSeller\) \{.*?\r?\n\s+setLoading\(true\);', p_text, re.DOTALL)
assert p_old_gen_guard, 'p_old_gen_guard not found'

p_new_gen_guard = """  const handleGenerate = async (shouldPrint: boolean) => {
    if (cashPaid < 0 || goldGiven < 0 || silverGiven < 0) {
      toast.error('Payments/deposits cannot be negative.');
      return;
    }
    setLoading(true);

    let effectiveSellerId = selectedSeller || null;
    if (!effectiveSellerId && sellers && sellers.length > 0) {
      effectiveSellerId = sellers[0].id;
    }"""
p_text = p_text.replace(p_old_gen_guard.group(0), p_new_gen_guard, 1)

# replace seller_id: selectedSeller || null
assert 'seller_id: selectedSeller || null,' in p_text, 'seller_id not found'
p_text = p_text.replace('seller_id: selectedSeller || null,', 'seller_id: effectiveSellerId,', 1)

# 4. Add window keydown listener after handleSaveNewSupplier
p_old_save_supplier_end = re.search(r'    \} finally \{\r?\n\s+setLoading\(false\);\r?\n\s+\}\r?\n\s+\};', p_text)
assert p_old_save_supplier_end, 'p_old_save_supplier_end not found'

p_new_keys = """    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const handleModalKeys = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.preventDefault();
        if (mode === 'new_supplier') {
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
  }, [mode, onClose, loading, isFullySettled, selectedSeller, cashPaid, goldGiven, silverGiven, sellers, currentCompanyId]);"""
p_text = p_text.replace(p_old_save_supplier_end.group(0), p_new_keys, 1)

# 5. Container enter callback
p_old_container = re.search(r'        onKeyDown=\{\(e\) => handleEnterKeyNavigation\(e, \'\[data-enter-container\]\', \(\) => \{\r?\n\s+if \(!loading && \(isFullySettled \|\| selectedSeller\)\) \{\r?\n\s+handleGenerate\(false\);\r?\n\s+\}\r?\n\s+\}\)\}', p_text)
assert p_old_container, 'p_old_container not found'
p_new_container = """        onKeyDown={(e) => handleEnterKeyNavigation(e, '[data-enter-container]', () => {
          if (!loading) {
            handleGenerate(false);
          }
        })}"""
p_text = p_text.replace(p_old_container.group(0), p_new_container, 1)

# 6. cashPaid input
p_old_cash_input = re.search(r'<input type="number" min="0" value=\{cashPaid === 0 \? \'\' : cashPaid\} onChange=\{e => setCashPaid\(Number\(e\.target\.value\)\)\} placeholder="0" className="[^"]*" />', p_text)
assert p_old_cash_input, 'p_old_cash_input not found'
p_new_cash_input = """<input 
                        ref={cashInputRef}
                        type="number" 
                        min="0" 
                        value={cashPaid === 0 ? '' : cashPaid} 
                        onChange={e => setCashPaid(Number(e.target.value))} 
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
p_text = p_text.replace(p_old_cash_input.group(0), p_new_cash_input, 1)

# 7. Buttons disabled attribute
p_old_buttons = re.search(r'<button \r?\n\s+type="button"\r?\n\s+data-nav-button="true" \r?\n\s+data-save-only="true"\r?\n\s+onClick=\{\(\) => handleGenerate\(false\)\} \r?\n\s+disabled=\{loading \|\| \(!isFullySettled && !selectedSeller\)\} \r?\n\s+className="([^"]*)"\r?\n\s+>\r?\n\s+\{loading \? \'Saving\.\.\.\' : \'💾 SAVE ONLY \(Enter\)\'\}\r?\n\s+</button>\r?\n\s+<button \r?\n\s+type="button"\r?\n\s+data-nav-button="true" \r?\n\s+onClick=\{\(\) => handleGenerate\(true\)\} \r?\n\s+disabled=\{loading \|\| \(!isFullySettled && !selectedSeller\)\} \r?\n\s+className="([^"]*)"\r?\n\s+>', p_text)
assert p_old_buttons, 'p_old_buttons not found'
p_new_buttons = """<button 
                  type="button"
                  data-nav-button="true" 
                  data-save-only="true"
                  onClick={() => handleGenerate(false)} 
                  disabled={loading} 
                  className="py-2.5 sm:py-3 px-4 bg-emerald-700 hover:bg-emerald-600 focus:ring-2 focus:ring-emerald-400 text-white font-bold rounded-lg disabled:opacity-50 transition-all flex-1 text-xs sm:text-sm shadow-md flex items-center justify-center gap-1.5 cursor-pointer"
                >
                  {loading ? 'Saving...' : '💾 SAVE ONLY (Enter)'}
                </button>
                <button 
                  type="button"
                  data-nav-button="true" 
                  onClick={() => handleGenerate(true)} 
                  disabled={loading} 
                  className="py-2.5 sm:py-3 px-4 bg-primary hover:bg-primary-dark focus:ring-2 focus:ring-primary text-black font-black rounded-lg disabled:opacity-50 flex justify-center items-center shadow-[0_0_15px_rgba(212,175,55,0.3)] transition-all flex-1 text-xs sm:text-sm cursor-pointer"
                >"""
p_text = p_text.replace(p_old_buttons.group(0), p_new_buttons, 1)

with open(purchase_path, 'w', encoding='utf-8') as f:
    f.write(p_text)

print("PurchaseCheckoutModal.tsx successfully patched!")


# ==================== PATCH EXCHANGE CHECKOUT MODAL ====================
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
assert e_old_cash in e_text, 'e_old_cash not found'
e_text = e_text.replace(e_old_cash, e_new_cash, 1)

# 3. In handleGenerate: remove blocking check and resolve effectiveCustomerId
e_old_gen_guard = re.search(r'  const handleGenerate = async \(shouldPrint: boolean\) => \{\r?\n\s+if \(!isFullySettled && !selectedCustomer\) \{.*?\r?\n\s+setLoading\(true\);', e_text, re.DOTALL)
assert e_old_gen_guard, 'e_old_gen_guard not found'

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
assert 'customer_id: selectedCustomer || null,' in e_text, 'exchange customer_id not found'
e_text = e_text.replace('customer_id: selectedCustomer || null,', 'customer_id: effectiveCustomerId,', 1)

# 4. Add window keydown listener after handleSaveNewCustomer
e_old_save_cust_end = re.search(r'    \} finally \{\r?\n\s+setLoading\(false\);\r?\n\s+\}\r?\n\s+\};', e_text)
assert e_old_save_cust_end, 'e_old_save_cust_end not found'

e_new_keys = """    } finally {
      setLoading(false);
    }
  };

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
e_text = e_text.replace(e_old_save_cust_end.group(0), e_new_keys, 1)

# 5. Container enter callback
e_old_container = re.search(r'        onKeyDown=\{\(e\) => handleEnterKeyNavigation\(e, \'\[data-enter-container\]\', \(\) => \{\r?\n\s+if \(!loading && \(isFullySettled \|\| selectedCustomer\)\) \{\r?\n\s+handleGenerate\(false\);\r?\n\s+\}\r?\n\s+\}\)\}', e_text)
assert e_old_container, 'e_old_container not found'
e_new_container = """        onKeyDown={(e) => handleEnterKeyNavigation(e, '[data-enter-container]', () => {
          if (!loading) {
            handleGenerate(false);
          }
        })}"""
e_text = e_text.replace(e_old_container.group(0), e_new_container, 1)

# 6. cashReceived input
e_old_cash_input = re.search(r'<input type="number" min="0" value=\{cashReceived === 0 \? \'\' : cashReceived\} onChange=\{e => setCashReceived\(Number\(e\.target\.value\)\)\} placeholder="0" className="[^"]*" />', e_text)
assert e_old_cash_input, 'e_old_cash_input not found'
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
e_old_buttons = re.search(r'<button data-nav-button="true" onClick=\{\(\) => handleGenerate\(false\)\} disabled=\{loading \|\| \(!isFullySettled && !selectedCustomer\)\} className="([^"]*)"\r?\n\s+>\r?\n\s+\{loading \? \'Saving\.\.\.\' : \'SAVE ONLY\'\}\r?\n\s+</button>\r?\n\s+<button data-nav-button="true" onClick=\{\(\) => handleGenerate\(true\)\} disabled=\{loading \|\| \(!isFullySettled && !selectedCustomer\)\} className="([^"]*)"\r?\n\s+>', e_text)
assert e_old_buttons, 'e_old_buttons not found'
e_new_buttons = """<button data-nav-button="true" data-save-only="true" onClick={() => handleGenerate(false)} disabled={loading} className="py-2.5 sm:py-3 px-4 bg-emerald-700 text-white font-bold rounded-lg hover:bg-emerald-600 disabled:opacity-50 transition-all order-2 sm:order-2 sm:flex-1 text-xs sm:text-sm cursor-pointer">
                  {loading ? 'Saving...' : '💾 SAVE ONLY (Enter)'}
                </button>
                <button data-nav-button="true" onClick={() => handleGenerate(true)} disabled={loading} className="py-2.5 sm:py-3 px-4 bg-primary text-black font-black rounded-lg hover:bg-primary-dark disabled:opacity-50 flex justify-center items-center shadow-[0_0_15px_rgba(212,175,55,0.3)] transition-all order-1 sm:order-3 sm:flex-1 text-xs sm:text-sm cursor-pointer">"""
e_text = e_text.replace(e_old_buttons.group(0), e_new_buttons, 1)

with open(exchange_path, 'w', encoding='utf-8') as f:
    f.write(e_text)

print("ExchangeCheckoutModal.tsx successfully patched!")
