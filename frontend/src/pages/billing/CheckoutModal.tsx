import { useState, useEffect, useMemo } from 'react';
import { axiosClient } from '../../api/axiosClient';
import toast from 'react-hot-toast';
import { Check, X, Calculator, UserPlus } from 'lucide-react';
import { useBillingStore } from '../../store/billingStore';
import { getErrorMessage } from '../../utils/errorUtils';

interface CheckoutModalProps {
  payload: any;
  grandTotal: number;
  onClose: () => void;
  onSuccess: (invoiceId: number) => void;
}

export default function CheckoutModal({ payload, grandTotal, onClose, onSuccess }: CheckoutModalProps) {
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

  const [paymentMethod, setPaymentMethod] = useState<'Cash' | 'Card' | 'UPI' | 'Cheque'>('Cash');
  const [upiId, setUpiId] = useState('');
  const [cardRef, setCardRef] = useState('');
  const [chequeNo, setChequeNo] = useState('');
  const [bankName, setBankName] = useState('');
  const [chequeDate, setChequeDate] = useState('');

  // STEP 1: Extract from payload
  const { totalGoldBilled, totalSilverBilled, goldRate, silverRate, hasGold, hasSilver } = useMemo(() => {
    let tg = 0, ts = 0, gr = 0, sr = 0;
    (payload.items || []).forEach((item: any) => {
      if (item.item_type === 'Gold') {
        const fw = Number(item.gold_calculation?.fine_weight || item.fine_weight || item.pure_weight || (item.net_weight && item.touch_purity ? (item.net_weight * item.touch_purity / 100) : item.net_weight) || 0);
        tg += fw;
        if (!gr) gr = item.gold_calculation?.applied_rate || 0;
      } else if (item.item_type === 'Silver') {
        const fw = Number(item.silver_calculation?.pure_weight || item.silver_calculation?.fine_weight || item.fine_weight || item.pure_weight || (item.net_weight && item.tanch_percentage ? (item.net_weight * item.tanch_percentage / 100) : item.net_weight) || 0);
        ts += fw;
        if (!sr) sr = item.silver_calculation?.applied_rate || 0;
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

  const isPureGold = hasGold && (goldRate === 0 || (payload.items || []).filter((i: any) => i.item_type === 'Gold').every((i: any) => (i.gold_calculation?.applied_rate || 0) === 0));
  const isPureSilver = hasSilver && (silverRate === 0 || (payload.items || []).filter((i: any) => i.item_type === 'Silver').every((i: any) => (i.silver_calculation?.applied_rate || 0) === 0));
  const isPureMetal = (hasGold ? isPureGold : true) && (hasSilver ? isPureSilver : true) && (hasGold || hasSilver);

  // cash | metal_gold | metal_silver | metal_both
  const [cashBalanceAction, setCashBalanceAction] = useState<'cash' | 'metal_gold' | 'metal_silver' | 'metal_both'>(() => {
    if (hasGold && hasSilver && (isPureGold || isPureSilver)) return 'metal_both';
    if (hasGold && isPureGold) return 'metal_gold';
    if (hasSilver && isPureSilver) return 'metal_silver';
    return 'cash';
  });

  // Metal type to receive at counter: 'gold' | 'silver' | 'both'
  const [receiveMetalType, setReceiveMetalType] = useState<'gold' | 'silver' | 'both'>(
    (hasGold && hasSilver) ? 'both' : (hasSilver && !hasGold) ? 'silver' : 'gold'
  );

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

  // STEP 2: Non-metal charges (Labour/Making, Expenses/Hallmark, and GST)
  const totalMakingCharges = useMemo(() => {
    return (payload.items || []).reduce((acc: number, item: any) => {
      const gMaking = item.gold_calculation?.making_charges_amount || 0;
      const sMaking = item.silver_calculation?.making_charges_amount || 0;
      return acc + Number(gMaking) + Number(sMaking);
    }, 0);
  }, [payload.items]);

  const totalOtherCharges = useMemo(() => {
    return (payload.items || []).reduce((acc: number, item: any) => {
      const gHallmark = item.gold_calculation?.hallmark_charges || 0;
      const gOther = item.gold_calculation?.other_charges || 0;
      const sOther = item.silver_calculation?.other_charges || 0;
      return acc + Number(gHallmark) + Number(gOther) + Number(sOther);
    }, 0);
  }, [payload.items]);

  const totalItemDiscounts = useMemo(() => {
    return (payload.items || []).reduce((acc: number, item: any) => {
      const gDisc = item.gold_calculation?.discount || 0;
      const sDisc = item.silver_calculation?.discount || 0;
      return acc + Number(gDisc) + Number(sDisc);
    }, 0);
  }, [payload.items]);

  const globalDiscount = Number(payload.discount_amount || 0);
  const totalDiscounts = totalItemDiscounts + globalDiscount;
  const totalGst = Number(payload.tax_amount || 0);
  const rawExpectedGrandTotal = Number(payload.subtotal || 0) - globalDiscount + totalGst;
  const billRoundOff = isPureMetal ? 0 : (Number(payload.grand_total ?? grandTotal ?? 0) - rawExpectedGrandTotal);
  const nonMetalCharges = totalMakingCharges + totalOtherCharges + totalGst - totalDiscounts + billRoundOff;

  // STEP 3: Counter metal deposit & Net metal left
  const fineGoldDeposited = goldDeposited * (goldDepositTanch / 100);
  const fineSilverDeposited = silverDeposited * (silverDepositTanch / 100);

  const goldValueReceived = fineGoldDeposited * (activeGoldRate / 10);
  const silverValueReceived = fineSilverDeposited * (activeSilverRate / 1000);
  const totalMetalValueReceived = goldValueReceived + silverValueReceived;

  const goldLeftGrams = totalGoldBilled - fineGoldDeposited;
  const silverLeftGrams = totalSilverBilled - fineSilverDeposited;

  const physicalGoldDue = Math.max(0, goldLeftGrams);
  const physicalSilverDue = Math.max(0, silverLeftGrams);

  const goldLeftRupees = physicalGoldDue * (activeGoldRate / 10);
  const silverLeftRupees = physicalSilverDue * (activeSilverRate / 1000);
  const totalMetalRupeesDue = goldLeftRupees + silverLeftRupees;
  const totalMonetaryBeforeCash = Math.max(0, totalMetalRupeesDue + nonMetalCharges);
  const cashBalanceDue = totalMonetaryBeforeCash - cashReceived;

  // --- Dynamic Option Calculations based on Cash Received ---

  // OPTION 1: Pay all in cash (No metal to ledgers)
  const opt1CashDue = Math.max(0, totalMonetaryBeforeCash - cashReceived);
  const opt1GoldToLedger = 0;
  const opt1SilverToLedger = 0;

  // OPTION 4: Convert Remaining Metal to Both Ledgers
  const opt4CashDue = Math.max(0, nonMetalCharges - cashReceived);
  const opt4CashForMetal = Math.max(0, cashReceived - nonMetalCharges);

  const opt4SilverRupeesPaid = Math.min(silverLeftRupees, opt4CashForMetal);
  const opt4RemainingCashForGold = opt4CashForMetal - opt4SilverRupeesPaid;
  const opt4GoldRupeesPaid = Math.min(goldLeftRupees, opt4RemainingCashForGold);

  const opt4RemainingSilverRupees = Math.max(0, silverLeftRupees - opt4SilverRupeesPaid);
  const opt4RemainingGoldRupees = Math.max(0, goldLeftRupees - opt4GoldRupeesPaid);

  const opt4SilverToLedger = isPureSilver
    ? Math.max(0, silverLeftGrams)
    : ((activeSilverRate > 0 && opt4RemainingSilverRupees > 0)
        ? (opt4RemainingSilverRupees / (activeSilverRate / 1000))
        : 0);
  const opt4GoldToLedger = isPureGold
    ? Math.max(0, goldLeftGrams)
    : ((activeGoldRate > 0 && opt4RemainingGoldRupees > 0)
        ? (opt4RemainingGoldRupees / (activeGoldRate / 10))
        : 0);

  // OPTION 2: Convert to Gold Ledger (Silver & Non-Metal in Cash)
  const opt2RequiredCash = nonMetalCharges + silverLeftRupees;
  const opt2CashDue = Math.max(0, opt2RequiredCash - cashReceived);
  const opt2CashForGold = Math.max(0, cashReceived - opt2RequiredCash);
  const opt2GoldRupeesPaid = Math.min(goldLeftRupees, opt2CashForGold);
  const opt2RemainingGoldRupees = Math.max(0, goldLeftRupees - opt2GoldRupeesPaid);
  const opt2GoldToLedger = isPureGold
    ? Math.max(0, goldLeftGrams)
    : ((activeGoldRate > 0 && opt2RemainingGoldRupees > 0)
        ? (opt2RemainingGoldRupees / (activeGoldRate / 10))
        : 0);
  const opt2SilverToLedger = 0;

  // OPTION 3: Convert to Silver Ledger (Gold & Non-Metal in Cash)
  const opt3RequiredCash = nonMetalCharges + goldLeftRupees;
  const opt3CashDue = Math.max(0, opt3RequiredCash - cashReceived);
  const opt3CashForSilver = Math.max(0, cashReceived - opt3RequiredCash);
  const opt3SilverRupeesPaid = Math.min(silverLeftRupees, opt3CashForSilver);
  const opt3RemainingSilverRupees = Math.max(0, silverLeftRupees - opt3SilverRupeesPaid);
  const opt3SilverToLedger = isPureSilver
    ? Math.max(0, silverLeftGrams)
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

    let updatedItems = [...(payload.items || [])];
    if (goldDeposited > 0) {
      updatedItems.push({
        item_name: 'Gold Deposit', item_type: 'Gold', final_price: 0,
        gold_calculation: {
          applied_rate: isPureMetal ? 0 : activeGoldRate, gross_weight: goldDeposited, net_weight: goldDeposited,
          stone_weight: 0, touch_purity: goldDepositTanch, wastage: 0, fine_weight: fineGoldDeposited,
          making_charge_type: 'flat', making_charge_rate: 0, making_charges_amount: 0,
          hallmark_charges: 0, other_charges: 0, discount: 0, total_gold_value: isPureMetal ? 0 : goldValueReceived,
        }
      });
    }
    if (silverDeposited > 0) {
      updatedItems.push({
        item_name: 'Silver Deposit', item_type: 'Silver', final_price: 0,
        silver_calculation: {
          applied_rate: isPureMetal ? 0 : activeSilverRate, gross_weight: silverDeposited, net_weight: silverDeposited,
          stone_weight: 0, tanch_percentage: silverDepositTanch, wastage: 0, pure_weight: fineSilverDeposited,
          making_charge_type: 'flat', making_charge_rate: 0, making_charges_amount: 0,
          other_charges: 0, discount: 0, total_silver_value: isPureMetal ? 0 : silverValueReceived,
        }
      });
    }

    const backendSettlementType = isPureMetal ? 'Metal' : (cashBalanceAction !== 'cash' ? 'Metal' : 'Cash');
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

    let recStrParts = [];
    if (fineGoldDeposited > 0) recStrParts.push(`${fineGoldDeposited.toFixed(3)}g Gold`);
    if (fineSilverDeposited > 0) recStrParts.push(`${fineSilverDeposited.toFixed(3)}g Silver`);
    const metalRecStr = recStrParts.join(' | ');

    const idempotencyKey = `chk_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
    const finalPayload = {
      ...payload,
      subtotal: isPureMetal ? 0 : payload.subtotal,
      tax_amount: isPureMetal ? 0 : payload.tax_amount,
      discount_amount: isPureMetal ? 0 : payload.discount_amount,
      grand_total: isPureMetal ? 0 : payload.grand_total,
      items: updatedItems,
      customer_id: selectedCustomer || null,
      status: isFullySettled ? 'Paid' : 'Completed',
      amount_paid: isPureMetal ? 0 : cashReceived,
      payment_method: isPureMetal ? 'Cash' : paymentMethod,
      payment_details: paymentMethod === 'UPI' ? { upi_id: upiId } : paymentMethod === 'Card' ? { card_ref: cardRef } : paymentMethod === 'Cheque' ? { cheque_no: chequeNo, bank_name: bankName, cheque_date: chequeDate } : null,
      bill_type: backendBillType,
      settlement_type: backendSettlementType,
      settlement_metal_type: cashBalanceAction === 'metal_gold' ? 'Gold' : cashBalanceAction === 'metal_silver' ? 'Silver' : cashBalanceAction === 'metal_both' ? 'Both' : null,
      metal_received_value: isPureMetal ? 0 : totalMetalValueReceived,
      metal_received_str: metalRecStr,
      cash_received: isPureMetal ? 0 : cashReceived,
      balance_amount: finalBalanceAmount,
      balance_metal_weight: 0,
      gold_balance_metal_weight: goldBalMetal,
      silver_balance_metal_weight: silverBalMetal,
      idempotency_key: idempotencyKey,
    };

    try {
      const res = await axiosClient.post('/invoices/', finalPayload, {
        headers: { 'Idempotency-Key': idempotencyKey }
      });
      toast.success(`Invoice ${res.data.invoice_number} generated!`);
      
      if (shouldPrint) {
        try {
          const pdfRes = await axiosClient.get(`/invoices/${res.data.id}/pdf-data`);
          const pdfData = pdfRes.data;
          pdfData.invoice.amount_paid    = cashReceived;
          pdfData.invoice.balance_due    = finalBalanceAmount;
          pdfData.invoice.payment_method = paymentMethod;
          pdfData.invoice.transaction_id = paymentMethod === 'UPI' ? upiId : paymentMethod === 'Card' ? cardRef : paymentMethod === 'Cheque' ? `${chequeNo} | ${bankName} | ${chequeDate}` : '-';
          pdfData.invoice.bill_type = backendBillType;
          pdfData.invoice.settlement_type = backendSettlementType;
          pdfData.invoice.settlement_metal_type = cashBalanceAction === 'metal_gold' ? 'Gold' : cashBalanceAction === 'metal_silver' ? 'Silver' : cashBalanceAction === 'metal_both' ? 'Both' : null;
          pdfData.invoice.gold_balance_metal_weight = goldBalMetal;
          pdfData.invoice.silver_balance_metal_weight = silverBalMetal;
          const { printInvoiceDirect } = await import('../../utils/invoicePdfUtils');
          await printInvoiceDirect(pdfData);
        } catch (pdfErr) { console.error('Auto print generation failed', pdfErr); }
      }
      
      onSuccess(res.data.id);
    } catch (e: any) {
      toast.error(getErrorMessage(e, 'Failed to generate invoice'));
    } finally { setLoading(false); }
  };

  const handleSaveNewCustomer = async () => {
    if (!newCustomer.first_name || (newCustomer.phone.length !== 10 && newCustomer.phone.length !== 12)) {
      toast.error('First name and 10 or 12-digit phone number are required');
      return;
    }
    setLoading(true);
    try {
      const res = await axiosClient.post('/customers/', {
        first_name: newCustomer.first_name,
        last_name: newCustomer.last_name,
        phone_number: newCustomer.phone,
        email: null,
        address: '',
        city: newCustomer.city
      });
      setCustomers([...customers, res.data]);
      setSelectedCustomer(res.data.id);
      setMode('checkout');
      toast.success('Customer added');
    } catch (e: any) {
      toast.error(getErrorMessage(e, 'Failed to save customer'));
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
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 sm:gap-3 p-2.5 sm:p-3 bg-gray-900/70 border border-gray-700/60 rounded-xl text-center">
                <div className="p-1">
                  <div className="text-[10px] text-gray-400 uppercase tracking-wider font-medium">New Items Bill</div>
                  <div className="text-sm sm:text-base font-mono text-white font-bold truncate">₹ {fmt(grandTotal)}</div>
                </div>
                <div>
                  <div className="text-[10px] text-gray-400 uppercase tracking-wider">Counter Metal Traded</div>
                  <div className="text-base font-mono text-red-400 font-bold">
                    {isPureMetal 
                      ? `${fineGoldDeposited > 0 ? `${fineGoldDeposited.toFixed(3)}g Au ` : ''}${fineSilverDeposited > 0 ? `${fineSilverDeposited.toFixed(3)}g Ag` : ''}${fineGoldDeposited === 0 && fineSilverDeposited === 0 ? '0.000 g' : ''}`
                      : `− ₹ ${fmt(totalMetalValueReceived)}`}
                  </div>
                </div>
                <div>
                  <div className="text-[10px] text-yellow-400 uppercase tracking-wider font-bold">Net Difference Due</div>
                  <div className="text-base font-mono text-yellow-400 font-bold">
                    {isPureMetal
                      ? (totalMonetaryBeforeCash > 0 ? `₹ ${fmt(totalMonetaryBeforeCash)}` : `${goldLeftGrams > 0.001 ? `${goldLeftGrams.toFixed(3)}g Au ` : ''}${silverLeftGrams > 0.001 ? `${silverLeftGrams.toFixed(3)}g Ag` : ''}`.trim() || '0.000 g')
                      : `₹ ${fmt(totalMonetaryBeforeCash)}`}
                  </div>
                </div>
              </div>

              {/* SECTION 1: Metal Received */}
              <div className="border border-gray-700 rounded-lg overflow-hidden">
                <div className="bg-gray-800/50 px-4 py-2 border-b border-gray-700 flex flex-wrap justify-between items-center gap-2">
                  <h3 className="text-xs font-bold text-gray-300 uppercase tracking-widest">Additional Metal Received at Counter (Optional)</h3>
                  <div className="flex items-center gap-1 bg-gray-900 border border-gray-700 rounded p-0.5 text-[10px]">
                    <button 
                      type="button" 
                      onClick={() => setReceiveMetalType('gold')} 
                      className={`px-2 py-0.5 rounded transition-colors ${receiveMetalType === 'gold' ? 'bg-yellow-500 text-black font-bold' : 'text-gray-400 hover:text-white'}`}
                    >
                      Gold
                    </button>
                    <button 
                      type="button" 
                      onClick={() => setReceiveMetalType('silver')} 
                      className={`px-2 py-0.5 rounded transition-colors ${receiveMetalType === 'silver' ? 'bg-gray-300 text-black font-bold' : 'text-gray-400 hover:text-white'}`}
                    >
                      Silver
                    </button>
                    <button 
                      type="button" 
                      onClick={() => setReceiveMetalType('both')} 
                      className={`px-2 py-0.5 rounded transition-colors ${receiveMetalType === 'both' ? 'bg-primary text-black font-bold' : 'text-gray-400 hover:text-white'}`}
                    >
                      Both (Gold + Silver)
                    </button>
                  </div>
                </div>
                <div className="p-4 space-y-4">
                  {(receiveMetalType === 'gold' || receiveMetalType === 'both') && (
                    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2">
                      <div>
                        <label className="block text-[9px] text-yellow-500 uppercase tracking-widest mb-1 font-bold">
                          {activeGoldRate > 0 ? `Total Gold @ ₹${conversionGoldRate}/10g` : 'Total Gold (Pure Metal)'}
                        </label>
                        <div className="text-sm font-mono text-yellow-400 font-bold">{totalGoldBilled.toFixed(3)} g</div>
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
                        <label className="block text-[9px] text-gray-500 uppercase tracking-widest mb-1">Fine Received</label>
                        <div className="text-sm font-mono text-yellow-400">{fineGoldDeposited.toFixed(3)} g</div>
                        {activeGoldRate > 0 && fineGoldDeposited > 0 && <div className="text-[9.5px] text-gray-400 font-mono">₹ {fmt(goldValueReceived)}</div>}
                      </div>
                      <div className="col-span-2 sm:col-span-1">
                        <label className="block text-[9px] text-gray-400 uppercase tracking-widest mb-1 font-bold">Due (Total − Recv)</label>
                        {goldLeftGrams > 0.001 ? (
                          <div className="text-sm font-mono text-red-400 font-bold">+{goldLeftGrams.toFixed(3)} g Due</div>
                        ) : goldLeftGrams < -0.001 ? (
                          <div className="text-sm font-mono text-green-400 font-bold">{Math.abs(goldLeftGrams).toFixed(3)} g Surplus</div>
                        ) : (
                          <div className="text-sm font-mono text-primary font-bold">0.000 g (Settled)</div>
                        )}
                        {activeGoldRate > 0 && goldLeftGrams > 0.001 && <div className="text-[9.5px] text-red-400/80 font-mono">₹ {fmt(goldLeftRupees)}</div>}
                      </div>
                    </div>
                  )}
                  {(receiveMetalType === 'silver' || receiveMetalType === 'both') && (
                    <div className={`grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2 ${(receiveMetalType === 'both' || hasGold) ? 'border-t border-gray-800 pt-4' : ''}`}>
                      <div>
                        <label className="block text-[9px] text-gray-300 uppercase tracking-widest mb-1 font-bold">
                          {activeSilverRate > 0 ? `Total Silver @ ₹${conversionSilverRate}/kg` : 'Total Silver (Pure Metal)'}
                        </label>
                        <div className="text-sm font-mono text-gray-200 font-bold">{totalSilverBilled.toFixed(3)} g</div>
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
                        <label className="block text-[9px] text-gray-500 uppercase tracking-widest mb-1">Fine Received</label>
                        <div className="text-sm font-mono text-gray-300">{fineSilverDeposited.toFixed(3)} g</div>
                        {activeSilverRate > 0 && fineSilverDeposited > 0 && <div className="text-[9.5px] text-gray-400 font-mono">₹ {fmt(silverValueReceived)}</div>}
                      </div>
                      <div className="col-span-2 sm:col-span-1">
                        <label className="block text-[9px] text-gray-400 uppercase tracking-widest mb-1 font-bold">Due (Total − Recv)</label>
                        {silverLeftGrams > 0.001 ? (
                          <div className="text-sm font-mono text-red-400 font-bold">+{silverLeftGrams.toFixed(3)} g Due</div>
                        ) : silverLeftGrams < -0.001 ? (
                          <div className="text-sm font-mono text-green-400 font-bold">{Math.abs(silverLeftGrams).toFixed(3)} g Surplus</div>
                        ) : (
                          <div className="text-sm font-mono text-primary font-bold">0.000 g (Settled)</div>
                        )}
                        {activeSilverRate > 0 && silverLeftGrams > 0.001 && <div className="text-[9.5px] text-red-400/80 font-mono">₹ {fmt(silverLeftRupees)}</div>}
                      </div>
                    </div>
                  )}
                  <div className="border-t border-gray-800 pt-4 grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
                    <div className="space-y-2">
                      <div className="bg-yellow-950/20 border border-yellow-700/40 rounded-lg p-2.5">
                        <label className="block text-[10px] text-yellow-500 font-bold uppercase tracking-widest mb-0.5">
                          {isPureMetal ? 'Total Cash / Non-Metal Payable' : 'Total Amount Payable (If 100% Cash)'}
                        </label>
                        <div className="text-2xl font-mono text-yellow-400 font-bold">
                          ₹ {fmt(totalMonetaryBeforeCash)}
                        </div>
                        <div className="text-[10px] text-gray-400 mt-0.5">
                          {isPureMetal 
                            ? `Pure Metal: ${goldLeftGrams > 0.001 ? `${goldLeftGrams.toFixed(3)}g Gold ` : ''}${silverLeftGrams > 0.001 ? `${silverLeftGrams.toFixed(3)}g Silver ` : ''}+ ₹${fmt(nonMetalCharges)} non-metal`
                            : `Includes ₹${fmt(totalMetalRupeesDue)} metal value + ₹${fmt(nonMetalCharges)} non-metal`}
                        </div>
                      </div>

                      <div className="p-2.5 bg-gray-900/60 border border-gray-700/50 rounded-lg text-[11px] space-y-1">
                        <div className="flex justify-between items-center text-gray-300 font-medium">
                          <span>{isPureMetal ? 'Metal Due (Unpriced / Pure):' : 'Remaining Metal Value:'}</span>
                          <span className="font-mono text-white font-bold">
                            {isPureMetal 
                              ? `${goldLeftGrams > 0.001 ? `${goldLeftGrams.toFixed(3)}g Au ` : ''}${silverLeftGrams > 0.001 ? `${silverLeftGrams.toFixed(3)}g Ag` : ''}${goldLeftGrams <= 0.001 && silverLeftGrams <= 0.001 ? '0.000 g' : ''}`
                              : `₹ ${fmt(totalMetalRupeesDue)}`}
                          </span>
                        </div>
                        {goldLeftGrams > 0.001 && (
                          <div className="flex justify-between text-[10px] text-gray-400 pl-2">
                            <span>• Gold Due:</span>
                            <span className="font-mono">{goldLeftGrams.toFixed(3)}g {activeGoldRate > 0 ? `(₹${fmt(goldLeftRupees)})` : '(Pure Metal)'}</span>
                          </div>
                        )}
                        {silverLeftGrams > 0.001 && (
                          <div className="flex justify-between text-[10px] text-gray-400 pl-2">
                            <span>• Silver Due:</span>
                            <span className="font-mono">{silverLeftGrams.toFixed(3)}g {activeSilverRate > 0 ? `(₹${fmt(silverLeftRupees)})` : '(Pure Metal)'}</span>
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
                          <span>• GST ({payload.tax_amount ? '3%' : '0%'}):</span>
                          <span className="font-mono">₹ {fmt(totalGst)}</span>
                        </div>
                        <div className="text-[9.5px] text-yellow-500/80 pt-0.5 font-medium italic">
                          * Must be paid in money / cash (cannot convert to metal).
                        </div>
                      </div>
                    </div>

                    <div>
                      <div className="flex justify-between items-center mb-1">
                        <label className="text-[10px] text-green-400 font-bold uppercase tracking-widest">Amount / Payment Received</label>
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
                            title="Auto-fill full payment"
                          >
                            Full (₹{fmt(totalMonetaryBeforeCash)})
                          </button>
                        </div>
                      </div>
                      <input type="number" min="0" value={cashReceived === 0 ? '' : cashReceived} onChange={e => setCashReceived(Number(e.target.value))} placeholder="0" className="w-full bg-background border border-green-900 rounded p-2 text-lg font-mono text-green-400 outline-none focus:border-green-500" />
                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mt-2">
                        {(['Cash', 'Card', 'UPI', 'Cheque'] as const).map(m => (
                          <label key={m} className={`flex items-center justify-center gap-1.5 py-1.5 px-2 rounded border cursor-pointer transition-colors ${paymentMethod === m ? 'border-green-500 bg-green-500/10 text-white font-bold' : 'border-gray-700 text-gray-400 hover:border-gray-600'}`}>
                            <input type="radio" checked={paymentMethod === m} onChange={() => setPaymentMethod(m)} className="accent-green-500" />
                            <span className="text-[10px] uppercase">{m === 'Cheque' ? 'Cheque / Bank' : m}</span>
                          </label>
                        ))}
                      </div>
                      {paymentMethod === 'Card' && (
                        <input type="text" placeholder="Card Auth Code / Reference No." value={cardRef} onChange={e => setCardRef(e.target.value)} className="w-full bg-background border border-gray-700 rounded p-1.5 text-xs text-white outline-none mt-2 focus:border-primary" />
                      )}
                      {paymentMethod === 'UPI' && (
                        <input type="text" placeholder="UPI / UTR / Transaction ID" value={upiId} onChange={e => setUpiId(e.target.value)} className="w-full bg-background border border-gray-700 rounded p-1.5 text-xs text-white outline-none mt-2 focus:border-primary" />
                      )}
                      {paymentMethod === 'Cheque' && (
                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-1.5 mt-2">
                          <input type="text" placeholder="Cheque No." value={chequeNo} onChange={e => setChequeNo(e.target.value)} className="w-full bg-background border border-gray-700 rounded p-1.5 text-xs text-white outline-none focus:border-primary" />
                          <input type="text" placeholder="Bank Name" value={bankName} onChange={e => setBankName(e.target.value)} className="w-full bg-background border border-gray-700 rounded p-1.5 text-xs text-white outline-none focus:border-primary" />
                          <input type="date" value={chequeDate} onChange={e => setChequeDate(e.target.value)} className="w-full bg-background border border-gray-700 rounded p-1.5 text-xs text-white outline-none [color-scheme:dark] focus:border-primary" />
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
                          ? `+${selectedGoldToLedger.toFixed(3)} g Due ${activeGoldRate > 0 ? `(₹${fmt(selectedGoldToLedger * (activeGoldRate / 10))})` : '(Pure Metal)'}` 
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
                          ? `+${selectedSilverToLedger.toFixed(3)} g Due ${activeSilverRate > 0 ? `(₹${fmt(selectedSilverToLedger * (activeSilverRate / 1000))})` : '(Pure Metal)'}` 
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

                {(physicalGoldDue > 0 || physicalSilverDue > 0 || cashBalanceDue > 0 || isPureMetal) && (
                  <div className="mt-4">
                    <label className="block text-[10px] text-gray-500 uppercase tracking-widest mb-2">How to settle the remaining balance?</label>
                    <div className="flex flex-col gap-2">
                      {/* GOLD LEDGER OPTION (Single Gold) */}
                      {hasGold && !hasSilver && (
                        <label className={`flex items-center gap-2 p-2 rounded border cursor-pointer ${cashBalanceAction === 'metal_gold' ? 'border-yellow-500/50 bg-yellow-500/10' : 'border-gray-700 hover:border-gray-600'}`}>
                          <input type="radio" checked={cashBalanceAction === 'metal_gold'} onChange={() => setCashBalanceAction('metal_gold')} className="accent-yellow-500" />
                          <span className="text-xs text-white font-medium flex flex-col">
                            <span className="flex items-center gap-2">
                              <span>{goldLeftGrams < -0.001 ? 'Credit Excess Metal as Gold Surplus (Advance)' : 'Convert Metal to Gold Ledger'}</span>
                              {isPureGold && <span className="text-[9px] bg-yellow-500/20 text-yellow-400 px-1.5 py-0.5 rounded font-bold">{goldLeftGrams < -0.001 ? 'Surplus Advance' : 'Pure Metal Recommended'}</span>}
                            </span>
                            <span className="text-[10px] text-yellow-400">
                              {goldLeftGrams < -0.001 ? (
                                <span className="text-green-400 font-bold">-{Math.abs(goldLeftGrams).toFixed(3)} g Gold Surplus (Advance Deposit)</span>
                              ) : (
                                `+${opt2GoldToLedger.toFixed(3)} g Gold to Ledger`
                              )} | <strong className={opt2CashDue > 0 ? 'text-red-400' : 'text-green-400'}>₹ {fmt(opt2CashDue)} Cash Due</strong> {opt2CashDue > 0 ? `(GST & non-metal: ₹${fmt(nonMetalCharges)})` : '(No money flow)'}
                            </span>
                          </span>
                        </label>
                      )}

                      {/* SILVER LEDGER OPTION (Single Silver) */}
                      {hasSilver && !hasGold && (
                        <label className={`flex items-center gap-2 p-2 rounded border cursor-pointer ${cashBalanceAction === 'metal_silver' ? 'border-yellow-500/50 bg-yellow-500/10' : 'border-gray-700 hover:border-gray-600'}`}>
                          <input type="radio" checked={cashBalanceAction === 'metal_silver'} onChange={() => setCashBalanceAction('metal_silver')} className="accent-yellow-500" />
                          <span className="text-xs text-white font-medium flex flex-col">
                            <span className="flex items-center gap-2">
                              <span>{silverLeftGrams < -0.001 ? 'Credit Excess Metal as Silver Surplus (Advance)' : 'Convert Metal to Silver Ledger'}</span>
                              {isPureSilver && <span className="text-[9px] bg-gray-400/20 text-gray-300 px-1.5 py-0.5 rounded font-bold">{silverLeftGrams < -0.001 ? 'Surplus Advance' : 'Pure Metal Recommended'}</span>}
                            </span>
                            <span className="text-[10px] text-gray-300">
                              {silverLeftGrams < -0.001 ? (
                                <span className="text-green-400 font-bold">-{Math.abs(silverLeftGrams).toFixed(3)} g Silver Surplus (Advance Deposit)</span>
                              ) : (
                                `+${opt3SilverToLedger.toFixed(3)} g Silver to Ledger`
                              )} | <strong className={opt3CashDue > 0 ? 'text-red-400' : 'text-green-400'}>₹ {fmt(opt3CashDue)} Cash Due</strong> {opt3CashDue > 0 ? `(GST & non-metal: ₹${fmt(nonMetalCharges)})` : '(No money flow)'}
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
                                <span>Convert Both Metals to Ledgers</span>
                                {isPureMetal && <span className="text-[9px] bg-primary/20 text-primary px-1.5 py-0.5 rounded font-bold">Both Metals Due</span>}
                              </span>
                              <span className="text-[10px] text-yellow-400">
                                Gold: {goldLeftGrams < -0.001 ? <strong className="text-green-400">-{Math.abs(goldLeftGrams).toFixed(3)} g Surplus</strong> : <strong>+{opt4GoldToLedger.toFixed(3)} g</strong>} | Silver: {silverLeftGrams < -0.001 ? <strong className="text-green-400">-{Math.abs(silverLeftGrams).toFixed(3)} g Surplus</strong> : <strong>+{opt4SilverToLedger.toFixed(3)} g</strong>} | <strong className={opt4CashDue > 0 ? 'text-red-400' : 'text-green-400'}>₹ {fmt(opt4CashDue)} Cash Due</strong> {opt4CashDue === 0 ? '(No money flow)' : ''}
                              </span>
                            </span>
                          </label>

                          <label className={`flex items-center gap-2 p-2 rounded border cursor-pointer ${cashBalanceAction === 'metal_gold' ? 'border-yellow-500/50 bg-yellow-500/10' : 'border-gray-700 hover:border-gray-600'}`}>
                            <input type="radio" checked={cashBalanceAction === 'metal_gold'} onChange={() => setCashBalanceAction('metal_gold')} className="accent-yellow-500" />
                            <span className="text-xs text-white font-medium flex flex-col">
                              <span>Convert Metal to Gold Ledger Only</span>
                              <span className="text-[10px] text-yellow-400">
                                {goldLeftGrams < -0.001 ? <strong className="text-green-400">-{Math.abs(goldLeftGrams).toFixed(3)} g Gold Surplus</strong> : `+${opt2GoldToLedger.toFixed(3)} g Gold`} | <strong className={opt2CashDue > 0 ? 'text-red-400' : 'text-green-400'}>₹ {fmt(opt2CashDue)} Cash Due</strong>
                              </span>
                            </span>
                          </label>

                          <label className={`flex items-center gap-2 p-2 rounded border cursor-pointer ${cashBalanceAction === 'metal_silver' ? 'border-yellow-500/50 bg-yellow-500/10' : 'border-gray-700 hover:border-gray-600'}`}>
                            <input type="radio" checked={cashBalanceAction === 'metal_silver'} onChange={() => setCashBalanceAction('metal_silver')} className="accent-yellow-500" />
                            <span className="text-xs text-white font-medium flex flex-col">
                              <span>Convert Metal to Silver Ledger Only</span>
                              <span className="text-[10px] text-gray-300">
                                {silverLeftGrams < -0.001 ? <strong className="text-green-400">-{Math.abs(silverLeftGrams).toFixed(3)} g Silver Surplus</strong> : `+${opt3SilverToLedger.toFixed(3)} g Silver`} | <strong className={opt3CashDue > 0 ? 'text-red-400' : 'text-green-400'}>₹ {fmt(opt3CashDue)} Cash Due</strong>
                              </span>
                            </span>
                          </label>
                        </>
                      )}

                      {/* OPTION: ALL IN CASH */}
                      <label className={`flex items-center gap-2 p-2 rounded border cursor-pointer ${cashBalanceAction === 'cash' ? 'border-yellow-500/50 bg-yellow-500/10' : 'border-gray-700 hover:border-gray-600'}`}>
                        <input type="radio" checked={cashBalanceAction === 'cash'} onChange={() => setCashBalanceAction('cash')} className="accent-yellow-500" />
                        <span className="text-xs text-white font-medium flex flex-col">
                          <span>Keep as Cash Due — pay all in cash</span>
                          <span className="text-[10px] text-gray-400">
                            Total Cash Due: <strong className={opt1CashDue > 0 ? 'text-red-400' : 'text-green-400'}>₹ {fmt(opt1CashDue)}</strong>
                            {isPureMetal ? ' (GST / Non-metal charges only — metal rate is ₹0)' : ` (includes ₹${fmt(totalMetalRupeesDue)} metal + ₹${fmt(nonMetalCharges)} GST)`}
                          </span>
                        </span>
                      </label>
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
                <label className="block text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-1">Last Name</label>
                <input placeholder="Last Name" className="w-full bg-background border border-gray-700 rounded p-2 text-white outline-none focus:border-primary" value={newCustomer.last_name} onChange={e => setNewCustomer({ ...newCustomer, last_name: e.target.value })} />
              </div>
              <div>
                <label className="block text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-1">Phone Number *</label>
                <input placeholder="Phone Number" className="w-full bg-background border border-gray-700 rounded p-2 text-white outline-none focus:border-primary" value={newCustomer.phone} onChange={e => setNewCustomer({ ...newCustomer, phone: e.target.value })} />
              </div>
              <div>
                <label className="block text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-1">City</label>
                <input placeholder="City" className="w-full bg-background border border-gray-700 rounded p-2 text-white outline-none focus:border-primary" value={newCustomer.city} onChange={e => setNewCustomer({ ...newCustomer, city: e.target.value })} />
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
