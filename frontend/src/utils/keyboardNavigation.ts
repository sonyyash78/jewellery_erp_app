import type { KeyboardEvent } from 'react';

export interface KeyNavOptions {
  containerSelector?: string;
  onComplete?: () => void;
  onCancel?: () => void;
  enableArrows?: boolean;
}

/**
 * Handles keyboard navigation (Enter, ArrowDown, ArrowUp, ArrowLeft, ArrowRight, Escape)
 * across form inputs, dropdowns, radio controls, and action buttons.
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

  // Preserve normal Enter inside multi-line textareas (unless Ctrl+Enter)
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

  // Container lookup: closest matching container -> form -> main -> body
  const container = target.closest(containerSelector) || 
                    target.closest('[role="dialog"]') ||
                    target.closest('.fixed.inset-0') ||
                    target.closest('form') || 
                    target.closest('main') || 
                    target.closest('[role="main"]') || 
                    document.body;

  if (!container) return;

  // Collect all navigable inputs, selects, and action buttons in DOM order
  const focusables = Array.from(
    container.querySelectorAll<HTMLElement>(
      'input:not([disabled]):not([type="hidden"]):not([readonly]):not([type="radio"]):not([type="checkbox"]), ' +
      'select:not([disabled]), ' +
      'button[data-nav-button="true"], ' +
      'button[data-save-only="true"], ' +
      'button[type="submit"], ' +
      'button[data-action="submit"]'
    )
  ).filter(el => {
    return el.offsetParent !== null && !el.classList.contains('cursor-not-allowed') && el.tabIndex !== -1;
  });

  const currentIndex = focusables.indexOf(target);
  if (currentIndex === -1) {
    if (isEnter && onComplete) {
      onComplete();
    }
    return;
  }

  const isButton = target.tagName === 'BUTTON';
  const isNumberInput = target instanceof HTMLInputElement && target.type === 'number';

  // For buttons: Left and Right arrow keys move between adjacent buttons
  if (isButton && (isLeft || isRight)) {
    e.preventDefault();
    const step = isRight ? 1 : -1;
    const nextIdx = currentIndex + step;
    if (nextIdx >= 0 && nextIdx < focusables.length) {
      focusables[nextIdx].focus();
    }
    return;
  }

  // Safe cursor check for text inputs
  if (!isButton && target instanceof HTMLInputElement && !isNumberInput) {
    try {
      const len = target.value.length;
      if (isRight) {
        const isAtEnd = target.selectionStart === len && target.selectionEnd === len;
        const isAllSelected = target.selectionStart === 0 && target.selectionEnd === len && len > 0;
        if (!isAtEnd && !isAllSelected) return;
      }
      if (isLeft) {
        const isAtStart = target.selectionStart === 0 && target.selectionEnd === 0;
        const isAllSelected = target.selectionStart === 0 && target.selectionEnd === len && len > 0;
        if (!isAtStart && !isAllSelected) return;
      }
    } catch (_) {}
  }

  // FORWARD NAVIGATION (Enter, Down, Right)
  if (isEnter || isDown || (isRight && !isNumberInput)) {
    e.preventDefault();

    if (isEnter && isButton) {
      (target as HTMLButtonElement).click();
      return;
    }

    if (currentIndex < focusables.length - 1) {
      const nextEl = focusables[currentIndex + 1];
      nextEl.focus();
      if (nextEl instanceof HTMLInputElement && nextEl.type !== 'number') {
        try { nextEl.select(); } catch (_) {}
      }
    } else if (currentIndex === focusables.length - 1) {
      if (isEnter) {
        if (onComplete) {
          onComplete();
        } else {
          const submitBtn = container.querySelector<HTMLButtonElement>(
            'button[data-save-only="true"], button[data-nav-button="true"]:last-of-type, button[type="submit"]'
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
  if (isUp || (isLeft && !isNumberInput)) {
    e.preventDefault();
    if (currentIndex > 0) {
      const prevEl = focusables[currentIndex - 1];
      prevEl.focus();
      if (prevEl instanceof HTMLInputElement && prevEl.type !== 'number') {
        try { prevEl.select(); } catch (_) {}
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
  }, 60);
}

/**
 * Global Enter Key Navigation across the ENTIRE ERP application.
 * Pressing Enter on any input/select automatically advances focus to the next field.
 * Pressing Shift+Enter moves focus to the previous field.
 * Scoped automatically to modals, drawers, or current page.
 */
let isGlobalEnterInstalled = false;

export function initGlobalEnterNavigation() {
  if (typeof window === 'undefined' || isGlobalEnterInstalled) return;
  isGlobalEnterInstalled = true;

  window.addEventListener('keydown', (e: globalThis.KeyboardEvent) => {
    // Only capture Enter key without modifiers (except Shift for reverse)
    if (e.key !== 'Enter' || e.altKey || e.ctrlKey || e.metaKey) return;
    
    // If an element already handled Enter explicitly (e.g. dropdown item click / barcode scanner), ignore
    if (e.defaultPrevented) return;

    const target = e.target as HTMLElement;
    if (!target) return;

    const isInput = target instanceof HTMLInputElement;
    const isSelect = target instanceof HTMLSelectElement;
    const isTextarea = target instanceof HTMLTextAreaElement;
    const isButton = target instanceof HTMLButtonElement;

    // Buttons: Enter should execute their normal click
    if (isButton) return;

    // Textareas: normal Enter produces a newline; Ctrl+Enter submits
    if (isTextarea && !e.ctrlKey) return;

    // Only process input fields and select elements
    if (!isInput && !isSelect && !isTextarea) return;

    // Ignore file inputs and checkbox/radio from auto-advancing
    if (isInput && (target.type === 'file' || target.type === 'checkbox' || target.type === 'radio')) return;

    // Determine current active container (modal / form / main / body)
    const container = target.closest('[role="dialog"]') ||
                      target.closest('.fixed.inset-0') ||
                      target.closest('[data-enter-container]') ||
                      target.closest('form') ||
                      target.closest('main') ||
                      document.body;

    if (!container) return;

    // Query all focusable interactive controls inside this container in DOM order
    const focusables = Array.from(
      container.querySelectorAll<HTMLElement>(
        'input:not([type="hidden"]):not([disabled]):not([readonly]):not([type="checkbox"]):not([type="radio"]), ' +
        'select:not([disabled]), ' +
        'textarea:not([disabled]):not([readonly]), ' +
        'button[data-save-only="true"], ' +
        'button[data-nav-button="true"], ' +
        'button[type="submit"], ' +
        'button[data-action="submit"]'
      )
    ).filter(el => {
      if (el.tabIndex === -1 || el.classList.contains('cursor-not-allowed')) return false;
      const rects = el.getClientRects();
      return rects.length > 0 && el.offsetParent !== null;
    });

    const currentIndex = focusables.indexOf(target);
    if (currentIndex === -1) return;

    if (e.shiftKey) {
      // Shift + Enter: Move to previous field
      e.preventDefault();
      if (currentIndex > 0) {
        const prevEl = focusables[currentIndex - 1];
        prevEl.focus();
        if (prevEl instanceof HTMLInputElement && prevEl.type !== 'number') {
          try { prevEl.select(); } catch (_) {}
        }
      }
      return;
    }

    // Normal Enter: Move to next field
    e.preventDefault();
    if (currentIndex < focusables.length - 1) {
      const nextEl = focusables[currentIndex + 1];
      nextEl.focus();
      if (nextEl instanceof HTMLInputElement && nextEl.type !== 'number') {
        try { nextEl.select(); } catch (_) {}
      }
    } else {
      // Last field reached: Click the primary submit/save button if available
      const submitBtn = container.querySelector<HTMLButtonElement>(
        'button[data-save-only="true"], button[type="submit"], button[data-action="submit"], button[data-nav-button="true"]:last-of-type'
      );
      if (submitBtn && !submitBtn.disabled) {
        submitBtn.click();
      }
    }
  }, false);
}
