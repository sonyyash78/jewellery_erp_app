import { useState, useEffect } from 'react';
import { useBillingStore } from '../../store/billingStore';
import type { BillItem } from '../../store/billingStore';
import toast from 'react-hot-toast';
import { ShoppingCart, RotateCcw } from 'lucide-react';

const InputLabel = ({ label }: { label: string }) => (
  <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1">{label}</label>
);

export default function MetalCalculator() {
  const [metal, setMetal] = useState<'Gold' | 'Silver'>('Gold');
  const {
    goldForm, updateGoldForm, resetGoldForm,
    silverForm, updateSilverForm, resetSilverForm,
    addToCart, liveRates, editingItemId, setEditingItemId, cart
  } = useBillingStore();

  useEffect(() => {
    if (editingItemId) {
      const item = cart.find(i => i.id === editingItemId);
      if (item && (item.itemType === 'Gold' || item.itemType === 'Silver')) {
        setMetal(item.itemType);
      }
    }
  }, [editingItemId, cart]);

  const handleMetalSwitch = (m: 'Gold' | 'Silver') => {
    setMetal(m);
  };

  const handleReset = () => {
    if (metal === 'Gold') resetGoldForm();
    else resetSilverForm();
  };

  const handleCancelEdit = () => {
    setEditingItemId(null);
    if (metal === 'Gold') resetGoldForm();
    else resetSilverForm();
  };

  // ── Gold calculations ──
  const gNetWeight = Math.max(0, (goldForm.grossWeight || 0) - (goldForm.stoneWeight || 0));
  const gFineWeight = gNetWeight * (((goldForm.touch || 0) + (goldForm.wastage || 0)) / 100);
  const gMetalValue = gFineWeight * ((goldForm.ratePerGm || 0) / 10);
  let gMaking = 0;
  if (goldForm.makingChargeType === 'percent') gMaking = gMetalValue * (goldForm.makingChargeValue / 100);
  else if (goldForm.makingChargeType === 'per_gm') gMaking = gNetWeight * goldForm.makingChargeValue;
  else gMaking = goldForm.makingChargeValue;
  const gTaxable = Math.max(0, gMetalValue + gMaking + (goldForm.hallmark || 0) + (goldForm.otherCharges || 0) - (goldForm.discount || 0));

  // ── Silver calculations ──
  const sNetWeight = Math.max(0, (silverForm.grossWeight || 0) - (silverForm.stoneWeight || 0));
  const sFineWeight = sNetWeight * (((silverForm.tanch || 0) + (silverForm.wastage || 0)) / 100);
  const sMetalValue = sFineWeight * ((silverForm.ratePerKg || 0) / 1000);
  let sMaking = 0;
  if (silverForm.makingChargeType === 'percent') sMaking = sMetalValue * (silverForm.makingChargeValue / 100);
  else if (silverForm.makingChargeType === 'per_gm') sMaking = sNetWeight * silverForm.makingChargeValue;
  else sMaking = silverForm.makingChargeValue;
  const sTaxable = Math.max(0, sMetalValue + sMaking + (silverForm.otherCharges || 0) - (silverForm.discount || 0));

  const handleGoldAdd = () => {
    if ((goldForm.grossWeight || 0) <= 0) { toast.error('Gross weight must be > 0'); return; }
    if (gNetWeight <= 0) { toast.error('Net weight must be > 0'); return; }
    if ((goldForm.touch || 0) + (goldForm.wastage || 0) > 100) { toast.error('Touch % + Wastage % cannot be greater than 100%'); return; }
    const item: BillItem = {
      id: editingItemId || Math.random().toString(36).substring(7),
      itemType: 'Gold', 
      itemName: goldForm.itemName.trim() || `${goldForm.purity} Gold`,
      purityDisplay: goldForm.purity, touchDisplay: goldForm.touch, wastageDisplay: goldForm.wastage,
      grossWeight: goldForm.grossWeight, stoneWeight: goldForm.stoneWeight, netWeight: gNetWeight, fineWeight: gFineWeight,
      rateDisplay: goldForm.ratePerGm, metalValue: gMetalValue, makingAmount: gMaking,
      hallmark: goldForm.hallmark, otherCharges: goldForm.otherCharges, discount: goldForm.discount,
      taxableAmount: gTaxable, rawGold: { ...goldForm }
    };
    addToCart(item); 
    toast.success(editingItemId ? 'Item Updated in Bill' : 'Added to Bill'); 
    resetGoldForm();
  };

  const handleSilverAdd = () => {
    if ((silverForm.grossWeight || 0) <= 0) { toast.error('Gross weight must be > 0'); return; }
    if (sNetWeight <= 0) { toast.error('Net weight must be > 0'); return; }
    if ((silverForm.tanch || 0) + (silverForm.wastage || 0) > 100) { toast.error('Tanch % + Wastage % cannot be greater than 100%'); return; }
    const item: BillItem = {
      id: editingItemId || Math.random().toString(36).substring(7),
      itemType: 'Silver', 
      itemName: silverForm.itemName.trim() || `${silverForm.silverPurity} Silver`,
      purityDisplay: silverForm.silverPurity, touchDisplay: silverForm.tanch, wastageDisplay: silverForm.wastage,
      grossWeight: silverForm.grossWeight, stoneWeight: silverForm.stoneWeight || 0,
      netWeight: sNetWeight, fineWeight: sFineWeight,
      rateDisplay: silverForm.ratePerKg, metalValue: sMetalValue, makingAmount: sMaking,
      hallmark: 0, otherCharges: silverForm.otherCharges, discount: silverForm.discount,
      taxableAmount: sTaxable, rawSilver: { ...silverForm }
    };
    addToCart(item); 
    toast.success(editingItemId ? 'Item Updated in Bill' : 'Added to Bill'); 
    resetSilverForm();
  };

  const isGold = metal === 'Gold';

  return (
    <div className="bg-[#111115] border border-gray-800 rounded-2xl p-4 shadow-[0_4px_20px_rgba(0,0,0,0.5)] flex flex-col h-full">
      {/* Header */}
      <div className="flex justify-between items-center border-b border-gray-800 pb-2 mb-3 shrink-0">
        <h3 className={`font-bold tracking-widest uppercase text-sm ${editingItemId ? 'text-amber-400' : isGold ? 'text-primary' : 'text-gray-300'}`}>
          {editingItemId ? '✏️ Edit Item' : 'Add Item'}
        </h3>
        <div className="flex items-center gap-2">
          {editingItemId && (
            <button onClick={handleCancelEdit} className="text-xs text-amber-400 hover:text-amber-300 underline font-medium">
              Cancel Edit
            </button>
          )}
          <button onClick={handleReset} className={`text-xs hover:text-white transition-colors flex items-center gap-1 ${isGold ? 'text-primary' : 'text-gray-400'}`}>
            <RotateCcw size={12} /> Reset
          </button>
        </div>
      </div>

      {/* Editing Banner */}
      {editingItemId && (
        <div className="bg-amber-500/10 border border-amber-500/40 rounded-xl p-2.5 mb-3 flex justify-between items-center shrink-0">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-400 animate-pulse" />
            <div>
              <div className="text-xs font-bold text-amber-400 uppercase tracking-wide">
                Editing Item In Bill
              </div>
              <div className="text-[11px] text-gray-300">
                {isGold ? (goldForm.itemName || `${goldForm.purity} Gold`) : (silverForm.itemName || `${silverForm.silverPurity} Silver`)}
              </div>
            </div>
          </div>
          <button 
            type="button" 
            onClick={handleCancelEdit}
            className="text-xs bg-gray-800 hover:bg-gray-700 text-gray-300 hover:text-white px-2.5 py-1 rounded transition-colors"
          >
            Cancel
          </button>
        </div>
      )}

      {/* Gold / Silver Toggle — pinned, always visible */}
      <div className="flex rounded-lg overflow-hidden border border-gray-700 bg-background shrink-0 mb-3">
        <button
          onClick={() => handleMetalSwitch('Gold')}
          className={`flex-1 py-2 text-xs font-bold uppercase tracking-wide transition-all ${isGold ? 'bg-yellow-500/20 text-yellow-400 border-b-2 border-yellow-500' : 'text-gray-500 hover:text-gray-200 hover:bg-gray-800/40'}`}
        >
          🥇 Gold
        </button>
        <button
          onClick={() => handleMetalSwitch('Silver')}
          className={`flex-1 py-2 text-xs font-bold uppercase tracking-wide transition-all ${!isGold ? 'bg-gray-600/30 text-gray-100 border-b-2 border-gray-400' : 'text-gray-500 hover:text-gray-200 hover:bg-gray-800/40'}`}
        >
          🥈 Silver
        </button>
      </div>

      {/* Scrollable form area */}
      <div className="flex-1 overflow-y-auto pr-2 space-y-3 custom-scrollbar pb-4 min-h-0">

        {isGold ? (
          <>
            {/* Gold Form */}
            <div>
              <InputLabel label="Item Name / Description" />
              <input value={goldForm.itemName} onChange={e => updateGoldForm('itemName', e.target.value)}
                placeholder="e.g. 22K Gold Ring, Chain, Bangle..."
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
                    onClick={() => { updateGoldForm('purity', p.val); updateGoldForm('ratePerGm', p.rate); updateGoldForm('touch', p.touch); }}
                    className={`px-3 py-1 text-[11px] font-medium rounded border transition-colors ${goldForm.purity === p.val ? 'bg-primary/20 border-primary text-primary font-bold' : 'bg-[#1A1A20] border-gray-700 text-gray-400 hover:border-gray-500 hover:text-gray-200'}`}>
                    {p.label}
                  </button>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-3 gap-3">
              <div><InputLabel label="Gross Wt(g)" /><input type="number" step="0.001" value={goldForm.grossWeight ? goldForm.grossWeight : ''} onChange={e => updateGoldForm('grossWeight', e.target.value === '' ? 0 : Number(e.target.value))} placeholder="0.000" className="w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm text-white focus:border-primary outline-none font-mono" /></div>
              <div><InputLabel label="Stone Wt(g)" /><input type="number" step="0.001" value={goldForm.stoneWeight ? goldForm.stoneWeight : ''} onChange={e => updateGoldForm('stoneWeight', e.target.value === '' ? 0 : Number(e.target.value))} placeholder="0.000" className="w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm text-white focus:border-primary outline-none font-mono" /></div>
              <div><InputLabel label="Net Wt(g)" /><input disabled value={gNetWeight.toFixed(3)} className="w-full bg-gray-900 border border-gray-800 rounded px-2 py-1 text-sm text-gray-500 outline-none font-mono cursor-not-allowed" /></div>
            </div>

            <div className="grid grid-cols-3 gap-3">
              <div><InputLabel label="Touch %" /><input type="number" step="0.1" value={goldForm.touch ? goldForm.touch : ''} onChange={e => updateGoldForm('touch', e.target.value === '' ? 0 : Number(e.target.value))} placeholder="91.6" className="w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm text-primary focus:border-primary outline-none font-mono" /></div>
              <div><InputLabel label="Wastage %" /><input type="number" step="0.1" value={goldForm.wastage ? goldForm.wastage : ''} onChange={e => updateGoldForm('wastage', e.target.value === '' ? 0 : Number(e.target.value))} placeholder="0.0" className="w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm text-primary focus:border-primary outline-none font-mono" /></div>
              <div><InputLabel label="Fine Wt(g)" /><input disabled value={gFineWeight.toFixed(3)} className="w-full bg-gray-900 border border-gray-800 rounded px-2 py-1 text-sm text-primary/70 outline-none font-mono cursor-not-allowed" /></div>
            </div>

            {/* Rate & Metal Value Dual Controls */}
            <div className="grid grid-cols-2 gap-3 p-2.5 bg-gray-900/40 rounded-lg border border-gray-800">
              <div>
                <div className="flex justify-between items-center mb-1">
                  <InputLabel label="Rate (₹/10g)" />
                  <span className="text-[10px] text-gray-400 font-mono">
                    ₹{((goldForm.ratePerGm || 0) / 10).toFixed(1)}/g
                  </span>
                </div>
                <input 
                  type="number" 
                  value={goldForm.ratePerGm ? goldForm.ratePerGm : ''} 
                  onChange={e => updateGoldForm('ratePerGm', e.target.value === '' ? 0 : Number(e.target.value))} 
                  placeholder="e.g. 72500" 
                  className="w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm text-white focus:border-primary outline-none font-mono" 
                />
              </div>
              <div>
                <div className="flex justify-between items-center mb-1">
                  <InputLabel label="Metal Value (₹)" />
                  <span className="text-[9px] text-primary/70 font-mono">Fine × Rate</span>
                </div>
                <input 
                  type="number" 
                  value={gMetalValue > 0 ? Number(gMetalValue.toFixed(2)) : ''} 
                  onChange={e => {
                    const val = Number(e.target.value);
                    if (gFineWeight > 0) {
                      const computedRate = Math.round((val / gFineWeight) * 10);
                      updateGoldForm('ratePerGm', computedRate);
                    }
                  }}
                  placeholder="0.00" 
                  className="w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm text-yellow-400 focus:border-primary outline-none font-mono" 
                />
              </div>
            </div>

            <div className="pt-1">
              <h4 className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-2 border-b border-gray-800 pb-1">Charges</h4>
              <div className="flex items-center justify-between mb-2">
                <span className="text-[10px] text-gray-500 uppercase tracking-wider font-bold">Making Charge Type</span>
                <div className="flex bg-[#1A1A20] rounded border border-gray-800">
                  {[{ label: '%', val: 'percent' }, { label: '₹/g', val: 'per_gm' }, { label: '₹ Flat', val: 'flat' }].map(t => (
                    <button key={t.val} onClick={() => updateGoldForm('makingChargeType', t.val)}
                      className={`px-3 py-0.5 text-xs rounded-sm transition-colors ${goldForm.makingChargeType === t.val ? 'bg-primary text-black font-bold' : 'text-gray-400'}`}>
                      {t.label}
                    </button>
                  ))}
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3 mb-3">
                <div><InputLabel label="Making Value" /><input type="number" value={goldForm.makingChargeValue ? goldForm.makingChargeValue : ''} onChange={e => updateGoldForm('makingChargeValue', e.target.value === '' ? 0 : Number(e.target.value))} placeholder="0" className="w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm text-white focus:border-primary outline-none font-mono" /></div>
                <div><InputLabel label="Total Making" /><input disabled value={`₹${gMaking.toFixed(2)}`} className="w-full bg-gray-900 border border-gray-800 rounded px-2 py-1 text-sm text-gray-500 outline-none font-mono cursor-not-allowed" /></div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div><InputLabel label="Hallmark (+)" /><input type="number" value={goldForm.hallmark ? goldForm.hallmark : ''} onChange={e => updateGoldForm('hallmark', e.target.value === '' ? 0 : Number(e.target.value))} placeholder="0" className="w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm text-white focus:border-primary outline-none font-mono" /></div>
                <div><InputLabel label="Other (+)" /><input type="number" value={goldForm.otherCharges ? goldForm.otherCharges : ''} onChange={e => updateGoldForm('otherCharges', e.target.value === '' ? 0 : Number(e.target.value))} placeholder="0" className="w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm text-white focus:border-primary outline-none font-mono" /></div>
              </div>
            </div>

            <div className="pt-1">
              <div className="grid grid-cols-2 gap-3">
                <div><InputLabel label="Discount (-)" /><input type="number" value={goldForm.discount ? goldForm.discount : ''} onChange={e => updateGoldForm('discount', e.target.value === '' ? 0 : Number(e.target.value))} placeholder="0" className="w-full bg-red-950/20 border border-red-900/50 rounded px-2 py-1 text-sm text-red-400 focus:border-red-500 outline-none font-mono" /></div>
              </div>
            </div>
          </>
        ) : (
          <>
            {/* Silver Form */}
            <div>
              <InputLabel label="Item Name / Description" />
              <input value={silverForm.itemName} onChange={e => updateSilverForm('itemName', e.target.value)}
                placeholder="e.g. Silver Payal, Idol, Utensil..."
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
                    onClick={() => { updateSilverForm('silverPurity', p.val); updateSilverForm('tanch', p.tanch); updateSilverForm('ratePerKg', liveRates.silver); }}
                    className={`px-3 py-1 text-[11px] font-medium rounded border transition-colors ${silverForm.silverPurity === p.val ? 'bg-gray-700/50 border-gray-300 text-gray-200 font-bold' : 'bg-[#1A1A20] border-gray-700 text-gray-400 hover:border-gray-500 hover:text-gray-200'}`}>
                    {p.label}
                  </button>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-3 gap-3">
              <div><InputLabel label="Gross Wt(g)" /><input type="number" step="0.01" value={silverForm.grossWeight ? silverForm.grossWeight : ''} onChange={e => updateSilverForm('grossWeight', e.target.value === '' ? 0 : Number(e.target.value))} placeholder="0.00" className="w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm text-white focus:border-gray-500 outline-none font-mono" /></div>
              <div><InputLabel label="Stone Wt(g)" /><input type="number" step="0.01" value={silverForm.stoneWeight ? silverForm.stoneWeight : ''} onChange={e => updateSilverForm('stoneWeight', e.target.value === '' ? 0 : Number(e.target.value))} placeholder="0.00" className="w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm text-white focus:border-gray-500 outline-none font-mono" /></div>
              <div><InputLabel label="Net Wt(g)" /><input disabled value={sNetWeight.toFixed(3)} className="w-full bg-gray-900 border border-gray-800 rounded px-2 py-1 text-sm text-gray-500 outline-none font-mono cursor-not-allowed" /></div>
            </div>

            <div className="grid grid-cols-3 gap-3">
              <div><InputLabel label="Tanch %" /><input type="number" step="0.1" value={silverForm.tanch ? silverForm.tanch : ''} onChange={e => updateSilverForm('tanch', e.target.value === '' ? 0 : Number(e.target.value))} placeholder="65.0" className="w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm text-gray-300 focus:border-gray-500 outline-none font-mono" /></div>
              <div><InputLabel label="Wastage %" /><input type="number" step="0.1" value={silverForm.wastage ? silverForm.wastage : ''} onChange={e => updateSilverForm('wastage', e.target.value === '' ? 0 : Number(e.target.value))} placeholder="0.0" className="w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm text-gray-300 focus:border-gray-500 outline-none font-mono" /></div>
              <div><InputLabel label="Fine Wt(g)" /><input disabled value={sFineWeight.toFixed(3)} className="w-full bg-gray-900 border border-gray-800 rounded px-2 py-1 text-sm text-gray-300/70 outline-none font-mono cursor-not-allowed" /></div>
            </div>

            {/* Silver Rate & Value Controls */}
            <div className="grid grid-cols-2 gap-3 p-2.5 bg-gray-900/40 rounded-lg border border-gray-800">
              <div>
                <div className="flex justify-between items-center mb-1">
                  <InputLabel label="Rate (₹/kg)" />
                  <span className="text-[10px] text-gray-400 font-mono">
                    ₹{((silverForm.ratePerKg || 0) / 1000).toFixed(1)}/g
                  </span>
                </div>
                <input 
                  type="number" 
                  value={silverForm.ratePerKg ? silverForm.ratePerKg : ''} 
                  onChange={e => updateSilverForm('ratePerKg', e.target.value === '' ? 0 : Number(e.target.value))} 
                  placeholder="e.g. 90000" 
                  className="w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm text-white focus:border-gray-500 outline-none font-mono" 
                />
              </div>
              <div>
                <div className="flex justify-between items-center mb-1">
                  <InputLabel label="Metal Value (₹)" />
                  <span className="text-[9px] text-gray-400 font-mono">Fine × Rate</span>
                </div>
                <input 
                  type="number" 
                  value={sMetalValue > 0 ? Number(sMetalValue.toFixed(2)) : ''} 
                  onChange={e => {
                    const val = Number(e.target.value);
                    if (sFineWeight > 0) {
                      const computedRate = Math.round((val / sFineWeight) * 1000);
                      updateSilverForm('ratePerKg', computedRate);
                    }
                  }}
                  placeholder="0.00" 
                  className="w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm text-gray-200 focus:border-gray-500 outline-none font-mono" 
                />
              </div>
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
                <div><InputLabel label="Making Value" /><input type="number" value={silverForm.makingChargeValue ? silverForm.makingChargeValue : ''} onChange={e => updateSilverForm('makingChargeValue', e.target.value === '' ? 0 : Number(e.target.value))} placeholder="0" className="w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm text-white focus:border-gray-500 outline-none font-mono" /></div>
                <div><InputLabel label="Total Making" /><input disabled value={`₹${sMaking.toFixed(2)}`} className="w-full bg-gray-900 border border-gray-800 rounded px-2 py-1 text-sm text-gray-500 outline-none font-mono cursor-not-allowed" /></div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div><InputLabel label="Other (+)" /><input type="number" value={silverForm.otherCharges ? silverForm.otherCharges : ''} onChange={e => updateSilverForm('otherCharges', e.target.value === '' ? 0 : Number(e.target.value))} placeholder="0" className="w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm text-white focus:border-gray-500 outline-none font-mono" /></div>
              </div>
            </div>

            <div className="pt-1">
              <div className="grid grid-cols-2 gap-3">
                <div><InputLabel label="Discount (-)" /><input type="number" value={silverForm.discount ? silverForm.discount : ''} onChange={e => updateSilverForm('discount', e.target.value === '' ? 0 : Number(e.target.value))} placeholder="0" className="w-full bg-red-950/20 border border-red-900/50 rounded px-2 py-1 text-sm text-red-400 focus:border-red-500 outline-none font-mono" /></div>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Footer */}
      <div className="mt-2 pt-3 border-t border-gray-800/50 shrink-0">
        <div className="flex justify-between items-center mb-3 px-1">
          <span className="text-gray-400 text-sm font-medium">Taxable Amount</span>
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
            <ShoppingCart size={18} /> {editingItemId ? 'UPDATE ITEM' : 'ADD TO BILL'}
          </button>
        </div>
      </div>
    </div>
  );
}
