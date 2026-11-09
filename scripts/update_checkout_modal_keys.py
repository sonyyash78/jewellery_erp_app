p = r'C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\pages\billing\CheckoutModal.tsx'
with open(p, 'r', encoding='utf-8') as f:
    text = f.read()

# Add focusFirstInput import and useEffect on mount
if 'focusFirstInput' not in text:
    text = text.replace(
        "import { handleEnterKeyNavigation } from '../../utils/keyboardNavigation';",
        "import { handleEnterKeyNavigation, focusFirstInput } from '../../utils/keyboardNavigation';"
    )

# Add autofocus useEffect
if "focusFirstInput('[data-enter-container]')" not in text:
    marker = "  useEffect(() => {\n    loadCustomers();\n  }, []);"
    replacement = "  useEffect(() => {\n    loadCustomers();\n    focusFirstInput('[data-enter-container]');\n  }, []);"
    text = text.replace(marker, replacement, 1)
    print("Added autofocus on mount in CheckoutModal!")

# Update Cancel button to have data-nav-button="true"
old_cancel = '''                <button 
                  type="button" 
                  onClick={onClose} 
                  className="py-2.5 sm:py-3 px-4 border border-gray-700 rounded-lg text-gray-400 hover:bg-gray-800 font-bold transition-colors text-xs sm:text-sm"
                >
                  Cancel (Esc)
                </button>'''

new_cancel = '''                <button 
                  type="button"
                  data-nav-button="true" 
                  onClick={onClose} 
                  className="py-2.5 sm:py-3 px-4 border border-gray-700 rounded-lg text-gray-400 hover:bg-gray-800 font-bold transition-colors text-xs sm:text-sm"
                >
                  Cancel (Esc)
                </button>'''

if old_cancel in text:
    text = text.replace(old_cancel, new_cancel, 1)
    print("Updated Cancel button in CheckoutModal!")

with open(p, 'w', encoding='utf-8') as f:
    f.write(text)
print("Saved CheckoutModal.tsx")
