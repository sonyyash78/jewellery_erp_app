import { useState, useEffect, useMemo } from 'react';
import { axiosClient } from '../../api/axiosClient';
import toast from 'react-hot-toast';
import { Check, X, Calculator, UserPlus } from 'lucide-react';
import { useBillingStore } from '../../store/billingStore';
import { getErrorMessage } from '../../utils/errorUtils';

interface PurchaseCheckoutModalProps {
  payload: any;
  grandTotal: number;
  onClose: () => void;
  onSuccess: (invoiceId: number) => void;
}

export default function PurchaseCheckoutModal({ payload, grandTotal, onClose, onSuccess }: PurchaseCheckoutModalProps) {
  const [loading, setLoading] = useState(false);
  const [sellers, setSellers] = useState<any[]>([]);
  const [selectedSeller, setSelectedSeller] = useState<number | ''>('');
  const [mode, setMode] = useState<'checkout' | 'new_supplier'>('checkout');
  const [newSeller, setNewSeller] = useState({ name: '', mobile: '', city: '' });

  const [cashPaid, setCashPaid] = useState<number>(0);
  const [goldGiven, setGoldGiven] = useState<number>(0);
  const [goldGivenTanch, setGoldGivenTanch] = useState<number>(100);
  const [silverGiven, setSilverGiven] = useState<number>(0);
  const [silverGivenTanch, setSilverGivenTanch] = useState<number>(100);

  // cash | metal_gold | metal_silver | metal_both
  const [cashBalanceAction, setCashBalanceAction] = useState<'cash' | 'metal_gold' | 'metal_silver' | 'metal_both'>('cash');

  const [paymentMethod, setPaymentMethod] = useState<'Cash' | 'UPI' | 'Cheque'>('Cash');
  const [upiId, setUpiId] = useState('');
  const [chequeNo, setChequeNo] = useState('');
  const [bankName, setBankName] = useState('');
  const [chequeDate, setChequeDate] = useState('');

  // STEP 1: Extract from payload
  const { totalGoldBilled, totalSilverBilled, goldRate, silverRate, hasGold, hasSilver } = useMemo(() => {
    let tg = 0, ts = 0, gr = 0, sr = 0;
    (payload.items || []).forEach((item: any) => {
      const fw = Number(item.fine_weight || item.pure_weight || (item.net_weight && item.touch_purity ? (item.net_weight * item.touch_purity / 100) : item.net_weight) || 0);
      if (item.metal_type === 'Gold') {
        tg += fw;
        if (!gr) gr = item.metal_rate || 0;
      } else if (item.metal_type === 'Silver') {
        ts += fw;
        if (!sr) sr = item.metal_rate || 0;
      }
    });
    if (gr > 0 && gr < 15000) gr = gr * 10;
    if (sr > 0 && sr < 1000) sr = sr * 1000;
    return {
      totalGoldBilled: tg,
      totalSilverBilled: ts,
      goldRate: gr,
      silverRate: sr,
      hasGold: tg > 0,
      hasSilver: ts > 0
    };
  }, [payload.items]);

  const isPureGold = hasGold && (goldRate === 0 || (payload.items || []).filter((i: any) => i.metal_type === 'Gold').every((i: any) => (i.metal_rate || 0) === 0));
  const isPureSilver = hasSilver && (silverRate === 0 || (payload.items || []).filter((i: any) => i.metal_type === 'Silver').every((i: any) => (i.metal_rate || 0) === 0));
  const isPureMetal = (hasGold ? isPureGold : true) && (hasSilver ? isPureSilver : true) && (hasGold || hasSilver);

  const { liveRates } = useBillingStore();
  let baseGoldRate = 0;
  if (!isPureGold) {
    baseGoldRate = goldRate || liveRates.gold22k || 72500;
    if (baseGoldRate > 0 && baseGoldRate < 15000) baseGoldRate = baseGoldRate * 10;
  }
  let baseSilverRate = 0;
  if (!isPureSilver) {
    baseSilverRate = silverRate || liveRates.silver || 90000;
    if (baseSilverRate > 0 && baseSilverRate < 1000) baseSilverRate = baseSilverRate * 1000;
  }

  const conversionGoldRate = baseGoldRate;
  const conversionSilverRate = baseSilverRate;
  const activeGoldRate = conversionGoldRate;
  const activeSilverRate = conversionSilverRate;

  useEffect(() => {
    if (isPureMetal) {
      if (hasGold && hasSilver) setCashBalanceAction('metal_both');
      else if (hasGold) setCashBalanceAction('metal_gold');
      else if (hasSilver) setCashBalanceAction('metal_silver');
    }
  }, [isPureMetal, hasGold, hasSilver]);

  // STEP 2: Non-metal charges / expenses & GST
  const totalLabourCharges = useMemo(() => {
    return (payload.items || []).reduce((acc: number, item: any) => acc + Number(item.labour_charge || 0), 0);
  }, [payload.items]);

  const totalOtherCharges = useMemo(() => {
    return (payload.items || []).reduce((acc: number, item: any) => {
      return acc + Number(item.hallmark_charge || 0) + Number(item.other_charges || 0) + Number(item.testing_melting_charge || 0);
    }, 0);
  }, [payload.items]);

  const totalDiscounts = useMemo(() => {
    return (payload.items || []).reduce((acc: number, item: any) => acc + Number(item.discount || 0), 0);
  }, [payload.items]);

  const totalGst = Number(payload.cgst || 0) + Number(payload.sgst || 0) + Number(payload.igst || 0);
  const nonMetalCharges = totalLabourCharges + totalOtherCharges + totalGst - totalDiscounts;

  // STEP 3: Counter metal given to supplier & Net metal left
  const fineGoldGiven = goldGiven * (goldGivenTanch / 100);
  const fineSilverGiven = silverGiven * (silverGivenTanch / 100);

  const goldValueReceived = fineGoldGiven * (activeGoldRate / 10);
  const silverValueReceived = fineSilverGiven * (activeSilverRate / 1000);
  const totalMetalValueReceived = goldValueReceived + silverValueReceived;

  const goldLeftGrams = totalGoldBilled - fineGoldGiven;
  const silverLeftGrams = totalSilverBilled - fineSilverGiven;

  const physicalGoldDue = Math.max(0, goldLeftGrams);
  const physicalSilverDue = Math.max(0, silverLeftGrams);

  const goldLeftRupees = physicalGoldDue * (activeGoldRate / 10);
  const silverLeftRupees = physicalSilverDue * (activeSilverRate / 1000);
  const totalMetalRupeesDue = goldLeftRupees + silverLeftRupees;
  const totalMonetaryBeforeCash = Math.max(0, totalMetalRupeesDue + nonMetalCharges);
  const cashBalanceDue = totalMonetaryBeforeCash - cashPaid;

  // --- Dynamic Option Calculations based on Cash Paid ---

  // OPTION 1: Pay all in cash (No metal to ledgers)
  const opt1CashDue = Math.max(0, totalMonetaryBeforeCash - cashPaid);
  const opt1GoldToLedger = 0;
  const opt1SilverToLedger = 0;

  // OPTION 4: Convert Remaining Metal to Both Ledgers
  const opt4CashDue = Math.max(0, nonMetalCharges - cashPaid);
  const opt4CashForMetal = Math.max(0, cashPaid - nonMetalCharges);

  const opt4SilverRupeesPaid = Math.min(silverLeftRupees, opt4CashForMetal);
  const opt4RemainingCashForGold = opt4CashForMetal - opt4SilverRupeesPaid;
  const opt4GoldRupeesPaid = Math.min(goldLeftRupees, opt4RemainingCashForGold);

  const opt4RemainingSilverRupees = Math.max(0, silverLeftRupees - opt4SilverRupeesPaid);
  const opt4RemainingGoldRupees = Math.max(0, goldLeftRupees - opt4GoldRupeesPaid);

  const opt4SilverToLedger = isPureSilver
    ? physicalSilverDue
    : ((activeSilverRate > 0 && opt4RemainingSilverRupees > 0)
      ? (opt4RemainingSilverRupees / (activeSilverRate / 1000))
      : 0);
  const opt4GoldToLedger = isPureGold
    ? physicalGoldDue
    : ((activeGoldRate > 0 && opt4RemainingGoldRupees > 0)
      ? (opt4RemainingGoldRupees / (activeGoldRate / 10))
      : 0);

  // OPTION 2: Convert to Gold Ledger (Silver & Non-Metal in Cash)
  const opt2RequiredCash = nonMetalCharges + (isPureSilver ? 0 : silverLeftRupees);
  const opt2CashDue = Math.max(0, opt2RequiredCash - cashPaid);
  const opt2CashForGold = Math.max(0, cashPaid - opt2RequiredCash);
  const opt2GoldRupeesPaid = Math.min(goldLeftRupees, opt2CashForGold);
  const opt2RemainingGoldRupees = Math.max(0, goldLeftRupees - opt2GoldRupeesPaid);
  const opt2GoldToLedger = isPureGold
    ? physicalGoldDue
    : ((activeGoldRate > 0 && opt2RemainingGoldRupees > 0)
      ? (opt2RemainingGoldRupees / (activeGoldRate / 10))
      : 0);
  const opt2SilverToLedger = 0;

  // OPTION 3: Convert to Silver Ledger (Gold & Non-Metal in Cash)
  const opt3RequiredCash = nonMetalCharges + (isPureGold ? 0 : goldLeftRupees);
  const opt3CashDue = Math.max(0, opt3RequiredCash - cashPaid);
  const opt3CashForSilver = Math.max(0, cashPaid - opt3RequiredCash);
  const opt3SilverRupeesPaid = Math.min(silverLeftRupees, opt3CashForSilver);
  const opt3RemainingSilverRupees = Math.max(0, silverLeftRupees - opt3SilverRupeesPaid);
  const opt3SilverToLedger = isPureSilver
    ? physicalSilverDue
    : ((activeSilverRate > 0 && opt3RemainingSilverRupees > 0)
      ? (opt3RemainingSilverRupees / (activeSilverRate / 1000))
      : 0);
  const opt3GoldToLedger = 0;

  let selectedGoldToLedger = 0;
  let selectedSilverToLedger = 0;
  let displayCashDue = opt1CashDue;

  if (cashBalanceAction === 'cash') {
    selectedGoldToLedger = opt1GoldToLedger;
    selectedSilverToLedger = opt1SilverToLedger;
    displayCashDue = opt1CashDue;
  } else if (cashBalanceAction === 'metal_gold') {
    selectedGoldToLedger = opt2GoldToLedger;
    selectedSilverToLedger = opt2SilverToLedger;
    displayCashDue = opt2CashDue;
  } else if (cashBalanceAction === 'metal_silver') {
    selectedGoldToLedger = opt3GoldToLedger;
    selectedSilverToLedger = opt3SilverToLedger;
    displayCashDue = opt3CashDue;
  } else if (cashBalanceAction === 'metal_both') {
    selectedGoldToLedger = opt4GoldToLedger;
    selectedSilverToLedger = opt4SilverToLedger;
    displayCashDue = opt4CashDue;
  }

  const isFullySettled = displayCashDue <= 0 && selectedGoldToLedger === 0 && selectedSilverToLedger === 0;
  const fmt = (n: number) => n.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

  useEffect(() => {
    axiosClient.get('/sellers/').then(res => setSellers(res.data.items || res.data || []));
  }, []);

  const handleGenerate = async (shouldPrint: boolean) => {
    if (!isFullySettled && !selectedSeller) {
      toast.error('A supplier must be selected for outstanding balances.');
      return;
    }
    if (cashPaid < 0 || goldGiven < 0 || silverGiven < 0) {
      toast.error('Payments/deposits cannot be negative.');
      return;
    }
    setLoading(true);

    let updatedItems = (payload.items || []).map((item: any) => {
      const defaultTouch = item.metal_type === 'Gold' ? 91.6 : 99.9;
      const touch = Number(item.touch_purity || item.touchPurity || defaultTouch);
      return {
        ...item,
        touch_purity: touch > 0 ? touch : defaultTouch
      };
    });
    if (goldGiven > 0) {
      const gTouch = Number(goldGivenTanch > 0 ? goldGivenTanch : 100);
      const fineG = goldGiven * (gTouch / 100);
      const gVal = isPureMetal ? 0 : fineG * (activeGoldRate / 10);
      updatedItems.push({
        item_name: 'Metal Given (Gold)',
        metal_type: 'Gold',
        category: 'Deposit',
        gross_weight: goldGiven,
        stone_weight: 0,
        net_weight: goldGiven,
        touch_purity: gTouch,
        wastage: 0,
        fine_weight: fineG,
        metal_rate: isPureMetal ? 0 : activeGoldRate,
        metal_value: gVal,
        labour_charge: 0,
        testing_melting_charge: 0,
        hallmark_charge: 0,
        other_charges: 0,
        discount: 0,
        taxable_amount: 0
      });
    }
    if (silverGiven > 0) {
      const sTouch = Number(silverGivenTanch > 0 ? silverGivenTanch : 100);
      const fineS = silverGiven * (sTouch / 100);
      const sVal = isPureMetal ? 0 : fineS * (activeSilverRate / 1000);
      updatedItems.push({
        item_name: 'Metal Given (Silver)',
        metal_type: 'Silver',
        category: 'Deposit',
        gross_weight: silverGiven,
        stone_weight: 0,
        net_weight: silverGiven,
        touch_purity: sTouch,
        wastage: 0,
        fine_weight: fineS,
        metal_rate: isPureMetal ? 0 : activeSilverRate,
        metal_value: sVal,
        labour_charge: 0,
        testing_melting_charge: 0,
        hallmark_charge: 0,
        other_charges: 0,
        discount: 0,
        taxable_amount: 0
      });
    }

    const backendSettlementType = isPureMetal ? 'Metal' : ((cashBalanceAction !== 'cash') ? 'Metal' : 'Cash');
    const goldBalMetal = selectedGoldToLedger > 0.001 
      ? selectedGoldToLedger 
      : (goldLeftGrams < -0.001 ? goldLeftGrams : 0);
    const silverBalMetal = selectedSilverToLedger > 0.001 
      ? selectedSilverToLedger 
      : (silverLeftGrams < -0.001 ? silverLeftGrams : 0);
    const finalBalanceAmount = isPureMetal ? 0 : displayCashDue;

    let backendBillType = 'Cash';
    if (isPureMetal) {
      backendBillType = 'Metal';
    } else if (hasGold && hasSilver) {
      backendBillType = 'Hybrid';
    } else if (totalMetalValueReceived > 0 || selectedGoldToLedger > 0 || selectedSilverToLedger > 0) {
      backendBillType = 'Hybrid';
    }

    const finalPayload = {
      ...payload,
      total_taxable: isPureMetal ? 0 : payload.total_taxable,
      cgst: isPureMetal ? 0 : payload.cgst,
      sgst: isPureMetal ? 0 : payload.sgst,
      igst: isPureMetal ? 0 : payload.igst,
      grand_total: isPureMetal ? 0 : payload.grand_total,
      items: updatedItems,
      seller_id: selectedSeller || null,
      status: isFullySettled ? 'Paid' : 'Completed',
      amount_paid: isPureMetal ? 0 : cashPaid,
      payment_method: isPureMetal ? 'Cash' : paymentMethod,
      payment_details: paymentMethod === 'UPI' ? { upi_id: upiId } : paymentMethod === 'Cheque' ? { cheque_no: chequeNo, bank_name: bankName, cheque_date: chequeDate } : null,
      bill_type: backendBillType,
      settlement_type: backendSettlementType,
      settlement_metal_type: cashBalanceAction === 'metal_gold' ? 'Gold' : cashBalanceAction === 'metal_silver' ? 'Silver' : cashBalanceAction === 'metal_both' ? 'Both' : null,
      metal_given_value: isPureMetal ? 0 : totalMetalValueReceived,
      cash_paid: isPureMetal ? 0 : cashPaid,
      balance_amount: finalBalanceAmount,
      balance_metal_weight: 0,
      gold_balance_metal_weight: goldBalMetal,
      silver_balance_metal_weight: silverBalMetal,
    };

    try {
      const res = await axiosClient.post('/purchases/', finalPayload);
      toast.success(`Purchase ${res.data.purchase_number || res.data.id} recorded!`);

      if (shouldPrint) {
        try {
          const pdfRes = await axiosClient.get(`/purchases/${res.data.id}/pdf-data`);
          const pdfData = pdfRes.data;
          pdfData.invoice.amount_paid    = Number(cashPaid) || 0;
          pdfData.invoice.cash_paid      = Number(cashPaid) || 0;
          pdfData.invoice.balance_due    = finalBalanceAmount;
          pdfData.invoice.balance_amount = finalBalanceAmount;
          pdfData.invoice.payment_method = paymentMethod;
          pdfData.invoice.transaction_id = paymentMethod === 'UPI' ? upiId : paymentMethod === 'Cheque' ? `${chequeNo} | ${bankName} | ${chequeDate}` : '-';
          pdfData.invoice.bill_type = backendBillType;
          pdfData.invoice.settlement_type = backendSettlementType;
          pdfData.invoice.settlement_metal_type = cashBalanceAction === 'metal_gold' ? 'Gold' : cashBalanceAction === 'metal_silver' ? 'Silver' : cashBalanceAction === 'metal_both' ? 'Both' : null;
          pdfData.invoice.gold_balance_metal_weight = goldBalMetal;
          pdfData.invoice.silver_balance_metal_weight = silverBalMetal;
          const { generateInvoicePDF } = await import('../../utils/invoicePdfUtils');
          await generateInvoicePDF(pdfData);
        } catch (pdfErr) {
          console.warn('Purchase PDF generation error:', pdfErr);
        }
      }

      onSuccess(res.data.id);
    } catch (e: any) {
      toast.error(getErrorMessage(e, 'Failed to record purchase'));
    } finally {
      setLoading(false);
    }
  };

  const handleSaveNewSupplier = async () => {
    if (!newSeller.name || newSeller.mobile.length !== 10) {
      toast.error('Name and 10-digit phone number are required');
      return;
    }
    setLoading(true);
    try {
      const res = await axiosClient.post('/sellers/', {
        name: newSeller.name,
        mobile: newSeller.mobile,
        address: '',
        city: newSeller.city
      });
      setSellers([...sellers, res.data]);
      setSelectedSeller(res.data.id);
      setMode('checkout');
      toast.success('Supplier added');
    } catch (e: any) {
      toast.error(getErrorMessage(e, 'Failed to save supplier'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-2 sm:p-4 overflow-hidden">
      <div className="bg-surface border border-gray-700 rounded-2xl shadow-2xl w-full max-w-3xl max-h-[92vh] flex flex-col overflow-hidden my-auto">
        <div className="flex justify-between items-center p-3.5 sm:p-4 border-b border-gray-700 bg-gray-900/90 sticky top-0 z-20 shrink-0">
          <h2 className="text-base sm:text-lg font-bold text-primary flex items-center gap-2"><Calculator size={20} /> Checkout Settlement</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white p-1 rounded hover:bg-gray-800 transition-colors"><X size={20} /></button>
        </div>
        <div className="p-3 sm:p-5 overflow-y-auto flex-1 custom-scrollbar space-y-4">
          {mode === 'checkout' && (
            <div className="space-y-4 sm:space-y-5">

              {/* TOP SUMMARY BANNER */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 sm:gap-3 p-2.5 sm:p-3 bg-gray-900/60 border border-gray-700/60 rounded-xl text-center">
                <div className="p-1">
                  <div className="text-[10px] text-gray-400 uppercase tracking-wider font-medium">Purchase Bill Amount</div>
                  <div className="text-sm sm:text-base font-mono text-white font-bold truncate">₹ {fmt(grandTotal)}</div>
                </div>
                <div className="p-1 border-t sm:border-t-0 sm:border-l border-gray-800">
                  <div className="text-[10px] text-gray-400 uppercase tracking-wider font-medium">Counter Metal Handed Over</div>
                  <div className="text-sm sm:text-base font-mono text-red-400 font-bold truncate">− ₹ {fmt(totalMetalValueReceived)}</div>
                </div>
                <div className="p-1 border-t sm:border-t-0 sm:border-l border-gray-800">
                  <div className="text-[10px] text-yellow-400 uppercase tracking-wider font-bold">Net Difference Due</div>
                  <div className="text-sm sm:text-base font-mono text-yellow-400 font-bold truncate">₹ {fmt(totalMonetaryBeforeCash)}</div>
                </div>
              </div>

              {/* SECTION 1: Metal Given to Supplier */}
              <div className="border border-gray-700 rounded-lg overflow-hidden">
                <div className="bg-gray-800/50 px-4 py-2 border-b border-gray-700">
                  <h3 className="text-xs font-bold text-gray-300 uppercase tracking-widest">Metal Given to Supplier at Counter (Optional)</h3>
                </div>
                <div className="p-4 space-y-4">
                  {hasGold && (
                    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2">
                      <div>
                        <label className="block text-[9px] text-yellow-500 uppercase tracking-widest mb-1 font-bold">
                          Net Gold Due {conversionGoldRate > 0 ? `@ ₹${conversionGoldRate}/10g` : '(Pure Metal)'}
                        </label>
                        <div className="text-sm font-mono text-yellow-400 font-bold">{totalGoldBilled.toFixed(3)} g</div>
                      </div>
                      <div>
                        <label className="block text-[9px] text-gray-500 uppercase tracking-widest mb-1">Gross Given</label>
                        <input type="number" min="0" step="0.001" value={goldGiven === 0 ? '' : goldGiven} onChange={e => setGoldGiven(Number(e.target.value))} placeholder="0.000" className="w-full bg-background border border-gray-700 rounded px-1 py-1 text-sm font-mono text-yellow-400 outline-none focus:border-yellow-500" />
                      </div>
                      <div>
                        <label className="block text-[9px] text-gray-500 uppercase tracking-widest mb-1">Tanch %</label>
                        <input type="number" min="0" max="100" step="0.01" value={goldGivenTanch} onChange={e => setGoldGivenTanch(Number(e.target.value))} className="w-full bg-background border border-gray-700 rounded px-1 py-1 text-sm font-mono text-yellow-400 outline-none focus:border-yellow-500" />
                      </div>
                      <div>
                        <label className="block text-[9px] text-gray-500 uppercase tracking-widest mb-1">Fine Metal</label>
                        <div className="text-sm font-mono text-yellow-400">{fineGoldGiven.toFixed(3)} g</div>
                        {fineGoldGiven > 0 && <div className="text-[9.5px] text-gray-400 font-mono">₹ {fmt(goldValueReceived)}</div>}
                      </div>
                      <div className="col-span-2 sm:col-span-1">
                        <label className="block text-[9px] text-gray-400 uppercase tracking-widest mb-1 font-bold">Left (Remaining)</label>
                        {goldLeftGrams > 0.001 ? (
                          <div className="text-sm font-mono text-red-400 font-bold">+{goldLeftGrams.toFixed(3)} g Due</div>
                        ) : goldLeftGrams < -0.001 ? (
                          <div className="text-sm font-mono text-green-400 font-bold">{Math.abs(goldLeftGrams).toFixed(3)} g Surplus</div>
                        ) : (
                          <div className="text-sm font-mono text-primary font-bold">0.000 g (Settled)</div>
                        )}
                        {goldLeftGrams > 0.001 && <div className="text-[9.5px] text-red-400/80 font-mono">₹ {fmt(goldLeftRupees)}</div>}
                      </div>
                    </div>
                  )}
                  {hasSilver && (
                    <div className={`grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2 ${hasGold ? 'border-t border-gray-800 pt-4' : ''}`}>
                      <div>
                        <label className="block text-[9px] text-gray-300 uppercase tracking-widest mb-1 font-bold">
                          Net Silver Due {conversionSilverRate > 0 ? `@ ₹${conversionSilverRate}/kg` : '(Pure Metal)'}
                        </label>
                        <div className="text-sm font-mono text-gray-200 font-bold">{totalSilverBilled.toFixed(3)} g</div>
                      </div>
                      <div>
                        <label className="block text-[9px] text-gray-500 uppercase tracking-widest mb-1">Gross Given</label>
                        <input type="number" min="0" step="0.001" value={silverGiven === 0 ? '' : silverGiven} onChange={e => setSilverGiven(Number(e.target.value))} placeholder="0.000" className="w-full bg-background border border-gray-700 rounded px-1 py-1 text-sm font-mono text-gray-300 outline-none focus:border-gray-400" />
                      </div>
                      <div>
                        <label className="block text-[9px] text-gray-500 uppercase tracking-widest mb-1">Tanch %</label>
                        <input type="number" min="0" max="100" step="0.01" value={silverGivenTanch} onChange={e => setSilverGivenTanch(Number(e.target.value))} className="w-full bg-background border border-gray-700 rounded px-1 py-1 text-sm font-mono text-gray-300 outline-none focus:border-gray-400" />
                      </div>
                      <div>
                        <label className="block text-[9px] text-gray-500 uppercase tracking-widest mb-1">Fine Metal</label>
                        <div className="text-sm font-mono text-gray-300">{fineSilverGiven.toFixed(3)} g</div>
                        {fineSilverGiven > 0 && <div className="text-[9.5px] text-gray-400 font-mono">₹ {fmt(silverValueReceived)}</div>}
                      </div>
                      <div className="col-span-2 sm:col-span-1">
                        <label className="block text-[9px] text-gray-400 uppercase tracking-widest mb-1 font-bold">Left (Remaining)</label>
                        {silverLeftGrams > 0.001 ? (
                          <div className="text-sm font-mono text-red-400 font-bold">+{silverLeftGrams.toFixed(3)} g Due</div>
                        ) : silverLeftGrams < -0.001 ? (
                          <div className="text-sm font-mono text-green-400 font-bold">{Math.abs(silverLeftGrams).toFixed(3)} g Surplus</div>
                        ) : (
                          <div className="text-sm font-mono text-primary font-bold">0.000 g (Settled)</div>
                        )}
                        {silverLeftGrams > 0.001 && <div className="text-[9.5px] text-red-400/80 font-mono">₹ {fmt(silverLeftRupees)}</div>}
                      </div>
                    </div>
                  )}
                  <div className="border-t border-gray-800 pt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <div className="bg-yellow-950/20 border border-yellow-700/40 rounded-lg p-2.5">
                        <label className="block text-[10px] text-yellow-500 font-bold uppercase tracking-widest mb-0.5">
                          {isPureMetal ? 'Pure Metal Settlement (No Money Flow)' : 'Total Amount Payable (If 100% Cash)'}
                        </label>
                        <div className="text-2xl font-mono text-yellow-400 font-bold">
                          {isPureMetal && nonMetalCharges === 0 ? '₹ 0.00' : `₹ ${fmt(totalMonetaryBeforeCash)}`}
                        </div>
                        <div className="text-[10px] text-gray-400 mt-0.5">
                          {isPureMetal
                            ? `${hasGold ? `+${physicalGoldDue.toFixed(3)}g Gold ` : ''}${hasSilver ? `+${physicalSilverDue.toFixed(3)}g Silver ` : ''}(Pure Metal to Ledger)`
                            : `Includes ₹${fmt(totalMetalRupeesDue)} metal value + ₹${fmt(nonMetalCharges)} non-metal`}
                        </div>
                      </div>

                      <div className="p-2.5 bg-gray-900/60 border border-gray-700/50 rounded-lg text-[11px] space-y-1">
                        <div className="flex justify-between items-center text-gray-300 font-medium">
                          <span>{isPureMetal ? 'Remaining Metal Balance:' : 'Remaining Metal Value:'}</span>
                          <span className="font-mono text-white font-bold">{isPureMetal ? 'Pure Weight (₹0.00)' : `₹ ${fmt(totalMetalRupeesDue)}`}</span>
                        </div>
                        {goldLeftRupees > 0 && (
                          <div className="flex justify-between text-[10px] text-gray-400 pl-2">
                            <span>• Gold ({physicalGoldDue.toFixed(3)}g):</span>
                            <span className="font-mono">₹ {fmt(goldLeftRupees)}</span>
                          </div>
                        )}
                        {silverLeftRupees > 0 && (
                          <div className="flex justify-between text-[10px] text-gray-400 pl-2">
                            <span>• Silver ({physicalSilverDue.toFixed(3)}g):</span>
                            <span className="font-mono">₹ {fmt(silverLeftRupees)}</span>
                          </div>
                        )}
                        <div className="border-t border-gray-800 pt-1 flex justify-between items-center text-primary font-medium">
                          <span>Non-Metal Charges (Labour + Other + GST):</span>
                          <span className="font-mono font-bold">₹ {fmt(nonMetalCharges)}</span>
                        </div>
                        <div className="flex justify-between text-[10px] text-gray-400 pl-2">
                          <span>• Labour Charges:</span>
                          <span className="font-mono">₹ {fmt(totalLabourCharges)}</span>
                        </div>
                        {totalOtherCharges > 0 && (
                          <div className="flex justify-between text-[10px] text-gray-400 pl-2">
                            <span>• Other / Testing Charges:</span>
                            <span className="font-mono">₹ {fmt(totalOtherCharges)}</span>
                          </div>
                        )}
                        <div className="flex justify-between text-[10px] text-gray-400 pl-2">
                          <span>• GST:</span>
                          <span className="font-mono">₹ {fmt(totalGst)}</span>
                        </div>
                      </div>
                    </div>

                    <div>
                      <div className="flex justify-between items-center mb-1">
                        <label className="text-[10px] text-green-400 font-bold uppercase tracking-widest">Cash Paid</label>
                        <div className="flex gap-1.5">
                          <button 
                            type="button"
                            onClick={() => setCashPaid(Math.round(totalMonetaryBeforeCash * 100) / 100)}
                            className="px-1.5 py-0.5 bg-green-900/40 hover:bg-green-900/70 text-green-400 border border-green-700/60 rounded text-[9px] font-mono cursor-pointer transition-colors"
                            title="Auto-fill full cash payment"
                          >
                            Full (₹{fmt(totalMonetaryBeforeCash)})
                          </button>
                        </div>
                      </div>
                      <input type="number" min="0" value={cashPaid === 0 ? '' : cashPaid} onChange={e => setCashPaid(Number(e.target.value))} placeholder="0" className="w-full bg-background border border-green-900 rounded p-2 text-lg font-mono text-green-400 outline-none focus:border-green-500" />
                      <div className="flex gap-3 mt-2">
                        {(['Cash', 'UPI', 'Cheque'] as const).map(m => (
                          <label key={m} className="flex items-center gap-1 cursor-pointer">
                            <input type="radio" checked={paymentMethod === m} onChange={() => setPaymentMethod(m)} className="accent-green-500" />
                            <span className="text-[9px] text-gray-400 uppercase">{m}</span>
                          </label>
                        ))}
                      </div>
                      {paymentMethod === 'UPI' && <input type="text" placeholder="Transaction ID" value={upiId} onChange={e => setUpiId(e.target.value)} className="w-full bg-background border border-gray-700 rounded p-1 text-xs text-white outline-none mt-2" />}
                      {paymentMethod === 'Cheque' && (
                        <div className="flex gap-1 mt-2">
                          <input type="text" placeholder="Cheque No." value={chequeNo} onChange={e => setChequeNo(e.target.value)} className="w-1/3 bg-background border border-gray-700 rounded p-1 text-xs text-white" />
                          <input type="text" placeholder="Bank" value={bankName} onChange={e => setBankName(e.target.value)} className="w-1/3 bg-background border border-gray-700 rounded p-1 text-xs text-white" />
                          <input type="date" value={chequeDate} onChange={e => setChequeDate(e.target.value)} className="w-1/3 bg-background border border-gray-700 rounded p-1 text-xs text-white [color-scheme:dark]" />
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              {/* SECTION 2: Final Settlement */}
              <div className="border border-primary/30 bg-primary/5 rounded-lg p-4">
                <h3 className="text-xs font-bold text-primary uppercase tracking-widest mb-3">Final Settlement Summary</h3>
                <div className="space-y-2 p-3 bg-yellow-900/10 border border-yellow-700/30 rounded-lg">
                  {hasGold && (
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-gray-400">Gold to Ledger:</span>
                      <span className={`font-mono font-bold ${selectedGoldToLedger > 0.001 ? 'text-yellow-400' : goldLeftGrams < -0.001 ? 'text-green-400' : 'text-green-400'}`}>
                        {selectedGoldToLedger > 0.001 
                          ? `+${selectedGoldToLedger.toFixed(3)} g Due (₹${fmt(selectedGoldToLedger * (activeGoldRate / 10))})` 
                          : goldLeftGrams < -0.001
                            ? `-${Math.abs(goldLeftGrams).toFixed(3)} g Surplus (Advance Credit)`
                            : '0.000 g (Settled / Paid)'}
                      </span>
                    </div>
                  )}
                  {hasSilver && (
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-gray-400">Silver to Ledger:</span>
                      <span className={`font-mono font-bold ${selectedSilverToLedger > 0.001 ? 'text-gray-300' : silverLeftGrams < -0.001 ? 'text-green-400' : 'text-green-400'}`}>
                        {selectedSilverToLedger > 0.001 
                          ? `+${selectedSilverToLedger.toFixed(3)} g Due (₹${fmt(selectedSilverToLedger * (activeSilverRate / 1000))})` 
                          : silverLeftGrams < -0.001
                            ? `-${Math.abs(silverLeftGrams).toFixed(3)} g Surplus (Advance Credit)`
                            : '0.000 g (Settled / Paid)'}
                      </span>
                    </div>
                  )}
                  <div className="flex justify-between items-center text-xs text-gray-400 pt-1 border-t border-gray-800">
                    <span>Non-Metal Charges (Labour + Other + GST):</span>
                    <span className="font-mono font-bold text-white">₹ {fmt(nonMetalCharges)}</span>
                  </div>
                  {cashPaid > 0 && (
                    <div className="flex justify-between items-center text-xs text-green-400">
                      <span>Cash Paid Now:</span>
                      <span className="font-mono font-bold text-green-400">− ₹ {fmt(cashPaid)}</span>
                    </div>
                  )}
                  {(hasGold || hasSilver) && <div className="border-t border-gray-700 my-1" />}
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-gray-400">{displayCashDue > 0 ? 'Amount Payable / Cash Due:' : displayCashDue < 0 ? 'Refund from Supplier:' : 'Amount Payable:'}</span>
                    <span className={`font-mono font-bold text-base ${displayCashDue > 0 ? 'text-red-400' : 'text-green-400'}`}>
                      {displayCashDue < 0 ? '(Refund) ' : ''}₹ {fmt(Math.abs(displayCashDue))}{displayCashDue === 0 && ' ✓ (Paid)'}
                    </span>
                  </div>
                  {displayCashDue < 0 && <div className="text-[10px] text-green-500">Overpaid to supplier. Outstanding credit ₹ {fmt(Math.abs(displayCashDue))}.</div>}
                </div>

                {(physicalGoldDue > 0 || physicalSilverDue > 0 || cashBalanceDue > 0) && (
                  <div className="mt-4">
                    <label className="block text-[10px] text-gray-500 uppercase tracking-widest mb-2">How to settle the remaining balance?</label>
                    <div className="flex flex-col gap-2">
                      {/* OPTION 1: ALL IN CASH */}
                      <label className={`flex items-center gap-2 p-2 rounded border cursor-pointer ${cashBalanceAction === 'cash' ? 'border-yellow-500/50 bg-yellow-500/10' : 'border-gray-700 hover:border-gray-600'}`}>
                        <input type="radio" checked={cashBalanceAction === 'cash'} onChange={() => setCashBalanceAction('cash')} className="accent-yellow-500" />
                        <span className="text-xs text-white font-medium flex flex-col">
                          <span>Keep as Cash Due — pay all in cash</span>
                          <span className="text-[10px] text-gray-400">
                            Total Cash Due: <strong className={opt1CashDue > 0 ? 'text-red-400' : 'text-green-400'}>₹ {fmt(opt1CashDue)}</strong>
                            {cashPaid > 0 ? ` (₹${fmt(totalMonetaryBeforeCash)} total − ₹${fmt(cashPaid)} cash paid)` : ` (includes ₹${fmt(totalMetalRupeesDue)} metal + ₹${fmt(nonMetalCharges)} charges)`}
                          </span>
                        </span>
                      </label>

                      {/* OPTION 2: GOLD LEDGER */}
                      {physicalGoldDue > 0 && !hasSilver && (
                        <label className={`flex items-center gap-2 p-2 rounded border cursor-pointer ${cashBalanceAction === 'metal_gold' ? 'border-yellow-500/50 bg-yellow-500/10' : 'border-gray-700 hover:border-gray-600'}`}>
                          <input type="radio" checked={cashBalanceAction === 'metal_gold'} onChange={() => setCashBalanceAction('metal_gold')} className="accent-yellow-500" />
                          <span className="text-xs text-white font-medium flex flex-col">
                            <span>Convert Metal to Gold Ledger</span>
                            <span className="text-[10px] text-yellow-400">
                              +{opt2GoldToLedger.toFixed(3)} g Gold to Ledger | <strong className={opt2CashDue > 0 ? 'text-red-400' : 'text-green-400'}>₹ {fmt(opt2CashDue)} Cash Due</strong> (Charges: ₹{fmt(nonMetalCharges)})
                            </span>
                          </span>
                        </label>
                      )}

                      {/* OPTION 3: SILVER LEDGER */}
                      {physicalSilverDue > 0 && !hasGold && (
                        <label className={`flex items-center gap-2 p-2 rounded border cursor-pointer ${cashBalanceAction === 'metal_silver' ? 'border-yellow-500/50 bg-yellow-500/10' : 'border-gray-700 hover:border-gray-600'}`}>
                          <input type="radio" checked={cashBalanceAction === 'metal_silver'} onChange={() => setCashBalanceAction('metal_silver')} className="accent-yellow-500" />
                          <span className="text-xs text-white font-medium flex flex-col">
                            <span>Convert Metal to Silver Ledger</span>
                            <span className="text-[10px] text-gray-300">
                              +{opt3SilverToLedger.toFixed(3)} g Silver to Ledger | <strong className={opt3CashDue > 0 ? 'text-red-400' : 'text-green-400'}>₹ {fmt(opt3CashDue)} Cash Due</strong> (Charges: ₹{fmt(nonMetalCharges)})
                            </span>
                          </span>
                        </label>
                      )}

                      {/* BOTH METALS OPTIONS */}
                      {hasGold && hasSilver && (
                        <>
                          <label className={`flex items-center gap-2 p-2 rounded border cursor-pointer ${cashBalanceAction === 'metal_both' ? 'border-yellow-500/50 bg-yellow-500/10' : 'border-gray-700 hover:border-gray-600'}`}>
                            <input type="radio" checked={cashBalanceAction === 'metal_both'} onChange={() => setCashBalanceAction('metal_both')} className="accent-yellow-500" />
                            <span className="text-xs text-white font-medium flex flex-col">
                              <span className="flex items-center gap-2">
                                Convert Both Metals to Ledgers
                                {isPureMetal && <span className="bg-yellow-500/20 text-yellow-400 text-[9px] px-1.5 py-0.2 rounded font-bold">Both Metals Due</span>}
                              </span>
                              <span className="text-[10px] text-yellow-400">
                                Gold: <strong>+{opt4GoldToLedger.toFixed(3)} g</strong> | Silver: <strong>+{opt4SilverToLedger.toFixed(3)} g</strong> {isPureMetal ? '| ₹ 0.00 Cash Due (No money flow)' : `| ${opt4CashDue > 0 ? `₹ ${fmt(opt4CashDue)} Cash Due` : '₹ 0.00 Cash Due'}`}
                              </span>
                            </span>
                          </label>
                          <label className={`flex items-center gap-2 p-2 rounded border cursor-pointer ${cashBalanceAction === 'metal_gold' ? 'border-yellow-500/50 bg-yellow-500/10' : 'border-gray-700 hover:border-gray-600'}`}>
                            <input type="radio" checked={cashBalanceAction === 'metal_gold'} onChange={() => setCashBalanceAction('metal_gold')} className="accent-yellow-500" />
                            <span className="text-xs text-white font-medium flex flex-col">
                              <span>Convert Metal to Gold Ledger Only</span>
                              <span className="text-[10px] text-yellow-400">
                                +{opt2GoldToLedger.toFixed(3)} g Gold | <strong className={opt2CashDue > 0 ? 'text-red-400' : 'text-green-400'}>₹ {fmt(opt2CashDue)} Cash Due</strong> {isPureMetal ? '' : `(Silver & charges: ₹${fmt(opt2RequiredCash)})`}
                              </span>
                            </span>
                          </label>
                          <label className={`flex items-center gap-2 p-2 rounded border cursor-pointer ${cashBalanceAction === 'metal_silver' ? 'border-yellow-500/50 bg-yellow-500/10' : 'border-gray-700 hover:border-gray-600'}`}>
                            <input type="radio" checked={cashBalanceAction === 'metal_silver'} onChange={() => setCashBalanceAction('metal_silver')} className="accent-yellow-500" />
                            <span className="text-xs text-white font-medium flex flex-col">
                              <span>Convert Metal to Silver Ledger Only</span>
                              <span className="text-[10px] text-gray-300">
                                +{opt3SilverToLedger.toFixed(3)} g Silver | <strong className={opt3CashDue > 0 ? 'text-red-400' : 'text-green-400'}>₹ {fmt(opt3CashDue)} Cash Due</strong> {isPureMetal ? '' : `(Gold & charges: ₹${fmt(opt3RequiredCash)})`}
                              </span>
                            </span>
                          </label>
                        </>
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* SECTION 3: Supplier */}
              <div className="border-t border-gray-800 pt-4">
                <div className="flex justify-between items-end mb-2">
                  <label className="block text-xs font-bold text-gray-500 uppercase tracking-widest">Select Supplier</label>
                  <button onClick={() => setMode('new_supplier')} className="text-[10px] bg-primary/20 text-primary px-2 py-1 rounded flex items-center gap-1 hover:bg-primary/30 transition-colors"><UserPlus size={12} /> New</button>
                </div>
                <select className="w-full bg-background border border-gray-700 rounded p-3 text-white outline-none focus:border-primary transition-colors" value={selectedSeller} onChange={e => setSelectedSeller(Number(e.target.value))}>
                  <option value="">-- Select Supplier / Seller --</option>
                  {sellers.map(s => <option key={s.id} value={s.id}>{s.name} ({s.mobile})</option>)}
                </select>
                {!isFullySettled && !selectedSeller && <p className="text-red-400 text-[10px] mt-1">* A supplier must be selected for outstanding balances.</p>}
              </div>

              <div className="flex space-x-2 mt-4">
                <button onClick={onClose} className="flex-1 py-3 border border-gray-700 rounded-lg text-gray-400 hover:bg-gray-800 font-bold transition-colors">Cancel</button>
                <button onClick={() => handleGenerate(false)} disabled={loading || (!isFullySettled && !selectedSeller)} className="flex-1 py-3 bg-gray-700 text-white font-bold rounded-lg hover:bg-gray-600 disabled:opacity-50 transition-all">
                  {loading ? 'Saving...' : 'SAVE ONLY'}
                </button>
                <button onClick={() => handleGenerate(true)} disabled={loading || (!isFullySettled && !selectedSeller)} className="flex-1 py-3 bg-primary text-black font-black rounded-lg hover:bg-primary-dark disabled:opacity-50 flex justify-center items-center shadow-[0_0_15px_rgba(212,175,55,0.3)] transition-all">
                  {loading ? 'Processing...' : <><Check size={18} className="mr-2" /> SAVE &amp; PRINT</>}
                </button>
              </div>
            </div>
          )}

          {mode === 'new_supplier' && (
            <div className="space-y-4">
              <h3 className="font-bold text-white mb-4 border-b border-gray-800 pb-2">Add New Supplier</h3>
              <div>
                <label className="block text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-1">Supplier Name *</label>
                <input placeholder="Supplier / Seller Name" className="w-full bg-background border border-gray-700 rounded p-2 text-white outline-none focus:border-primary" value={newSeller.name} onChange={e => setNewSeller({ ...newSeller, name: e.target.value })} />
              </div>
              <div>
                <label className="block text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-1">Mobile Number *</label>
                <input placeholder="10-digit Mobile Number" className="w-full bg-background border border-gray-700 rounded p-2 text-white outline-none focus:border-primary" value={newSeller.mobile} onChange={e => setNewSeller({ ...newSeller, mobile: e.target.value })} />
              </div>
              <div>
                <label className="block text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-1">City</label>
                <input placeholder="City" className="w-full bg-background border border-gray-700 rounded p-2 text-white outline-none focus:border-primary" value={newSeller.city} onChange={e => setNewSeller({ ...newSeller, city: e.target.value })} />
              </div>
              <div className="flex space-x-3 mt-6">
                <button onClick={() => setMode('checkout')} className="flex-1 py-2 border border-gray-700 rounded text-gray-400 hover:bg-gray-800">Cancel</button>
                <button onClick={handleSaveNewSupplier} disabled={loading} className="flex-1 py-2 bg-primary text-black font-bold rounded hover:bg-primary/90">{loading ? 'Saving...' : 'Save Supplier'}</button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
