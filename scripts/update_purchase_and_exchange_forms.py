import os

# New content for PurchaseMetalForm.tsx
purchase_metal_form_code = """import { useState, useEffect } from 'react';
import { usePurchaseStore } from '../../store/purchaseStore';
import type { PurchaseItem } from '../../store/purchaseStore';
import { RotateCcw, ShoppingCart } from 'lucide-react';
import { useBillingStore } from '../../store/billingStore';
import toast from 'react-hot-toast';

const InputLabel = ({ label }: { label: string }) => (
  <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1">{label}</label>
);

export default function PurchaseMetalForm() {
  const [metal, setMetal] = useState<'Gold' | 'Silver' | 'Diamond'>('Gold');
  const { 
    goldForm, updateGoldForm, 
    silverForm, updateSilverForm, 
    diamondForm, updateDiamondForm,
    resetForms, addItem, editingItemId, items, setEditingItemId 
  } = usePurchaseStore();
  const { liveRates } = useBillingStore();

  useEffect(() => {
    if (editingItemId) {
      const item = items.find(i => i.id === editingItemId);
      if (item && (item.metalType === 'Gold' || item.metalType === 'Silver' || item.metalType === 'Diamond')) {
        setMetal(item.metalType as 'Gold' | 'Silver' | 'Diamond');
      }
    }
  }, [editingItemId, items]);

  // Auto-update rate and purity when switching metal (only when not editing an existing item)
  useEffect(() => {
    if (!editingItemId) {
      if (metal === 'Gold') {
        if (!goldForm.metalRate) updateGoldForm('metalRate', liveRates.gold22k || 72500);
        if (!goldForm.touchPurity || goldForm.touchPurity <= 0) updateGoldForm('touchPurity', 91.6);
      } else if (metal === 'Silver') {
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
  const isDiamond = metal === 'Diamond';

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

  // ── Diamond calculations (Weight in Grams) ──
  const dWeight = Math.max(0, diamondForm.weightGm || 0);
  const dRate = Math.max(0, diamondForm.ratePerGm || 0);
  const dSubtotal = dWeight * dRate;
  const dTaxable = Math.max(0, dSubtotal + (diamondForm.labourCharge || 0) + (diamondForm.otherCharges || 0) - (diamondForm.discount || 0));

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

  const handleDiamondAdd = () => {
    if (dWeight <= 0) { toast.error('Diamond weight in grams must be > 0'); return; }
    if (dRate <= 0) { toast.error('Rate per gram must be > 0'); return; }
    const item: PurchaseItem = {
      id: editingItemId || Math.random().toString(36).substring(7),
      metalType: 'Diamond',
      itemName: diamondForm.itemName.trim() || `${diamondForm.diamondType} ${diamondForm.shape} Diamond`,
      category: 'Diamond',
      grossWeight: dWeight,
      stoneWeight: 0,
      netWeight: dWeight,
      touchPurity: 100,
      wastage: 0,
      fineWeight: dWeight,
      metalRate: dRate,
      metalValue: dSubtotal,
      labourCharge: diamondForm.labourCharge || 0,
      makingChargeType: 'flat',
      makingChargeValue: 0,
      testingMeltingCharge: 0,
      hallmarkCharge: 0,
      otherCharges: diamondForm.otherCharges || 0,
      discount: diamondForm.discount || 0,
      taxableAmount: dTaxable,
      diamondType: diamondForm.diamondType,
      shape: diamondForm.shape,
      pieces: diamondForm.pieces,
      colour: diamondForm.colour,
      clarity: diamondForm.clarity,
      certificateNo: diamondForm.certificateNo,
      weightGm: dWeight,
      ratePerGm: dRate
    };
    addItem(item);
    toast.success('Diamond added to purchase list');
    resetForms();
  };

  return (
    <div className="bg-[#111115] border border-gray-800 rounded-2xl p-4 shadow-[0_4px_20px_rgba(0,0,0,0.5)] flex flex-col h-full">
      {/* Header */}
      <div className="flex justify-between items-center border-b border-gray-800 pb-2 mb-3 shrink-0">
        <h3 className={`font-bold tracking-widest uppercase text-sm ${isDiamond ? 'text-cyan-400' : isGold ? 'text-primary' : 'text-gray-300'}`}>
          Purchase — {isDiamond ? 'Diamond (Gms)' : isGold ? 'Gold' : 'Silver'}
        </h3>
        <button onClick={resetForms} className={`text-xs hover:text-white transition-colors flex items-center gap-1 ${isDiamond ? 'text-cyan-400' : isGold ? 'text-primary' : 'text-gray-400'}`}>
          <RotateCcw size={12} /> Reset
        </button>
      </div>

      {/* Metal Toggle — pinned */}
      <div className="flex rounded-lg overflow-hidden border border-gray-700 bg-background shrink-0 mb-3">
        <button onClick={() => setMetal('Gold')}
          className={`flex-1 py-2 text-xs font-bold uppercase tracking-wide transition-all ${isGold ? 'bg-yellow-500/20 text-yellow-400 border-b-2 border-yellow-500' : 'text-gray-500 hover:text-gray-200 hover:bg-gray-800/40'}`}>
          🥇 Gold
        </button>
        <button onClick={() => setMetal('Silver')}
          className={`flex-1 py-2 text-xs font-bold uppercase tracking-wide transition-all ${metal === 'Silver' ? 'bg-gray-600/30 text-gray-100 border-b-2 border-gray-400' : 'text-gray-500 hover:text-gray-200 hover:bg-gray-800/40'}`}>
          🥈 Silver
        </button>
        <button onClick={() => setMetal('Diamond')}
          className={`flex-1 py-2 text-xs font-bold uppercase tracking-wide transition-all ${isDiamond ? 'bg-cyan-500/20 text-cyan-400 border-b-2 border-cyan-400' : 'text-gray-500 hover:text-gray-200 hover:bg-gray-800/40'}`}>
          💎 Diamond
        </button>
      </div>

      {/* Scrollable form area */}
      <div className="flex-1 overflow-y-auto pr-2 space-y-3 custom-scrollbar pb-4 min-h-0">
        {isDiamond ? (
          <>
            <div>
              <InputLabel label="Diamond Description" />
              <input value={diamondForm.itemName} onChange={e => updateDiamondForm('itemName', e.target.value)}
                placeholder="e.g. Diamond Parcel / Cut Polished / Solitaire"
                className="w-full bg-[#1A1A20] border border-gray-800 rounded px-3 py-2 text-sm text-white focus:border-cyan-500 outline-none transition-all placeholder-gray-600" />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <InputLabel label="Diamond Type" />
                <select value={diamondForm.diamondType} onChange={e => updateDiamondForm('diamondType', e.target.value)}
                  className="w-full bg-[#1A1A20] border border-gray-800 rounded px-2 py-1.5 text-xs text-white focus:border-cyan-500 outline-none">
                  <option value="NATURAL">Natural Diamond</option>
                  <option value="SYNTHETIC">Synthetic / Lab Grown</option>
                </select>
              </div>
              <div>
                <InputLabel label="Shape" />
                <select value={diamondForm.shape} onChange={e => updateDiamondForm('shape', e.target.value)}
                  className="w-full bg-[#1A1A20] border border-gray-800 rounded px-2 py-1.5 text-xs text-white focus:border-cyan-500 outline-none">
                  {['Round', 'Princess', 'Cushion', 'Oval', 'Emerald', 'Pear', 'Radiant', 'Marquise', 'Heart'].map(s => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-2">
              <div>
                <InputLabel label="Weight in Grams (gm)" />
                <input type="number" step="0.001" value={diamondForm.weightGm || ''}
                  onChange={e => updateDiamondForm('weightGm', e.target.value === '' ? 0 : Number(e.target.value))}
                  placeholder="0.000 gm" className="w-full bg-[#1A1A20] border border-cyan-800/60 rounded px-2 py-1 text-sm text-cyan-300 font-bold focus:border-cyan-400 outline-none font-mono" />
              </div>
              <div>
                <InputLabel label="Pieces" />
                <input type="number" value={diamondForm.pieces || ''}
                  onChange={e => updateDiamondForm('pieces', e.target.value === '' ? 1 : Number(e.target.value))}
                  placeholder="1" className="w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm text-white focus:border-cyan-500 outline-none font-mono" />
              </div>
              <div>
                <InputLabel label="Rate / Gram (₹/gm)" />
                <input type="number" value={diamondForm.ratePerGm || ''}
                  onChange={e => updateDiamondForm('ratePerGm', e.target.value === '' ? 0 : Number(e.target.value))}
                  placeholder="25000" className="w-full bg-[#1A1A20] border border-cyan-800/60 rounded px-2 py-1 text-sm text-cyan-300 font-bold focus:border-cyan-400 outline-none font-mono" />
              </div>
            </div>

            <div className="grid grid-cols-3 gap-2">
              <div>
                <InputLabel label="Colour" />
                <select value={diamondForm.colour} onChange={e => updateDiamondForm('colour', e.target.value)}
                  className="w-full bg-[#1A1A20] border border-gray-800 rounded px-2 py-1 text-xs text-white focus:border-cyan-500 outline-none">
                  {['D', 'E', 'F', 'G', 'H', 'I', 'J', 'K-M'].map(c => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>
              <div>
                <InputLabel label="Clarity" />
                <select value={diamondForm.clarity} onChange={e => updateDiamondForm('clarity', e.target.value)}
                  className="w-full bg-[#1A1A20] border border-gray-800 rounded px-2 py-1 text-xs text-white focus:border-cyan-500 outline-none">
                  {['FL', 'IF', 'VVS1', 'VVS2', 'VS1', 'VS2', 'SI1', 'SI2', 'I1'].map(cl => <option key={cl} value={cl}>{cl}</option>)}
                </select>
              </div>
              <div>
                <InputLabel label="Certificate No." />
                <input value={diamondForm.certificateNo} onChange={e => updateDiamondForm('certificateNo', e.target.value)}
                  placeholder="IGI/GIA..." className="w-full bg-[#1A1A20] border border-gray-800 rounded px-2 py-1 text-xs text-white focus:border-cyan-500 outline-none" />
              </div>
            </div>

            <div className="pt-1">
              <h4 className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-2 border-b border-gray-800 pb-1">Charges &amp; Discount</h4>
              <div className="grid grid-cols-3 gap-2">
                <div>
                  <InputLabel label="Labour/Setting (+)" />
                  <input type="number" value={diamondForm.labourCharge || ''}
                    onChange={e => updateDiamondForm('labourCharge', e.target.value === '' ? 0 : Number(e.target.value))}
                    placeholder="0" className="w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm text-white focus:border-cyan-500 outline-none font-mono" />
                </div>
                <div>
                  <InputLabel label="Other (+)" />
                  <input type="number" value={diamondForm.otherCharges || ''}
                    onChange={e => updateDiamondForm('otherCharges', e.target.value === '' ? 0 : Number(e.target.value))}
                    placeholder="0" className="w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm text-white focus:border-cyan-500 outline-none font-mono" />
                </div>
                <div>
                  <InputLabel label="Discount (-)" />
                  <input type="number" value={diamondForm.discount || ''}
                    onChange={e => updateDiamondForm('discount', e.target.value === '' ? 0 : Number(e.target.value))}
                    placeholder="0" className="w-full bg-red-950/20 border border-red-900/50 rounded px-2 py-1 text-sm text-red-400 focus:border-red-500 outline-none font-mono" />
                </div>
              </div>
            </div>
          </>
        ) : isGold ? (
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
          <span className={`font-bold text-lg font-mono ${isDiamond ? 'text-cyan-400' : isGold ? 'text-primary' : 'text-gray-300'}`}>
            ₹{isDiamond ? dTaxable.toFixed(2) : isGold ? gTaxable.toFixed(2) : sTaxable.toFixed(2)}
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
            onClick={isDiamond ? handleDiamondAdd : isGold ? handleGoldAdd : handleSilverAdd}
            className={`flex-1 font-bold py-3 rounded-lg flex items-center justify-center gap-2 transition-all ${isDiamond
              ? 'bg-cyan-500 hover:bg-cyan-400 text-black shadow-[0_0_15px_rgba(6,182,212,0.3)]'
              : isGold
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
"""

# New content for OldItemsForm.tsx
old_items_form_code = """import { useState, useEffect } from 'react';
import { useExchangeStore } from '../../store/exchangeStore';
import { Plus } from 'lucide-react';
import { useBillingStore } from '../../store/billingStore';
import toast from 'react-hot-toast';

export default function OldItemsForm() {
  const { addOldItem, editingOldItem, updateOldItem, setEditingOldItem } = useExchangeStore();
  const { liveRates } = useBillingStore();
  
  const handlePuritySelect = (purityLabel: string, touchVal: number, rateVal: number) => {
    setPurity(purityLabel);
    setTouch(touchVal);
    if (rateVal > 0) setRateApplied(rateVal);
  };
  const [metal, setMetal] = useState<'Gold'|'Silver'|'Diamond'>('Gold');
  
  const [itemName, setItemName] = useState('');
  const [purity, setPurity] = useState('22K');
  const [touch, setTouch] = useState(91.6);
  const [wastage, setWastage] = useState(0);
  const [grossWeight, setGrossWeight] = useState(0);
  const [stoneWeight, setStoneWeight] = useState(0);
  const [rateApplied, setRateApplied] = useState(72500);
  
  // Deductions & Additions
  const [labourCharge, setLabourCharge] = useState(0);
  const [testingMeltingCharge, setTestingMeltingCharge] = useState(0);
  const [hallmarkCharge, setHallmarkCharge] = useState(0);
  const [discount, setDiscount] = useState(0); // For buying old gold, discount acts as deduction
  const [otherCharges, setOtherCharges] = useState(0);

  useEffect(() => {
    if (!editingOldItem) {
      if (metal === 'Gold') {
        setRateApplied(liveRates.gold22k || 72500);
        setTouch(91.6);
        setPurity('22K');
      } else if (metal === 'Silver') {
        setRateApplied(liveRates.silver || 90000);
        setTouch(99.9);
        setPurity('Fine');
      } else {
        setRateApplied(25000); // Default diamond rate per gram
        setTouch(100);
        setPurity('Diamond');
      }
    }
  }, [metal]);

  useEffect(() => {
    if (editingOldItem) {
      setMetal(editingOldItem.metal as 'Gold'|'Silver'|'Diamond');
      setItemName(editingOldItem.itemName);
      setPurity(editingOldItem.purity);
      setTouch(editingOldItem.touch);
      setWastage(editingOldItem.wastage || 0);
      setGrossWeight(editingOldItem.grossWeight);
      setStoneWeight(editingOldItem.stoneWeight);
      setRateApplied(editingOldItem.rateApplied);
      setLabourCharge(editingOldItem.labourCharge || 0);
      setTestingMeltingCharge(editingOldItem.testingMeltingCharge || 0);
      setHallmarkCharge(editingOldItem.hallmarkCharge || 0);
      setDiscount(editingOldItem.discount || 0);
      setOtherCharges(editingOldItem.otherCharges || 0);
    }
  }, [editingOldItem]);

  const isDiamond = metal === 'Diamond';
  const netWeight = grossWeight - stoneWeight;
  const fineWeight = isDiamond ? netWeight : (netWeight * ((touch + wastage) / 100));
  const metalValue = isDiamond
    ? (netWeight * rateApplied)
    : fineWeight * (metal === 'Gold' ? (rateApplied / 10) : (rateApplied / 1000));
  
  const calculatedValue = Math.max(0, metalValue - labourCharge - testingMeltingCharge - hallmarkCharge - discount + otherCharges);

  const handleAdd = (e: React.FormEvent) => {
    e.preventDefault();
    if (grossWeight <= 0) return toast.error('Please enter a valid weight');
    if (netWeight <= 0) return toast.error('Net weight must be > 0');
    if (!isDiamond && (touch || 0) + (wastage || 0) > 100) return toast.error('Touch % + Wastage % cannot be greater than 100%');
    
    const finalItemName = itemName.trim() || (isDiamond ? 'Old Diamond Jewellery' : `${purity} Old ${metal}`);
    const itemData = {
      id: editingOldItem ? editingOldItem.id : Date.now().toString(),
      itemName: finalItemName, metal, purity, touch, grossWeight, stoneWeight, netWeight, 
      wastage, fineWeight,
      labourCharge, testingMeltingCharge, hallmarkCharge, otherCharges, discount,
      rateApplied, calculatedValue
    };

    if (editingOldItem) {
      updateOldItem(editingOldItem.id, itemData);
      toast.success("Old item updated");
    } else {
      addOldItem(itemData);
      toast.success("Old item added");
    }
    
    // Reset Form
    setEditingOldItem(null);
    setItemName('');
    setGrossWeight(0);
    setStoneWeight(0);
    setLabourCharge(0);
    setTestingMeltingCharge(0);
    setHallmarkCharge(0);
    setDiscount(0);
    setOtherCharges(0);
    if (metal === 'Gold') {
      setPurity('22K');
      setTouch(91.6);
      setWastage(0);
      setRateApplied(liveRates.gold22k || 72500);
    } else if (metal === 'Silver') {
      setPurity('Fine');
      setTouch(99.9);
      setWastage(0);
      setRateApplied(liveRates.silver || 90000);
    } else {
      setPurity('Diamond');
      setTouch(100);
      setWastage(0);
      setRateApplied(25000);
    }
  };

  return (
    <div className="bg-surface border border-gray-800 rounded-xl p-4 sm:p-5 shadow-lg">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-base sm:text-lg font-bold flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span>
          {editingOldItem ? 'Edit Old Item' : 'Add Old Metal Received'}
        </h3>
        {editingOldItem && (
          <button 
            type="button" 
            onClick={() => {
              setEditingOldItem(null);
              setItemName('');
              setGrossWeight(0);
              setStoneWeight(0);
            }}
            className="text-xs text-textMuted hover:text-white"
          >
            Cancel Edit
          </button>
        )}
      </div>

      <div className="flex bg-background border border-gray-800 rounded-lg p-1 mb-4">
        <button
          type="button"
          onClick={() => setMetal('Gold')}
          className={`flex-1 py-1.5 text-xs font-bold rounded-md transition-all ${metal === 'Gold' ? 'bg-primary text-background' : 'text-textMuted hover:text-textMain'}`}
        >
          🥇 Gold
        </button>
        <button
          type="button"
          onClick={() => setMetal('Silver')}
          className={`flex-1 py-1.5 text-xs font-bold rounded-md transition-all ${metal === 'Silver' ? 'bg-gray-400 text-background' : 'text-textMuted hover:text-textMain'}`}
        >
          🥈 Silver
        </button>
        <button
          type="button"
          onClick={() => setMetal('Diamond')}
          className={`flex-1 py-1.5 text-xs font-bold rounded-md transition-all ${metal === 'Diamond' ? 'bg-cyan-500 text-background' : 'text-textMuted hover:text-textMain'}`}
        >
          💎 Diamond (Gms)
        </button>
      </div>

      <form onSubmit={handleAdd} className="space-y-4">
        <div>
          <label className="block text-xs font-medium text-textMuted mb-1">Item Description</label>
          <input 
            type="text" 
            value={itemName} 
            onChange={(e) => setItemName(e.target.value)} 
            placeholder={isDiamond ? "e.g., Old Diamond Ring / Bangles" : "e.g., Old Kundan Set / Payal"} 
            className="w-full bg-background border border-gray-800 rounded-lg px-3 py-2 text-sm text-textMain focus:border-primary outline-none"
          />
        </div>

        {isDiamond ? (
          <div className="bg-[#16161D] border border-cyan-800/40 rounded-xl p-3 space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-cyan-400 mb-1">Weight in Grams (gm)</label>
                <input 
                  type="number" 
                  step="0.001" 
                  value={grossWeight || ''} 
                  onChange={(e) => setGrossWeight(Number(e.target.value))} 
                  placeholder="0.000 gm"
                  className="w-full bg-background border border-cyan-700/60 rounded-lg px-3 py-2 text-sm font-mono font-bold text-cyan-300 focus:border-cyan-400 outline-none" 
                  required 
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-cyan-400 mb-1">Buying Rate / Gram (₹/gm)</label>
                <input 
                  type="number" 
                  value={rateApplied || ''} 
                  onChange={(e) => setRateApplied(Number(e.target.value))} 
                  placeholder="25000"
                  className="w-full bg-background border border-cyan-700/60 rounded-lg px-3 py-2 text-sm font-mono font-bold text-cyan-300 focus:border-cyan-400 outline-none" 
                  required 
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-textMuted mb-1">Stone/Wax Deduction (gm)</label>
                <input 
                  type="number" 
                  step="0.001" 
                  value={stoneWeight || ''} 
                  onChange={(e) => setStoneWeight(Number(e.target.value))} 
                  className="w-full bg-background border border-gray-800 rounded-lg px-3 py-2 text-sm font-mono text-textMain focus:border-cyan-500 outline-none" 
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-textMuted mb-1">Net Diamond Weight (gm)</label>
                <input 
                  type="text" 
                  value={`${netWeight > 0 ? netWeight.toFixed(3) : '0.000'} gm`} 
                  disabled 
                  className="w-full bg-gray-900 border border-gray-800 rounded-lg px-3 py-2 text-sm font-mono text-cyan-400 outline-none cursor-not-allowed" 
                />
              </div>
            </div>
          </div>
        ) : (
          <>
            <div>
              <label className="block text-xs font-medium text-textMuted mb-1.5">Preset Purity</label>
              <div className="flex flex-wrap gap-2">
                {metal === 'Gold' ? (
                  <>
                    <button type="button" onClick={() => handlePuritySelect('18K', 75.0, liveRates.gold18k || 0)} className={`px-2.5 py-1 text-xs rounded border transition-colors ${purity === '18K' ? 'bg-primary/20 border-primary text-primary' : 'border-gray-800 text-textMuted hover:border-gray-700'}`}>18K (75%)</button>
                    <button type="button" onClick={() => handlePuritySelect('20K', 83.3, liveRates.gold20k || 0)} className={`px-2.5 py-1 text-xs rounded border transition-colors ${purity === '20K' ? 'bg-primary/20 border-primary text-primary' : 'border-gray-800 text-textMuted hover:border-gray-700'}`}>20K (83.3%)</button>
                    <button type="button" onClick={() => handlePuritySelect('22K', 91.6, liveRates.gold22k || 72500)} className={`px-2.5 py-1 text-xs rounded border transition-colors ${purity === '22K' ? 'bg-primary/20 border-primary text-primary' : 'border-gray-800 text-textMuted hover:border-gray-700'}`}>22K (91.6%)</button>
                    <button type="button" onClick={() => handlePuritySelect('24K', 99.9, liveRates.gold24k || 0)} className={`px-2.5 py-1 text-xs rounded border transition-colors ${purity === '24K' ? 'bg-primary/20 border-primary text-primary' : 'border-gray-800 text-textMuted hover:border-gray-700'}`}>24K (99.9%)</button>
                  </>
                ) : (
                  <>
                    <button type="button" onClick={() => handlePuritySelect('92.5', 92.5, liveRates.silver || 90000)} className={`px-2.5 py-1 text-xs rounded border transition-colors ${purity === '92.5' ? 'bg-gray-400/20 border-gray-400 text-gray-200' : 'border-gray-800 text-textMuted hover:border-gray-700'}`}>92.5 Sterling</button>
                    <button type="button" onClick={() => handlePuritySelect('70.0', 70.0, liveRates.silver ? liveRates.silver * 0.7 : 63000)} className={`px-2.5 py-1 text-xs rounded border transition-colors ${purity === '70.0' ? 'bg-gray-400/20 border-gray-400 text-gray-200' : 'border-gray-800 text-textMuted hover:border-gray-700'}`}>70% Common</button>
                    <button type="button" onClick={() => handlePuritySelect('Fine', 99.9, liveRates.silver || 90000)} className={`px-2.5 py-1 text-xs rounded border transition-colors ${purity === 'Fine' ? 'bg-gray-400/20 border-gray-400 text-gray-200' : 'border-gray-800 text-textMuted hover:border-gray-700'}`}>99.9 Pure</button>
                  </>
                )}
              </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div>
                <label className="block text-xs font-medium text-textMuted mb-1">Gross Wt (g)</label>
                <input 
                  type="number" 
                  step="0.001" 
                  value={grossWeight || ''} 
                  onChange={(e) => setGrossWeight(Number(e.target.value))} 
                  className="w-full bg-background border border-gray-800 rounded-lg px-3 py-2 text-sm font-mono text-textMain focus:border-primary outline-none" 
                  required 
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-textMuted mb-1">Stone Wt (g)</label>
                <input 
                  type="number" 
                  step="0.001" 
                  value={stoneWeight || ''} 
                  onChange={(e) => setStoneWeight(Number(e.target.value))} 
                  className="w-full bg-background border border-gray-800 rounded-lg px-3 py-2 text-sm font-mono text-textMain focus:border-primary outline-none" 
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-textMuted mb-1">Touch / Purity %</label>
                <input 
                  type="number" 
                  step="0.1" 
                  value={touch || ''} 
                  onChange={(e) => setTouch(Number(e.target.value))} 
                  className="w-full bg-background border border-gray-800 rounded-lg px-3 py-2 text-sm font-mono text-textMain focus:border-primary outline-none" 
                  required 
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-textMuted mb-1">Wastage %</label>
                <input 
                  type="number" 
                  step="0.1" 
                  value={wastage || ''} 
                  onChange={(e) => setWastage(Number(e.target.value))} 
                  className="w-full bg-background border border-gray-800 rounded-lg px-3 py-2 text-sm font-mono text-textMain focus:border-primary outline-none" 
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-textMuted mb-1">
                Rate Applied ({metal === 'Gold' ? '₹/10g' : '₹/kg'})
              </label>
              <input 
                type="number" 
                value={rateApplied || ''} 
                onChange={(e) => setRateApplied(Number(e.target.value))} 
                className="w-full bg-background border border-gray-800 rounded-lg px-3 py-2 text-sm font-mono text-textMain focus:border-primary outline-none" 
                required 
              />
            </div>
          </>
        )}

        {/* Deductions & Additions */}
        <div className="pt-2 border-t border-gray-800">
          <div className="text-xs font-bold text-textMuted uppercase tracking-wider mb-2">Adjustments &amp; Deductions</div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            <div>
              <label className="block text-[10px] text-textMuted mb-1">Labour Ded. (-)</label>
              <input type="number" value={labourCharge || ''} onChange={e => setLabourCharge(Number(e.target.value))} placeholder="0" className="w-full bg-background border border-gray-800 rounded px-2 py-1 text-xs font-mono" />
            </div>
            <div>
              <label className="block text-[10px] text-textMuted mb-1">Test/Melt (-)</label>
              <input type="number" value={testingMeltingCharge || ''} onChange={e => setTestingMeltingCharge(Number(e.target.value))} placeholder="0" className="w-full bg-background border border-gray-800 rounded px-2 py-1 text-xs font-mono" />
            </div>
            <div>
              <label className="block text-[10px] text-textMuted mb-1">Discount (-)</label>
              <input type="number" value={discount || ''} onChange={e => setDiscount(Number(e.target.value))} placeholder="0" className="w-full bg-background border border-gray-800 rounded px-2 py-1 text-xs font-mono" />
            </div>
            <div>
              <label className="block text-[10px] text-textMuted mb-1">Other Adj. (+)</label>
              <input type="number" value={otherCharges || ''} onChange={e => setOtherCharges(Number(e.target.value))} placeholder="0" className="w-full bg-background border border-gray-800 rounded px-2 py-1 text-xs font-mono" />
            </div>
          </div>
        </div>

        {/* Calculation Summary Box */}
        <div className="bg-background border border-gray-800 rounded-lg p-3 space-y-1.5 font-mono text-xs">
          <div className="flex justify-between text-textMuted">
            <span>Net Weight:</span>
            <span>{netWeight > 0 ? netWeight.toFixed(3) : '0.000'} {isDiamond ? 'gm' : 'g'}</span>
          </div>
          {!isDiamond && (
            <div className="flex justify-between text-textMuted">
              <span>Fine Weight ({touch + wastage}%):</span>
              <span className="text-primary">{fineWeight > 0 ? fineWeight.toFixed(3) : '0.000'} g</span>
            </div>
          )}
          <div className="flex justify-between text-textMuted">
            <span>Base Metal Value:</span>
            <span>₹{metalValue.toFixed(2)}</span>
          </div>
          <div className="flex justify-between text-textMain font-bold pt-1 border-t border-gray-800 text-sm">
            <span>Exchange Value Credit:</span>
            <span className={isDiamond ? 'text-cyan-400' : 'text-primary'}>₹{calculatedValue.toFixed(2)}</span>
          </div>
        </div>

        <button 
          type="submit" 
          className={`w-full font-bold py-2.5 rounded-lg flex items-center justify-center gap-2 transition-all shadow-lg ${isDiamond ? 'bg-cyan-500 hover:bg-cyan-400 text-black' : 'bg-primary hover:bg-primary-dark text-background'}`}
        >
          <Plus size={16} /> {editingOldItem ? 'Update Old Item' : 'Add to Exchange List'}
        </button>
      </form>
    </div>
  );
}
"""

paths_purchase = [
    r'C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\pages\purchase\PurchaseMetalForm.tsx',
    r'C:\Users\YASH SONI\Desktop\Saideep\jewellery-erp\frontend\src\pages\purchase\PurchaseMetalForm.tsx'
]
for p in paths_purchase:
    with open(p, 'w', encoding='utf-8') as f:
        f.write(purchase_metal_form_code)
    print(f"Updated {p}")

paths_exchange = [
    r'C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\pages\exchange\OldItemsForm.tsx',
    r'C:\Users\YASH SONI\Desktop\Saideep\jewellery-erp\frontend\src\pages\exchange\OldItemsForm.tsx'
]
for p in paths_exchange:
    with open(p, 'w', encoding='utf-8') as f:
        f.write(old_items_form_code)
    print(f"Updated {p}")
