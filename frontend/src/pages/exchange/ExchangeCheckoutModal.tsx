import { useState, useEffect, useMemo } from 'react';
import { axiosClient } from '../../api/axiosClient';
import toast from 'react-hot-toast';
import { Check, X, Calculator, UserPlus } from 'lucide-react';
import { useBillingStore } from '../../store/billingStore';
import { getErrorMessage } from '../../utils/errorUtils';



export default function ExchangeCheckoutModal({ payload, differenceAmount: _differenceAmount, onClose, onSuccess }: { payload: any; differenceAmount?: number; onClose: () => void; onSuccess: (id: string) => void; }) {
  const [loading, setLoading] = useState(false);
  const [customers, setCustomers] = useState<any[]>([]);
  const initialCustomerId = useBillingStore.getState().selectedCustomerId;
  const [selectedCustomer, setSelectedCustomer] = useState<number | ''>(initialCustomerId || '');
  const [mode, setMode] = useState<'checkout' | 'new_customer'>('checkout');
  const [newCustomer, setNewCustomer] = useState({ first_name: '', last_name: '', phone: '', city: '' });

  const [cashReceived, setCashReceived] = useState<number>(0);
  const [goldDeposited, setGoldDeposited] = useState<number>(0);
  const [goldDepositTanch, setGoldDepositTanch] = useState<number>(100);
  const [silverDeposited, setSilverDeposited] = useState<number>(0);
  const [silverDepositTanch, setSilverDepositTanch] = useState<number>(100);

  // cash | metal_gold | metal_silver | metal_both
  const [cashBalanceAction, setCashBalanceAction] = useState<'cash' | 'metal_gold' | 'metal_silver' | 'metal_both'>('cash');

  const [paymentMethod, setPaymentMethod] = useState<'Cash' | 'UPI' | 'Cheque'>('Cash');
  const [upiId, setUpiId] = useState('');
  const [chequeNo, setChequeNo] = useState('');
  const [bankName, setBankName] = useState('');
  const [chequeDate, setChequeDate] = useState('');

  // STEP 1: Extract from payload
  const { 
    goldRate, 
    silverRate,
    tgNew, tgOld,
    tsNew, tsOld,
    netGoldRequired,
    netSilverRequired,
    hasGold,
    hasSilver
  } = useMemo(() => {
    let newGold = 0, oldGold = 0, newSilver = 0, oldSilver = 0, gr = 0, sr = 0;
    
    const extractFine = (item: any) => {
      return Number(
        item.fine_weight ||
        item.pure_weight ||
        (item.net_weight && (item.touch_purity || item.touch || item.tanch_percentage) ? (item.net_weight * Number(item.touch_purity || item.touch || item.tanch_percentage) / 100) : item.net_weight) ||
        0
      );
    };

    (payload.new_items || []).forEach((item: any) => {
      const m = (item.metal || '').toLowerCase();
      if (m === 'gold') {
        newGold += extractFine(item);
        if (!gr) gr = Number(item.rate_applied || item.rate || item.applied_rate || 0);
      } else if (m === 'silver') {
        newSilver += extractFine(item);
        if (!sr) sr = Number(item.rate_applied || item.rate || item.applied_rate || 0);
      }
    });
    
    (payload.old_items || []).forEach((item: any) => {
      const m = (item.metal || '').toLowerCase();
      if (m === 'gold') {
        oldGold += extractFine(item);
        if (!gr) gr = Number(item.rate_applied || item.rate || item.applied_rate || 0);
      } else if (m === 'silver') {
        oldSilver += extractFine(item);
        if (!sr) sr = Number(item.rate_applied || item.rate || item.applied_rate || 0);
      }
    });

    if (gr > 0 && gr < 15000) gr = gr * 10;
    if (sr > 0 && sr < 1000) sr = sr * 1000;

    // Net metal required: New metal MINUS old metal already traded in
    const netGold = Math.max(0, newGold - oldGold);
    const netSilver = Math.max(0, newSilver - oldSilver);
    
    return { 
      totalGoldBilled: netGold, 
      totalSilverBilled: netSilver, 
      goldRate: gr, 
      silverRate: sr,
      tgNew: newGold,
      tgOld: oldGold,
      tsNew: newSilver,
      tsOld: oldSilver,
      netGoldRequired: netGold,
      netSilverRequired: netSilver,
      hasGold: newGold > 0 || oldGold > 0,
      hasSilver: newSilver > 0 || oldSilver > 0
    };
  }, [payload.new_items, payload.old_items]);

  const isPureGold = hasGold && (goldRate === 0 || (
    [...(payload.new_items || []), ...(payload.old_items || [])]
      .filter((i: any) => (i.metal || '').toLowerCase() === 'gold')
      .every((i: any) => Number(i.rate_applied || i.rate || i.applied_rate || 0) === 0)
  ));
  const isPureSilver = hasSilver && (silverRate === 0 || (
    [...(payload.new_items || []), ...(payload.old_items || [])]
      .filter((i: any) => (i.metal || '').toLowerCase() === 'silver')
      .every((i: any) => Number(i.rate_applied || i.rate || i.applied_rate || 0) === 0)
  ));
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

  const conversionGoldRate   = baseGoldRate;
  const conversionSilverRate = baseSilverRate;
  const activeGoldRate   = conversionGoldRate;
  const activeSilverRate = conversionSilverRate;

  useEffect(() => {
    if (isPureMetal) {
      if (hasGold && hasSilver) setCashBalanceAction('metal_both');
      else if (hasGold) setCashBalanceAction('metal_gold');
      else if (hasSilver) setCashBalanceAction('metal_silver');
    }
  }, [isPureMetal, hasGold, hasSilver]);

  // STEP 2.1: Non-metal charges (Labour/Making, Expenses/Hallmark, and GST)
  // CRITICAL RULE: These are services and taxes that CANNOT be converted into metal grams and must be in Amount Payable!
  const totalMakingCharges = useMemo(() => {
    return (payload.new_items || []).reduce((acc: number, item: any) => acc + Number(item.making_charges_amount || 0), 0);
  }, [payload.new_items]);

  const totalOtherCharges = useMemo(() => {
    return (payload.new_items || []).reduce((acc: number, item: any) => 
      acc + Number(item.hallmark_charges || 0) + Number(item.other_charges || 0), 0);
  }, [payload.new_items]);

  const totalNewDiscounts = useMemo(() => {
    return (payload.new_items || []).reduce((acc: number, item: any) => acc + Number(item.discount || 0), 0);
  }, [payload.new_items]);

  const totalOldNetDeductions = useMemo(() => {
    return (payload.old_items || []).reduce((acc: number, item: any) => {
      return acc
        + Number(item.labour_charge || 0)
        + Number(item.testing_melting_charge || 0)
        + Number(item.hallmark_charge || 0)
        + Number(item.discount || 0)
        - Number(item.other_charges || 0);
    }, 0);
  }, [payload.old_items]);

  const totalGst = Number(payload.gst_amount || 0);

  // Non-metal charges MUST always remain in amount payable (cash/money)
  const nonMetalCharges = totalMakingCharges + totalOtherCharges + totalGst - totalNewDiscounts + totalOldNetDeductions;

  // STEP 3: Counter metal deposit & Net metal left
  const fineGoldDeposited = goldDeposited * (goldDepositTanch / 100);
  const fineSilverDeposited = silverDeposited * (silverDepositTanch / 100);

  const goldValueReceived   = fineGoldDeposited * (activeGoldRate / 10);
  const silverValueReceived = fineSilverDeposited * (activeSilverRate / 1000);

  // Exact physical net metal left after trade-in and counter deposit
  const goldLeftGrams = netGoldRequired - fineGoldDeposited;
  const silverLeftGrams = netSilverRequired - fineSilverDeposited;

  const physicalGoldDue   = Math.max(0, goldLeftGrams);
  const physicalSilverDue = Math.max(0, silverLeftGrams);

  // Monetary value of remaining metal due (in Rupees)
  const goldLeftRupees = physicalGoldDue * (activeGoldRate / 10);
  const silverLeftRupees = physicalSilverDue * (activeSilverRate / 1000);
  const totalMetalRupeesDue = goldLeftRupees + silverLeftRupees;
  const totalMonetaryBeforeCash = totalMetalRupeesDue + nonMetalCharges;
  const cashBalanceDue = totalMonetaryBeforeCash - cashReceived;

  // --- Dynamic Option Calculations based on Cash Received ---

  // OPTION 1: Pay all in cash (No metal to ledgers)
  const opt1CashDue = Math.max(0, totalMonetaryBeforeCash - cashReceived);
  const opt1GoldToLedger = 0;
  const opt1SilverToLedger = 0;

  // OPTION 4: Convert Remaining Metal to Both Ledgers
  // Cash first pays nonMetalCharges (GST, making, expenses).
  // Any remaining cash DIRECTLY reduces the remaining metal due!
  const opt4CashDue = Math.max(0, nonMetalCharges - cashReceived);
  const opt4CashForMetal = Math.max(0, cashReceived - nonMetalCharges);

  // Cash pays off silver first, then gold
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
  // Cash must cover non-metal charges + silver. Any remaining cash reduces Gold!
  const opt2RequiredCash = nonMetalCharges + (isPureSilver ? 0 : silverLeftRupees);
  const opt2CashDue = Math.max(0, opt2RequiredCash - cashReceived);
  const opt2CashForGold = Math.max(0, cashReceived - opt2RequiredCash);
  const opt2GoldRupeesPaid = Math.min(goldLeftRupees, opt2CashForGold);
  const opt2RemainingGoldRupees = Math.max(0, goldLeftRupees - opt2GoldRupeesPaid);
  const opt2GoldToLedger = isPureGold
    ? physicalGoldDue
    : ((activeGoldRate > 0 && opt2RemainingGoldRupees > 0) 
      ? (opt2RemainingGoldRupees / (activeGoldRate / 10)) 
      : 0);
  const opt2SilverToLedger = 0;

  // OPTION 3: Convert to Silver Ledger (Gold & Non-Metal in Cash)
  // Cash must cover non-metal charges + gold. Any remaining cash reduces Silver!
  const opt3RequiredCash = nonMetalCharges + (isPureGold ? 0 : goldLeftRupees);
  const opt3CashDue = Math.max(0, opt3RequiredCash - cashReceived);
  const opt3CashForSilver = Math.max(0, cashReceived - opt3RequiredCash);
  const opt3SilverRupeesPaid = Math.min(silverLeftRupees, opt3CashForSilver);
  const opt3RemainingSilverRupees = Math.max(0, silverLeftRupees - opt3SilverRupeesPaid);
  const opt3SilverToLedger = isPureSilver
    ? physicalSilverDue
    : ((activeSilverRate > 0 && opt3RemainingSilverRupees > 0) 
      ? (opt3RemainingSilverRupees / (activeSilverRate / 1000)) 
      : 0);
  const opt3GoldToLedger = 0;

  // Values based on currently selected action:
  let displayCashDue = opt1CashDue;
  let selectedGoldToLedger = opt1GoldToLedger;
  let selectedSilverToLedger = opt1SilverToLedger;

  if (cashBalanceAction === 'metal_gold') {
    displayCashDue = opt2CashDue;
    selectedGoldToLedger = opt2GoldToLedger;
    selectedSilverToLedger = opt2SilverToLedger;
  } else if (cashBalanceAction === 'metal_silver') {
    displayCashDue = opt3CashDue;
    selectedGoldToLedger = opt3GoldToLedger;
    selectedSilverToLedger = opt3SilverToLedger;
  } else if (cashBalanceAction === 'metal_both') {
    displayCashDue = opt4CashDue;
    selectedGoldToLedger = opt4GoldToLedger;
    selectedSilverToLedger = opt4SilverToLedger;
  }

  // Fully settled if no cash is due and no metal is left to record in ledger
  const isFullySettled = displayCashDue <= 0.01 && selectedGoldToLedger <= 0.001 && selectedSilverToLedger <= 0.001;

  const fmt = (n: number) => n.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

  useEffect(() => {
    axiosClient.get('/customers/').then(res => setCustomers(res.data.items || []));
  }, []);

  const handleGenerate = async (shouldPrint: boolean) => {
    if (!isFullySettled && !selectedCustomer) {
      toast.error('A customer must be selected for outstanding balances.');
      return;
    }
    if (cashReceived < 0 || goldDeposited < 0 || silverDeposited < 0) {
      toast.error('Deposits cannot be negative.');
      return;
    }
    setLoading(true);

    let updatedOldItems = [...(payload.old_items || [])];
    if (goldDeposited > 0) {
      updatedOldItems.push({
        item_name: 'Metal Given Now (Gold)',
        metal: 'Gold',
        purity: `${goldDepositTanch}%`,
        touch: goldDepositTanch,
        gross_weight: goldDeposited,
        stone_weight: 0,
        net_weight: goldDeposited,
        wastage: 0,
        fine_weight: fineGoldDeposited,
        labour_charge: 0,
        testing_melting_charge: 0,
        hallmark_charge: 0,
        other_charges: 0,
        discount: 0,
        rate_applied: isPureMetal ? 0 : activeGoldRate,
        calculated_value: isPureMetal ? 0 : goldValueReceived
      });
    }
    if (silverDeposited > 0) {
      updatedOldItems.push({
        item_name: 'Metal Given Now (Silver)',
        metal: 'Silver',
        purity: `${silverDepositTanch}%`,
        touch: silverDepositTanch,
        gross_weight: silverDeposited,
        stone_weight: 0,
        net_weight: silverDeposited,
        wastage: 0,
        fine_weight: fineSilverDeposited,
        labour_charge: 0,
        testing_melting_charge: 0,
        hallmark_charge: 0,
        other_charges: 0,
        discount: 0,
        rate_applied: isPureMetal ? 0 : activeSilverRate,
        calculated_value: isPureMetal ? 0 : silverValueReceived
      });
    }

    let finalBalanceAmount = isPureMetal && nonMetalCharges === 0 ? 0 : displayCashDue;

    let backendSettlementType = isPureMetal ? (hasGold && hasSilver ? 'Hybrid' : 'Metal') : 'Cash';
    if (cashBalanceAction !== 'cash') {
      if (cashBalanceAction === 'metal_both') backendSettlementType = 'Hybrid';
      else backendSettlementType = 'Metal';
    }

    let goldBalMetal = selectedGoldToLedger > 0.001 
      ? selectedGoldToLedger 
      : (goldLeftGrams < -0.001 ? goldLeftGrams : 0);
    let silverBalMetal = selectedSilverToLedger > 0.001 
      ? selectedSilverToLedger 
      : (silverLeftGrams < -0.001 ? silverLeftGrams : 0);

    const finalPayload = {
      ...payload,
      subtotal: isPureMetal && nonMetalCharges === 0 ? 0 : payload.subtotal,
      total_taxable: isPureMetal && nonMetalCharges === 0 ? 0 : payload.total_taxable,
      tax_amount: isPureMetal && nonMetalCharges === 0 ? 0 : payload.tax_amount,
      gst_amount: isPureMetal && nonMetalCharges === 0 ? 0 : payload.gst_amount,
      grand_total: isPureMetal && nonMetalCharges === 0 ? 0 : payload.grand_total,
      old_items: updatedOldItems, 
      customer_id: selectedCustomer || null,
      amount_paid: isPureMetal && nonMetalCharges === 0 ? 0 : cashReceived, 
      payment_method: paymentMethod,
      settlement_type: backendSettlementType,
      settlement_metal_type: cashBalanceAction === 'metal_gold' ? 'Gold' : cashBalanceAction === 'metal_silver' ? 'Silver' : cashBalanceAction === 'metal_both' ? 'Both' : null,
      balance_amount: finalBalanceAmount,
      gold_balance_metal_weight: goldBalMetal,
      silver_balance_metal_weight: silverBalMetal
    };

    try {
      const res = await axiosClient.post('/exchanges/', finalPayload);
      toast.success(`Exchange ${res.data.exchange_number || res.data.id} generated!`);
      
      if (shouldPrint) {
        try {
          const pdfRes = await axiosClient.get(`/exchanges/${res.data.id}/pdf-data`);
          const pdfData = pdfRes.data;
          pdfData.invoice.amount_paid    = Number(cashReceived) || 0;
          pdfData.invoice.balance_due    = finalBalanceAmount;
          pdfData.invoice.payment_method = paymentMethod;
          pdfData.invoice.transaction_id = paymentMethod === 'UPI' ? upiId : paymentMethod === 'Cheque' ? `${chequeNo} | ${bankName} | ${chequeDate}` : '-';
          pdfData.invoice.bill_type = 'Exchange';
          pdfData.invoice.settlement_type = backendSettlementType;
          pdfData.invoice.settlement_metal_type = cashBalanceAction === 'metal_gold' ? 'Gold' : cashBalanceAction === 'metal_silver' ? 'Silver' : cashBalanceAction === 'metal_both' ? 'Both' : null;
          pdfData.invoice.gold_balance_metal_weight = goldBalMetal;
          pdfData.invoice.silver_balance_metal_weight = silverBalMetal;
          const { generateInvoicePDF } = await import('../../utils/invoicePdfUtils');
          await generateInvoicePDF(pdfData);
        } catch (pdfErr) { console.error('Auto PDF generation failed', pdfErr); }
      }
      
      onSuccess(res.data.id);
    } catch (e: any) {
      toast.error(getErrorMessage(e, 'Failed to generate exchange'));
    } finally { setLoading(false); }
  };

  const handleSaveNewCustomer = async () => {
    if (!newCustomer.first_name || (newCustomer.phone.length !== 10 && newCustomer.phone.length !== 12)) { toast.error('First name and 10 or 12-digit phone number are required'); return; }
    setLoading(true);
    try {
      const res = await axiosClient.post('/customers/', { first_name: newCustomer.first_name, last_name: newCustomer.last_name, phone_number: newCustomer.phone, email: null, address: '', city: newCustomer.city });
      setCustomers([...customers, res.data]); setSelectedCustomer(res.data.id); setMode('checkout'); toast.success('Customer added');
    } catch (e: any) { toast.error(getErrorMessage(e, 'Failed to save customer')); } finally { setLoading(false); }
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
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 sm:gap-3 p-2.5 sm:p-3 bg-gray-900/70 border border-gray-700/60 rounded-xl text-center">
                <div className="p-1">
                  <div className="text-[10px] text-gray-400 uppercase tracking-wider font-medium">New Items Bill</div>
                  <div className="text-sm sm:text-base font-mono text-white font-bold truncate">₹ {fmt(Number(payload.grand_total || (Number(payload.total_new_value || 0) + totalGst)))}</div>
                </div>
                <div className="p-1 border-t sm:border-t-0 sm:border-l border-gray-800">
                  <div className="text-[10px] text-gray-400 uppercase tracking-wider font-medium">Old Items Traded</div>
                  <div className="text-sm sm:text-base font-mono text-red-400 font-bold truncate">− ₹ {fmt(Number(payload.total_old_value || 0))}</div>
                </div>
                <div className="p-1 border-t sm:border-t-0 sm:border-l border-gray-800">
                  <div className="text-[10px] text-yellow-400 uppercase tracking-wider font-bold">Net Difference Due</div>
                  <div className="text-sm sm:text-base font-mono text-yellow-400 font-bold truncate">₹ {fmt(Number(_differenceAmount || payload.difference_amount || 0))}</div>
                </div>
              </div>

              {/* SECTION 1: Metal Received */}
              <div className="border border-gray-700 rounded-lg overflow-hidden">
                <div className="bg-gray-800/50 px-4 py-2 border-b border-gray-700">
                  <h3 className="text-xs font-bold text-gray-300 uppercase tracking-widest">Additional Metal Received at Counter (Optional)</h3>
                </div>
                <div className="p-4 space-y-4">
                  {(payload.old_items || []).length > 0 && (
                    <div className="p-2.5 bg-yellow-900/20 border border-yellow-700/40 rounded text-xs text-yellow-400">
                      <strong>✓ {(payload.old_items || []).length} Old Item(s) already added from Cart.</strong>
                      <div className="text-[11px] text-gray-400 mt-0.5">Enter below ONLY if customer is handing over additional metal directly at checkout.</div>
                    </div>
                  )}
                  {hasGold && (
                    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2">
                      <div>
                        <label className="block text-[9px] text-yellow-500 uppercase tracking-widest mb-1 font-bold">
                          Net Gold Due {conversionGoldRate > 0 ? `@ ₹${conversionGoldRate}/10g` : '(Pure Metal)'}
                        </label>
                        <div className="text-sm font-mono text-yellow-400 font-bold">{netGoldRequired.toFixed(3)} g</div>
                        {tgOld > 0 && <div className="text-[9px] text-gray-400 font-mono">New {tgNew.toFixed(3)}g − Old {tgOld.toFixed(3)}g</div>}
                      </div>
                      <div>
                        <label className="block text-[9px] text-gray-500 uppercase tracking-widest mb-1">Gross Given</label>
                        <input type="number" min="0" step="0.001" value={goldDeposited === 0 ? '' : goldDeposited} onChange={e => setGoldDeposited(Number(e.target.value))} placeholder="0.000" className="w-full bg-background border border-gray-700 rounded px-1 py-1 text-sm font-mono text-yellow-400 outline-none focus:border-yellow-500" />
                      </div>
                      <div>
                        <label className="block text-[9px] text-gray-500 uppercase tracking-widest mb-1">Tanch %</label>
                        <input type="number" min="0" max="100" step="0.01" value={goldDepositTanch} onChange={e => setGoldDepositTanch(Number(e.target.value))} className="w-full bg-background border border-gray-700 rounded px-1 py-1 text-sm font-mono text-yellow-400 outline-none focus:border-yellow-500" />
                      </div>
                      <div>
                        <label className="block text-[9px] text-gray-500 uppercase tracking-widest mb-1">Fine Metal</label>
                        <div className="text-sm font-mono text-yellow-400">{fineGoldDeposited.toFixed(3)} g</div>
                        {fineGoldDeposited > 0 && <div className="text-[9.5px] text-gray-400 font-mono">₹ {fmt(goldValueReceived)}</div>}
                      </div>
                      <div>
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
                        <div className="text-sm font-mono text-gray-200 font-bold">{netSilverRequired.toFixed(3)} g</div>
                        {tsOld > 0 && <div className="text-[9px] text-gray-400 font-mono">New {tsNew.toFixed(3)}g − Old {tsOld.toFixed(3)}g</div>}
                      </div>
                      <div>
                        <label className="block text-[9px] text-gray-500 uppercase tracking-widest mb-1">Gross Given</label>
                        <input type="number" min="0" step="0.001" value={silverDeposited === 0 ? '' : silverDeposited} onChange={e => setSilverDeposited(Number(e.target.value))} placeholder="0.000" className="w-full bg-background border border-gray-700 rounded px-1 py-1 text-sm font-mono text-gray-300 outline-none focus:border-gray-400" />
                      </div>
                      <div>
                        <label className="block text-[9px] text-gray-500 uppercase tracking-widest mb-1">Tanch %</label>
                        <input type="number" min="0" max="100" step="0.01" value={silverDepositTanch} onChange={e => setSilverDepositTanch(Number(e.target.value))} className="w-full bg-background border border-gray-700 rounded px-1 py-1 text-sm font-mono text-gray-300 outline-none focus:border-gray-400" />
                      </div>
                      <div>
                        <label className="block text-[9px] text-gray-500 uppercase tracking-widest mb-1">Fine Metal</label>
                        <div className="text-sm font-mono text-gray-300">{fineSilverDeposited.toFixed(3)} g</div>
                        {fineSilverDeposited > 0 && <div className="text-[9.5px] text-gray-400 font-mono">₹ {fmt(silverValueReceived)}</div>}
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
                        <div className="text-xl sm:text-2xl font-mono text-yellow-400 font-bold truncate">
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
                          <span>Non-Metal Charges (GST + Making):</span>
                          <span className="font-mono font-bold">₹ {fmt(nonMetalCharges)}</span>
                        </div>
                        <div className="flex justify-between text-[10px] text-gray-400 pl-2">
                          <span>• Making Charges:</span>
                          <span className="font-mono">₹ {fmt(totalMakingCharges)}</span>
                        </div>
                        {totalOtherCharges > 0 && (
                          <div className="flex justify-between text-[10px] text-gray-400 pl-2">
                            <span>• Other Charges:</span>
                            <span className="font-mono">₹ {fmt(totalOtherCharges)}</span>
                          </div>
                        )}
                        <div className="flex justify-between text-[10px] text-gray-400 pl-2">
                          <span>• GST ({payload.gst_amount ? '3%' : '0%'}):</span>
                          <span className="font-mono">₹ {fmt(totalGst)}</span>
                        </div>
                        <div className="text-[9.5px] text-yellow-500/80 pt-0.5 font-medium italic">
                          * Must be paid in money / cash (cannot convert to metal).
                        </div>
                      </div>
                    </div>

                    <div>
                      <div className="flex justify-between items-center mb-1">
                        <label className="text-[10px] text-green-400 font-bold uppercase tracking-widest">Cash Received</label>
                        <div className="flex gap-1.5">
                          <button 
                            type="button"
                            onClick={() => setCashReceived(Math.round(nonMetalCharges * 100) / 100)}
                            className="px-1.5 py-0.5 bg-yellow-900/40 hover:bg-yellow-900/70 text-yellow-400 border border-yellow-700/60 rounded text-[9px] font-mono cursor-pointer transition-colors"
                            title="Auto-fill GST & Non-metal charges"
                          >
                            GST (₹{fmt(nonMetalCharges)})
                          </button>
                          <button 
                            type="button"
                            onClick={() => setCashReceived(Math.round(totalMonetaryBeforeCash * 100) / 100)}
                            className="px-1.5 py-0.5 bg-green-900/40 hover:bg-green-900/70 text-green-400 border border-green-700/60 rounded text-[9px] font-mono cursor-pointer transition-colors"
                            title="Auto-fill full cash payment"
                          >
                            Full (₹{fmt(totalMonetaryBeforeCash)})
                          </button>
                        </div>
                      </div>
                      <input type="number" min="0" value={cashReceived === 0 ? '' : cashReceived} onChange={e => setCashReceived(Number(e.target.value))} placeholder="0" className="w-full bg-background border border-green-900 rounded p-2 text-lg font-mono text-green-400 outline-none focus:border-green-500" />
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
                    <span>Non-Metal Charges (GST + Making + Expense):</span>
                    <span className="font-mono font-bold text-white">₹ {fmt(nonMetalCharges)}</span>
                  </div>
                  {cashReceived > 0 && (
                    <div className="flex justify-between items-center text-xs text-green-400">
                      <span>Cash Paid Now:</span>
                      <span className="font-mono font-bold text-green-400">− ₹ {fmt(cashReceived)}</span>
                    </div>
                  )}
                  {(hasGold || hasSilver) && <div className="border-t border-gray-700 my-1" />}
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-gray-400">{displayCashDue > 0 ? 'Amount Payable / Cash Due:' : displayCashDue < 0 ? 'Refund to Customer:' : 'Amount Payable:'}</span>
                    <span className={`font-mono font-bold text-base ${displayCashDue > 0 ? 'text-red-400' : 'text-green-400'}`}>
                      {displayCashDue < 0 ? '(Refund) ' : ''}₹ {fmt(Math.abs(displayCashDue))}{displayCashDue === 0 && ' ✓ (Paid)'}
                    </span>
                  </div>
                  {displayCashDue < 0 && <div className="text-[10px] text-green-500">Customer overpaid. Please return ₹ {fmt(Math.abs(displayCashDue))}.</div>}
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
                            {cashReceived > 0 ? ` (₹${fmt(totalMonetaryBeforeCash)} total − ₹${fmt(cashReceived)} cash paid)` : ` (includes ₹${fmt(totalMetalRupeesDue)} metal + ₹${fmt(nonMetalCharges)} GST)`}
                          </span>
                        </span>
                      </label>

                      {/* OPTION 2: GOLD LEDGER */}
                      {physicalGoldDue > 0 && !hasSilver && (
                        <label className={`flex items-center gap-2 p-2 rounded border cursor-pointer ${cashBalanceAction === 'metal_gold' ? 'border-yellow-500/50 bg-yellow-500/10' : 'border-gray-700 hover:border-gray-600'}`}>
                          <input type="radio" checked={cashBalanceAction === 'metal_gold'} onChange={() => setCashBalanceAction('metal_gold')} className="accent-yellow-500" />
                          <span className="text-xs text-white font-medium flex flex-col">
                            <span>Convert Metal to Gold Ledger</span>
                            <span className="text-[10px] text-gray-300">
                              <strong className={opt2GoldToLedger > 0.001 ? 'text-yellow-400' : 'text-green-400'}>+{opt2GoldToLedger.toFixed(3)} g Gold</strong> to Ledger | 
                              <strong className={opt2CashDue > 0 ? 'text-red-400' : 'text-green-400'}> ₹ {fmt(opt2CashDue)} Cash Due</strong>
                              {opt2GoldRupeesPaid > 0 && <span className="text-gray-400"> (₹{fmt(opt2GoldRupeesPaid)} cash applied to reduce Gold)</span>}
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
                              <strong className={opt3SilverToLedger > 0.001 ? 'text-gray-200' : 'text-green-400'}>+{opt3SilverToLedger.toFixed(3)} g Silver</strong> to Ledger | 
                              <strong className={opt3CashDue > 0 ? 'text-red-400' : 'text-green-400'}> ₹ {fmt(opt3CashDue)} Cash Due</strong>
                              {opt3SilverRupeesPaid > 0 && <span className="text-gray-400"> (₹{fmt(opt3SilverRupeesPaid)} cash applied to reduce Silver)</span>}
                            </span>
                          </span>
                        </label>
                      )}

                      {/* OPTIONS FOR BOTH METALS */}
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

                          {physicalGoldDue > 0 && (
                            <label className={`flex items-center gap-2 p-2 rounded border cursor-pointer ${cashBalanceAction === 'metal_gold' ? 'border-yellow-500/50 bg-yellow-500/10' : 'border-gray-700 hover:border-gray-600'}`}>
                              <input type="radio" checked={cashBalanceAction === 'metal_gold'} onChange={() => setCashBalanceAction('metal_gold')} className="accent-yellow-500" />
                              <span className="text-xs text-white font-medium flex flex-col">
                                <span>Convert Metal to Gold Ledger Only</span>
                                <span className="text-[10px] text-gray-300">
                                  <strong className={opt2GoldToLedger > 0.001 ? 'text-yellow-400' : 'text-green-400'}>+{opt2GoldToLedger.toFixed(3)} g Gold</strong> to Ledger | 
                                  <strong className={opt2CashDue > 0 ? 'text-red-400' : 'text-green-400'}> ₹ {fmt(opt2CashDue)} Cash Due</strong>
                                  {!isPureMetal && (
                                    <span className="text-gray-400">
                                      {cashReceived > 0 ? ` (Silver & GST: ₹${fmt(opt2RequiredCash)}${opt2GoldRupeesPaid > 0 ? `; ₹${fmt(opt2GoldRupeesPaid)} cash applied to Gold` : ''})` : ` (GST ₹${fmt(nonMetalCharges)} + Silver ₹${fmt(silverLeftRupees)})`}
                                    </span>
                                  )}
                                </span>
                              </span>
                            </label>
                          )}

                          {physicalSilverDue > 0 && (
                            <label className={`flex items-center gap-2 p-2 rounded border cursor-pointer ${cashBalanceAction === 'metal_silver' ? 'border-yellow-500/50 bg-yellow-500/10' : 'border-gray-700 hover:border-gray-600'}`}>
                              <input type="radio" checked={cashBalanceAction === 'metal_silver'} onChange={() => setCashBalanceAction('metal_silver')} className="accent-yellow-500" />
                              <span className="text-xs text-white font-medium flex flex-col">
                                <span>Convert Metal to Silver Ledger Only</span>
                                <span className="text-[10px] text-gray-300">
                                  <strong className={opt3SilverToLedger > 0.001 ? 'text-gray-200' : 'text-green-400'}>+{opt3SilverToLedger.toFixed(3)} g Silver</strong> to Ledger | 
                                  <strong className={opt3CashDue > 0 ? 'text-red-400' : 'text-green-400'}> ₹ {fmt(opt3CashDue)} Cash Due</strong>
                                  {!isPureMetal && (
                                    <span className="text-gray-400">
                                      {cashReceived > 0 ? ` (Gold & GST: ₹${fmt(opt3RequiredCash)}${opt3SilverRupeesPaid > 0 ? `; ₹${fmt(opt3SilverRupeesPaid)} cash applied to Silver` : ''})` : ` (GST ₹${fmt(nonMetalCharges)} + Gold ₹${fmt(goldLeftRupees)})`}
                                    </span>
                                  )}
                                </span>
                              </span>
                            </label>
                          )}
                        </>
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* SECTION 3: Customer */}
              <div className="border-t border-gray-800 pt-4">
                <div className="flex justify-between items-end mb-2">
                  <label className="block text-xs font-bold text-gray-500 uppercase tracking-widest">Select Customer</label>
                  <button onClick={() => setMode('new_customer')} className="text-[10px] bg-primary/20 text-primary px-2 py-1 rounded flex items-center gap-1 hover:bg-primary/30 transition-colors"><UserPlus size={12} /> New</button>
                </div>
                <select className="w-full bg-background border border-gray-700 rounded p-3 text-white outline-none focus:border-primary transition-colors" value={selectedCustomer} onChange={e => setSelectedCustomer(Number(e.target.value))}>
                  <option value="">-- Walk-in Customer --</option>
                  {customers.map(c => <option key={c.id} value={c.id}>{c.first_name} {c.last_name || ''} ({c.phone_number})</option>)}
                </select>
                {!isFullySettled && !selectedCustomer && <p className="text-red-400 text-[10px] mt-1">* A customer must be selected for outstanding balances.</p>}
              </div>

              <div className="flex flex-col sm:flex-row gap-2 mt-4 pt-3 border-t border-gray-800 bg-surface sticky bottom-0 z-10 shrink-0">
                <button onClick={onClose} className="py-2.5 sm:py-3 px-4 border border-gray-700 rounded-lg text-gray-400 hover:bg-gray-800 font-bold transition-colors order-3 sm:order-1 sm:flex-1 text-xs sm:text-sm">Cancel</button>
                <button onClick={() => handleGenerate(false)} disabled={loading || (!isFullySettled && !selectedCustomer)} className="py-2.5 sm:py-3 px-4 bg-gray-700 text-white font-bold rounded-lg hover:bg-gray-600 disabled:opacity-50 transition-all order-2 sm:order-2 sm:flex-1 text-xs sm:text-sm">
                  {loading ? 'Saving...' : 'SAVE ONLY'}
                </button>
                <button onClick={() => handleGenerate(true)} disabled={loading || (!isFullySettled && !selectedCustomer)} className="py-2.5 sm:py-3 px-4 bg-primary text-black font-black rounded-lg hover:bg-primary-dark disabled:opacity-50 flex justify-center items-center shadow-[0_0_15px_rgba(212,175,55,0.3)] transition-all order-1 sm:order-3 sm:flex-1 text-xs sm:text-sm">
                  {loading ? 'Processing...' : <><Check size={18} className="mr-2" /> SAVE &amp; PRINT</>}
                </button>
              </div>
            </div>
          )}

          {mode === 'new_customer' && (
            <div className="space-y-4">
              <h3 className="font-bold text-white mb-4 border-b border-gray-800 pb-2">Add New Customer</h3>
              <div>
                <label className="block text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-1">First Name *</label>
                <input placeholder="First Name" className="w-full bg-background border border-gray-700 rounded p-2 text-white outline-none focus:border-primary" value={newCustomer.first_name} onChange={e => setNewCustomer({ ...newCustomer, first_name: e.target.value })} />
              </div>
              <div>
                <label className="block text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-1">Phone Number *</label>
                <input placeholder="Phone Number" className="w-full bg-background border border-gray-700 rounded p-2 text-white outline-none focus:border-primary" value={newCustomer.phone} onChange={e => setNewCustomer({ ...newCustomer, phone: e.target.value })} />
              </div>
              <div className="flex space-x-3 mt-6">
                <button onClick={() => setMode('checkout')} className="flex-1 py-2 border border-gray-700 rounded text-gray-400 hover:bg-gray-800">Cancel</button>
                <button onClick={handleSaveNewCustomer} disabled={loading} className="flex-1 py-2 bg-primary text-black font-bold rounded hover:bg-primary/90">{loading ? 'Saving...' : 'Save Customer'}</button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
