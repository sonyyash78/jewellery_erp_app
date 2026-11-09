def wire_metal_calculator():
    path = r"C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\pages\billing\MetalCalculator.tsx"
    with open(path, "r", encoding="utf-8") as f:
        c = f.read()

    if "handleEnterKeyNavigation" not in c:
        c = "import { handleEnterKeyNavigation } from '../../utils/keyboardNavigation';\n" + c

    # Add focus reset after add
    focus_reset = """    setTimeout(() => {
      const firstInput = document.querySelector<HTMLInputElement>('[data-enter-container] input:not([disabled])');
      firstInput?.focus();
      firstInput?.select();
    }, 50);"""

    if focus_reset not in c:
        c = c.replace(
            "toast.success(editingItemId ? 'Item Updated in Bill' : 'Added to Bill');",
            f"toast.success(editingItemId ? 'Item Updated in Bill' : 'Added to Bill');\n{focus_reset}"
        )

    # Attach to container
    target_container = '<div className="h-full flex flex-col p-4 bg-surface text-textMain overflow-hidden">'
    replace_container = """<div 
      data-enter-container="true"
      onKeyDown={(e) => handleEnterKeyNavigation(e, '[data-enter-container]', () => {
        if (isDiamond) handleDiamondAdd();
        else if (isGold) handleGoldAdd();
        else handleSilverAdd();
      })}
      className="h-full flex flex-col p-4 bg-surface text-textMain overflow-hidden">"""

    if target_container in c:
        c = c.replace(target_container, replace_container)

    with open(path, "w", encoding="utf-8") as f:
        f.write(c)
    print("Wired Enter key in MetalCalculator.tsx")

def wire_checkout_modal():
    path = r"C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\pages\billing\CheckoutModal.tsx"
    with open(path, "r", encoding="utf-8") as f:
        c = f.read()

    if "handleEnterKeyNavigation" not in c:
        c = "import { handleEnterKeyNavigation } from '../../utils/keyboardNavigation';\n" + c

    target_div = '<div className="bg-surface border border-gray-700 rounded-2xl shadow-2xl w-full max-w-4xl max-h-[92vh] flex flex-col overflow-hidden my-auto">'
    replace_div = """<div 
        data-enter-container="true"
        onKeyDown={(e) => handleEnterKeyNavigation(e, '[data-enter-container]', () => {
          if (!loading && (isFullySettled || selectedCustomer)) {
            handleGenerate(false);
          }
        })}
        className="bg-surface border border-gray-700 rounded-2xl shadow-2xl w-full max-w-4xl max-h-[92vh] flex flex-col overflow-hidden my-auto">"""

    if target_div in c:
        c = c.replace(target_div, replace_div)

    with open(path, "w", encoding="utf-8") as f:
        f.write(c)
    print("Wired Enter key in CheckoutModal.tsx")

def wire_purchase_form():
    path = r"C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\pages\purchase\PurchaseMetalForm.tsx"
    with open(path, "r", encoding="utf-8") as f:
        c = f.read()

    if "handleEnterKeyNavigation" not in c:
        c = "import { handleEnterKeyNavigation } from '../../utils/keyboardNavigation';\n" + c

    target_container = '<div className="h-full flex flex-col p-4 bg-surface text-textMain overflow-hidden">'
    replace_container = """<div 
      data-enter-container="true"
      onKeyDown={(e) => handleEnterKeyNavigation(e, '[data-enter-container]', () => {
        if (isDiamond) handleDiamondAdd();
        else if (isGold) handleGoldAdd();
        else handleSilverAdd();
      })}
      className="h-full flex flex-col p-4 bg-surface text-textMain overflow-hidden">"""

    if target_container in c:
        c = c.replace(target_container, replace_container)

    with open(path, "w", encoding="utf-8") as f:
        f.write(c)
    print("Wired Enter key in PurchaseMetalForm.tsx")

def wire_purchase_checkout():
    path = r"C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\pages\purchase\PurchaseCheckoutModal.tsx"
    with open(path, "r", encoding="utf-8") as f:
        c = f.read()

    if "handleEnterKeyNavigation" not in c:
        c = "import { handleEnterKeyNavigation } from '../../utils/keyboardNavigation';\n" + c

    target_div = '<div className="bg-surface border border-gray-700 rounded-2xl shadow-2xl w-full max-w-3xl max-h-[92vh] flex flex-col overflow-hidden my-auto">'
    replace_div = """<div 
        data-enter-container="true"
        onKeyDown={(e) => handleEnterKeyNavigation(e, '[data-enter-container]', () => {
          if (!loading && (isFullySettled || selectedSeller)) {
            handleGenerate();
          }
        })}
        className="bg-surface border border-gray-700 rounded-2xl shadow-2xl w-full max-w-3xl max-h-[92vh] flex flex-col overflow-hidden my-auto">"""

    if target_div in c:
        c = c.replace(target_div, replace_div)

    with open(path, "w", encoding="utf-8") as f:
        f.write(c)
    print("Wired Enter key in PurchaseCheckoutModal.tsx")

def wire_exchange_form():
    path = r"C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\pages\exchange\OldItemsForm.tsx"
    with open(path, "r", encoding="utf-8") as f:
        c = f.read()

    if "handleEnterKeyNavigation" not in c:
        c = "import { handleEnterKeyNavigation } from '../../utils/keyboardNavigation';\n" + c

    target_form = '<form onSubmit={handleSubmit} className="space-y-4">'
    replace_form = """<form 
        data-enter-container="true"
        onKeyDown={(e) => handleEnterKeyNavigation(e, '[data-enter-container]')}
        onSubmit={handleSubmit} 
        className="space-y-4">"""

    if target_form in c:
        c = c.replace(target_form, replace_form)

    with open(path, "w", encoding="utf-8") as f:
        f.write(c)
    print("Wired Enter key in OldItemsForm.tsx")

def wire_exchange_checkout():
    path = r"C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\pages\exchange\ExchangeCheckoutModal.tsx"
    with open(path, "r", encoding="utf-8") as f:
        c = f.read()

    if "handleEnterKeyNavigation" not in c:
        c = "import { handleEnterKeyNavigation } from '../../utils/keyboardNavigation';\n" + c

    target_div = '<div className="bg-surface border border-gray-700 rounded-2xl shadow-2xl w-full max-w-3xl max-h-[92vh] flex flex-col overflow-hidden my-auto">'
    replace_div = """<div 
        data-enter-container="true"
        onKeyDown={(e) => handleEnterKeyNavigation(e, '[data-enter-container]', () => {
          if (!loading && (isFullySettled || selectedCustomer)) {
            handleGenerate();
          }
        })}
        className="bg-surface border border-gray-700 rounded-2xl shadow-2xl w-full max-w-3xl max-h-[92vh] flex flex-col overflow-hidden my-auto">"""

    if target_div in c:
        c = c.replace(target_div, replace_div)

    with open(path, "w", encoding="utf-8") as f:
        f.write(c)
    print("Wired Enter key in ExchangeCheckoutModal.tsx")

if __name__ == "__main__":
    wire_metal_calculator()
    wire_checkout_modal()
    wire_purchase_form()
    wire_purchase_checkout()
    wire_exchange_form()
    wire_exchange_checkout()
