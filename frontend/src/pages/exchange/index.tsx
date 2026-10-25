import { useState, useEffect } from 'react';
import OldItemsForm from './OldItemsForm';
import NewItemScanner from './NewItemScanner';
import { useExchangeStore } from '../../store/exchangeStore';
import { axiosClient } from '../../api/axiosClient';
import toast from 'react-hot-toast';
import { Trash2, Edit2 } from 'lucide-react';
import ExchangeCheckoutModal from './ExchangeCheckoutModal';

export default function ExchangeModule() {
  const { oldItems, newItems, gstState, setGstState, removeOldItem, removeNewItem, customerId, setCustomerId, clearExchange, setEditingOldItem, setEditingNewItem } = useExchangeStore();
  
  const [customers, setCustomers] = useState<any[]>([]);
  const [showCheckout, setShowCheckout] = useState(false);
  
  const totalOldValue = oldItems.reduce((acc, i) => acc + i.calculatedValue, 0);
  const totalNewValue = newItems.reduce((acc, i) => acc + i.finalPrice, 0);
  
  // Tax calculation on New Value
  let gstAmount = 0;
  if (gstState !== 'none') {
    gstAmount = totalNewValue * 0.03; // 3% GST standard on jewellery
  }
  const grandTotal = totalNewValue + gstAmount;
  
  // Difference = What customer pays - what we owe them
  const differenceAmount = grandTotal - totalOldValue;

  useEffect(() => {
    axiosClient.get('/customers/').then(res => setCustomers(res.data.items)).catch();
  }, []);

  const handleProcessExchange = () => {
    // if (!customerId) return toast.error("Select a customer"); // We'll let the modal handle it or require it there
    if (oldItems.length === 0 && newItems.length === 0) return toast.error("No items in exchange");
    setShowCheckout(true);
  };

  const getPayload = () => {
    return {
      total_old_value: totalOldValue,
      total_new_value: totalNewValue,
      gst_amount: gstAmount,
      grand_total: grandTotal,
      difference_amount: differenceAmount,
      old_items: oldItems.map(i => ({
        item_name: i.itemName, metal: i.metal, purity: i.purity, touch: i.touch,
        gross_weight: i.grossWeight, stone_weight: i.stoneWeight, net_weight: i.netWeight,
        wastage: i.wastage || 0, fine_weight: i.fineWeight || 0,
        labour_charge: i.labourCharge || 0, testing_melting_charge: i.testingMeltingCharge || 0,
        hallmark_charge: i.hallmarkCharge || 0, other_charges: i.otherCharges || 0,
        discount: i.discount || 0,
        rate_applied: i.rateApplied, calculated_value: i.calculatedValue
      })),
      new_items: newItems.map(i => ({
        stock_item_id: i.stockItemId, item_name: i.itemName, metal: i.metal,
        net_weight: i.netWeight, gross_weight: i.grossWeight || 0,
        stone_weight: i.stoneWeight || 0, touch_purity: i.touchPurity || 100,
        wastage: i.wastage || 0, fine_weight: i.fineWeight || 0,
        making_charge_type: i.makingChargeType || 'flat',
        making_charge_rate: i.makingChargeRate || 0,
        making_charges_amount: i.makingCharges || 0,
        hallmark_charges: i.hallmark || 0, other_charges: i.otherCharges || 0,
        discount: i.discount || 0, rate_applied: i.rateApplied || 0,
        final_price: i.finalPrice
      }))
    };
  };

  // Metal IN / OUT calculations
  const goldOldFine = oldItems.filter(i => i.metal === 'Gold').reduce((acc, i) => acc + (i.fineWeight || 0), 0);
  const goldNewFine = newItems.filter(i => i.metal === 'Gold').reduce((acc, i) => acc + (i.fineWeight || 0), 0);
  const goldNetFine = goldNewFine - goldOldFine; // Positive = Customer owes gold (New > Old), Negative = Customer has surplus gold

  const silverOldFine = oldItems.filter(i => i.metal === 'Silver').reduce((acc, i) => acc + (i.fineWeight || 0), 0);
  const silverNewFine = newItems.filter(i => i.metal === 'Silver').reduce((acc, i) => acc + (i.fineWeight || 0), 0);
  const silverNetFine = silverNewFine - silverOldFine; // Positive = Customer owes silver (New > Old), Negative = Customer has surplus silver

  const hasMetalActivity = goldOldFine > 0 || goldNewFine > 0 || silverOldFine > 0 || silverNewFine > 0;

  return (
    <div className="h-auto lg:h-[calc(100vh-4.5rem)] flex flex-col gap-2.5 overflow-y-auto lg:overflow-hidden p-0.5 sm:p-1">
      
      {/* Top Bar Customer Select */}
      <div className="bg-surface border border-gray-800 rounded-xl px-3 sm:px-4 py-2 shadow-lg flex flex-wrap justify-between items-center z-10 shrink-0 gap-2 sm:gap-3">
        <div className="flex items-center gap-2 flex-1 min-w-[200px] sm:min-w-[240px]">
          <label className="text-xs font-bold text-gray-500 uppercase shrink-0">Customer</label>
          <select 
            value={customerId || ''} 
            onChange={(e) => setCustomerId(Number(e.target.value))}
            className="bg-background border border-gray-700 rounded px-2.5 sm:px-3 py-1.5 outline-none text-textMain text-xs sm:text-sm w-full max-w-[320px]"
          >
            <option value="">-- Select Customer --</option>
            {customers.map(c => (
              <option key={c.id} value={c.id}>{c.first_name} {c.last_name || ''} ({c.phone_number})</option>
            ))}
          </select>
        </div>
        <div className="text-primary font-bold text-xs tracking-widest uppercase flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-primary animate-pulse" />
          Exchange Module
        </div>
      </div>

      {/* Main Layout: Responsive 1-col on mobile/tablet, 3-col on desktop */}
      <div className="flex-1 min-h-0 grid grid-cols-1 lg:grid-cols-12 gap-3 lg:overflow-hidden pb-8 lg:pb-0">
        
        {/* Left Column: Old Metal Evaluation */}
        <div className="lg:col-span-4 min-h-[480px] lg:min-h-0 h-full flex flex-col overflow-hidden">
          <OldItemsForm />
        </div>

        {/* Center Column: Purchase New Item */}
        <div className="lg:col-span-4 min-h-[440px] lg:min-h-0 h-full flex flex-col overflow-hidden">
          <NewItemScanner />
        </div>

        {/* Right Column: Receipt Summary */}
        <div className="lg:col-span-4 min-h-[460px] lg:min-h-0 h-full flex flex-col bg-surface border border-primary/30 rounded-2xl shadow-[0_4px_20px_rgba(0,0,0,0.5)] overflow-hidden">
          <div className="bg-background border-b border-gray-800 px-4 py-2.5 flex justify-between items-center shrink-0">
            <h2 className="text-sm font-bold text-primary flex items-center gap-2 uppercase tracking-widest">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>
              Exchange Summary
            </h2>
            <span className="text-[11px] font-mono bg-primary/10 text-primary px-2 py-0.5 rounded font-bold">ITEMS: {oldItems.length + newItems.length}</span>
          </div>

          {/* Scrollable Items List */}
          <div className="flex-1 min-h-0 overflow-y-auto p-3 custom-scrollbar space-y-2.5">
            {oldItems.length === 0 && newItems.length === 0 ? (
              <div className="h-full flex items-center justify-center text-textMuted text-xs italic">No items added yet</div>
            ) : (
              <>
                {oldItems.map(item => (
                  <div key={`old-${item.id}`} className="bg-background border border-gray-800 rounded p-2.5 relative group">
                    <div className="absolute top-1.5 right-1.5 flex space-x-1.5 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button onClick={() => setEditingOldItem(item)} className="text-gray-600 hover:text-blue-400 transition-colors"><Edit2 size={14} /></button>
                      <button onClick={() => removeOldItem(item.id)} className="text-gray-600 hover:text-red-400 transition-colors"><Trash2 size={14} /></button>
                    </div>
                    <div className="flex justify-between items-start mb-1.5 pr-10">
                      <div>
                        <span className="text-[10px] font-bold px-1.5 py-0.5 rounded mr-1.5 bg-green-500/20 text-green-400">OLD (IN)</span>
                        <span className="text-xs text-textMain font-medium">{item.itemName}</span>
                      </div>
                      <span className="text-xs font-mono text-green-400 font-bold">- ₹{item.calculatedValue.toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2})}</span>
                    </div>
                    <div className="grid grid-cols-2 gap-x-3 gap-y-0.5 text-[10.5px] text-textMuted">
                      <div className="flex justify-between"><span>Net Wt:</span><span className="font-mono">{item.netWeight}g</span></div>
                      <div className="flex justify-between"><span>Tanch:</span><span className="font-mono">{item.touch}%</span></div>
                      <div className="flex justify-between"><span>Fine:</span><span className="font-mono text-primary font-bold">{item.fineWeight.toFixed(3)}g</span></div>
                      <div className="flex justify-between"><span>Rate:</span><span className="font-mono">₹{item.rateApplied}</span></div>
                    </div>
                  </div>
                ))}
                
                {newItems.map(item => (
                  <div key={`new-${item.id}`} className="bg-background border border-gray-800 rounded p-2.5 relative group">
                    <div className="absolute top-1.5 right-1.5 flex space-x-1.5 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button onClick={() => setEditingNewItem(item)} className="text-gray-600 hover:text-blue-400 transition-colors" title="Edit Item"><Edit2 size={14} /></button>
                      <button onClick={() => removeNewItem(item.id)} className="text-gray-600 hover:text-red-400 transition-colors" title="Delete Item"><Trash2 size={14} /></button>
                    </div>
                    <div className="flex justify-between items-start mb-1.5 pr-10">
                      <div>
                        <span className="text-[10px] font-bold px-1.5 py-0.5 rounded mr-1.5 bg-primary/20 text-primary">NEW (OUT)</span>
                        <span className="text-xs text-textMain font-medium">{item.itemName}</span>
                      </div>
                      <span className="text-xs font-mono text-red-400 font-bold">+ ₹{item.finalPrice.toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2})}</span>
                    </div>
                    <div className="grid grid-cols-2 gap-x-3 gap-y-0.5 text-[10.5px] text-textMuted">
                      <div className="flex justify-between"><span>Net Wt:</span><span className="font-mono">{item.netWeight}g</span></div>
                      <div className="flex justify-between"><span>Making:</span><span className="font-mono">₹{item.makingCharges.toLocaleString()}</span></div>
                      <div className="flex justify-between"><span>Other:</span><span className="font-mono">₹{(item.hallmark + item.otherCharges).toLocaleString()}</span></div>
                      <div className="flex justify-between"><span>Rate:</span><span className="font-mono">₹{item.rateApplied}</span></div>
                    </div>
                  </div>
                ))}
              </>
            )}
          </div>

          {/* Bottom Fixed Summary & Totals */}
          <div className="bg-background border-t border-gray-800 p-3 shrink-0">
            
            {/* Metal In / Out Summary Card */}
            {hasMetalActivity && (
              <div className="bg-[#16161D] border border-gray-700/60 rounded-lg p-2.5 mb-2.5 space-y-1.5 shadow-inner">
                <div className="text-[9.5px] font-bold text-gray-400 uppercase tracking-widest flex items-center justify-between border-b border-gray-800 pb-1">
                  <span className="flex items-center gap-1.5 text-primary">⚖️ Metal In / Out Summary</span>
                  <span className="text-[8.5px] text-gray-500 font-normal">Fine Weights</span>
                </div>
                
                {/* Gold Row */}
                {(goldOldFine > 0 || goldNewFine > 0) && (
                  <div className="bg-yellow-950/20 border border-yellow-800/40 rounded px-2 py-1 flex items-center justify-between text-xs">
                    <span className="font-bold text-yellow-400">🥇 Gold</span>
                    <div className="flex items-center gap-3 text-[10.5px] font-mono">
                      <span className="text-gray-400">In: <strong className="text-green-400">{goldOldFine.toFixed(3)}g</strong></span>
                      <span className="text-gray-400">Out: <strong className="text-yellow-400">{goldNewFine.toFixed(3)}g</strong></span>
                      <span className={`font-bold px-1.5 py-0.5 rounded text-[10px] ${goldNetFine > 0.001 ? 'bg-red-500/20 text-red-400' : goldNetFine < -0.001 ? 'bg-green-500/20 text-green-400' : 'bg-gray-800 text-gray-400'}`}>
                        {goldNetFine > 0.001 ? `+${goldNetFine.toFixed(3)}g Due` : goldNetFine < -0.001 ? `${goldNetFine.toFixed(3)}g Surplus` : '0.000g'}
                      </span>
                    </div>
                  </div>
                )}

                {/* Silver Row */}
                {(silverOldFine > 0 || silverNewFine > 0) && (
                  <div className="bg-gray-800/30 border border-gray-700/40 rounded px-2 py-1 flex items-center justify-between text-xs">
                    <span className="font-bold text-gray-300">🥈 Silver</span>
                    <div className="flex items-center gap-3 text-[10.5px] font-mono">
                      <span className="text-gray-400">In: <strong className="text-green-400">{silverOldFine.toFixed(3)}g</strong></span>
                      <span className="text-gray-400">Out: <strong className="text-gray-200">{silverNewFine.toFixed(3)}g</strong></span>
                      <span className={`font-bold px-1.5 py-0.5 rounded text-[10px] ${silverNetFine > 0.001 ? 'bg-red-500/20 text-red-400' : silverNetFine < -0.001 ? 'bg-green-500/20 text-green-400' : 'bg-gray-800 text-gray-400'}`}>
                        {silverNetFine > 0.001 ? `+${silverNetFine.toFixed(3)}g Due` : silverNetFine < -0.001 ? `${silverNetFine.toFixed(3)}g Surplus` : '0.000g'}
                      </span>
                    </div>
                  </div>
                )}
              </div>
            )}

            <div className="flex justify-between items-center mb-2">
              <span className="text-xs text-textMuted font-medium">GST Type</span>
              <div className="flex gap-1.5">
                <button onClick={() => setGstState('same_state')} className={`px-2 py-0.5 rounded text-[10px] font-bold transition-colors ${gstState === 'same_state' ? 'bg-primary text-black' : 'bg-gray-800 text-gray-400'}`}>Same State</button>
                <button onClick={() => setGstState('different_state')} className={`px-2 py-0.5 rounded text-[10px] font-bold transition-colors ${gstState === 'different_state' ? 'bg-primary text-black' : 'bg-gray-800 text-gray-400'}`}>Interstate</button>
                <button onClick={() => setGstState('none')} className={`px-2 py-0.5 rounded text-[10px] font-bold transition-colors ${gstState === 'none' ? 'bg-primary text-black' : 'bg-gray-800 text-gray-400'}`}>No GST</button>
              </div>
            </div>

            <div className="space-y-0.5 mb-2.5 text-xs">
              <div className="flex justify-between text-textMuted"><span>Total New Value</span><span className="font-mono">₹{totalNewValue.toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2})}</span></div>
              <div className="flex justify-between text-textMuted"><span>GST ({gstState === 'none' ? '0%' : '3%'})</span><span className="font-mono">₹{gstAmount.toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2})}</span></div>
              <div className="flex justify-between text-textMain font-bold"><span>Grand Total (Bill)</span><span className="font-mono">₹{grandTotal.toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2})}</span></div>
              <div className="flex justify-between text-green-400"><span>Old Items Trade-In</span><span className="font-mono">- ₹{totalOldValue.toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2})}</span></div>
              
              <div className="flex justify-between text-base font-bold pt-1.5 border-t border-gray-800 mt-1 items-center">
                <span className="text-xs uppercase text-gray-400 font-bold">{differenceAmount > 0 ? 'Customer Pays' : differenceAmount < 0 ? 'You Pay' : 'Settled'}</span>
                <span className={`font-mono ${differenceAmount > 0 ? 'text-primary' : 'text-green-400'}`}>₹{Math.abs(differenceAmount).toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2})}</span>
              </div>
            </div>

            <button 
              disabled={oldItems.length === 0 && newItems.length === 0}
              onClick={handleProcessExchange}
              className="bg-primary hover:bg-primary-dark text-black font-bold py-2.5 rounded w-full flex items-center justify-center gap-2 transition-colors disabled:opacity-50 text-sm shadow-md"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path><polyline points="17 21 17 13 7 13 7 21"></polyline><polyline points="7 3 7 8 15 8"></polyline></svg>
              Process Exchange
            </button>
          </div>
        </div>
      </div>
      
      {showCheckout && (
        <ExchangeCheckoutModal 
          payload={getPayload()}
          differenceAmount={differenceAmount}
          onClose={() => setShowCheckout(false)}
          onSuccess={() => {
            setShowCheckout(false);
            clearExchange();
          }}
        />
      )}
    </div>
  );
}
