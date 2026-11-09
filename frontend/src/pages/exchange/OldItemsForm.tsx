import { handleEnterKeyNavigation } from '../../utils/keyboardNavigation';
import { useState, useEffect } from 'react';
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

  useEffect(() => {
    const handleExchangeHotkeys = (e: KeyboardEvent) => {
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
    window.addEventListener('keydown', handleExchangeHotkeys);
    return () => window.removeEventListener('keydown', handleExchangeHotkeys);
  }, []);
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
    // Validated touch and wastage
    
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

      <form 
        data-enter-container="true"
        onKeyDown={(e) => handleEnterKeyNavigation(e, '[data-enter-container]', () => {
          handleAdd(e as any);
        })}
        onSubmit={handleAdd} 
        className="space-y-4">
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
                <label className="block text-xs font-medium text-textMuted mb-1">Touch / Tanch</label>
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
                <label className="block text-xs font-medium text-textMuted mb-1">Wastage (gm)</label>
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
              <span>Fine Weight:</span>
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
