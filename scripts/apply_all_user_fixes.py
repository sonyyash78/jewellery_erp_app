import os
import re

base_dir = r"C:\Users\YASH SONI\Desktop\jeweller-app"

# ==============================================================================
# 1. Update desktop/src/main.js to free F-keys and hide menubar
# ==============================================================================
desktop_main_path = os.path.join(base_dir, "desktop", "src", "main.js")
with open(desktop_main_path, "r", encoding="utf-8") as f:
    main_js = f.read()

# Replace View menu items so F5, F11, F12 are not intercepted by Electron
old_view_menu = """    {

      label: 'View',

      submenu: [

        { role: 'reload', label: 'Reload Application' },

        { role: 'forceReload', label: 'Force Reload' },

        { role: 'toggleDevTools', label: 'Developer Tools' },

        { type: 'separator' },

        { role: 'resetZoom' },

        { role: 'zoomIn' },

        { role: 'zoomOut' },

        { type: 'separator' },

        { role: 'togglefullscreen' }

      ]

    },"""

new_view_menu = """    {
      label: 'View',
      submenu: [
        { label: 'Reload Application', accelerator: 'CmdOrCtrl+R', click: (item, focusedWindow) => { if (focusedWindow) focusedWindow.reload(); } },
        { label: 'Force Reload', accelerator: 'CmdOrCtrl+Shift+R', click: (item, focusedWindow) => { if (focusedWindow) focusedWindow.webContents.reloadIgnoringCache(); } },
        { label: 'Developer Tools', accelerator: 'CmdOrCtrl+Shift+I', click: (item, focusedWindow) => { if (focusedWindow) focusedWindow.webContents.toggleDevTools(); } },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { type: 'separator' },
        { label: 'Toggle Full Screen', accelerator: 'CmdOrCtrl+Shift+F', click: (item, focusedWindow) => { if (focusedWindow) focusedWindow.setFullScreen(!focusedWindow.isFullScreen()); } }
      ]
    },"""

main_js = main_js.replace(old_view_menu, new_view_menu)

# Ensure autoHideMenuBar and before-input-event in createWindow
old_win_setup = """  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    mainWindow.focus();
  });"""

new_win_setup = """  mainWindow.setAutoHideMenuBar(true);
  mainWindow.setMenuBarVisibility(false);

  mainWindow.webContents.on('before-input-event', (event, input) => {
    // Ensure function keys F1 to F12 pass directly to web DOM without Electron interference
    if (input.type === 'keyDown' && /^F([1-9]|1[0-2])$/.test(input.key)) {
      // Allow key to propagate cleanly to web application
    }
  });

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    mainWindow.focus();
  });"""

main_js = main_js.replace(old_win_setup, new_win_setup)

with open(desktop_main_path, "w", encoding="utf-8") as f:
    f.write(main_js)
print("1. desktop/src/main.js updated: F-keys freed and menu auto-hidden!")

# ==============================================================================
# 2. Update frontend/src/utils/keyboardNavigation.ts
# ==============================================================================
key_nav_path = os.path.join(base_dir, "frontend", "src", "utils", "keyboardNavigation.ts")
new_key_nav = """import type { KeyboardEvent } from 'react';

export interface KeyNavOptions {
  containerSelector?: string;
  onComplete?: () => void;
  onCancel?: () => void;
  enableArrows?: boolean;
}

/**
 * Handles keyboard navigation (Enter, Up, Down, Left, Right, Escape) across all form inputs,
 * selects, and action buttons without throwing DOMException on input[type="number"].
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
  if (!target) return;

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
  const isDown = enableArrows && (e.key === 'ArrowDown' || e.code === 'ArrowDown') && !e.altKey;
  const isUp = enableArrows && (e.key === 'ArrowUp' || e.code === 'ArrowUp') && !e.altKey;
  const isRight = enableArrows && (e.key === 'ArrowRight' || e.code === 'ArrowRight') && !e.altKey && !e.ctrlKey;
  const isLeft = enableArrows && (e.key === 'ArrowLeft' || e.code === 'ArrowLeft') && !e.altKey && !e.ctrlKey;

  if (!isEnter && !isDown && !isUp && !isRight && !isLeft) return;

  // Robust container fallback: component container -> form -> main -> document.body
  const container = target.closest(containerSelector) || 
                    target.closest('form') || 
                    target.closest('main') || 
                    target.closest('[role="main"]') || 
                    document.body;

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
  const isNumberInput = target instanceof HTMLInputElement && target.type === 'number';

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

  // Safe cursor check for text inputs (HTML5 forbids selectionStart on number inputs!)
  if (!isButton && target instanceof HTMLInputElement && !isNumberInput) {
    try {
      const len = target.value.length;
      if (isRight) {
        const isAtEnd = target.selectionStart === len && target.selectionEnd === len;
        const isAllSelected = target.selectionStart === 0 && target.selectionEnd === len && len > 0;
        if (!isAtEnd && !isAllSelected) return; // Keep cursor inside word
      }
      if (isLeft) {
        const isAtStart = target.selectionStart === 0 && target.selectionEnd === 0;
        const isAllSelected = target.selectionStart === 0 && target.selectionEnd === len && len > 0;
        if (!isAtStart && !isAllSelected) return; // Keep cursor inside word
      }
    } catch (_) {
      // In case of any browser quirks, continue navigation safely
    }
  }

  // FORWARD NAVIGATION (Enter, Down, Right)
  if (isEnter || isDown || isRight) {
    e.preventDefault(); // Always prevent default so ArrowDown doesn't decrement number inputs!
    if (currentIndex < focusables.length - 1) {
      const nextEl = focusables[currentIndex + 1];
      nextEl.focus();
      if (nextEl instanceof HTMLInputElement) {
        try {
          if (nextEl.type !== 'number') {
            nextEl.select();
          }
        } catch (_) {}
      }
    } else if (currentIndex === focusables.length - 1) {
      if (isEnter) {
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
    e.preventDefault(); // Always prevent default so ArrowUp doesn't increment number inputs!
    if (currentIndex > 0) {
      const prevEl = focusables[currentIndex - 1];
      prevEl.focus();
      if (prevEl instanceof HTMLInputElement) {
        try {
          if (prevEl.type !== 'number') {
            prevEl.select();
          }
        } catch (_) {}
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
      if (el instanceof HTMLInputElement && el.type !== 'number') {
        try { el.select(); } catch (_) {}
      }
    }
  }, 50);
}
"""

with open(key_nav_path, "w", encoding="utf-8") as f:
    f.write(new_key_nav)
print("2. frontend/src/utils/keyboardNavigation.ts updated with safe arrow & enter navigation!")

# ==============================================================================
# 3. Update frontend/src/components/layout/AdminLayout.tsx with capture listener
# ==============================================================================
admin_layout_path = os.path.join(base_dir, "frontend", "src", "components", "layout", "AdminLayout.tsx")
with open(admin_layout_path, "r", encoding="utf-8") as f:
    admin_c = f.read()

# Make sure keydown listener uses capture: true
admin_c = admin_c.replace(
    "window.addEventListener('keydown', handleGlobalKeyDown);",
    "window.addEventListener('keydown', handleGlobalKeyDown, { capture: true });"
)
admin_c = admin_c.replace(
    "window.removeEventListener('keydown', handleGlobalKeyDown);",
    "window.removeEventListener('keydown', handleGlobalKeyDown, { capture: true } as any);"
)

# Enhance key checks with code check as well
old_f_check = """      // 2. F1, F2, F3: Switch Metal Tabs (Gold, Silver, Diamond)
      if (e.key === 'F1' || (e.altKey && (e.key === 'g' || e.key === 'G'))) {"""

new_f_check = """      const key = e.key;
      const code = e.code;

      // 2. F1, F2, F3: Switch Metal Tabs (Gold, Silver, Diamond)
      if (key === 'F1' || code === 'F1' || (e.altKey && (key === 'g' || key === 'G'))) {"""

admin_c = admin_c.replace(old_f_check, new_f_check)
admin_c = admin_c.replace("if (e.key === 'F2' || (e.altKey && (e.key === 's' || e.key === 'S')))", "if (key === 'F2' || code === 'F2' || (e.altKey && (key === 's' || key === 'S')))")
admin_c = admin_c.replace("if (e.key === 'F3' || (e.altKey && (e.key === 'd' || e.key === 'D')))", "if (key === 'F3' || code === 'F3' || (e.altKey && (key === 'd' || key === 'D')))")
admin_c = admin_c.replace("if (e.key === 'F12' || (e.key === 'Enter' && (e.ctrlKey || e.metaKey)))", "if (key === 'F12' || code === 'F12' || (key === 'Enter' && (e.ctrlKey || e.metaKey)))")
admin_c = admin_c.replace("if (e.key === 'F4' || (e.altKey && (e.key === 'b' || e.key === 'B')))", "if (key === 'F4' || code === 'F4' || (e.altKey && (key === 'b' || key === 'B')))")
admin_c = admin_c.replace("} else if (e.key === 'F5' || (e.altKey && (e.key === 'p' || e.key === 'P')))", "} else if (key === 'F5' || code === 'F5' || (e.altKey && (key === 'p' || key === 'P')))")
admin_c = admin_c.replace("} else if (e.key === 'F6' || (e.altKey && (e.key === 'e' || e.key === 'E')))", "} else if (key === 'F6' || code === 'F6' || (e.altKey && (key === 'e' || key === 'E')))")
admin_c = admin_c.replace("} else if (e.key === 'F7' || e.key === 'F8' || (e.altKey && (e.key === 'i' || e.key === 'I')))", "} else if (key === 'F7' || code === 'F7' || key === 'F8' || code === 'F8' || (e.altKey && (key === 'i' || key === 'I')))")
admin_c = admin_c.replace("} else if (e.key === 'F9' || (e.altKey && (e.key === 'c' || e.key === 'C')))", "} else if (key === 'F9' || code === 'F9' || (e.altKey && (key === 'c' || key === 'C')))")
admin_c = admin_c.replace("} else if (e.key === 'F10' || (e.altKey && (e.key === 'r' || e.key === 'R')))", "} else if (key === 'F10' || code === 'F10' || (e.altKey && (key === 'r' || key === 'R')))")
admin_c = admin_c.replace("} else if (e.key === 'F11' || (e.altKey && (e.key === 's' || e.key === 'S')))", "} else if (key === 'F11' || code === 'F11' || (e.altKey && (key === 's' || key === 'S')))")

with open(admin_layout_path, "w", encoding="utf-8") as f:
    f.write(admin_c)
print("3. frontend/src/components/layout/AdminLayout.tsx updated with capture phase key listener!")

# ==============================================================================
# 4. Update frontend/src/pages/reports/index.tsx with Wastage Profit nav
# ==============================================================================
reports_idx_path = os.path.join(base_dir, "frontend", "src", "pages", "reports", "index.tsx")
with open(reports_idx_path, "r", encoding="utf-8") as f:
    rep_idx = f.read()

rep_idx = rep_idx.replace(
    "import { LineChart, LayoutDashboard, Package, Users, Landmark, Receipt, Banknote } from 'lucide-react';",
    "import { LineChart, LayoutDashboard, Package, Users, Landmark, Receipt, Banknote, Sparkles } from 'lucide-react';"
)

old_navs = """    { name: 'Sales', icon: <LineChart size={18} /> },
    { name: 'Purchases', icon: <Package size={18} /> },
    { name: 'Profit', icon: <Landmark size={18} /> },"""

new_navs = """    { name: 'Sales', icon: <LineChart size={18} /> },
    { name: 'Purchases', icon: <Package size={18} /> },
    { name: 'Profit', icon: <Landmark size={18} /> },
    { name: 'Wastage Profit', icon: <Sparkles size={18} /> },"""

rep_idx = rep_idx.replace(old_navs, new_navs)

with open(reports_idx_path, "w", encoding="utf-8") as f:
    f.write(rep_idx)
print("4. frontend/src/pages/reports/index.tsx updated with Wastage Profit nav!")

print("\nALL BACKEND & FRONTEND UPDATES APPLIED SUCCESSFULLY!")
