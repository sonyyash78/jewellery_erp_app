import re

p = r'C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\pages\billing\MetalCalculator.tsx'
with open(p, 'r', encoding='utf-8') as f:
    text = f.read()

# Fix corrupted CSS strings
text = text.replace('rgba(6₹82,212,0.3)', 'rgba(6,182,212,0.3)')
text = text.replace('rgba(212₹75,55,0.2)', 'rgba(212,175,55,0.2)')

# Ensure ADD TO BILL button has data-nav-button="true" and id="btn-add-to-bill"
old_add_btn = '''          <button
            onClick={isDiamond ? handleDiamondAdd : isGold ? handleGoldAdd : handleSilverAdd}
            className={`flex-1 font-bold py-3 rounded-lg flex items-center justify-center gap-2 transition-all ${isDiamond
              ? 'bg-cyan-500 hover:bg-cyan-400 text-black shadow-[0_0_15px_rgba(6,182,212,0.3)]'
              : isGold
              ? 'bg-primary hover:bg-primary-dark text-black shadow-[0_0_15px_rgba(212,175,55,0.2)]'
              : 'bg-gray-300 hover:bg-gray-400 text-black shadow-[0_0_15px_rgba(200,200,200,0.1)]'}`}
          >
            <ShoppingCart size={18} /> {editingItemId ? 'UPDATE ITEM' : 'ADD TO BILL'}
          </button>'''

new_add_btn = '''          <button
            id="btn-add-to-bill"
            data-nav-button="true"
            type="button"
            onClick={() => {
              if (isDiamond) handleDiamondAdd();
              else if (isGold) handleGoldAdd();
              else handleSilverAdd();
              // After adding to bill, focus GENERATE BILL button
              setTimeout(() => {
                const genBtn = document.getElementById('btn-generate-bill');
                if (genBtn) genBtn.focus();
              }, 120);
            }}
            className={`flex-1 font-bold py-3 rounded-lg flex items-center justify-center gap-2 transition-all focus:ring-2 focus:ring-offset-2 focus:ring-primary ${isDiamond
              ? 'bg-cyan-500 hover:bg-cyan-400 text-black shadow-[0_0_15px_rgba(6,182,212,0.3)]'
              : isGold
              ? 'bg-primary hover:bg-primary-dark text-black shadow-[0_0_15px_rgba(212,175,55,0.2)]'
              : 'bg-gray-300 hover:bg-gray-400 text-black shadow-[0_0_15px_rgba(200,200,200,0.1)]'}`}
          >
            <ShoppingCart size={18} /> {editingItemId ? 'UPDATE ITEM (Enter)' : 'ADD TO BILL (Enter)'}
          </button>'''

if old_add_btn in text:
    text = text.replace(old_add_btn, new_add_btn, 1)
    print("Updated ADD TO BILL button in MetalCalculator.tsx!")
else:
    # Try more generic replacement
    pattern = r'<button\s+onClick=\{isDiamond \? handleDiamondAdd : isGold \? handleGoldAdd : handleSilverAdd\}[\s\S]+?<\/button>'
    m = re.search(pattern, text)
    if m:
        text = text[:m.start()] + new_add_btn + text[m.end():]
        print("Updated ADD TO BILL button with regex!")
    else:
        print("Could not match ADD TO BILL button!")

# Add autofocus hook on mount
if 'focusFirstInput' not in text:
    text = text.replace(
        "import { handleEnterKeyNavigation } from '../../utils/keyboardNavigation';",
        "import { handleEnterKeyNavigation, focusFirstInput } from '../../utils/keyboardNavigation';"
    )
    # Add useEffect to focus first input on mount
    text = text.replace(
        "useEffect(() => {\n    const handleCustomSwitch",
        "useEffect(() => {\n    focusFirstInput('[data-enter-container]');\n  }, [metal]);\n\n  useEffect(() => {\n    const handleCustomSwitch"
    )
    print("Added focusFirstInput effect on mount & tab change!")

with open(p, 'w', encoding='utf-8') as f:
    f.write(text)
print("Saved MetalCalculator.tsx")
