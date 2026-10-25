import { useState, useEffect } from 'react';
import { useBillingStore } from '../../store/billingStore';
import type { BillItem } from '../../store/billingStore';
import { Calculator, Trash2, Edit2, RotateCcw, Edit, Receipt } from 'lucide-react';
import toast from 'react-hot-toast';
import CheckoutModal from './CheckoutModal';
import LiveRatesModal from './LiveRatesModal';

export default function LiveBillSummary() {
  const {
    cart,
    gstState,
    setGstState,
    clearCart,
    liveRates,
    globalDiscount,
    setGlobalDiscount,
    editingItemId,
    setEditingItemId,
    removeFromCart
  } = useBillingStore();

  const [showCheckout, setShowCheckout] = useState(false);
  const [showRatesModal, setShowRatesModal] = useState(false);
  const [checkoutPayload, setCheckoutPayload] = useState<any>(null);

  // ── Totals & Calculations ──
  const baseTaxableAmount = cart.reduce((sum, item) => sum + (item.taxableAmount || 0), 0);
  const taxableAmount = Math.max(0, baseTaxableAmount - globalDiscount);

  // GST Calculation (Standard Indian Jewellery GST: 3%)
  let cgst = 0, sgst = 0, igst = 0;
  if (gstState === 'same_state') {
    cgst = taxableAmount * 0.015;
    sgst = taxableAmount * 0.015;
  } else if (gstState === 'different_state') {
    igst = taxableAmount * 0.03;
  }
  const gstAmount = cgst + sgst + igst;

  // Round Off & Grand Total
  const exactTotal = taxableAmount + gstAmount;
  const grandTotal = Math.round(exactTotal);
  const roundOff = grandTotal - exactTotal;

  // Fine Metal Weights
  const goldItems = cart.filter(i => i.itemType === 'Gold');
  const silverItems = cart.filter(i => i.itemType === 'Silver');

  const totalGoldFine = goldItems.reduce((acc, i) => acc + (i.fineWeight || 0), 0);
  const totalGoldNet = goldItems.reduce((acc, i) => acc + (i.netWeight || 0), 0);

  const totalSilverFine = silverItems.reduce((acc, i) => acc + (i.fineWeight || 0), 0);
  const totalSilverNet = silverItems.reduce((acc, i) => acc + (i.netWeight || 0), 0);

  const hasMetalActivity = totalGoldFine > 0 || totalSilverFine > 0;

  // Equivalent 24K Gold & Fine Silver (Benchmark gold rate is ₹/10g; silver rate is ₹/kg)
  const goldRatePerGm = (liveRates.gold24k || 79100) / 10;
  const equivalentGold = goldRatePerGm > 0 ? (grandTotal / goldRatePerGm) : 0;

  const silverRatePerGm = (liveRates.silver || 90000) / 1000;
  const equivalentSilver = silverRatePerGm > 0 ? (grandTotal / silverRatePerGm) : 0;

  // ── Edit Item Handler ──
  const handleEdit = (item: BillItem) => {
    if (item.itemType === 'Gold') {
      const fallbackRate = item.rateDisplay > 10000 ? item.rateDisplay : (item.rateDisplay * 10 || 72500);
      useBillingStore.setState({
        goldForm: item.rawGold || {
          itemName: item.itemName || '',
          category: '',
          hsn: '',
          purity: item.purityDisplay || '22K Gold',
          touch: item.touchDisplay || 91.6,
          wastage: item.wastageDisplay || 0,
          grossWeight: item.grossWeight || 0,
          stoneWeight: item.stoneWeight || 0,
          ratePerGm: fallbackRate,
          makingChargeType: 'flat',
          makingChargeValue: item.makingAmount || 0,
          hallmark: item.hallmark || 0,
          otherCharges: item.otherCharges || 0,
          discount: item.discount || 0
        }
      });
    } else if (item.itemType === 'Silver') {
      useBillingStore.setState({
        silverForm: item.rawSilver || {
          itemName: item.itemName || '',
          category: '',
          hsn: '',
          tanch: item.touchDisplay || 65,
          wastage: item.wastageDisplay || 0,
          silverPurity: item.purityDisplay || 'Fine',
          grossWeight: item.grossWeight || 0,
          stoneWeight: item.stoneWeight || 0,
          ratePerKg: item.rateDisplay || 90000,
          makingChargeType: 'flat',
          makingChargeValue: item.makingAmount || 0,
          otherCharges: item.otherCharges || 0,
          discount: item.discount || 0
        }
      });
    }

    setEditingItemId(item.id);
    toast.success(`Loaded "${item.itemName}" into calculator for editing`);
  };

  // ── Checkout / Generate Handler ──
  const handleGenerate = () => {
    if (cart.length === 0) {
      toast.error("Cart is empty. Add items to bill first.");
      return;
    }

    const payload = {
      subtotal: baseTaxableAmount,
      tax_amount: gstAmount,
      discount_amount: globalDiscount,
      grand_total: grandTotal,
      items: cart.map(item => ({
        stock_item_id: item.stockItemId || null,
        item_name: item.itemName,
        item_type: item.itemType,
        final_price: item.taxableAmount,
        gold_calculation: item.itemType === 'Gold' ? {
          metal_rate_id: null,
          applied_rate: item.rateDisplay,
          gross_weight: item.grossWeight,
          stone_weight: item.stoneWeight || 0,
          net_weight: item.netWeight,
          touch_purity: item.touchDisplay,
          wastage: item.wastageDisplay,
          fine_weight: item.fineWeight,
          making_charge_type: (item.rawGold as any)?.makingChargeType || 'flat',
          making_charge_rate: (item.rawGold as any)?.makingChargeValue || 0,
          making_charges_amount: item.makingAmount,
          hallmark_charges: item.hallmark || 0,
          other_charges: item.otherCharges || 0,
          discount: item.discount || 0,
          total_gold_value: item.metalValue
        } : null,
        silver_calculation: item.itemType === 'Silver' ? {
          metal_rate_id: null,
          applied_rate: item.rateDisplay,
          gross_weight: item.grossWeight,
          stone_weight: item.stoneWeight || 0,
          net_weight: item.netWeight,
          tanch_percentage: item.touchDisplay,
          wastage: item.wastageDisplay,
          pure_weight: item.fineWeight,
          making_charge_type: (item.rawSilver as any)?.makingChargeType || 'flat',
          making_charge_rate: (item.rawSilver as any)?.makingChargeValue || 0,
          making_charges_amount: item.makingAmount,
          other_charges: item.otherCharges || 0,
          discount: item.discount || 0,
          total_silver_value: item.metalValue
        } : null
      }))
    };

    setCheckoutPayload(payload);
    setShowCheckout(true);
  };

  // Keyboard shortcut F7 to trigger checkout
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'F7') {
        e.preventDefault();
        handleGenerate();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [cart, grandTotal, taxableAmount, globalDiscount, gstAmount]);

  return (
    <div className="flex flex-col h-full overflow-hidden bg-surface">
      {/* Top Header */}
      <div className="bg-background border-b border-gray-800 px-4 py-2.5 flex justify-between items-center shrink-0">
        <h2 className="text-sm font-bold text-primary flex items-center gap-2 uppercase tracking-widest">
          <Receipt size={16} />
          Bill Summary
        </h2>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowRatesModal(true)}
            className="text-[11px] bg-primary/10 hover:bg-primary/20 text-primary border border-primary/30 px-2 py-0.5 rounded font-bold flex items-center gap-1 transition-colors"
            title="Configure Live Metal Rates"
          >
            <Edit size={11} /> Rates
          </button>
          <span className="text-[11px] font-mono bg-primary/20 text-primary px-2 py-0.5 rounded font-bold border border-primary/40">
            ITEMS: {cart.length}
          </span>
        </div>
      </div>

      {/* Scrollable Items List */}
      <div className="flex-1 min-h-0 overflow-y-auto p-3 custom-scrollbar space-y-2.5">
        {cart.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-4">
            <Receipt size={32} className="text-gray-600 mb-2" />
            <p className="text-gray-400 text-xs font-medium">No items added yet</p>
            <p className="text-gray-600 text-[11px] mt-1 max-w-[200px]">
              Lookup barcodes or calculate jewellery to add them to this bill.
            </p>
          </div>
        ) : (
          cart.map(item => {
            const isEditing = editingItemId === item.id;
            const isGold = item.itemType === 'Gold';

            return (
              <div
                key={item.id}
                className={`bg-background border rounded-lg p-2.5 relative group transition-all ${
                  isEditing
                    ? 'border-amber-500 bg-amber-500/10 ring-1 ring-amber-500/50 shadow-md'
                    : 'border-gray-800 hover:border-gray-700'
                }`}
              >
                {/* Action Buttons Top-Right */}
                <div className="absolute top-1.5 right-1.5 flex items-center space-x-1">
                  <button
                    onClick={() => handleEdit(item)}
                    title="Edit Item in Calculator"
                    className={`p-1 rounded transition-colors ${
                      isEditing
                        ? 'bg-amber-400 text-black font-bold'
                        : 'text-gray-400 hover:text-blue-400 hover:bg-blue-500/10'
                    }`}
                  >
                    <Edit2 size={13} />
                  </button>
                  <button
                    onClick={() => {
                      removeFromCart(item.id);
                      if (editingItemId === item.id) setEditingItemId(null);
                      toast.success(`Removed "${item.itemName}"`);
                    }}
                    title="Delete Item"
                    className="p-1 rounded text-gray-400 hover:text-red-400 hover:bg-red-500/10 transition-colors"
                  >
                    <Trash2 size={13} />
                  </button>
                </div>

                {/* Header row: Metal badge, Name, and Price */}
                <div className="flex justify-between items-start mb-1.5 pr-14">
                  <div>
                    <span
                      className={`text-[10px] font-bold px-1.5 py-0.5 rounded mr-1.5 ${
                        isGold
                          ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'
                          : 'bg-gray-400/20 text-gray-200 border border-gray-400/30'
                      }`}
                    >
                      {item.itemType.toUpperCase()}
                    </span>
                    <span className="text-xs text-textMain font-medium">{item.itemName}</span>
                  </div>
                  <span className="text-xs font-mono text-primary font-bold">
                    ₹{item.taxableAmount.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </span>
                </div>

                {/* Detail Grid */}
                <div className="grid grid-cols-2 gap-x-3 gap-y-0.5 text-[10.5px] text-textMuted">
                  <div className="flex justify-between">
                    <span>Net Wt:</span>
                    <span className="font-mono text-gray-200">{item.netWeight.toFixed(3)}g</span>
                  </div>
                  <div className="flex justify-between">
                    <span>{isGold ? 'Touch:' : 'Tanch:'}</span>
                    <span className="font-mono text-gray-300">
                      {item.touchDisplay}%{item.wastageDisplay > 0 ? ` (+${item.wastageDisplay}%)` : ''}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Fine Wt:</span>
                    <span className="font-mono text-primary font-bold">{item.fineWeight.toFixed(3)}g</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Rate:</span>
                    <span className="font-mono text-gray-300">
                      ₹{item.rateDisplay.toLocaleString()}{isGold ? '/10g' : '/kg'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Making:</span>
                    <span className="font-mono text-gray-300">
                      ₹{item.makingAmount.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Other:</span>
                    <span className="font-mono text-gray-300">
                      ₹{(item.hallmark + item.otherCharges).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                    </span>
                  </div>
                </div>

                {/* Item-level discount if any */}
                {item.discount > 0 && (
                  <div className="text-[10.5px] text-red-400 flex justify-between mt-1 pt-1 border-t border-gray-800/60 font-mono">
                    <span>Item Discount:</span>
                    <span>- ₹{item.discount.toFixed(2)}</span>
                  </div>
                )}

                {/* Active Edit Indicator */}
                {isEditing && (
                  <div className="text-[10px] text-amber-400 font-bold uppercase mt-1.5 flex items-center gap-1.5 pt-1 border-t border-amber-500/30">
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-ping" />
                    Currently Editing in Calculator
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>

      {/* Bottom Fixed Summary & Totals */}
      <div className="bg-background border-t border-gray-800 p-3 shrink-0">
        {/* Metal Summary Card */}
        {hasMetalActivity && (
          <div className="bg-[#16161D] border border-gray-700/60 rounded-lg p-2.5 mb-2.5 space-y-1.5 shadow-inner">
            <div className="text-[9.5px] font-bold text-gray-400 uppercase tracking-widest flex items-center justify-between border-b border-gray-800 pb-1">
              <span className="flex items-center gap-1.5 text-primary">⚖️ Fine Metal Summary</span>
              <span className="text-[8.5px] text-gray-500 font-normal">Fine Weights</span>
            </div>

            {/* Gold Row */}
            {totalGoldFine > 0 && (
              <div className="bg-yellow-950/20 border border-yellow-800/40 rounded px-2 py-1 flex items-center justify-between text-xs">
                <span className="font-bold text-yellow-400">🥇 Gold</span>
                <div className="flex items-center gap-3 text-[10.5px] font-mono">
                  <span className="text-gray-400">
                    Net: <strong className="text-gray-200">{totalGoldNet.toFixed(3)}g</strong>
                  </span>
                  <span className="text-gray-400">
                    Fine: <strong className="text-yellow-400 font-bold">{totalGoldFine.toFixed(3)}g</strong>
                  </span>
                </div>
              </div>
            )}

            {/* Silver Row */}
            {totalSilverFine > 0 && (
              <div className="bg-gray-800/30 border border-gray-700/40 rounded px-2 py-1 flex items-center justify-between text-xs">
                <span className="font-bold text-gray-300">🥈 Silver</span>
                <div className="flex items-center gap-3 text-[10.5px] font-mono">
                  <span className="text-gray-400">
                    Net: <strong className="text-gray-200">{totalSilverNet.toFixed(3)}g</strong>
                  </span>
                  <span className="text-gray-400">
                    Fine: <strong className="text-gray-100 font-bold">{totalSilverFine.toFixed(3)}g</strong>
                  </span>
                </div>
              </div>
            )}
          </div>
        )}

        {/* GST Type Selector Buttons */}
        <div className="flex justify-between items-center mb-2">
          <span className="text-xs text-textMuted font-medium">GST Type</span>
          <div className="flex gap-1.5">
            <button
              type="button"
              onClick={() => setGstState('same_state')}
              className={`px-2.5 py-1 rounded text-[10.5px] font-bold transition-colors ${
                gstState === 'same_state' ? 'bg-primary text-black' : 'bg-gray-800 text-gray-400 hover:text-white'
              }`}
            >
              Same State
            </button>
            <button
              type="button"
              onClick={() => setGstState('different_state')}
              className={`px-2.5 py-1 rounded text-[10.5px] font-bold transition-colors ${
                gstState === 'different_state' ? 'bg-primary text-black' : 'bg-gray-800 text-gray-400 hover:text-white'
              }`}
            >
              Interstate
            </button>
            <button
              type="button"
              onClick={() => setGstState('none')}
              className={`px-2.5 py-1 rounded text-[10.5px] font-bold transition-colors ${
                gstState === 'none' ? 'bg-primary text-black' : 'bg-gray-800 text-gray-400 hover:text-white'
              }`}
            >
              No GST
            </button>
          </div>
        </div>

        {/* Breakdown Rows */}
        <div className="space-y-1 mb-2 text-xs">
          <div className="flex justify-between text-textMuted">
            <span>Subtotal (Taxable)</span>
            <span className="font-mono">₹{baseTaxableAmount.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
          </div>

          <div className="flex justify-between items-center text-red-400">
            <span>Bill Discount</span>
            <div className="flex items-center">
              <span className="mr-1">- ₹</span>
              <input
                type="number"
                value={globalDiscount === 0 ? '' : globalDiscount}
                onChange={e => setGlobalDiscount(Math.max(0, Number(e.target.value)))}
                placeholder="0"
                className="bg-gray-900 border border-red-900/50 rounded w-16 text-right px-1 font-mono text-red-400 text-xs outline-none focus:border-red-500"
              />
            </div>
          </div>

          <div className="flex justify-between text-textMuted">
            <span>
              GST ({gstState === 'none' ? '0%' : gstState === 'same_state' ? 'CGST 1.5% + SGST 1.5%' : 'IGST 3%'})
            </span>
            <span className="font-mono">₹{gstAmount.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
          </div>

          {Math.abs(roundOff) > 0.001 && (
            <div className="flex justify-between text-gray-500">
              <span>Round Off</span>
              <span className="font-mono">{roundOff > 0 ? '+' : ''}{roundOff.toFixed(2)}</span>
            </div>
          )}

          <div className="flex justify-between text-base font-bold pt-1.5 border-t border-gray-800 mt-1 items-center">
            <span className="text-xs uppercase text-gray-400 font-bold">Grand Total (Bill)</span>
            <span className="font-mono text-primary text-lg font-black">₹{grandTotal.toLocaleString()}</span>
          </div>
        </div>

        {/* Metal Equivalents */}
        {grandTotal > 0 && (
          <div className="grid grid-cols-2 gap-2 mb-2.5">
            <div className="bg-[#1a1500] border border-[#4d3d00] rounded px-2 py-1 flex justify-between items-center">
              <span className="text-yellow-600/90 font-bold text-[9px] uppercase tracking-wider">Or Gold (24K)</span>
              <span className="text-yellow-400 font-mono font-bold text-xs">{equivalentGold.toFixed(3)}g</span>
            </div>
            <div className="bg-[#0a1128] border border-[#1a2d66] rounded px-2 py-1 flex justify-between items-center">
              <span className="text-blue-500/90 font-bold text-[9px] uppercase tracking-wider">Or Silver (Fine)</span>
              <span className="text-blue-300 font-mono font-bold text-xs">{equivalentSilver.toFixed(3)}g</span>
            </div>
          </div>
        )}

        {/* Generate Bill Button */}
        <button
          disabled={cart.length === 0}
          onClick={handleGenerate}
          className="bg-primary hover:bg-primary-dark text-black font-bold py-2.5 rounded w-full flex items-center justify-center gap-2 transition-colors disabled:opacity-50 text-sm shadow-md"
        >
          <Calculator size={16} />
          GENERATE BILL (F7)
        </button>

        {/* Secondary Actions */}
        <div className="flex items-center gap-2 mt-2">
          <button
            type="button"
            onClick={() => {
              if (cart.length > 0 && window.confirm("Clear all items from bill?")) {
                clearCart();
              }
            }}
            disabled={cart.length === 0}
            className="w-full py-1 text-[11px] bg-background border border-gray-800 hover:border-red-900/60 hover:text-red-400 rounded text-gray-500 flex items-center justify-center gap-1 transition-colors disabled:opacity-30"
          >
            <RotateCcw size={11} /> Clear Bill
          </button>
        </div>
      </div>

      {/* Checkout Modal */}
      {showCheckout && checkoutPayload && (
        <CheckoutModal
          payload={checkoutPayload}
          grandTotal={grandTotal}
          onClose={() => setShowCheckout(false)}
          onSuccess={() => {
            setShowCheckout(false);
            setCheckoutPayload(null);
            clearCart();
            useBillingStore.getState().setSelectedCustomerId(null);
          }}
        />
      )}

      {/* Rates Modal */}
      {showRatesModal && (
        <LiveRatesModal onClose={() => setShowRatesModal(false)} />
      )}
    </div>
  );
}
