import os

repo_root = r"C:\Users\YASH SONI\Desktop\jeweller-app"

# 1. Update frontend/src/utils/keyboardNavigation.ts
nav_file = os.path.join(repo_root, "frontend", "src", "utils", "keyboardNavigation.ts")

new_nav_code = '''import type { KeyboardEvent } from 'react';

export interface KeyNavOptions {
  containerSelector?: string;
  onComplete?: () => void;
  onCancel?: () => void;
  enableArrows?: boolean;
}

/**
 * Handles keyboard navigation (Enter, Up, Down, Left, Right, Escape) across all form inputs,
 * selects, and action buttons.
 */
export function handleFormKeyNavigation(
  e: KeyboardEvent<HTMLElement>,
  optionsOrSelector: string | KeyNavOptions = '[data-enter-container]',
  maybeOnComplete?: () => void
) {
  let containerSelector = '[data-enter-container]';
  let onComplete = maybeOnComplete;
  let onCancel: (() => void) | undefined;
  let enableArrows = true;

  if (typeof optionsOrSelector === 'string') {
    containerSelector = optionsOrSelector;
  } else if (typeof optionsOrSelector === 'object') {
    containerSelector = optionsOrSelector.containerSelector || '[data-enter-container]';
    onComplete = optionsOrSelector.onComplete || maybeOnComplete;
    onCancel = optionsOrSelector.onCancel;
    if (optionsOrSelector.enableArrows !== undefined) {
      enableArrows = optionsOrSelector.enableArrows;
    }
  }

  const target = e.target as HTMLElement;

  // ESCAPE: Close or Cancel
  if (e.key === 'Escape') {
    if (onCancel) {
      e.preventDefault();
      onCancel();
    }
    return;
  }

  // Preserve normal Enter/Arrow behavior inside multi-line textareas (unless Ctrl+Enter)
  if (target.tagName === 'TEXTAREA') {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      if (onComplete) onComplete();
    }
    return;
  }

  const isEnter = e.key === 'Enter' && !e.shiftKey;
  const isDown = enableArrows && e.key === 'ArrowDown' && !e.altKey;
  const isUp = enableArrows && e.key === 'ArrowUp' && !e.altKey;
  const isRight = enableArrows && e.key === 'ArrowRight' && !e.altKey && !e.ctrlKey;
  const isLeft = enableArrows && e.key === 'ArrowLeft' && !e.altKey && !e.ctrlKey;

  if (!isEnter && !isDown && !isUp && !isRight && !isLeft) return;

  const container = target.closest(containerSelector) || target.closest('form');
  if (!container) return;

  // Collect all navigable inputs, selects, and action buttons in DOM order
  const focusables = Array.from(
    container.querySelectorAll<HTMLElement>(
      'input:not([disabled]):not([type="hidden"]):not([readonly]):not([type="radio"]):not([type="checkbox"]), select:not([disabled]), button[data-nav-button="true"], button[type="submit"]'
    )
  ).filter(el => {
    return el.offsetParent !== null && !el.classList.contains('cursor-not-allowed') && el.tabIndex !== -1;
  });

  const currentIndex = focusables.indexOf(target);
  if (currentIndex === -1) return;

  const isButton = target.tagName === 'BUTTON';

  // For buttons, Left and Right arrow keys move between adjacent buttons
  if (isButton && (isLeft || isRight)) {
    e.preventDefault();
    const step = isRight ? 1 : -1;
    const nextIdx = currentIndex + step;
    if (nextIdx >= 0 && nextIdx < focusables.length) {
      focusables[nextIdx].focus();
    }
    return;
  }

  // If inside an input, only navigate on Left/Right if cursor is at the boundary
  if (!isButton && target instanceof HTMLInputElement) {
    const len = target.value.length;
    if (isRight) {
      const isAtEnd = target.selectionStart === len && target.selectionEnd === len;
      const isAllSelected = target.selectionStart === 0 && target.selectionEnd === len && len > 0;
      if (!isAtEnd && !isAllSelected) return; // Keep cursor within word
    }
    if (isLeft) {
      const isAtStart = target.selectionStart === 0 && target.selectionEnd === 0;
      const isAllSelected = target.selectionStart === 0 && target.selectionEnd === len && len > 0;
      if (!isAtStart && !isAllSelected) return; // Keep cursor within word
    }
  }

  // FORWARD NAVIGATION (Enter, Down, Right)
  if (isEnter || isDown || isRight) {
    if (currentIndex < focusables.length - 1) {
      e.preventDefault();
      const nextEl = focusables[currentIndex + 1];
      nextEl.focus();
      if (nextEl instanceof HTMLInputElement && (nextEl.type === 'text' || nextEl.type === 'number')) {
        nextEl.select();
      }
    } else if (currentIndex === focusables.length - 1) {
      if (isEnter) {
        e.preventDefault();
        if (isButton) {
          (target as HTMLButtonElement).click();
        } else if (onComplete) {
          onComplete();
        } else {
          const submitBtn = container.querySelector<HTMLButtonElement>(
            'button[type="submit"], button[data-action="submit"], button[data-nav-button="true"]:last-of-type'
          );
          if (submitBtn && !submitBtn.disabled) {
            submitBtn.click();
          }
        }
      }
    }
    return;
  }

  // BACKWARD NAVIGATION (Up, Left)
  if (isUp || isLeft) {
    if (currentIndex > 0) {
      e.preventDefault();
      const prevEl = focusables[currentIndex - 1];
      prevEl.focus();
      if (prevEl instanceof HTMLInputElement && (prevEl.type === 'text' || prevEl.type === 'number')) {
        prevEl.select();
      }
    }
    return;
  }
}

// Keep handleEnterKeyNavigation as an alias for full backwards compatibility
export const handleEnterKeyNavigation = handleFormKeyNavigation;

/**
 * Focuses the first visible input field within a container and selects its content.
 */
export function focusFirstInput(containerSelector: string = '[data-enter-container]') {
  setTimeout(() => {
    const el = document.querySelector<HTMLInputElement | HTMLSelectElement>(
      `${containerSelector} input:not([disabled]):not([readonly]):not([type="hidden"]), ${containerSelector} select:not([disabled])`
    );
    if (el) {
      el.focus();
      if (el instanceof HTMLInputElement && (el.type === 'text' || el.type === 'number')) {
        el.select();
      }
    }
  }, 50);
}
'''

with open(nav_file, "w", encoding="utf-8") as f:
    f.write(new_nav_code)
print("Updated keyboardNavigation.ts with Up/Down/Left/Right/Enter support")

# 2. Update MetalCalculator.tsx to add F1/F2/F3 metal switching
mc_path = os.path.join(repo_root, "frontend", "src", "pages", "billing", "MetalCalculator.tsx")
with open(mc_path, "r", encoding="utf-8") as f:
    mc_code = f.read()

hotkey_mc = """  useEffect(() => {
    const handleCalculatorHotkeys = (e: KeyboardEvent) => {
      // Don't intercept if inside checkout modal or typing in textarea
      if (document.querySelector('.fixed.inset-0.z-50')) return;
      if ((e.altKey && (e.key === 'g' || e.key === 'G')) || e.key === 'F1') {
        e.preventDefault();
        setMetal('Gold');
        setTimeout(() => {
          const firstInput = document.querySelector<HTMLInputElement>('[data-enter-container] input:not([disabled])');
          firstInput?.focus();
          firstInput?.select();
        }, 50);
      } else if ((e.altKey && (e.key === 's' || e.key === 'S')) || e.key === 'F2') {
        e.preventDefault();
        setMetal('Silver');
        setTimeout(() => {
          const firstInput = document.querySelector<HTMLInputElement>('[data-enter-container] input:not([disabled])');
          firstInput?.focus();
          firstInput?.select();
        }, 50);
      } else if ((e.altKey && (e.key === 'd' || e.key === 'D')) || e.key === 'F3') {
        e.preventDefault();
        setMetal('Diamond');
        setTimeout(() => {
          const firstInput = document.querySelector<HTMLInputElement>('[data-enter-container] input:not([disabled])');
          firstInput?.focus();
          firstInput?.select();
        }, 50);
      }
    };
    window.addEventListener('keydown', handleCalculatorHotkeys);
    return () => window.removeEventListener('keydown', handleCalculatorHotkeys);
  }, []);"""

if "handleCalculatorHotkeys" not in mc_code:
    target_pos = "  const handleMetalSwitch = (m: 'Gold' | 'Silver' | 'Diamond') => {\n"
    if target_pos in mc_code:
        mc_code = mc_code.replace(target_pos, target_pos + hotkey_mc + "\n")
        print("Added hotkeys (F1/F2/F3/Alt+G/S/D) to MetalCalculator.tsx")
        with open(mc_path, "w", encoding="utf-8") as f:
            f.write(mc_code)

# 3. Update CheckoutModal.tsx to add data-nav-button on action buttons and Escape key handling
chk_path = os.path.join(repo_root, "frontend", "src", "pages", "billing", "CheckoutModal.tsx")
with open(chk_path, "r", encoding="utf-8") as f:
    chk_code = f.read()

# Add Escape listener
esc_listener = """  useEffect(() => {
    const handleModalEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.preventDefault();
        if (mode === 'new_customer') {
          setMode('checkout');
        } else {
          onClose();
        }
      }
    };
    window.addEventListener('keydown', handleModalEsc);
    return () => window.removeEventListener('keydown', handleModalEsc);
  }, [mode, onClose]);"""

if "handleModalEsc" not in chk_code:
    chk_code = chk_code.replace("  const [chequeNo, setChequeNo] = useState('');",
                                "  const [chequeNo, setChequeNo] = useState('');\n" + esc_listener)
    print("Added Escape key listener to CheckoutModal.tsx")

# Add data-nav-button to buttons
chk_code = chk_code.replace('<button onClick={onClose} className="py-2.5 sm:py-3 px-4 border',
                            '<button data-nav-button="true" onClick={onClose} className="py-2.5 sm:py-3 px-4 border')
chk_code = chk_code.replace('<button onClick={() => handleGenerate(false)} disabled={loading',
                            '<button data-nav-button="true" onClick={() => handleGenerate(false)} disabled={loading')
chk_code = chk_code.replace('<button onClick={() => handleGenerate(true)} disabled={loading',
                            '<button data-nav-button="true" onClick={() => handleGenerate(true)} disabled={loading')

with open(chk_path, "w", encoding="utf-8") as f:
    f.write(chk_code)
print("Updated action buttons with data-nav-button in CheckoutModal.tsx")

# 4. Update AdminLayout.tsx to add global shortcuts
admin_path = os.path.join(repo_root, "frontend", "src", "components", "layout", "AdminLayout.tsx")
with open(admin_path, "r", encoding="utf-8") as f:
    admin_code = f.read()

# Import useNavigate if not present
if "useNavigate" not in admin_code:
    admin_code = admin_code.replace("import { Outlet, useLocation, Link, Navigate } from 'react-router-dom';",
                                    "import { Outlet, useLocation, Link, Navigate, useNavigate } from 'react-router-dom';")

# Add useCompanyStore import if not present
if "useCompanyStore" not in admin_code:
    admin_code = admin_code.replace("import CompanySelector from '../common/CompanySelector';",
                                    "import CompanySelector from '../common/CompanySelector';\nimport { useCompanyStore } from '../../store/companyStore';")

global_shortcuts_code = """  const navigate = useNavigate();
  const { companies, selectCompany } = useCompanyStore();

  useEffect(() => {
    const handleGlobalKeyDown = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement;
      const isInput = target && (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.tagName === 'SELECT');

      // Alt + 1 or Alt + 2: Company switching anywhere
      if (e.altKey && (e.key === '1' || e.key === '2')) {
        e.preventDefault();
        const cid = e.key === '1' ? 1 : 2;
        const comp = companies.find(c => c.id === cid);
        if (comp) {
          selectCompany(cid);
          toast.success(`Switched to ${comp.name} (${comp.gst_enabled ? 'GST' : 'Normal'})`, { id: 'comp-switch' });
        }
        return;
      }

      // F12 or Ctrl+Enter: Quick Checkout trigger
      if (e.key === 'F12' || (e.key === 'Enter' && (e.ctrlKey || e.metaKey))) {
        e.preventDefault();
        window.dispatchEvent(new CustomEvent('trigger-quick-checkout'));
        return;
      }

      // Global Navigation with Function Keys or Alt+Letter (even when in inputs if function key)
      if (e.key === 'F4' || (e.altKey && (e.key === 'b' || e.key === 'B'))) {
        e.preventDefault();
        navigate('/billing');
      } else if (e.key === 'F5' || (e.altKey && (e.key === 'p' || e.key === 'P'))) {
        e.preventDefault();
        navigate('/purchases');
      } else if (e.key === 'F6' || (e.altKey && (e.key === 'e' || e.key === 'E'))) {
        e.preventDefault();
        navigate('/exchange');
      } else if (e.key === 'F7' || (e.altKey && (e.key === 'i' || e.key === 'I'))) {
        e.preventDefault();
        navigate('/invoices');
      } else if (e.key === 'F8' || (e.altKey && (e.key === 'r' || e.key === 'R'))) {
        e.preventDefault();
        navigate('/reports');
      } else if (e.key === 'F9' || (e.altKey && (e.key === 'c' || e.key === 'C'))) {
        e.preventDefault();
        navigate('/customers');
      } else if (e.key === 'F10' || (e.altKey && (e.key === 's' || e.key === 'S'))) {
        e.preventDefault();
        navigate('/settings');
      } else if (e.altKey && (e.key === 'h' || e.key === 'H')) {
        e.preventDefault();
        navigate('/');
      }
    };

    window.addEventListener('keydown', handleGlobalKeyDown);
    return () => window.removeEventListener('keydown', handleGlobalKeyDown);
  }, [navigate, companies, selectCompany]);"""

if "handleGlobalKeyDown" not in admin_code:
    target_admin_pos = "  const isElectron = Boolean((window as any).electronAPI);\n"
    if target_admin_pos in admin_code:
        admin_code = admin_code.replace(target_admin_pos, target_admin_pos + global_shortcuts_code + "\n")
        print("Added global keyboard shortcuts to AdminLayout.tsx")
        with open(admin_path, "w", encoding="utf-8") as f:
            f.write(admin_code)

# 5. Update LiveBillSummary.tsx to listen for trigger-quick-checkout
lbs_path = os.path.join(repo_root, "frontend", "src", "pages", "billing", "LiveBillSummary.tsx")
with open(lbs_path, "r", encoding="utf-8") as f:
    lbs_code = f.read()

quick_chk_listener = """    const handleQuickCheckout = () => {
      if (cart.length > 0) {
        handleGenerate();
      } else {
        toast.error('Add at least one item before checkout');
      }
    };
    window.addEventListener('trigger-quick-checkout', handleQuickCheckout);"""

quick_chk_cleanup = """      window.removeEventListener('trigger-quick-checkout', handleQuickCheckout);"""

if "trigger-quick-checkout" not in lbs_code:
    lbs_code = lbs_code.replace("    window.addEventListener('keydown', handleKeyDown);",
                                f"{quick_chk_listener}\n    window.addEventListener('keydown', handleKeyDown);")
    lbs_code = lbs_code.replace("    return () => window.removeEventListener('keydown', handleKeyDown);",
                                f"    return () => {{\n      window.removeEventListener('keydown', handleKeyDown);\n{quick_chk_cleanup}\n    }};")
    print("Added trigger-quick-checkout listener to LiveBillSummary.tsx")
    with open(lbs_path, "w", encoding="utf-8") as f:
        f.write(lbs_code)

print("All keyboard navigation enhancements applied successfully!")
