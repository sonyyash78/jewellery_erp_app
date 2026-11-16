import { useState, useEffect } from 'react';
import { useExchangeStore } from '../../store/exchangeStore';
import { ScanLine, Plus } from 'lucide-react';
import { useBillingStore } from '../../store/billingStore';
import { axiosClient } from '../../api/axiosClient';
import toast from 'react-hot-toast';
import { getErrorMessage } from '../../utils/errorUtils';
import { useCompanyStore } from '../../store/companyStore';
import { validateWastage, formatWastageInputValue } from '../../utils/wastageValidation';

export default function NewItemScanner() {
  const { addNewItem, newItems, editingNewItem, updateNewItem, setEditingNewItem } = useExchangeStore();
  const { liveRates } = useBillingStore();
  
  const handlePuritySelect = (touchVal: number, rateVal: number) => {
    setTouch(touchVal);
    if (rateVal > 0) setRateApplied(rateVal);
  };
  
  const [tab, setTab] = useState<'scan' | 'manual'>('scan');
  
  // Scan state
  const [manualCode, setManualCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [goldRate, setGoldRate] = useState(72500);
  const [silverRate, setSilverRate] = useState(90000);

  // Manual state
  const [metal, setMetal] = useState<'Gold' | 'Silver' | 'Diamond'>('Gold');
  const [itemName, setItemName] = useState('');
  const [touch, setTouch] = useState(91.6);
  const [grossWeight, setGrossWeight] = useState(0);
  const [stoneWeight, setStoneWeight] = useState(0);
  const [wastage, setWastage] = useState<number | ''>('');
  const [rateApplied, setRateApplied] = useState(72500);
  const [makingChargeType, setMakingChargeType] = useState('per_gm');
  const [makingChargeValue, setMakingChargeValue] = useState(0);
  const [hallmark, setHallmark] = useState(0);
  const [otherCharges, setOtherCharges] = useState(0);
  const [discount, setDiscount] = useState(0);

  // Diamond specific state
  const [diamondType, setDiamondType] = useState<'NATURAL' | 'SYNTHETIC'>('NATURAL');
  const [shape, setShape] = useState('Round');
  const [pieces, setPieces] = useState(1);
  const [colour, setColour] = useState('G-H');
  const [clarity, setClarity] = useState('VS1-VS2');
  const [certificateNo, setCertificateNo] = useState('');

  useEffect(() => {
    if (editingNewItem) {
      setTab('manual');
      const m = (editingNewItem.metal as 'Gold' | 'Silver' | 'Diamond') || 'Gold';
      setMetal(m);
      setItemName(editingNewItem.itemName || '');
      setGrossWeight(editingNewItem.grossWeight || 0);
      setStoneWeight(editingNewItem.stoneWeight || 0);
      setTouch(editingNewItem.touchPurity || (m === 'Gold' ? 91.6 : m === 'Silver' ? 99.9 : 100));
      setWastage(editingNewItem.wastage ?? '');
      setRateApplied(editingNewItem.rateApplied || (m === 'Gold' ? (liveRates.gold22k || 72500) : m === 'Silver' ? (liveRates.silver || 90000) : 25000));
      setMakingChargeType(editingNewItem.makingChargeType || 'per_gm');
      setMakingChargeValue(editingNewItem.makingChargeRate || 0);
      setHallmark(editingNewItem.hallmark || 0);
      setOtherCharges(editingNewItem.otherCharges || 0);
      setDiscount(editingNewItem.discount || 0);

      if (editingNewItem.diamondDetails) {
        setDiamondType((editingNewItem.diamondDetails.diamondType as any) || 'NATURAL');
        setShape(editingNewItem.diamondDetails.shape || 'Round');
        setPieces(editingNewItem.diamondDetails.pieces || 1);
        setColour(editingNewItem.diamondDetails.colour || 'G-H');
        setClarity(editingNewItem.diamondDetails.clarity || 'VS1-VS2');
        setCertificateNo(editingNewItem.diamondDetails.certificateNo || '');
      }
    }
  }, [editingNewItem]);

  useEffect(() => {
    if (!editingNewItem) {
      if (metal === 'Gold') {
        setRateApplied(liveRates.gold22k || 72500);
        setTouch(91.6);
      } else if (metal === 'Silver') {
        setRateApplied(liveRates.silver || 90000);
        setTouch(99.9);
      } else {
        setRateApplied(25000);
        setTouch(100);
      }
    }
  }, [metal, editingNewItem]);

  const isDiamond = metal === 'Diamond';

  const handleManualSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!manualCode.trim()) return;
    const code = manualCode.trim().toUpperCase();
    
    // Check if already in exchange
    if (newItems.some(item => item.itemCode === code)) {
      toast.error(`Item ${code} is already in the list`);
      return;
    }

    setLoading(true);
    try {
      const { activeCompany } = useCompanyStore.getState();
      const res = await axiosClient.get(`/stock/scan/${code}`, {
        params: { company_id: activeCompany?.id || 1 }
      });
      const item = res.data;

      if (item.status.toLowerCase() === 'sold') {
        toast.error(`Item ${code} is already sold!`);
        return;
      }

      const mLower = (item.metal || '').toLowerCase();
      const isGold = mLower === 'gold';
      const isDia = mLower === 'diamond';

      let metalRate = goldRate;
      let metalVal = 0;
      let fineWt = 0;
      let touchPurity = 100;
      let itemWastage = 0;

      if (isDia) {
        metalRate = Number(item.rate || 25000);
        const dWt = item.gross_weight || item.net_weight || 0;
        metalVal = dWt * metalRate;
        fineWt = 0;
        touchPurity = 100;
        itemWastage = 0;
      } else if (isGold) {
        metalRate = goldRate;
        touchPurity = item.tanch || (item.purity ? parseFloat(item.purity) : 91.6);
        itemWastage = item.wastage || 0;
        fineWt = item.net_weight * ((touchPurity + itemWastage) / 100);
        metalVal = fineWt * (metalRate / 10);
      } else {
        metalRate = silverRate;
        touchPurity = item.tanch || (item.purity ? parseFloat(item.purity) : 99.9);
        itemWastage = item.wastage || 0;
        fineWt = item.net_weight * ((touchPurity + itemWastage) / 100);
        metalVal = fineWt * (metalRate / 1000);
      }

      const makingAmount = item.making_type === 'flat' 
        ? item.making_charge 
        : (item.making_charge * item.net_weight);
      
      const itemHallmark = item.hallmark || 0;
      const itemOtherCharges = item.other_charges || 0;
      const itemDiscount = 0;
      
      const calculatedFinal = metalVal + makingAmount + itemHallmark + itemOtherCharges - itemDiscount;

      addNewItem({
        id: Math.random().toString(36).substring(7),
        stockItemId: item.id,
        itemCode: item.item_code,
        itemName: item.item_name,
        metal: isDia ? 'Diamond' : isGold ? 'Gold' : 'Silver',
        grossWeight: item.gross_weight || item.net_weight,
        stoneWeight: item.stone_weight || 0,
        netWeight: item.net_weight,
        touchPurity,
        wastage: itemWastage,
        fineWeight: fineWt,
        rateApplied: metalRate,
        makingChargeType: item.making_type || 'flat',
        makingChargeRate: item.making_charge || 0,
        makingCharges: makingAmount,
        hallmark: itemHallmark,
        otherCharges: itemOtherCharges,
        discount: itemDiscount,
        finalPrice: calculatedFinal,
        diamondDetails: isDia ? {
          diamondType: (item.diamond_type as any) || 'NATURAL',
          shape: item.shape || 'Round',
          caratWeight: (item.net_weight || 0) * 5,
          weightGm: item.net_weight || 0,
          pieces: item.pieces || 1,
          ratePerGm: metalRate,
          ratePerCarat: metalRate / 5,
          colour: item.colour || 'G-H',
          clarity: item.clarity || 'VS1-VS2',
          certificateNo: item.certificate_no || ''
        } : undefined
      });

      toast.success(`Added: ${item.item_name}`);
      setManualCode('');

    } catch (e: any) {
      if (e.response?.status === 400 || e.response?.status === 422) {
        toast.error(getErrorMessage(e, 'Invalid item data'));
      } else if (e.response?.status === 404) {
        toast.error(`Item ${code} not found`);
      } else {
        toast.error(getErrorMessage(e, 'Failed to fetch item'));
      }
    } finally {
      setLoading(false);
    }
  };

  const netWeight = isDiamond ? grossWeight : Math.max(0, grossWeight - stoneWeight);
  const fineWeight = isDiamond ? 0 : netWeight * (((touch || 0) + (Number(wastage) || 0)) / 100);
  const metalValue = isDiamond
    ? (netWeight * rateApplied)
    : fineWeight * (metal === 'Gold' ? (rateApplied / 10) : (rateApplied / 1000));
  
  let making = 0;
  if (makingChargeType === 'percent') making = metalValue * (makingChargeValue / 100);
  else if (makingChargeType === 'per_gm') making = netWeight * makingChargeValue;
  else making = makingChargeValue;

  const finalPrice = Math.max(0, metalValue + making + hallmark + otherCharges - discount);

  const handleAddManualItem = (e: React.FormEvent) => {
    e.preventDefault();
    if (grossWeight <= 0) return toast.error(isDiamond ? 'Please enter a valid diamond weight' : 'Please enter a valid gross weight');
    if (!isDiamond) {
      const wastageErr = validateWastage(touch, wastage);
      if (wastageErr) {
        toast.error(wastageErr);
        return;
      }
    }

    const finalItemName = itemName.trim() || (isDiamond ? 'Diamond Jewellery' : `${metal} Jewellery`);
    const itemData = {
      id: editingNewItem ? editingNewItem.id : Math.random().toString(36).substring(7),
      stockItemId: editingNewItem ? editingNewItem.stockItemId : null,
      itemCode: editingNewItem ? editingNewItem.itemCode : 'MANUAL',
      itemName: finalItemName,
      metal,
      grossWeight,
      stoneWeight: isDiamond ? 0 : stoneWeight,
      netWeight,
      touchPurity: isDiamond ? 100 : touch,
      wastage: isDiamond ? 0 : Number(wastage),
      fineWeight,
      rateApplied,
      makingChargeType,
      makingChargeRate: makingChargeValue,
      makingCharges: making,
      hallmark,
      otherCharges,
      discount,
      finalPrice,
      diamondDetails: isDiamond ? {
        diamondType,
        shape,
        caratWeight: netWeight * 5,
        weightGm: netWeight,
        pieces,
        ratePerGm: rateApplied,
        ratePerCarat: rateApplied / 5,
        colour,
        clarity,
        certificateNo
      } : undefined
    };

    if (editingNewItem) {
      updateNewItem(editingNewItem.id, itemData);
      toast.success("New item updated");
    } else {
      addNewItem(itemData);
      toast.success(isDiamond ? "Added new Diamond item" : "Added new item");
    }

    setItemName('');
    setGrossWeight(0);
    setStoneWeight(0);
    setWastage('');
    setMakingChargeValue(0);
    setHallmark(0);
    setOtherCharges(0);
    setDiscount(0);
    setCertificateNo('');
    setEditingNewItem(null);
  };

  const handleCancelEdit = () => {
    setEditingNewItem(null);
    setItemName('');
    setGrossWeight(0);
    setStoneWeight(0);
    setWastage('');
    setMakingChargeValue(0);
    setHallmark(0);
    setOtherCharges(0);
    setDiscount(0);
    setCertificateNo('');
  };

  const InputLabel = ({ label }: { label: string }) => (
    <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1">{label}</label>
  );

  return (
    <div className="bg-[#111115] border border-gray-800 rounded-2xl p-3 sm:p-4 flex flex-col gap-3 sm:gap-4 shadow-[0_4px_20px_rgba(0,0,0,0.5)] h-auto lg:h-full min-h-[380px] overflow-hidden">
      
      <div className="flex justify-between items-center border-b border-gray-800 pb-2">
        <h2 className="text-primary font-bold uppercase tracking-wider text-sm flex items-center gap-2">
          <span>Purchase New Item</span>
          {isDiamond && <span className="text-[10px] bg-cyan-950/70 border border-cyan-700/60 text-cyan-300 font-bold px-2 py-0.5 rounded-full">DIAMOND MODE</span>}
        </h2>
        <div className="flex bg-background border border-gray-700 rounded overflow-hidden">
          <button 
            type="button"
            onClick={() => setTab('scan')}
            className={`px-3 py-1 text-xs font-bold transition-colors ${tab === 'scan' ? 'bg-primary text-black' : 'text-gray-400 hover:text-white'}`}
          >
            Scan
          </button>
          <button 
            type="button"
            onClick={() => setTab('manual')}
            className={`px-3 py-1 text-xs font-bold transition-colors ${tab === 'manual' ? 'bg-primary text-black' : 'text-gray-400 hover:text-white'}`}
          >
            Manual
          </button>
        </div>
      </div>

      {tab === 'scan' ? (
        <div className="flex-1 flex flex-col gap-4">
            <div className="grid grid-cols-2 gap-3 mb-2">
              <div><InputLabel label="Gold Rate (₹/10g)" /><input type="number" value={goldRate} onChange={e=>setGoldRate(Number(e.target.value))} className="w-full bg-[#1A1A20] border border-gray-800 rounded px-3 py-2 text-sm text-yellow-500 font-mono outline-none focus:border-primary" /></div>
              <div><InputLabel label="Silver Rate (₹/kg)" /><input type="number" value={silverRate} onChange={e=>setSilverRate(Number(e.target.value))} className="w-full bg-[#1A1A20] border border-gray-800 rounded px-3 py-2 text-sm text-gray-300 font-mono outline-none focus:border-primary" /></div>
            </div>

            <form onSubmit={handleManualSubmit} className="flex flex-col gap-2">
              <InputLabel label="Scan Barcode / Enter Item Code (Gold / Silver / Diamond)" />
              <div className="flex gap-2">
                <div className="relative flex-1">
                  <ScanLine className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
                  <input 
                    autoFocus
                    value={manualCode}
                    onChange={(e) => setManualCode(e.target.value)}
                    placeholder="e.g. RING001, DIA-102"
                    className="w-full bg-[#1A1A20] border border-gray-700 rounded-lg pl-10 pr-4 py-3 text-white focus:border-primary outline-none transition-all placeholder-gray-600 uppercase font-mono"
                  />
                </div>
                <button 
                  type="submit" 
                  disabled={loading || !manualCode.trim()}
                  className="bg-primary hover:bg-primary-dark disabled:opacity-50 text-black font-bold px-6 rounded-lg transition-colors shadow-[0_0_10px_rgba(212,175,55,0.2)]"
                >
                  {loading ? '...' : 'Add'}
                </button>
              </div>
            </form>
        </div>
      ) : (
        <>
          {/* Gold / Silver / Diamond selector — pinned above scroll, always visible */}
          <div className="flex rounded-lg overflow-hidden border border-gray-700 bg-background shrink-0">
            <button type="button" onClick={() => setMetal('Gold')}
              className={`flex-1 py-2 text-xs font-bold uppercase tracking-wide transition-all ${metal === 'Gold' ? 'bg-yellow-500/20 text-yellow-400 border-b-2 border-yellow-500' : 'text-gray-500 hover:text-gray-200 hover:bg-gray-800/40'}`}>
              🥇 Gold
            </button>
            <button type="button" onClick={() => setMetal('Silver')}
              className={`flex-1 py-2 text-xs font-bold uppercase tracking-wide transition-all ${metal === 'Silver' ? 'bg-gray-600/30 text-gray-100 border-b-2 border-gray-400' : 'text-gray-500 hover:text-gray-200 hover:bg-gray-800/40'}`}>
              🥈 Silver
            </button>
            <button type="button" onClick={() => setMetal('Diamond')}
              className={`flex-1 py-2 text-xs font-bold uppercase tracking-wide transition-all ${metal === 'Diamond' ? 'bg-cyan-500/20 text-cyan-400 border-b-2 border-cyan-400' : 'text-gray-500 hover:text-gray-200 hover:bg-gray-800/40'}`}>
              💎 Diamond
            </button>
          </div>

          <form onSubmit={handleAddManualItem} className="flex-1 overflow-y-auto pr-2 space-y-3 custom-scrollbar pb-4 flex flex-col min-h-0">

          {/* Item Name */}
          <div>
            <input 
              value={itemName} 
              onChange={e => setItemName(e.target.value)} 
              placeholder={isDiamond ? "Diamond Item Name (e.g. Solitaire Studs, Diamond Ring)" : "Item Name / Description (Optional)"}
              className={`w-full bg-[#1A1A20] border rounded px-3 py-2 text-sm text-white outline-none transition-all placeholder-gray-600 ${isDiamond ? 'border-cyan-800 focus:border-cyan-400' : 'border-gray-800 focus:border-primary'}`} 
            />
          </div>

          {isDiamond ? (
            /* 💎 DIAMOND CALCULATOR FORM 💎 */
            <div className="bg-[#141419] border border-cyan-900/50 rounded-xl p-3 space-y-3">
              {/* Type & Shape */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <InputLabel label="Diamond Type" />
                  <select 
                    value={diamondType} 
                    onChange={e => setDiamondType(e.target.value as any)}
                    className="w-full bg-[#1A1A20] border border-gray-800 rounded px-2 py-1.5 text-xs text-white focus:border-cyan-500 outline-none"
                  >
                    <option value="NATURAL">Natural Diamond</option>
                    <option value="SYNTHETIC">Synthetic / Lab Grown</option>
                  </select>
                </div>
                <div>
                  <InputLabel label="Shape" />
                  <select 
                    value={shape} 
                    onChange={e => setShape(e.target.value)}
                    className="w-full bg-[#1A1A20] border border-gray-800 rounded px-2 py-1.5 text-xs text-white focus:border-cyan-500 outline-none"
                  >
                    {['Round', 'Princess', 'Cushion', 'Oval', 'Emerald', 'Pear', 'Radiant', 'Marquise', 'Heart'].map(s => (
                      <option key={s} value={s}>{s}</option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Weight in Grams, Carats display, Pieces, Rate/gm */}
              <div className="grid grid-cols-3 gap-2">
                <div>
                  <InputLabel label="Weight (gm)" />
                  <input 
                    type="number" 
                    step="0.001" 
                    value={grossWeight === 0 ? '' : grossWeight} 
                    onChange={e => setGrossWeight(Number(e.target.value))} 
                    placeholder="0.000 gm" 
                    className="w-full bg-[#1A1A20] border border-cyan-800/80 rounded px-2 py-1 text-sm text-cyan-300 font-bold focus:border-cyan-400 outline-none font-mono" 
                  />
                  <span className="text-[10px] text-cyan-500/80 font-mono mt-0.5 block">
                    = {(grossWeight * 5).toFixed(3)} cts
                  </span>
                </div>
                <div>
                  <InputLabel label="Pieces" />
                  <input 
                    type="number" 
                    value={pieces || 1} 
                    onChange={e => setPieces(e.target.value === '' ? 1 : Number(e.target.value))} 
                    placeholder="1" 
                    className="w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm text-white focus:border-cyan-500 outline-none font-mono" 
                  />
                  <span className="text-[10px] text-gray-500 block mt-0.5">stones</span>
                </div>
                <div>
                  <InputLabel label="Rate (₹/gm)" />
                  <input 
                    type="number" 
                    value={rateApplied === 0 ? '' : rateApplied} 
                    onChange={e => setRateApplied(Number(e.target.value))} 
                    placeholder="25000" 
                    className="w-full bg-[#1A1A20] border border-cyan-800/80 rounded px-2 py-1 text-sm text-cyan-300 font-bold focus:border-cyan-400 outline-none font-mono" 
                  />
                  <span className="text-[10px] text-cyan-500/80 font-mono mt-0.5 block">
                    ≈ ₹{(rateApplied / 5).toFixed(0)}/ct
                  </span>
                </div>
              </div>

              {/* Colour, Clarity, Certificate */}
              <div className="grid grid-cols-3 gap-2">
                <div>
                  <InputLabel label="Colour" />
                  <select 
                    value={colour} 
                    onChange={e => setColour(e.target.value)}
                    className="w-full bg-[#1A1A20] border border-gray-800 rounded px-2 py-1 text-xs text-white focus:border-cyan-500 outline-none"
                  >
                    {['D', 'E', 'F', 'G-H', 'I-J', 'K-M'].map(c => <option key={c} value={c}>{c}</option>)}
                  </select>
                </div>
                <div>
                  <InputLabel label="Clarity" />
                  <select 
                    value={clarity} 
                    onChange={e => setClarity(e.target.value)}
                    className="w-full bg-[#1A1A20] border border-gray-800 rounded px-2 py-1 text-xs text-white focus:border-cyan-500 outline-none"
                  >
                    {['FL', 'IF', 'VVS1', 'VVS2', 'VS1-VS2', 'SI1', 'SI2', 'I1'].map(cl => <option key={cl} value={cl}>{cl}</option>)}
                  </select>
                </div>
                <div>
                  <InputLabel label="Certificate No." />
                  <input 
                    value={certificateNo} 
                    onChange={e => setCertificateNo(e.target.value)}
                    placeholder="IGI / GIA..." 
                    className="w-full bg-[#1A1A20] border border-gray-800 rounded px-2 py-1 text-xs text-white focus:border-cyan-500 outline-none font-mono" 
                  />
                </div>
              </div>

              {/* Base Diamond Value Preview */}
              <div className="flex justify-between items-center bg-cyan-950/30 border border-cyan-900/40 rounded-lg px-2.5 py-1.5 text-xs font-mono">
                <span className="text-cyan-400 font-medium">Base Diamond Value:</span>
                <span className="text-cyan-300 font-bold">₹{metalValue.toFixed(2)}</span>
              </div>
            </div>
          ) : (
            <>
              {/* Purity Toggles for Gold/Silver */}
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

              {/* Weights for Gold / Silver */}
              <div className="grid grid-cols-3 gap-3">
                <div><InputLabel label="Gross Wt(g)" /><input type="number" step="0.001" value={grossWeight === 0 ? '' : grossWeight} onChange={e=>setGrossWeight(Number(e.target.value))} className="w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm text-white focus:border-primary outline-none font-mono" /></div>
                <div><InputLabel label="Stone Wt(g)" /><input type="number" step="0.001" value={stoneWeight === 0 ? '' : stoneWeight} onChange={e=>setStoneWeight(Number(e.target.value))} className="w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm text-white focus:border-primary outline-none font-mono" /></div>
                <div><InputLabel label="Net Wt(g)" /><input disabled value={netWeight.toFixed(3)} className="w-full bg-gray-900 border border-gray-800 rounded px-2 py-1 text-sm text-gray-500 outline-none font-mono cursor-not-allowed" /></div>
              </div>

              {/* Calculations for Gold / Silver */}
              <div className="grid grid-cols-3 gap-3">
                <div><InputLabel label="Touch / Tanch" /><input type="number" step="0.1" value={touch === 0 ? '' : touch} onChange={e=>setTouch(Number(e.target.value))} className={`w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm focus:border-primary outline-none font-mono ${metal === 'Gold' ? 'text-primary' : 'text-gray-300'}`} /></div>
                <div><InputLabel label="Wastage (gm) *" /><input type="number" step="0.1" min="0" value={formatWastageInputValue(wastage)} onChange={e=>setWastage(e.target.value === '' ? '' : Number(e.target.value))} placeholder="Required (0+)" className={`w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm focus:border-primary outline-none font-mono ${metal === 'Gold' ? 'text-primary' : 'text-gray-300'}`} /></div>
                <div><InputLabel label="Fine Wt(g)" /><input disabled value={fineWeight.toFixed(3)} className={`w-full bg-gray-900 border border-gray-800 rounded px-2 py-1 text-sm outline-none font-mono cursor-not-allowed ${metal === 'Gold' ? 'text-primary/70' : 'text-gray-300/70'}`} /></div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div><InputLabel label={`Live Rate (₹/${metal === 'Gold' ? '10g' : 'kg'})`} /><input type="number" value={rateApplied === 0 ? '' : rateApplied} onChange={e=>setRateApplied(Number(e.target.value))} className="w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm text-white focus:border-primary outline-none font-mono" /></div>
                <div><InputLabel label="Metal Value" /><input disabled value={`₹${metalValue.toFixed(2)}`} className="w-full bg-gray-900 border border-gray-800 rounded px-2 py-1 text-sm text-gray-500 outline-none font-mono cursor-not-allowed" /></div>
              </div>
            </>
          )}

          {/* Charges (Making / Setting, Hallmark, Other) */}
          <div className="pt-1">
            <h4 className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-2 border-b border-gray-800 pb-1">
              {isDiamond ? 'Diamond Setting & Charges' : 'Making & Charges'}
            </h4>
            
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] text-gray-500 uppercase tracking-wider font-bold">
                {isDiamond ? 'Setting Charge Type' : 'Making Charge Type'}
              </span>
              <div className="flex bg-[#1A1A20] rounded border border-gray-800">
                {[
                  { label: '%', val: 'percent' },
                  { label: isDiamond ? '₹/g' : '₹/g', val: 'per_gm' },
                  { label: '₹ Flat', val: 'flat' }
                ].map(t => (
                  <button 
                    type="button"
                    key={t.val}
                    onClick={() => setMakingChargeType(t.val)}
                    className={`px-3 py-0.5 text-xs rounded-sm transition-colors ${makingChargeType === t.val ? (isDiamond ? 'bg-cyan-500 text-black font-bold' : 'bg-primary text-black font-bold') : 'text-gray-400'}`}
                  >
                    {t.label}
                  </button>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3 mb-3">
              <div><InputLabel label={isDiamond ? "Setting Value (+)" : "Making Value (+)"} /><input type="number" value={makingChargeValue === 0 ? '' : makingChargeValue} onChange={e=>setMakingChargeValue(Number(e.target.value))} className="w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm text-white focus:border-primary outline-none font-mono" /></div>
              <div><InputLabel label={isDiamond ? "Total Setting" : "Total Making"} /><input disabled value={`₹${making.toFixed(2)}`} className="w-full bg-gray-900 border border-gray-800 rounded px-2 py-1 text-sm text-gray-500 outline-none font-mono cursor-not-allowed" /></div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div><InputLabel label={isDiamond ? "Cert/Hallmark (+)" : "Hallmark (+)"} /><input type="number" value={hallmark === 0 ? '' : hallmark} onChange={e=>setHallmark(Number(e.target.value))} className="w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm text-white focus:border-primary outline-none font-mono" /></div>
              <div><InputLabel label="Other Charges (+)" /><input type="number" value={otherCharges === 0 ? '' : otherCharges} onChange={e=>setOtherCharges(Number(e.target.value))} className="w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm text-white focus:border-primary outline-none font-mono" /></div>
            </div>
          </div>

          {/* Deductions */}
          <div className="pt-1">
            <div className="grid grid-cols-2 gap-3">
              <div><InputLabel label="Discount (-)" /><input type="number" value={discount === 0 ? '' : discount} onChange={e=>setDiscount(Number(e.target.value))} className="w-full bg-red-950/20 border border-red-900/50 rounded px-2 py-1 text-sm text-red-400 focus:border-red-500 outline-none font-mono" /></div>
            </div>
          </div>

          <div className="flex-1"></div>

          <div className="mt-2 pt-3 border-t border-gray-800/50">
            <div className="flex justify-between items-center mb-3 px-1">
                <span className="text-gray-400 text-sm font-medium">Total Item Price</span>
                <span className={`font-bold text-lg font-mono ${isDiamond ? 'text-cyan-400' : 'text-red-400'}`}>₹{finalPrice.toFixed(2)}</span>
            </div>
            <div className="flex gap-2">
              {editingNewItem && (
                <button type="button" onClick={handleCancelEdit} className="w-1/3 bg-gray-800 hover:bg-gray-700 text-white font-bold py-3 rounded-lg flex items-center justify-center transition-all">
                  Cancel
                </button>
              )}
              <button 
                type="submit" 
                className={`flex-1 font-bold py-3 rounded-lg flex items-center justify-center gap-2 transition-all ${isDiamond ? 'bg-cyan-500 hover:bg-cyan-400 text-black shadow-[0_0_15px_rgba(6,182,212,0.3)]' : 'bg-primary hover:bg-primary-dark text-black shadow-[0_0_15px_rgba(212,175,55,0.2)]'}`}
              >
                <Plus size={18} /> {editingNewItem ? 'UPDATE ITEM' : isDiamond ? 'ADD DIAMOND TO BILL' : 'ADD TO BILL'}
              </button>
            </div>
          </div>
        </form>
        </>
      )}
    </div>
  );
}
