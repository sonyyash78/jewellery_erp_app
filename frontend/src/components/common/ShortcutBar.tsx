import { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Keyboard, HelpCircle, X, ChevronDown, ChevronUp, Building2, Coins, ArrowRight, CornerDownLeft } from 'lucide-react';

export default function ShortcutBar() {
  const location = useLocation();
  const navigate = useNavigate();
  const [showModal, setShowModal] = useState(false);
  const [collapsed, setCollapsed] = useState(false);

  // Global listener for '?' to open shortcut guide
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement;
      const isInput = target && (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable);
      if (!isInput && e.key === '?') {
        e.preventDefault();
        setShowModal(prev => !prev);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const path = location.pathname;
  const isBilling = path === '/' || path === '/billing';
  const isInvoices = path.startsWith('/invoices');
  const isPurchases = path.startsWith('/purchases');
  const isExchange = path.startsWith('/exchange');
  const isReports = path.startsWith('/reports');

  return (
    <>
      {/* Sticky Bottom Shortcut Helper Bar - High contrast, non-clipping, responsive */}
      <div className="fixed bottom-0 left-0 right-0 z-40 print:hidden pointer-events-none flex justify-center pb-1 px-2 sm:px-4">
        <div className="pointer-events-auto bg-gray-950/95 backdrop-blur-md border border-gray-800 shadow-[0_-4px_25px_rgba(0,0,0,0.7)] rounded-t-xl px-2.5 sm:px-4 py-1.5 flex items-center gap-1.5 sm:gap-3 max-w-full overflow-x-auto text-[11px] text-gray-300">
          
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="flex items-center gap-1 text-primary hover:text-primary-light font-bold shrink-0 transition-colors cursor-pointer py-0.5 px-1 rounded hover:bg-gray-800/60"
            title={collapsed ? "Expand Shortcuts Bar" : "Collapse Shortcuts Bar"}
          >
            <Keyboard size={14} className="text-primary" />
            <span className="hidden md:inline uppercase tracking-wider font-mono text-[10px]">Shortcuts</span>
            {collapsed ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
          </button>

          {!collapsed && (
            <div className="flex items-center gap-1.5 sm:gap-2.5 overflow-x-auto whitespace-nowrap scrollbar-none py-0.5">
              
              {isBilling && (
                <>
                  <div className="flex items-center gap-1">
                    <kbd className="px-1.5 py-0.5 bg-amber-500/20 border border-amber-500/40 rounded text-amber-300 font-mono font-bold text-[10px]">F1</kbd>
                    <span className="text-gray-300">Gold</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <kbd className="px-1.5 py-0.5 bg-cyan-500/20 border border-cyan-500/40 rounded text-cyan-300 font-mono font-bold text-[10px]">F2</kbd>
                    <span className="text-gray-300">Silver</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <kbd className="px-1.5 py-0.5 bg-purple-500/20 border border-purple-500/40 rounded text-purple-300 font-mono font-bold text-[10px]">F3</kbd>
                    <span className="text-gray-300">Diamond</span>
                  </div>
                  <div className="h-3 w-px bg-gray-800 hidden sm:block" />
                  <div className="flex items-center gap-1">
                    <kbd className="px-1.5 py-0.5 bg-emerald-500/20 border border-emerald-500/40 rounded text-emerald-400 font-mono font-bold text-[10px]">Enter / ↓</kbd>
                    <span className="text-gray-300">Next Field</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <kbd className="px-1.5 py-0.5 bg-primary/20 border border-primary/40 rounded text-primary font-mono font-bold text-[10px]">F12</kbd>
                    <span className="text-primary font-semibold">Checkout</span>
                  </div>
                </>
              )}

              {isPurchases && (
                <>
                  <div className="flex items-center gap-1">
                    <kbd className="px-1.5 py-0.5 bg-amber-500/20 border border-amber-500/40 rounded text-amber-300 font-mono font-bold text-[10px]">F1</kbd>
                    <span className="text-gray-300">Gold</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <kbd className="px-1.5 py-0.5 bg-cyan-500/20 border border-cyan-500/40 rounded text-cyan-300 font-mono font-bold text-[10px]">F2</kbd>
                    <span className="text-gray-300">Silver</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <kbd className="px-1.5 py-0.5 bg-emerald-500/20 border border-emerald-500/40 rounded text-emerald-400 font-mono font-bold text-[10px]">Enter / ↓</kbd>
                    <span className="text-gray-300">Next Field</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <kbd className="px-1.5 py-0.5 bg-primary/20 border border-primary/40 rounded text-primary font-mono font-bold text-[10px]">F12</kbd>
                    <span className="text-primary font-semibold">Checkout</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <kbd className="px-1.5 py-0.5 bg-gray-800 border border-gray-700 rounded text-gray-300 font-mono font-bold text-[10px]">F4</kbd>
                    <span className="text-gray-400">Billing</span>
                  </div>
                </>
              )}

              {isExchange && (
                <>
                  <div className="flex items-center gap-1">
                    <kbd className="px-1.5 py-0.5 bg-emerald-500/20 border border-emerald-500/40 rounded text-emerald-400 font-mono font-bold text-[10px]">Enter / ↓</kbd>
                    <span className="text-gray-300">Next Field</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <kbd className="px-1.5 py-0.5 bg-primary/20 border border-primary/40 rounded text-primary font-mono font-bold text-[10px]">F12</kbd>
                    <span className="text-primary font-semibold">Checkout</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <kbd className="px-1.5 py-0.5 bg-gray-800 border border-gray-700 rounded text-gray-300 font-mono font-bold text-[10px]">F4</kbd>
                    <span className="text-gray-400">Billing</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <kbd className="px-1.5 py-0.5 bg-gray-800 border border-gray-700 rounded text-gray-300 font-mono font-bold text-[10px]">F8</kbd>
                    <span className="text-gray-400">Invoices</span>
                  </div>
                </>
              )}

              {isInvoices && (
                <>
                  <div className="flex items-center gap-1">
                    <kbd className="px-1.5 py-0.5 bg-primary/20 border border-primary/40 rounded text-primary font-mono font-bold text-[10px]">F4</kbd>
                    <span className="text-gray-300">Billing POS</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <kbd className="px-1.5 py-0.5 bg-gray-800 border border-gray-700 rounded text-gray-300 font-mono font-bold text-[10px]">F5</kbd>
                    <span className="text-gray-400">Purchases</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <kbd className="px-1.5 py-0.5 bg-gray-800 border border-gray-700 rounded text-gray-300 font-mono font-bold text-[10px]">F6</kbd>
                    <span className="text-gray-400">Exchange</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <kbd className="px-1.5 py-0.5 bg-gray-800 border border-gray-700 rounded text-gray-300 font-mono font-bold text-[10px]">F10</kbd>
                    <span className="text-gray-400">Reports</span>
                  </div>
                </>
              )}

              {isReports && (
                <>
                  <div className="flex items-center gap-1">
                    <kbd className="px-1.5 py-0.5 bg-primary/20 border border-primary/40 rounded text-primary font-mono font-bold text-[10px]">F4</kbd>
                    <span className="text-gray-300">Billing</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <kbd className="px-1.5 py-0.5 bg-gray-800 border border-gray-700 rounded text-gray-300 font-mono font-bold text-[10px]">F8</kbd>
                    <span className="text-gray-400">Invoices</span>
                  </div>
                </>
              )}

              {/* Company Switchers always available */}
              <div className="h-3 w-px bg-gray-800 hidden sm:block" />
              <div className="flex items-center gap-1">
                <kbd className="px-1.5 py-0.5 bg-amber-500/20 border border-amber-500/40 rounded text-amber-300 font-mono font-bold text-[10px]">Alt+1</kbd>
                <span className="text-gray-400 hidden sm:inline">Normal Co.</span>
              </div>
              <div className="flex items-center gap-1">
                <kbd className="px-1.5 py-0.5 bg-cyan-500/20 border border-cyan-500/40 rounded text-cyan-300 font-mono font-bold text-[10px]">Alt+2</kbd>
                <span className="text-gray-400 hidden sm:inline">GST Co.</span>
              </div>

            </div>
          )}

          {/* Guide Modal Trigger */}
          <button
            onClick={() => setShowModal(true)}
            className="flex items-center gap-1 text-primary hover:text-primary-light font-bold shrink-0 transition-colors ml-auto bg-primary/10 hover:bg-primary/20 px-2 py-0.5 rounded border border-primary/30 cursor-pointer text-[10px]"
            title="Open Complete Keyboard Shortcuts Guide (?)"
          >
            <HelpCircle size={13} className="text-primary" />
            <span>Guide (?)</span>
          </button>

        </div>
      </div>

      {/* FULL KEYBOARD SHORTCUTS GUIDE MODAL */}
      {showModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-3 sm:p-4 overflow-y-auto">
          <div className="bg-surface border border-gray-700 rounded-2xl shadow-2xl max-w-2xl w-full max-h-[92vh] flex flex-col overflow-hidden my-auto animate-in fade-in zoom-in-95 duration-150">
            
            {/* Modal Header */}
            <div className="flex justify-between items-center p-4 border-b border-gray-800 bg-gray-900/90">
              <div className="flex items-center gap-2">
                <Keyboard className="text-primary" size={20} />
                <h2 className="text-base sm:text-lg font-bold text-white tracking-wide">
                  Complete Keyboard Shortcuts Guide
                </h2>
              </div>
              <button
                onClick={() => setShowModal(false)}
                className="text-gray-400 hover:text-white p-1 rounded hover:bg-gray-800 transition-colors"
              >
                <X size={18} />
              </button>
            </div>

            {/* Modal Content */}
            <div className="p-4 sm:p-5 overflow-y-auto space-y-4 custom-scrollbar text-xs sm:text-sm">
              
              {/* Category 1: Form & Enter Key Workflow */}
              <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-3 sm:p-4">
                <h3 className="text-xs font-bold text-emerald-400 uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
                  <CornerDownLeft size={15} />
                  1. Calculator &amp; Form Keyboard Workflow (Next-to-Next)
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                  <div className="flex items-center justify-between p-2 bg-background/60 border border-gray-800/80 rounded-lg">
                    <span className="text-gray-300 font-medium">Move to Next Field / Button</span>
                    <kbd className="px-2 py-0.5 bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 font-mono font-bold rounded">Enter / ↓</kbd>
                  </div>
                  <div className="flex items-center justify-between p-2 bg-background/60 border border-gray-800/80 rounded-lg">
                    <span className="text-gray-300 font-medium">Move to Previous Field</span>
                    <kbd className="px-2 py-0.5 bg-gray-800 border border-gray-700 text-gray-300 font-mono font-bold rounded">↑ (Up Arrow)</kbd>
                  </div>
                  <div className="flex items-center justify-between p-2 bg-background/60 border border-gray-800/80 rounded-lg">
                    <span className="text-gray-300 font-medium">Switch Action Buttons</span>
                    <kbd className="px-2 py-0.5 bg-gray-800 border border-gray-700 text-gray-300 font-mono font-bold rounded">← / → (Arrows)</kbd>
                  </div>
                  <div className="flex items-center justify-between p-2 bg-background/60 border border-gray-800/80 rounded-lg">
                    <span className="text-gray-300 font-medium">Silent Save to PC &amp; USB</span>
                    <kbd className="px-2 py-0.5 bg-emerald-700 text-white font-mono font-bold rounded">Enter on SAVE ONLY</kbd>
                  </div>
                  <div className="flex items-center justify-between p-2 bg-background/60 border border-gray-800/80 rounded-lg">
                    <span className="text-gray-300 font-medium">Checkout / Open Settlement</span>
                    <kbd className="px-2 py-0.5 bg-primary/20 border border-primary/40 text-primary font-mono font-bold rounded">F12 / Ctrl+Enter</kbd>
                  </div>
                  <div className="flex items-center justify-between p-2 bg-background/60 border border-gray-800/80 rounded-lg">
                    <span className="text-gray-300 font-medium">Close Modal / Cancel</span>
                    <kbd className="px-2 py-0.5 bg-gray-800 border border-gray-700 text-gray-400 font-mono font-bold rounded">Escape (Esc)</kbd>
                  </div>
                </div>
              </div>

              {/* Category 2: Metal Calculator Switchers */}
              <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-3 sm:p-4">
                <h3 className="text-xs font-bold text-amber-400 uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
                  <Coins size={15} />
                  2. Metal Calculator Tabs
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-xs">
                  <div className="flex items-center justify-between p-2 bg-background/60 border border-amber-500/30 rounded-lg">
                    <span className="text-amber-300 font-bold">Gold Tab</span>
                    <kbd className="px-2 py-0.5 bg-amber-500/20 border border-amber-500/40 text-amber-300 font-mono font-bold rounded">F1 / Alt+G</kbd>
                  </div>
                  <div className="flex items-center justify-between p-2 bg-background/60 border border-cyan-500/30 rounded-lg">
                    <span className="text-cyan-300 font-bold">Silver Tab</span>
                    <kbd className="px-2 py-0.5 bg-cyan-500/20 border border-cyan-500/40 text-cyan-300 font-mono font-bold rounded">F2 / Alt+S</kbd>
                  </div>
                  <div className="flex items-center justify-between p-2 bg-background/60 border border-purple-500/30 rounded-lg">
                    <span className="text-purple-300 font-bold">Diamond Tab</span>
                    <kbd className="px-2 py-0.5 bg-purple-500/20 border border-purple-500/40 text-purple-300 font-mono font-bold rounded">F3 / Alt+D</kbd>
                  </div>
                </div>
              </div>

              {/* Category 3: Multi-Company Isolation Switchers */}
              <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-3 sm:p-4">
                <h3 className="text-xs font-bold text-cyan-400 uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
                  <Building2 size={15} />
                  3. Multi-Company Switchers (Both SAIDEEP JEWELLERS)
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                  <div className="flex items-center justify-between p-2.5 bg-background/60 border border-amber-500/30 rounded-lg">
                    <div>
                      <div className="text-amber-300 font-bold">SAIDEEP JEWELLERS (Normal)</div>
                      <div className="text-[10px] text-gray-400">Retail non-GST estimates</div>
                    </div>
                    <kbd className="px-2 py-1 bg-amber-500/20 border border-amber-500/40 text-amber-300 font-mono font-bold rounded">Alt + 1</kbd>
                  </div>
                  <div className="flex items-center justify-between p-2.5 bg-background/60 border border-cyan-500/30 rounded-lg">
                    <div>
                      <div className="text-cyan-300 font-bold">SAIDEEP JEWELLERS (GST)</div>
                      <div className="text-[10px] text-gray-400">Strict GST Tax Invoices (SJ/S/01/26-27)</div>
                    </div>
                    <kbd className="px-2 py-1 bg-cyan-500/20 border border-cyan-500/40 text-cyan-300 font-mono font-bold rounded">Alt + 2</kbd>
                  </div>
                </div>
              </div>

              {/* Category 4: Page Navigation */}
              <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-3 sm:p-4">
                <h3 className="text-xs font-bold text-primary uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
                  <ArrowRight size={15} />
                  4. Page Navigation Hotkeys
                </h3>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
                  <button onClick={() => { navigate('/billing'); setShowModal(false); }} className="flex items-center justify-between p-2 bg-background/40 hover:bg-background border border-gray-800 rounded-lg text-left transition-colors cursor-pointer">
                    <span className="text-gray-300">Billing POS</span>
                    <kbd className="px-1.5 py-0.5 bg-primary/20 border border-primary/40 rounded font-mono text-[10px] text-primary font-bold">F4</kbd>
                  </button>
                  <button onClick={() => { navigate('/purchases'); setShowModal(false); }} className="flex items-center justify-between p-2 bg-background/40 hover:bg-background border border-gray-800 rounded-lg text-left transition-colors cursor-pointer">
                    <span className="text-gray-300">Purchases</span>
                    <kbd className="px-1.5 py-0.5 bg-gray-800 border border-gray-700 rounded font-mono text-[10px] text-primary font-bold">F5</kbd>
                  </button>
                  <button onClick={() => { navigate('/exchange'); setShowModal(false); }} className="flex items-center justify-between p-2 bg-background/40 hover:bg-background border border-gray-800 rounded-lg text-left transition-colors cursor-pointer">
                    <span className="text-gray-300">Exchange</span>
                    <kbd className="px-1.5 py-0.5 bg-gray-800 border border-gray-700 rounded font-mono text-[10px] text-primary font-bold">F6</kbd>
                  </button>
                  <button onClick={() => { navigate('/inventory'); setShowModal(false); }} className="flex items-center justify-between p-2 bg-background/40 hover:bg-background border border-gray-800 rounded-lg text-left transition-colors cursor-pointer">
                    <span className="text-gray-300">Inventory</span>
                    <kbd className="px-1.5 py-0.5 bg-gray-800 border border-gray-700 rounded font-mono text-[10px] text-primary font-bold">F7</kbd>
                  </button>
                  <button onClick={() => { navigate('/invoices'); setShowModal(false); }} className="flex items-center justify-between p-2 bg-background/40 hover:bg-background border border-gray-800 rounded-lg text-left transition-colors cursor-pointer">
                    <span className="text-gray-300">Invoices</span>
                    <kbd className="px-1.5 py-0.5 bg-gray-800 border border-gray-700 rounded font-mono text-[10px] text-primary font-bold">F8</kbd>
                  </button>
                  <button onClick={() => { navigate('/customers'); setShowModal(false); }} className="flex items-center justify-between p-2 bg-background/40 hover:bg-background border border-gray-800 rounded-lg text-left transition-colors cursor-pointer">
                    <span className="text-gray-300">Customers CRM</span>
                    <kbd className="px-1.5 py-0.5 bg-gray-800 border border-gray-700 rounded font-mono text-[10px] text-primary font-bold">F9</kbd>
                  </button>
                  <button onClick={() => { navigate('/reports'); setShowModal(false); }} className="flex items-center justify-between p-2 bg-background/40 hover:bg-background border border-gray-800 rounded-lg text-left transition-colors cursor-pointer">
                    <span className="text-gray-300">Reports</span>
                    <kbd className="px-1.5 py-0.5 bg-gray-800 border border-gray-700 rounded font-mono text-[10px] text-primary font-bold">F10</kbd>
                  </button>
                  <button onClick={() => { navigate('/settings'); setShowModal(false); }} className="flex items-center justify-between p-2 bg-background/40 hover:bg-background border border-gray-800 rounded-lg text-left transition-colors cursor-pointer">
                    <span className="text-gray-300">Settings</span>
                    <kbd className="px-1.5 py-0.5 bg-gray-800 border border-gray-700 rounded font-mono text-[10px] text-primary font-bold">F11</kbd>
                  </button>
                </div>
              </div>

            </div>

            {/* Modal Footer */}
            <div className="p-3 bg-gray-900 border-t border-gray-800 flex justify-between items-center text-xs text-gray-400">
              <span>Press <kbd className="px-1.5 py-0.5 bg-gray-800 border border-gray-700 rounded font-mono text-gray-300">Esc</kbd> or <kbd className="px-1.5 py-0.5 bg-gray-800 border border-gray-700 rounded font-mono text-gray-300">?</kbd> to toggle</span>
              <button
                onClick={() => setShowModal(false)}
                className="px-4 py-1.5 bg-primary text-black font-bold rounded-lg hover:bg-primary-dark transition-colors cursor-pointer"
              >
                Close Guide
              </button>
            </div>

          </div>
        </div>
      )}
    </>
  );
}
