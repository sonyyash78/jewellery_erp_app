import { useState, useEffect } from 'react';
import { usePurchaseStore } from '../../store/purchaseStore';
import type { PurchaseItem } from '../../store/purchaseStore';
import { RotateCcw, ShoppingCart } from 'lucide-react';
import { useBillingStore } from '../../store/billingStore';
import toast from 'react-hot-toast';

const InputLabel = ({ label }: { label: string }) => (
  <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1">{label}</label>
);

export default function PurchaseMetalForm() {
  const [metal, setMetal] = useState<'Gold' | 'Silver'>('Gold');
  const { goldForm, updateGoldForm, silverForm, updateSilverForm, resetForms, addItem, editingItemId, items, setEditingItemId } = usePurchaseStore();
  const { liveRates } = useBillingStore();

  useEffect(() => {
    if (editingItemId) {
      const item = items.find(i => i.id === editingItemId);
      if (item && (item.metalType === 'Gold' || item.metalType === 'Silver')) {
        setMetal(item.metalType as 'Gold' | 'Silver');
      }
    }
  }, [editingItemId, items]);

  // Auto-update rate and purity when switching metal (only when not editing an existing item)
  useEffect(() => {
    if (!editingItemId) {
      if (metal === 'Gold') {
        if (!goldForm.metalRate) updateGoldForm('metalRate', liveRates.gold22k || 72500);
        if (!goldForm.touchPurity || goldForm.touchPurity <= 0) updateGoldForm('touchPurity', 91.6);
      } else {
        if (!silverForm.metalRate) updateSilverForm('metalRate', liveRates.silver || 90000);
        if (!silverForm.tanch || silverForm.tanch <= 0) updateSilverForm('tanch', 99.9);
      }
    }
  }, [metal, editingItemId, goldForm.touchPurity, silverForm.tanch]);

  const handleCancelEdit = () => {
    setEditingItemId(null);
    resetForms();
  };

  const isGold = metal === 'Gold';

  // ── Gold calculations ──
  const gNet = (goldForm.grossWeight || 0) - (goldForm.stoneWeight || 0);
  const gFine = gNet * (((goldForm.touchPurity || 0) + (goldForm.wastage || 0)) / 100);
  const gMetal = gFine * ((goldForm.metalRate || 0) / 10);
  let gMaking = 0; if(goldForm.makingChargeType==='percent') gMaking = gMetal*((goldForm.makingChargeValue||0)/100); else if(goldForm.makingChargeType==='per_gm') gMaking = gNet*(goldForm.makingChargeValue||0); else gMaking = goldForm.makingChargeValue||0;
  const gTaxable = Math.max(0, gMetal + gMaking + (goldForm.labourCharge || 0) + (goldForm.hallmarkCharge || 0) + (goldForm.otherCharges || 0) - (goldForm.discount || 0));

  // ── Silver calculations ──
  const sNet = (silverForm.grossWeight || 0) - (silverForm.stoneWeight || 0);
  const sFine = sNet * (((silverForm.tanch || 0) + (silverForm.wastage || 0)) / 100);
  const sMetal = sFine * ((silverForm.metalRate || 0) / 1000);
  let sMaking = 0; if(silverForm.makingChargeType==='percent') sMaking = sMetal*((silverForm.makingChargeValue||0)/100); else if(silverForm.makingChargeType==='per_gm') sMaking = sNet*(silverForm.makingChargeValue||0); else sMaking = silverForm.makingChargeValue||0;
  const sTaxable = Math.max(0, sMetal + sMaking + (silverForm.testingMeltingCharge || 0) + (silverForm.otherCharges || 0) - (silverForm.discount || 0));

  const handleGoldAdd = () => {
    if ((goldForm.grossWeight || 0) <= 0) { toast.error('Gross weight must be > 0'); return; }
    if (gNet <= 0) { toast.error('Net weight must be > 0'); return; }
    const touch = Number(goldForm.touchPurity || 91.6);
    if (touch <= 0) { toast.error('Touch purity must be greater than 0'); return; }
    if (touch + (goldForm.wastage || 0) > 100) { toast.error('Touch % + Wastage % cannot be greater than 100%'); return; }
    const item: PurchaseItem = {
      id: editingItemId || Math.random().toString(36).substring(7),
      metalType: 'Gold', itemName: goldForm.itemName || 'Gold Item',
      category: goldForm.category || 'Gold',
      grossWeight: goldForm.grossWeight, stoneWeight: goldForm.stoneWeight, netWeight: gNet,
      touchPurity: touch, wastage: goldForm.wastage || 0, fineWeight: gFine,
      metalRate: goldForm.metalRate, metalValue: gMetal,
      labourCharge: (goldForm.labourCharge || 0) + gMaking,
      makingChargeType: goldForm.makingChargeType || 'flat',
      makingChargeValue: goldForm.makingChargeValue || 0,
      testingMeltingCharge: 0,
      hallmarkCharge: goldForm.hallmarkCharge || 0, otherCharges: goldForm.otherCharges || 0,
      discount: goldForm.discount || 0, taxableAmount: gTaxable
    };
    addItem(item); toast.success('Gold added to purchase list'); resetForms();
  };

  const handleSilverAdd = () => {
    if ((silverForm.grossWeight || 0) <= 0) { toast.error('Gross weight must be > 0'); return; }
    if (sNet <= 0) { toast.error('Net weight must be > 0'); return; }
    const tanch = Number(silverForm.tanch || 99.9);
    if (tanch <= 0) { toast.error('Tanch / Touch purity must be greater than 0'); return; }
    if (tanch + (silverForm.wastage || 0) > 100) { toast.error('Tanch % + Wastage % cannot be greater than 100%'); return; }
    const item: PurchaseItem = {
      id: editingItemId || Math.random().toString(36).substring(7),
      metalType: 'Silver', itemName: silverForm.itemName || 'Silver Item',
      category: 'Silver',
      grossWeight: silverForm.grossWeight, stoneWeight: silverForm.stoneWeight || 0, netWeight: sNet,
      touchPurity: tanch, wastage: silverForm.wastage || 0, fineWeight: sFine,
      metalRate: silverForm.metalRate, metalValue: sMetal,
      labourCharge: sMaking,
      makingChargeType: silverForm.makingChargeType || 'flat',
      makingChargeValue: silverForm.makingChargeValue || 0,
      testingMeltingCharge: silverForm.testingMeltingCharge || 0,
      hallmarkCharge: 0, otherCharges: silverForm.otherCharges || 0,
      discount: silverForm.discount || 0, taxableAmount: sTaxable
    };
    addItem(item); toast.success('Silver added to purchase list'); resetForms();
  };

  return (
    <div className="bg-[#111115] border border-gray-800 rounded-2xl p-4 shadow-[0_4px_20px_rgba(0,0,0,0.5)] flex flex-col h-full">
      {/* Header */}
      <div className="flex justify-between items-center border-b border-gray-800 pb-2 mb-3 shrink-0">
        <h3 className={`font-bold tracking-widest uppercase text-sm ${isGold ? 'text-primary' : 'text-gray-300'}`}>
          Purchase — {isGold ? 'Gold' : 'Silver'}
        </h3>
        <button onClick={resetForms} className={`text-xs hover:text-white transition-colors flex items-center gap-1 ${isGold ? 'text-primary' : 'text-gray-400'}`}>
          <RotateCcw size={12} /> Reset
        </button>
      </div>

      {/* Gold / Silver Toggle — pinned */}
      <div className="flex rounded-lg overflow-hidden border border-gray-700 bg-background shrink-0 mb-3">
        <button onClick={() => setMetal('Gold')}
          className={`flex-1 py-2 text-xs font-bold uppercase tracking-wide transition-all ${isGold ? 'bg-yellow-500/20 text-yellow-400 border-b-2 border-yellow-500' : 'text-gray-500 hover:text-gray-200 hover:bg-gray-800/40'}`}>
          🥇 Gold
        </button>
        <button onClick={() => setMetal('Silver')}
          className={`flex-1 py-2 text-xs font-bold uppercase tracking-wide transition-all ${!isGold ? 'bg-gray-600/30 text-gray-100 border-b-2 border-gray-400' : 'text-gray-500 hover:text-gray-200 hover:bg-gray-800/40'}`}>
          🥈 Silver
        </button>
      </div>

      {/* Scrollable form area */}
      <div className="flex-1 overflow-y-auto pr-2 space-y-3 custom-scrollbar pb-4 min-h-0">
        {isGold ? (
          <>
            <div>
              <input value={goldForm.itemName} onChange={e => updateGoldForm('itemName', e.target.value)}
                placeholder="Item Name / Description (Optional)"
                className="w-full bg-[#1A1A20] border border-gray-800 rounded px-3 py-2 text-sm text-white focus:border-primary outline-none transition-all placeholder-gray-600" />
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-400 mb-1.5">Gold Purity</label>
              <div className="flex flex-wrap gap-2">
                {[
                  { label: '14K', val: '14K Gold', rate: liveRates.gold14k, touch: 58.3 },
                  { label: '18K', val: '18K Gold', rate: liveRates.gold18k, touch: 75.0 },
                  { label: '20K', val: '20K Gold', rate: liveRates.gold20k, touch: 83.3 },
                  { label: '22K', val: '22K Gold', rate: liveRates.gold22k, touch: 91.6 },
                  { label: '24K', val: '24K Gold', rate: liveRates.gold24k, touch: 99.9 },
                ].map(p => (
                  <button key={p.val}
                    onClick={() => { updateGoldForm('category', p.val); updateGoldForm('metalRate', p.rate); updateGoldForm('touchPurity', p.touch); }}
                    className={`px-3 py-1 text-[11px] font-medium rounded border transition-colors ${goldForm.category === p.val ? 'bg-primary/20 border-primary text-primary' : 'bg-[#1A1A20] border-gray-700 text-gray-400 hover:border-gray-500 hover:text-gray-200'}`}>
                    {p.label}
                  </button>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-3 gap-3">
              <div><InputLabel label="Gross Wt(g)" /><input type="number" value={goldForm.grossWeight === 0 ? 0 : goldForm.grossWeight || ''} onChange={e => updateGoldForm('grossWeight', Number(e.target.value))} className="w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm text-white focus:border-primary outline-none font-mono" /></div>
              <div><InputLabel label="Stone Wt(g)" /><input type="number" value={goldForm.stoneWeight === 0 ? 0 : goldForm.stoneWeight || ''} onChange={e => updateGoldForm('stoneWeight', Number(e.target.value))} className="w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm text-white focus:border-primary outline-none font-mono" /></div>
              <div><InputLabel label="Net Wt(g)" /><input disabled value={gNet.toFixed(3)} className="w-full bg-gray-900 border border-gray-800 rounded px-2 py-1 text-sm text-gray-500 outline-none font-mono cursor-not-allowed" /></div>
            </div>

            <div className="grid grid-cols-3 gap-3">
              <div><InputLabel label="Touch %" /><input type="number" step="0.1" value={goldForm.touchPurity === 0 ? 0 : goldForm.touchPurity || ''} onChange={e => updateGoldForm('touchPurity', Number(e.target.value))} className="w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm text-primary focus:border-primary outline-none font-mono" /></div>
              <div><InputLabel label="Wastage %" /><input type="number" step="0.1" value={goldForm.wastage === 0 ? 0 : goldForm.wastage || ''} onChange={e => updateGoldForm('wastage', Number(e.target.value))} className="w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm text-primary focus:border-primary outline-none font-mono" /></div>
              <div><InputLabel label="Fine Wt(g)" /><input disabled value={gFine.toFixed(3)} className="w-full bg-gray-900 border border-gray-800 rounded px-2 py-1 text-sm text-primary/70 outline-none font-mono cursor-not-allowed" /></div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div><InputLabel label="Rate (₹/10g)" /><input type="number" value={goldForm.metalRate === 0 ? 0 : goldForm.metalRate || ''} onChange={e => updateGoldForm('metalRate', Number(e.target.value))} className="w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm text-white focus:border-primary outline-none font-mono" /></div>
              <div><InputLabel label="Metal Value" /><input disabled value={`₹${gMetal.toFixed(2)}`} className="w-full bg-gray-900 border border-gray-800 rounded px-2 py-1 text-sm text-gray-500 outline-none font-mono cursor-not-allowed" /></div>
            </div>

            <div className="pt-1">
              <h4 className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-2 border-b border-gray-800 pb-1">Charges</h4>
              <div className="flex items-center justify-between mb-2">
                <span className="text-[10px] text-gray-500 uppercase tracking-wider font-bold">Making Charge Type</span>
                <div className="flex bg-[#1A1A20] rounded border border-gray-800">
                  {[{ label: '%', val: 'percent' }, { label: '₹/g', val: 'per_gm' }, { label: '₹ Flat', val: 'flat' }].map(t => (
                    <button key={t.val} onClick={() => updateGoldForm('makingChargeType', t.val)}
                      className={`px-3 py-0.5 text-xs rounded-sm transition-colors ${goldForm.makingChargeType === t.val ? 'bg-gray-300 text-black font-bold' : 'text-gray-400'}`}>
                      {t.label}
                    </button>
                  ))}
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3 mb-3">
                <div><InputLabel label="Making Value" /><input type="number" value={goldForm.makingChargeValue === 0 ? 0 : goldForm.makingChargeValue || ''} onChange={e => updateGoldForm('makingChargeValue', Number(e.target.value))} className="w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm text-white focus:border-gray-500 outline-none font-mono" /></div>
                <div><InputLabel label="Total Making" /><input disabled value={`₹${gMaking.toFixed(2)}`} className="w-full bg-gray-900 border border-gray-800 rounded px-2 py-1 text-sm text-gray-500 outline-none font-mono cursor-not-allowed" /></div>
              </div>
              
              <h4 className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-2 border-b border-gray-800 pb-1">Additional Charges &amp; Discount</h4>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 sm:gap-3 mb-3">
                <div><InputLabel label="Labour (+)" /><input type="number" value={goldForm.labourCharge === 0 ? 0 : goldForm.labourCharge || ''} onChange={e => updateGoldForm('labourCharge', Number(e.target.value))} className="w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm text-white focus:border-primary outline-none font-mono" /></div>
                <div><InputLabel label="Hallmark (+)" /><input type="number" value={goldForm.hallmarkCharge === 0 ? 0 : goldForm.hallmarkCharge || ''} onChange={e => updateGoldForm('hallmarkCharge', Number(e.target.value))} className="w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm text-white focus:border-primary outline-none font-mono" /></div>
                <div><InputLabel label="Other (+)" /><input type="number" value={goldForm.otherCharges === 0 ? 0 : goldForm.otherCharges || ''} onChange={e => updateGoldForm('otherCharges', Number(e.target.value))} className="w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm text-white focus:border-primary outline-none font-mono" /></div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div><InputLabel label="Discount (-)" /><input type="number" value={goldForm.discount === 0 ? 0 : goldForm.discount || ''} onChange={e => updateGoldForm('discount', Number(e.target.value))} className="w-full bg-red-950/20 border border-red-900/50 rounded px-2 py-1 text-sm text-red-400 focus:border-red-500 outline-none font-mono" /></div>
              </div>
            </div>
          </>
        ) : (
          <>
            <div>
              <input value={silverForm.itemName} onChange={e => updateSilverForm('itemName', e.target.value)}
                placeholder="Item Name / Description (Optional)"
                className="w-full bg-[#1A1A20] border border-gray-800 rounded px-3 py-2 text-sm text-white focus:border-gray-500 outline-none transition-all placeholder-gray-600" />
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-400 mb-1.5">Silver Purity</label>
              <div className="flex flex-wrap gap-2">
                {[
                  { label: 'Fine (99.9)', val: 'Fine', tanch: 99.9 },
                  { label: 'Sterling (92.5)', val: 'Sterling', tanch: 92.5 },
                  { label: 'Custom (65.0)', val: 'Custom', tanch: 65.0 },
                ].map(p => (
                  <button key={p.val}
                    onClick={() => updateSilverForm('tanch', p.tanch)}
                    className={`px-3 py-1 text-[11px] font-medium rounded border transition-colors ${silverForm.tanch === p.tanch ? 'bg-gray-700/50 border-gray-300 text-gray-200' : 'bg-[#1A1A20] border-gray-700 text-gray-400 hover:border-gray-500 hover:text-gray-200'}`}>
                    {p.label}
                  </button>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-3 gap-3">
              <div><InputLabel label="Gross Wt(g)" /><input type="number" step="0.01" value={silverForm.grossWeight === 0 ? 0 : silverForm.grossWeight || ''} onChange={e => updateSilverForm('grossWeight', Number(e.target.value))} className="w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm text-white focus:border-gray-500 outline-none font-mono" /></div>
              <div><InputLabel label="Stone Wt(g)" /><input type="number" step="0.01" value={silverForm.stoneWeight === 0 ? 0 : silverForm.stoneWeight || ''} onChange={e => updateSilverForm('stoneWeight', Number(e.target.value))} className="w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm text-white focus:border-gray-500 outline-none font-mono" /></div>
              <div><InputLabel label="Net Wt(g)" /><input disabled value={sNet.toFixed(3)} className="w-full bg-gray-900 border border-gray-800 rounded px-2 py-1 text-sm text-gray-500 outline-none font-mono cursor-not-allowed" /></div>
            </div>

            <div className="grid grid-cols-3 gap-3">
              <div><InputLabel label="Tanch %" /><input type="number" step="0.1" value={silverForm.tanch === 0 ? 0 : silverForm.tanch || ''} onChange={e => updateSilverForm('tanch', Number(e.target.value))} className="w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm text-gray-300 focus:border-gray-500 outline-none font-mono" /></div>
              <div><InputLabel label="Wastage %" /><input type="number" step="0.1" value={silverForm.wastage === 0 ? 0 : silverForm.wastage || ''} onChange={e => updateSilverForm('wastage', Number(e.target.value))} className="w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm text-gray-300 focus:border-gray-500 outline-none font-mono" /></div>
              <div><InputLabel label="Fine Wt(g)" /><input disabled value={sFine.toFixed(3)} className="w-full bg-gray-900 border border-gray-800 rounded px-2 py-1 text-sm text-gray-300/70 outline-none font-mono cursor-not-allowed" /></div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div><InputLabel label="Rate (₹/kg)" /><input type="number" value={silverForm.metalRate === 0 ? 0 : silverForm.metalRate || ''} onChange={e => updateSilverForm('metalRate', Number(e.target.value))} className="w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm text-white focus:border-gray-500 outline-none font-mono" /></div>
              <div><InputLabel label="Metal Value" /><input disabled value={`₹${sMetal.toFixed(2)}`} className="w-full bg-gray-900 border border-gray-800 rounded px-2 py-1 text-sm text-gray-500 outline-none font-mono cursor-not-allowed" /></div>
            </div>

            <div className="pt-1">
              <h4 className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-2 border-b border-gray-800 pb-1">Charges</h4>
              <div className="flex items-center justify-between mb-2">
                <span className="text-[10px] text-gray-500 uppercase tracking-wider font-bold">Making Charge Type</span>
                <div className="flex bg-[#1A1A20] rounded border border-gray-800">
                  {[{ label: '%', val: 'percent' }, { label: '₹/g', val: 'per_gm' }, { label: '₹ Flat', val: 'flat' }].map(t => (
                    <button key={t.val} onClick={() => updateSilverForm('makingChargeType', t.val)}
                      className={`px-3 py-0.5 text-xs rounded-sm transition-colors ${silverForm.makingChargeType === t.val ? 'bg-gray-300 text-black font-bold' : 'text-gray-400'}`}>
                      {t.label}
                    </button>
                  ))}
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3 mb-3">
                <div><InputLabel label="Making Value" /><input type="number" value={silverForm.makingChargeValue === 0 ? 0 : silverForm.makingChargeValue || ''} onChange={e => updateSilverForm('makingChargeValue', Number(e.target.value))} className="w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm text-white focus:border-gray-500 outline-none font-mono" /></div>
                <div><InputLabel label="Total Making" /><input disabled value={`₹${sMaking.toFixed(2)}`} className="w-full bg-gray-900 border border-gray-800 rounded px-2 py-1 text-sm text-gray-500 outline-none font-mono cursor-not-allowed" /></div>
              </div>
              
              <h4 className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-2 border-b border-gray-800 pb-1">Additional Charges &amp; Discount</h4>
              <div className="grid grid-cols-2 gap-3 mb-3">
                <div><InputLabel label="Test/Melt (+)" /><input type="number" value={silverForm.testingMeltingCharge === 0 ? 0 : silverForm.testingMeltingCharge || ''} onChange={e => updateSilverForm('testingMeltingCharge', Number(e.target.value))} className="w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm text-white focus:border-gray-500 outline-none font-mono" /></div>
                <div><InputLabel label="Other (+)" /><input type="number" value={silverForm.otherCharges === 0 ? 0 : silverForm.otherCharges || ''} onChange={e => updateSilverForm('otherCharges', Number(e.target.value))} className="w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm text-white focus:border-gray-500 outline-none font-mono" /></div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div><InputLabel label="Discount (-)" /><input type="number" value={silverForm.discount === 0 ? 0 : silverForm.discount || ''} onChange={e => updateSilverForm('discount', Number(e.target.value))} className="w-full bg-red-950/20 border border-red-900/50 rounded px-2 py-1 text-sm text-red-400 focus:border-red-500 outline-none font-mono" /></div>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Footer */}
      <div className="mt-2 pt-3 border-t border-gray-800/50 shrink-0">
        <div className="flex justify-between items-center mb-3 px-1">
          <span className="text-gray-400 text-sm font-medium">Payable Amount</span>
          <span className={`font-bold text-lg font-mono ${isGold ? 'text-primary' : 'text-gray-300'}`}>
            ₹{isGold ? gTaxable.toFixed(2) : sTaxable.toFixed(2)}
          </span>
        </div>
        <div className="flex gap-2">
          {editingItemId && (
            <button
              type="button"
              onClick={handleCancelEdit}
              className="w-1/3 bg-gray-800 hover:bg-gray-700 text-white font-bold py-3 rounded-lg flex items-center justify-center transition-all"
            >
              Cancel
            </button>
          )}
          <button
            onClick={isGold ? handleGoldAdd : handleSilverAdd}
            className={`flex-1 font-bold py-3 rounded-lg flex items-center justify-center gap-2 transition-all ${isGold
              ? 'bg-primary hover:bg-primary-dark text-black shadow-[0_0_15px_rgba(212,175,55,0.2)]'
              : 'bg-gray-300 hover:bg-gray-400 text-black shadow-[0_0_15px_rgba(200,200,200,0.1)]'}`}
          >
            <ShoppingCart size={18} /> {editingItemId ? 'UPDATE ITEM' : 'ADD TO RECEIPT'}
          </button>
        </div>
      </div>
    </div>
  );
}
