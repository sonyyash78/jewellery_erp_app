p_pur = r'C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\pages\purchase\PurchaseMetalForm.tsx'
with open(p_pur, 'r', encoding='utf-8') as f:
    text_pur = f.read()

text_pur = text_pur.replace('rgba(6₹82,212,0.3)', 'rgba(6,182,212,0.3)')
text_pur = text_pur.replace('rgba(212₹75,55,0.2)', 'rgba(212,175,55,0.2)')

old_pur_btn = '''          <button
            onClick={isDiamond ? handleDiamondAdd : isGold ? handleGoldAdd : handleSilverAdd}
            className={`flex-1 font-bold py-3 rounded-lg flex items-center justify-center gap-2 transition-all ${isDiamond
              ? 'bg-cyan-500 hover:bg-cyan-400 text-black shadow-[0_0_15px_rgba(6,182,212,0.3)]'
              : isGold
              ? 'bg-primary hover:bg-primary-dark text-black shadow-[0_0_15px_rgba(212,175,55,0.2)]'
              : 'bg-gray-300 hover:bg-gray-400 text-black shadow-[0_0_15px_rgba(200,200,200,0.1)]'}`}
          >
            <ShoppingCart size={18} /> {editingItemId ? 'UPDATE ITEM' : 'ADD TO RECEIPT'}
          </button>'''

new_pur_btn = '''          <button
            id="btn-add-purchase-item"
            data-nav-button="true"
            type="button"
            onClick={() => {
              if (isDiamond) handleDiamondAdd();
              else if (isGold) handleGoldAdd();
              else handleSilverAdd();
            }}
            className={`flex-1 font-bold py-3 rounded-lg flex items-center justify-center gap-2 transition-all focus:ring-2 focus:ring-offset-2 focus:ring-primary ${isDiamond
              ? 'bg-cyan-500 hover:bg-cyan-400 text-black shadow-[0_0_15px_rgba(6,182,212,0.3)]'
              : isGold
              ? 'bg-primary hover:bg-primary-dark text-black shadow-[0_0_15px_rgba(212,175,55,0.2)]'
              : 'bg-gray-300 hover:bg-gray-400 text-black shadow-[0_0_15px_rgba(200,200,200,0.1)]'}`}
          >
            <ShoppingCart size={18} /> {editingItemId ? 'UPDATE ITEM (Enter)' : 'ADD TO RECEIPT (Enter)'}
          </button>'''

if old_pur_btn in text_pur:
    text_pur = text_pur.replace(old_pur_btn, new_pur_btn, 1)
    print("Updated ADD TO RECEIPT in PurchaseMetalForm.tsx!")

if 'focusFirstInput' not in text_pur:
    text_pur = text_pur.replace(
        "import { handleEnterKeyNavigation } from '../../utils/keyboardNavigation';",
        "import { handleEnterKeyNavigation, focusFirstInput } from '../../utils/keyboardNavigation';"
    )
    text_pur = text_pur.replace(
        "useEffect(() => {\n    const handleCustomSwitch",
        "useEffect(() => {\n    focusFirstInput('[data-enter-container]');\n  }, [metal]);\n\n  useEffect(() => {\n    const handleCustomSwitch"
    )

with open(p_pur, 'w', encoding='utf-8') as f:
    f.write(text_pur)
print("Saved PurchaseMetalForm.tsx")

# Now update OldItemsForm.tsx
p_exc = r'C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\pages\exchange\OldItemsForm.tsx'
with open(p_exc, 'r', encoding='utf-8') as f:
    text_exc = f.read()

text_exc = text_exc.replace('rgba(6₹82,212,0.3)', 'rgba(6,182,212,0.3)')
text_exc = text_exc.replace('rgba(212₹75,55,0.2)', 'rgba(212,175,55,0.2)')

# Ensure Add old item button has data-nav-button="true"
old_exc_btn = '''            <button
              onClick={handleAdd}
              className="w-full bg-primary hover:bg-primary-dark text-black font-bold py-2 px-4 rounded flex items-center justify-center space-x-2 transition-colors shadow-lg"
            >'''

new_exc_btn = '''            <button
              id="btn-add-old-item"
              data-nav-button="true"
              type="button"
              onClick={handleAdd}
              className="w-full bg-primary hover:bg-primary-dark text-black font-bold py-2 px-4 rounded flex items-center justify-center space-x-2 transition-colors shadow-lg focus:ring-2 focus:ring-offset-2 focus:ring-primary"
            >'''

if old_exc_btn in text_exc:
    text_exc = text_exc.replace(old_exc_btn, new_exc_btn, 1)
    print("Updated handleAdd in OldItemsForm.tsx!")

with open(p_exc, 'w', encoding='utf-8') as f:
    f.write(text_exc)
print("Saved OldItemsForm.tsx")
