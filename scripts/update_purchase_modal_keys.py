import os

path = r'C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\pages\purchase\PurchaseCheckoutModal.tsx'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Add useEffect for modal hotkeys
target_hook = "  useEffect(() => {\n    loadSellers();\n  }, []);"
new_hook = """  useEffect(() => {
    loadSellers();
  }, []);

  useEffect(() => {
    const handlePurchaseModalKeys = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.preventDefault();
        onClose();
        return;
      }
      if (e.key === 'F12') {
        e.preventDefault();
        if (!loading && (isFullySettled || selectedSeller)) {
          handleGenerate(true);
        }
        return;
      }
      if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        if (!loading && (isFullySettled || selectedSeller)) {
          handleGenerate(false);
        }
        return;
      }
    };
    window.addEventListener('keydown', handlePurchaseModalKeys);
    return () => window.removeEventListener('keydown', handlePurchaseModalKeys);
  }, [onClose, loading, isFullySettled, selectedSeller]);"""

text = text.replace(target_hook, new_hook)

# 2. Reorder buttons: SAVE ONLY first, SAVE & PRINT second, Cancel third
old_buttons = """              <div className="flex space-x-2 mt-4">

                <button onClick={onClose} className="flex-1 py-3 border border-gray-700 rounded-lg text-gray-400 hover:bg-gray-800 font-bold transition-colors">Cancel</button>

                <button data-nav-button="true" onClick={() => handleGenerate(false)} disabled={loading || (!isFullySettled && !selectedSeller)} className="flex-1 py-3 bg-gray-700 text-white font-bold rounded-lg hover:bg-gray-600 disabled:opacity-50 transition-all">

                  {loading ? 'Saving...' : 'SAVE ONLY'}

                </button>

                <button data-nav-button="true" onClick={() => handleGenerate(true)} disabled={loading || (!isFullySettled && !selectedSeller)} className="flex-1 py-3 bg-primary text-black font-black rounded-lg hover:bg-primary-dark disabled:opacity-50 flex justify-center items-center shadow-[0_0_15px_rgba(212,175,55,0.3)] transition-all">

                  {loading ? 'Processing...' : <><Check size={18} className="mr-2" /> SAVE &amp; PRINT</>}

                </button>

              </div>"""

new_buttons = """              <div className="flex flex-col sm:flex-row gap-2 mt-4 pt-3 border-t border-gray-800 bg-surface sticky bottom-0 z-10 shrink-0">
                <button 
                  type="button"
                  data-nav-button="true" 
                  data-save-only="true"
                  onClick={() => handleGenerate(false)} 
                  disabled={loading || (!isFullySettled && !selectedSeller)} 
                  className="py-2.5 sm:py-3 px-4 bg-emerald-700 hover:bg-emerald-600 focus:ring-2 focus:ring-emerald-400 text-white font-bold rounded-lg disabled:opacity-50 transition-all flex-1 text-xs sm:text-sm shadow-md flex items-center justify-center gap-1.5"
                >
                  {loading ? 'Saving...' : '💾 SAVE ONLY (Enter)'}
                </button>
                <button 
                  type="button"
                  data-nav-button="true" 
                  onClick={() => handleGenerate(true)} 
                  disabled={loading || (!isFullySettled && !selectedSeller)} 
                  className="py-2.5 sm:py-3 px-4 bg-primary hover:bg-primary-dark focus:ring-2 focus:ring-primary text-black font-black rounded-lg disabled:opacity-50 flex justify-center items-center shadow-[0_0_15px_rgba(212,175,55,0.3)] transition-all flex-1 text-xs sm:text-sm"
                >
                  {loading ? 'Processing...' : <><Check size={18} className="mr-2" /> SAVE &amp; PRINT (F12)</>}
                </button>
                <button 
                  type="button"
                  data-nav-button="true" 
                  onClick={onClose} 
                  className="py-2.5 sm:py-3 px-4 border border-gray-700 rounded-lg text-gray-400 hover:bg-gray-800 font-bold transition-colors flex-1 text-xs sm:text-sm"
                >
                  Cancel (Esc)
                </button>
              </div>"""

text = text.replace(old_buttons, new_buttons)

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)

print("PurchaseCheckoutModal.tsx updated successfully!")
