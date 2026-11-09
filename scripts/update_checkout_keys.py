path = r'C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\pages\billing\CheckoutModal.tsx'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Add modal keydown handler for F12, Ctrl+Enter, Esc
old_esc = """  useEffect(() => {
    const handleModalEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    window.addEventListener('keydown', handleModalEsc);
    return () => window.removeEventListener('keydown', handleModalEsc);
  }, [onClose]);"""

new_esc = """  useEffect(() => {
    const handleModalKeys = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.preventDefault();
        onClose();
        return;
      }
      // F12 inside modal triggers SAVE & PRINT
      if (e.key === 'F12') {
        e.preventDefault();
        if (!loading && (isFullySettled || selectedCustomer)) {
          handleGenerate(true);
        }
        return;
      }
      // Ctrl+Enter inside modal triggers SAVE ONLY
      if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        if (!loading && (isFullySettled || selectedCustomer)) {
          handleGenerate(false);
        }
        return;
      }
    };
    window.addEventListener('keydown', handleModalKeys);
    return () => window.removeEventListener('keydown', handleModalKeys);
  }, [onClose, loading, isFullySettled, selectedCustomer]);"""

text = text.replace(old_esc, new_esc)

# 2. Update address input so pressing Enter directly targets SAVE ONLY
old_addr = """                    <input 
                      type="text"
                      value={buyerDetails.address}
                      onChange={e => setBuyerDetails({ ...buyerDetails, address: e.target.value })}
                      placeholder="e.g. 167, Ward No. 3, Khedawas, Takhatgarh, Pali (Raj.)-306912"
                      className="w-full bg-background border border-gray-700 rounded px-2.5 py-1.5 text-xs text-white outline-none focus:border-primary font-medium"
                    />"""

new_addr = """                    <input 
                      type="text"
                      value={buyerDetails.address}
                      onChange={e => setBuyerDetails({ ...buyerDetails, address: e.target.value })}
                      onKeyDown={e => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                          e.preventDefault();
                          const saveBtn = document.querySelector<HTMLButtonElement>('[data-save-only="true"]');
                          saveBtn?.focus();
                        }
                      }}
                      placeholder="e.g. 167, Ward No. 3, Khedawas, Takhatgarh, Pali (Raj.)-306912"
                      className="w-full bg-background border border-gray-700 rounded px-2.5 py-1.5 text-xs text-white outline-none focus:border-primary font-medium"
                    />"""

text = text.replace(old_addr, new_addr)

# 3. Update bottom buttons: SAVE ONLY first, SAVE & PRINT second, Cancel third
old_buttons = """              <div className="flex flex-col sm:flex-row gap-2 mt-4 pt-3 border-t border-gray-800 bg-surface sticky bottom-0 z-10 shrink-0">
                <button data-nav-button="true" onClick={onClose} className="py-2.5 sm:py-3 px-4 border border-gray-700 rounded-lg text-gray-400 hover:bg-gray-800 font-bold transition-colors order-3 sm:order-1 sm:flex-1 text-xs sm:text-sm">Cancel</button>
                <button data-nav-button="true" onClick={() => handleGenerate(false)} disabled={loading || (!isFullySettled && !selectedCustomer)} className="py-2.5 sm:py-3 px-4 bg-gray-700 text-white font-bold rounded-lg hover:bg-gray-600 disabled:opacity-50 transition-all order-2 sm:order-2 sm:flex-1 text-xs sm:text-sm">
                  {loading ? 'Saving...' : 'SAVE ONLY'}
                </button>
                <button data-nav-button="true" onClick={() => handleGenerate(true)} disabled={loading || (!isFullySettled && !selectedCustomer)} className="py-2.5 sm:py-3 px-4 bg-primary text-black font-black rounded-lg hover:bg-primary-dark disabled:opacity-50 flex justify-center items-center shadow-[0_0_15px_rgba(212,175,55,0.3)] transition-all order-1 sm:order-3 sm:flex-1 text-xs sm:text-sm">
                  {loading ? 'Processing...' : <><Check size={18} className="mr-2" /> SAVE &amp; PRINT</>}
                </button>
              </div>"""

new_buttons = """              <div className="flex flex-col sm:flex-row gap-2 mt-4 pt-3 border-t border-gray-800 bg-surface sticky bottom-0 z-10 shrink-0">
                <button 
                  type="button"
                  data-nav-button="true" 
                  data-save-only="true"
                  onClick={() => handleGenerate(false)} 
                  disabled={loading || (!isFullySettled && !selectedCustomer)} 
                  className="py-2.5 sm:py-3 px-4 bg-emerald-700 hover:bg-emerald-600 focus:ring-2 focus:ring-emerald-400 text-white font-bold rounded-lg disabled:opacity-50 transition-all flex-1 text-xs sm:text-sm shadow-md flex items-center justify-center gap-1.5"
                >
                  {loading ? 'Saving...' : '💾 SAVE ONLY (Enter)'}
                </button>
                <button 
                  type="button"
                  data-nav-button="true" 
                  onClick={() => handleGenerate(true)} 
                  disabled={loading || (!isFullySettled && !selectedCustomer)} 
                  className="py-2.5 sm:py-3 px-4 bg-primary hover:bg-primary-dark focus:ring-2 focus:ring-primary text-black font-black rounded-lg disabled:opacity-50 flex justify-center items-center shadow-[0_0_15px_rgba(212,175,55,0.3)] transition-all flex-1 text-xs sm:text-sm"
                >
                  {loading ? 'Processing...' : <><Check size={18} className="mr-1.5" /> SAVE &amp; PRINT (F12)</>}
                </button>
                <button 
                  type="button" 
                  onClick={onClose} 
                  className="py-2.5 sm:py-3 px-4 border border-gray-700 rounded-lg text-gray-400 hover:bg-gray-800 font-bold transition-colors text-xs sm:text-sm"
                >
                  Cancel (Esc)
                </button>
              </div>"""

text = text.replace(old_buttons, new_buttons)

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
print('Updated CheckoutModal.tsx successfully!')
