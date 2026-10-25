import { useState, useEffect } from 'react';
import { useExchangeStore } from '../../store/exchangeStore';
import { Plus } from 'lucide-react';
import { useBillingStore } from '../../store/billingStore';
import toast from 'react-hot-toast';

export default function OldItemsForm() {
  const { addOldItem, editingOldItem, updateOldItem, setEditingOldItem } = useExchangeStore();
  const { liveRates } = useBillingStore();
  
  const handlePuritySelect = (touchVal: number, rateVal: number) => {
    setTouch(touchVal);
    if (rateVal > 0) setRateApplied(rateVal);
  };
  const [metal, setMetal] = useState<'Gold'|'Silver'>('Gold');
  
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
  const [discount, setDiscount] = useState(0); // For buying old gold, discount might act as deduction
  const [otherCharges, setOtherCharges] = useState(0);

  useEffect(() => {
    if (!editingOldItem) {
      if (metal === 'Gold') {
        setRateApplied(liveRates.gold22k || 72500);
        setTouch(91.6);
      } else {
        setRateApplied(liveRates.silver || 90000);
        setTouch(99.9);
      }
    }
  }, [metal]);

  useEffect(() => {
    if (editingOldItem) {
      setMetal(editingOldItem.metal as 'Gold'|'Silver');
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

  const netWeight = grossWeight - stoneWeight;
  const fineWeight = netWeight * ((touch + wastage) / 100);
  const metalValue = fineWeight * (metal === 'Gold' ? (rateApplied / 10) : (rateApplied / 1000));
  
  const calculatedValue = metalValue - labourCharge - testingMeltingCharge - hallmarkCharge - discount + otherCharges;

  const handleAdd = (e: React.FormEvent) => {
    e.preventDefault();
    if (grossWeight <= 0) return toast.error('Please enter a valid gross weight');
    if (netWeight <= 0) return toast.error('Net weight must be > 0');
    if ((touch || 0) + (wastage || 0) > 100) return toast.error('Touch % + Wastage % cannot be greater than 100%');
    
    const finalItemName = itemName.trim() || `${purity} Old ${metal}`;
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
    
    // reset form partially
    setItemName('');
    setGrossWeight(0);
    setStoneWeight(0);
    setWastage(0);
    setLabourCharge(0);
    setTestingMeltingCharge(0);
    setHallmarkCharge(0);
    setDiscount(0);
    setOtherCharges(0);
    setEditingOldItem(null);
  };

  const handleCancelEdit = () => {
    setEditingOldItem(null);
    setItemName('');
    setGrossWeight(0);
    setStoneWeight(0);
  };

  const InputLabel = ({ label }: { label: string }) => (
    <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1">{label}</label>
  );

  
  return (
    <div className="bg-[#111115] border border-gray-800 rounded-2xl p-3 sm:p-4 shadow-[0_4px_20px_rgba(0,0,0,0.5)] flex flex-col h-auto lg:h-full min-h-[380px] overflow-hidden">
      <div className="flex justify-between items-center border-b border-gray-800 pb-2 mb-3 shrink-0">
        <h3 className={`font-bold tracking-widest uppercase text-sm ${metal === 'Gold' ? 'text-primary' : 'text-gray-300'}`}>Old Metal Evaluation</h3>
      </div>
      
      {/* Gold / Silver Toggle — pinned */}
      <div className="flex rounded-lg overflow-hidden border border-gray-700 bg-background shrink-0 mb-3">
        <button type="button" onClick={() => setMetal('Gold')}
          className={`flex-1 py-2 text-xs font-bold uppercase tracking-wide transition-all ${metal === 'Gold' ? 'bg-yellow-500/20 text-yellow-400 border-b-2 border-yellow-500' : 'text-gray-500 hover:text-gray-200 hover:bg-gray-800/40'}`}>
          🥇 Gold
        </button>
        <button type="button" onClick={() => setMetal('Silver')}
          className={`flex-1 py-2 text-xs font-bold uppercase tracking-wide transition-all ${metal === 'Silver' ? 'bg-gray-600/30 text-gray-100 border-b-2 border-gray-400' : 'text-gray-500 hover:text-gray-200 hover:bg-gray-800/40'}`}>
          🥈 Silver
        </button>
      </div>
      
      <form onSubmit={handleAdd} className="flex-1 overflow-y-auto pr-2 space-y-3 custom-scrollbar pb-4 flex flex-col min-h-0">
        {/* Item Name */}
        <div>
          <input 
            value={itemName} 
            onChange={e => setItemName(e.target.value)} 
            placeholder="Item Name / Description (Optional)"
            className="w-full bg-[#1A1A20] border border-gray-800 rounded px-3 py-2 text-sm text-white focus:border-primary outline-none transition-all placeholder-gray-600" 
          />
        </div>

        {/* Purity Toggles */}
        <div>
          <label className="block text-xs font-medium text-gray-400 mb-1.5">{metal} Purity</label>
          <div className="flex flex-wrap gap-2">
            {metal === 'Gold' ? (
              [
                { label: '14K', touch: 58.3, rate: liveRates.gold14k },
                { label: '18K', touch: 75.0, rate: liveRates.gold18k },
                { label: '20K', touch: 83.3, rate: liveRates.gold20k },
                { label: '22K', touch: 91.6, rate: liveRates.gold22k },
                { label: '24K', touch: 99.9, rate: liveRates.gold24k },
              ].map(p => (
                <button 
                  type="button"
                  key={p.label}
                  onClick={() => handlePuritySelect(p.touch, p.rate)}
                  className={`px-3 py-1 text-[11px] font-medium rounded border transition-colors ${touch === p.touch ? 'bg-primary/20 border-primary text-primary' : 'bg-[#1A1A20] border-gray-700 text-gray-400 hover:border-gray-500 hover:text-gray-200'}`}
                >
                  {p.label}
                </button>
              ))
            ) : (
              [
                { label: 'Fine (99.9)', touch: 99.9, rate: 0 },
                { label: 'Sterling (92.5)', touch: 92.5, rate: 0 },
                { label: 'Custom (65.0)', touch: 65.0, rate: 0 },
              ].map(p => (
                <button 
                  type="button"
                  key={p.label}
                  onClick={() => handlePuritySelect(p.touch, 0)}
                  className={`px-3 py-1 text-[11px] font-medium rounded border transition-colors ${touch === p.touch ? 'bg-gray-700/50 border-gray-300 text-gray-200' : 'bg-[#1A1A20] border-gray-700 text-gray-400 hover:border-gray-500 hover:text-gray-200'}`}
                >
                  {p.label}
                </button>
              ))
            )}
          </div>
        </div>

        {/* Weights */}
        <div className="grid grid-cols-3 gap-3">
          <div><InputLabel label="Gross Wt(g)" /><input type="number" step="0.001" value={grossWeight === 0 ? '' : grossWeight} onChange={e=>setGrossWeight(Number(e.target.value))} className="w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm text-white focus:border-primary outline-none font-mono" /></div>
          <div><InputLabel label="Stone Wt(g)" /><input type="number" step="0.001" value={stoneWeight === 0 ? '' : stoneWeight} onChange={e=>setStoneWeight(Number(e.target.value))} className="w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm text-white focus:border-primary outline-none font-mono" /></div>
          <div><InputLabel label="Net Wt(g)" /><input disabled value={netWeight.toFixed(3)} className="w-full bg-gray-900 border border-gray-800 rounded px-2 py-1 text-sm text-gray-500 outline-none font-mono cursor-not-allowed" /></div>
        </div>

        {/* Calculations */}
        <div className="grid grid-cols-3 gap-3">
          <div><InputLabel label="Touch %" /><input type="number" step="0.1" value={touch === 0 ? '' : touch} onChange={e=>setTouch(Number(e.target.value))} className={`w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm focus:border-primary outline-none font-mono ${metal === 'Gold' ? 'text-primary' : 'text-gray-300'}`} /></div>
          <div><InputLabel label="Wastage %" /><input type="number" step="0.1" value={wastage === 0 ? '' : wastage} onChange={e=>setWastage(Number(e.target.value))} className={`w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm focus:border-primary outline-none font-mono ${metal === 'Gold' ? 'text-primary' : 'text-gray-300'}`} /></div>
          <div><InputLabel label="Fine Wt(g)" /><input disabled value={fineWeight.toFixed(3)} className={`w-full bg-gray-900 border border-gray-800 rounded px-2 py-1 text-sm outline-none font-mono cursor-not-allowed ${metal === 'Gold' ? 'text-primary/70' : 'text-gray-300/70'}`} /></div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div><InputLabel label={`Rate (₹/${metal === 'Gold' ? '10g' : 'kg'})`} /><input type="number" value={rateApplied === 0 ? '' : rateApplied} onChange={e=>setRateApplied(Number(e.target.value))} className="w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm text-white focus:border-primary outline-none font-mono" /></div>
          <div><InputLabel label="Metal Value" /><input disabled value={`₹${metalValue.toFixed(2)}`} className="w-full bg-gray-900 border border-gray-800 rounded px-2 py-1 text-sm text-gray-500 outline-none font-mono cursor-not-allowed" /></div>
        </div>

        {/* Deductions */}
        <div className="pt-1">
          <h4 className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-2 border-b border-gray-800 pb-1">Deductions</h4>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 sm:gap-3 mb-3">
            <div><InputLabel label="Labour (-)" /><input type="number" value={labourCharge === 0 ? '' : labourCharge} onChange={e=>setLabourCharge(Number(e.target.value))} className="w-full bg-red-950/20 border border-red-900/50 rounded px-2 py-1 text-sm text-red-400 focus:border-red-500 outline-none font-mono" /></div>
            <div><InputLabel label="Test/Melt (-)" /><input type="number" value={testingMeltingCharge === 0 ? '' : testingMeltingCharge} onChange={e=>setTestingMeltingCharge(Number(e.target.value))} className="w-full bg-red-950/20 border border-red-900/50 rounded px-2 py-1 text-sm text-red-400 focus:border-red-500 outline-none font-mono" /></div>
            <div><InputLabel label="Hallmark (-)" /><input type="number" value={hallmarkCharge === 0 ? '' : hallmarkCharge} onChange={e=>setHallmarkCharge(Number(e.target.value))} className="w-full bg-red-950/20 border border-red-900/50 rounded px-2 py-1 text-sm text-red-400 focus:border-red-500 outline-none font-mono" /></div>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 sm:gap-3">
            <div><InputLabel label="Discount (-)" /><input type="number" value={discount === 0 ? '' : discount} onChange={e=>setDiscount(Number(e.target.value))} className="w-full bg-red-950/20 border border-red-900/50 rounded px-2 py-1 text-sm text-red-400 focus:border-red-500 outline-none font-mono" /></div>
            <div><InputLabel label="Other (+)" /><input type="number" value={otherCharges === 0 ? '' : otherCharges} onChange={e=>setOtherCharges(Number(e.target.value))} className="w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm text-white focus:border-primary outline-none font-mono" /></div>
          </div>
        </div>

        <div className="flex-1"></div>

        <div className="mt-2 pt-3 border-t border-gray-800/50">
          <div className="flex justify-between items-center mb-3 px-1">
              <span className="text-gray-400 text-sm font-medium">Exchange Value</span>
              <span className="text-primary font-bold text-lg font-mono">₹{calculatedValue.toFixed(2)}</span>
          </div>
          <div className="flex gap-2">
              {editingOldItem && (
                  <button type="button" onClick={handleCancelEdit} className="w-1/3 bg-gray-800 hover:bg-gray-700 text-white font-bold py-3 rounded-lg flex items-center justify-center transition-all">
                    Cancel
                  </button>
              )}
              <button type="submit" className="flex-1 bg-primary hover:bg-primary-dark text-black font-bold py-3 rounded-lg flex items-center justify-center gap-2 shadow-[0_0_15px_rgba(212,175,55,0.2)] transition-all">
                <Plus size={18} /> {editingOldItem ? 'UPDATE ITEM' : 'ADD TO EXCHANGE'}
              </button>
          </div>
        </div>
      </form>
    </div>
  );

}
