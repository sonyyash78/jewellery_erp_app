import React, { useState, useMemo } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity, ScrollView, Alert, ActivityIndicator } from 'react-native';
import { axiosClient } from '../../api/axiosClient';
import * as Print from 'expo-print';
import { generateInvoiceHtml } from '../../utils/invoicePdfUtils';

export default function CheckoutScreen({ route, navigation }: any) {
  const {
    items = [],
    subtotal = 0,
    tax: initialTax = 0,
    discount = 0,
    grandTotal: initialGrandTotal = 0,
    gstType: initialGstType = 'same',
    selectedCustomer = null
  } = route.params || {};

  const [loading, setLoading] = useState(false);
  const [gstType, setGstType] = useState<'same' | 'inter' | 'none'>(initialGstType || 'same');

  // Dynamic GST calculation
  const currentTax = (gstType === 'same' || gstType === 'inter')
    ? Math.round((subtotal || 0) * 0.03 * 100) / 100
    : 0;
  const currentGrandTotal = Math.round((subtotal || 0) + currentTax);

  const [cashReceived, setCashReceived] = useState('');
  const [paymentMethod, setPaymentMethod] = useState<'Cash' | 'UPI' | 'Cheque'>('Cash');
  const [cashBalanceAction, setCashBalanceAction] = useState<'cash' | 'metal_gold' | 'metal_silver' | 'metal_both'>('cash');

  // Metal deposit at checkout
  const [goldDeposited, setGoldDeposited] = useState('');
  const [goldDepositTanch, setGoldDepositTanch] = useState('100');
  const [silverDeposited, setSilverDeposited] = useState('');
  const [silverDepositTanch, setSilverDepositTanch] = useState('100');

  // Non-metal charges (Making charges + Hallmark/Other charges + GST)
  const totalMakingCharges = useMemo(() => {
    return items.reduce((sum: number, i: any) => 
      sum + (Number(i.gold_calculation?.making_charges_amount || i.silver_calculation?.making_charges_amount || 0)), 0);
  }, [items]);

  const totalOtherCharges = useMemo(() => {
    return items.reduce((sum: number, i: any) => 
      sum + (Number(i.gold_calculation?.hallmark_charges || 0) + Number(i.gold_calculation?.other_charges || i.silver_calculation?.other_charges || 0)), 0);
  }, [items]);

  const nonMetalCharges = totalMakingCharges + totalOtherCharges + currentTax;

  // Extract metal billed
  const { totalGoldBilled, totalSilverBilled, goldRate, silverRate } = useMemo(() => {
    let tg = 0, ts = 0, gr = 0, sr = 0;
    (items || []).forEach((item: any) => {
      if (item.item_type === 'Gold') {
        tg += (item.gold_calculation?.fine_weight || item.net_weight || 0);
        if (!gr) gr = item.gold_calculation?.applied_rate || 0;
      } else if (item.item_type === 'Silver') {
        ts += (item.silver_calculation?.pure_weight || item.net_weight || 0);
        if (!sr) sr = item.silver_calculation?.applied_rate || 0;
      }
    });
    return {
      totalGoldBilled: tg,
      totalSilverBilled: ts,
      goldRate: gr || 72500,
      silverRate: sr || 90000
    };
  }, [items]);

  const hasGold = totalGoldBilled > 0;
  const hasSilver = totalSilverBilled > 0;

  // Additional metal given at checkout
  const parsedGoldGiven = parseFloat(goldDeposited) || 0;
  const parsedGoldTanch = parseFloat(goldDepositTanch) || 100;
  const fineGoldGiven = parsedGoldGiven * (parsedGoldTanch / 100);
  const goldValueGiven = fineGoldGiven * (goldRate / 10);

  const parsedSilverGiven = parseFloat(silverDeposited) || 0;
  const parsedSilverTanch = parseFloat(silverDepositTanch) || 100;
  const fineSilverGiven = parsedSilverGiven * (parsedSilverTanch / 100);
  const silverValueGiven = fineSilverGiven * (silverRate / 1000);

  const totalAdditionalMetalValue = goldValueGiven + silverValueGiven;

  // Remaining metal required
  const remGoldReq = Math.max(0, totalGoldBilled - fineGoldGiven);
  const remSilverReq = Math.max(0, totalSilverBilled - fineSilverGiven);

  const goldLeftRupees = goldRate > 0 ? remGoldReq * (goldRate / 10) : 0;
  const silverLeftRupees = silverRate > 0 ? remSilverReq * (silverRate / 1000) : 0;
  const totalMetalRupeesDue = goldLeftRupees + silverLeftRupees;

  const monetaryBeforeCash = totalMetalRupeesDue + nonMetalCharges;
  const parsedCash = parseFloat(cashReceived) || 0;
  const cashBalanceDue = Math.max(0, monetaryBeforeCash - parsedCash);

  // --- Dynamic 4 Settlement Options Math ---

  // Option 1: All Cash
  const opt1CashDue = Math.max(0, monetaryBeforeCash - parsedCash);
  const opt1GoldToLedger = 0;
  const opt1SilverToLedger = 0;

  // Option 4: Both Metals (metal_both)
  const opt4CashDue = Math.max(0, nonMetalCharges - parsedCash);
  const opt4CashForMetal = Math.max(0, parsedCash - nonMetalCharges);

  const opt4SilverRupeesPaid = Math.min(silverLeftRupees, opt4CashForMetal);
  const opt4RemainingCashForGold = opt4CashForMetal - opt4SilverRupeesPaid;
  const opt4GoldRupeesPaid = Math.min(goldLeftRupees, opt4RemainingCashForGold);

  const opt4RemainingSilverRupees = Math.max(0, silverLeftRupees - opt4SilverRupeesPaid);
  const opt4RemainingGoldRupees = Math.max(0, goldLeftRupees - opt4GoldRupeesPaid);

  const opt4SilverToLedger = (silverRate > 0 && opt4RemainingSilverRupees > 0)
    ? (opt4RemainingSilverRupees / (silverRate / 1000))
    : 0;
  const opt4GoldToLedger = (goldRate > 0 && opt4RemainingGoldRupees > 0)
    ? (opt4RemainingGoldRupees / (goldRate / 10))
    : 0;

  // Option 2: Gold Ledger
  const opt2RequiredCash = nonMetalCharges + silverLeftRupees;
  const opt2CashDue = Math.max(0, opt2RequiredCash - parsedCash);
  const opt2CashForGold = Math.max(0, parsedCash - opt2RequiredCash);
  const opt2GoldRupeesPaid = Math.min(goldLeftRupees, opt2CashForGold);
  const opt2RemainingGoldRupees = Math.max(0, goldLeftRupees - opt2GoldRupeesPaid);
  const opt2GoldToLedger = (goldRate > 0 && opt2RemainingGoldRupees > 0)
    ? (opt2RemainingGoldRupees / (goldRate / 10))
    : 0;
  const opt2SilverToLedger = 0;

  // Option 3: Silver Ledger
  const opt3RequiredCash = nonMetalCharges + goldLeftRupees;
  const opt3CashDue = Math.max(0, opt3RequiredCash - parsedCash);
  const opt3CashForSilver = Math.max(0, parsedCash - opt3RequiredCash);
  const opt3SilverRupeesPaid = Math.min(silverLeftRupees, opt3CashForSilver);
  const opt3RemainingSilverRupees = Math.max(0, silverLeftRupees - opt3SilverRupeesPaid);
  const opt3SilverToLedger = (silverRate > 0 && opt3RemainingSilverRupees > 0)
    ? (opt3RemainingSilverRupees / (silverRate / 1000))
    : 0;
  const opt3GoldToLedger = 0;

  // Selected action values:
  let finalBalanceAmount = opt1CashDue;
  let finalGoldDebt = opt1GoldToLedger;
  let finalSilverDebt = opt1SilverToLedger;

  if (cashBalanceAction === 'metal_gold') {
    finalBalanceAmount = opt2CashDue;
    finalGoldDebt = opt2GoldToLedger;
    finalSilverDebt = opt2SilverToLedger;
  } else if (cashBalanceAction === 'metal_silver') {
    finalBalanceAmount = opt3CashDue;
    finalGoldDebt = opt3GoldToLedger;
    finalSilverDebt = opt3SilverToLedger;
  } else if (cashBalanceAction === 'metal_both') {
    finalBalanceAmount = opt4CashDue;
    finalGoldDebt = opt4GoldToLedger;
    finalSilverDebt = opt4SilverToLedger;
  }

  const isFullySettled = finalBalanceAmount <= 0.01 && finalGoldDebt <= 0.001 && finalSilverDebt <= 0.001;

  const fmt = (n?: any) => {
    const num = Number(n);
    if (isNaN(num)) return '0.00';
    return num.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  };

  const handleGenerate = async (andPrint: boolean = false) => {
    if (!isFullySettled && !selectedCustomer) {
      Alert.alert('Error', 'A customer must be selected for outstanding balances.');
      return;
    }

    setLoading(true);

    let updatedItems = [...items];
    if (parsedGoldGiven > 0) {
      updatedItems.push({
        item_name: 'Gold Deposit',
        item_type: 'Gold',
        final_price: 0,
        gold_calculation: {
          applied_rate: goldRate,
          gross_weight: parsedGoldGiven,
          net_weight: parsedGoldGiven,
          stone_weight: 0,
          touch_purity: parsedGoldTanch,
          wastage: 0,
          fine_weight: fineGoldGiven,
          making_charge_type: 'flat',
          making_charge_rate: 0,
          making_charges_amount: 0,
          hallmark_charges: 0,
          other_charges: 0,
          discount: 0,
          total_gold_value: goldValueGiven,
        }
      });
    }

    if (parsedSilverGiven > 0) {
      updatedItems.push({
        item_name: 'Silver Deposit',
        item_type: 'Silver',
        final_price: 0,
        silver_calculation: {
          applied_rate: silverRate,
          gross_weight: parsedSilverGiven,
          net_weight: parsedSilverGiven,
          stone_weight: 0,
          tanch_percentage: parsedSilverTanch,
          wastage: 0,
          pure_weight: fineSilverGiven,
          making_charge_type: 'flat',
          making_charge_rate: 0,
          making_charges_amount: 0,
          other_charges: 0,
          discount: 0,
          total_silver_value: silverValueGiven,
        }
      });
    }

    let backendSettlementType = 'Cash';
    if (cashBalanceAction !== 'cash') {
      if (cashBalanceAction === 'metal_both') backendSettlementType = 'Hybrid';
      else backendSettlementType = 'Metal';
    }

    let backendBillType = 'Cash';
    if (hasGold && hasSilver) backendBillType = 'Hybrid';
    else if (totalAdditionalMetalValue > 0 || finalGoldDebt > 0 || finalSilverDebt > 0) backendBillType = 'Metal';

    let recStrParts = [];
    if (fineGoldGiven > 0) recStrParts.push(`${fineGoldGiven.toFixed(3)}g Gold`);
    if (fineSilverGiven > 0) recStrParts.push(`${fineSilverGiven.toFixed(3)}g Silver`);
    const metalRecStr = recStrParts.join(' | ');

    const payload = {
      customer_id: selectedCustomer ? selectedCustomer.id : null,
      subtotal: subtotal,
      tax_amount: currentTax,
      discount_amount: discount || 0,
      grand_total: currentGrandTotal,
      status: isFullySettled ? 'Paid' : 'Completed',
      items: updatedItems,
      amount_paid: parsedCash,
      payment_method: paymentMethod,
      bill_type: backendBillType,
      settlement_type: backendSettlementType,
      settlement_metal_type: cashBalanceAction === 'metal_gold' ? 'Gold' : cashBalanceAction === 'metal_silver' ? 'Silver' : cashBalanceAction === 'metal_both' ? 'Both' : null,
      metal_received_value: totalAdditionalMetalValue,
      metal_received_str: metalRecStr,
      cash_received: parsedCash,
      balance_amount: Math.max(0, finalBalanceAmount),
      balance_metal_weight: 0,
      gold_balance_metal_weight: finalGoldDebt,
      silver_balance_metal_weight: finalSilverDebt,
    };

    try {
      const res = await axiosClient.post('/invoices/', payload);
      const invoiceId = res.data.id;

      if (andPrint) {
        try {
          const [pdfRes, settingsRes] = await Promise.all([
            axiosClient.get(`/invoices/${invoiceId}/pdf-data`),
            axiosClient.get('/settings/').catch(() => ({ data: {} })),
          ]);
          const fullPdfData = {
            ...pdfRes.data,
            settings: { ...(pdfRes.data?.settings || {}), ...(settingsRes.data || {}) },
          };
          if (fullPdfData.invoice) {
            fullPdfData.invoice.amount_paid = parsedCash;
            fullPdfData.invoice.balance_due = finalBalanceAmount;
            fullPdfData.invoice.payment_method = paymentMethod;
            fullPdfData.invoice.bill_type = backendBillType;
            fullPdfData.invoice.settlement_type = backendSettlementType;
            fullPdfData.invoice.settlement_metal_type = cashBalanceAction === 'metal_gold' ? 'Gold' : cashBalanceAction === 'metal_silver' ? 'Silver' : cashBalanceAction === 'metal_both' ? 'Both' : null;
            fullPdfData.invoice.gold_balance_metal_weight = finalGoldDebt;
            fullPdfData.invoice.silver_balance_metal_weight = finalSilverDebt;
          }
          const html = generateInvoiceHtml(fullPdfData);
          await Print.printAsync({ html });
        } catch (printErr) {
          console.error('Print failed', printErr);
        }
      }

      Alert.alert('Success', `Invoice ${res.data.invoice_number} generated!`);
      navigation.navigate('Billing');
    } catch (e: any) {
      console.log('Checkout Error:', e.response?.data || e);
      Alert.alert('Error', e.response?.data?.detail || 'Failed to generate invoice');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <ScrollView contentContainerStyle={{ padding: 16 }}>
        <Text style={styles.headerTitle}>Checkout Settlement</Text>

        {/* GST OPTIONS CARD */}
        <View style={styles.card}>
          <Text style={styles.sectionHeaderTitle}>GST OPTIONS</Text>
          <View style={styles.gstOptionsRow}>
            {[
              { label: 'Intra-State (CGST 1.5% + SGST 1.5% = 3%)', val: 'same' },
              { label: 'Inter-State (IGST 3%)', val: 'inter' },
              { label: 'Without GST (0%)', val: 'none' }
            ].map(opt => (
              <TouchableOpacity
                key={opt.val}
                style={[styles.gstOptionBtn, gstType === opt.val && styles.gstOptionBtnActive]}
                onPress={() => setGstType(opt.val as any)}
              >
                <View style={[styles.radioCircle, gstType === opt.val && styles.radioCircleActive]}>
                  {gstType === opt.val && <View style={styles.radioInner} />}
                </View>
                <Text style={[styles.gstOptionText, gstType === opt.val && styles.gstOptionTextActive]}>
                  {opt.label}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* METAL RECEIVED FROM CUSTOMER */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Counter Metal Received (Trade-In / Deposit)</Text>
          
          {hasGold && (
            <View style={styles.metalBlock}>
              <Text style={styles.metalReq}>Gold Required @ ₹{goldRate}/10g: {totalGoldBilled.toFixed(3)}g</Text>
              <View style={styles.row}>
                <View style={styles.col}>
                  <Text style={styles.lbl}>Gross Given</Text>
                  <TextInput style={styles.inputSmall} keyboardType="numeric" value={goldDeposited} onChangeText={setGoldDeposited} placeholder="0" placeholderTextColor="#555"/>
                </View>
                <View style={styles.col}>
                  <Text style={styles.lbl}>Tanch %</Text>
                  <TextInput style={styles.inputSmall} keyboardType="numeric" value={goldDepositTanch} onChangeText={setGoldDepositTanch} />
                </View>
                <View style={styles.col}>
                  <Text style={styles.lbl}>Fine / Value</Text>
                  <Text style={styles.valText}>{fineGoldGiven.toFixed(3)}g</Text>
                  <Text style={styles.valTextGreen}>₹{fmt(goldValueGiven)}</Text>
                </View>
              </View>
            </View>
          )}

          {hasSilver && (
            <View style={[styles.metalBlock, hasGold && { borderTopWidth: 1, borderTopColor: '#333', paddingTop: 16 }]}>
              <Text style={styles.metalReq}>Silver Required @ ₹{silverRate}/kg: {totalSilverBilled.toFixed(3)}g</Text>
              <View style={styles.row}>
                <View style={styles.col}>
                  <Text style={styles.lbl}>Gross Given</Text>
                  <TextInput style={styles.inputSmall} keyboardType="numeric" value={silverDeposited} onChangeText={setSilverDeposited} placeholder="0" placeholderTextColor="#555"/>
                </View>
                <View style={styles.col}>
                  <Text style={styles.lbl}>Tanch %</Text>
                  <TextInput style={styles.inputSmall} keyboardType="numeric" value={silverDepositTanch} onChangeText={setSilverDepositTanch} />
                </View>
                <View style={styles.col}>
                  <Text style={styles.lbl}>Fine / Value</Text>
                  <Text style={styles.valText}>{fineSilverGiven.toFixed(3)}g</Text>
                  <Text style={styles.valTextGreen}>₹{fmt(silverValueGiven)}</Text>
                </View>
              </View>
            </View>
          )}
        </View>

        {/* MONETARY BALANCE & CASH RECEIVED */}
        <View style={styles.card}>
          <View style={styles.cashSectionRow}>
            <View style={{ flex: 1 }}>
              <Text style={styles.lbl}>TOTAL AMOUNT PAYABLE (IF 100% CASH)</Text>
              <Text style={styles.monetaryBal}>₹ {fmt(monetaryBeforeCash)}</Text>
              <Text style={{ color: '#888', fontSize: 11, marginTop: 2 }}>
                Includes ₹{fmt(totalMetalRupeesDue)} metal + ₹{fmt(nonMetalCharges)} GST & charges
              </Text>
            </View>

            <View style={{ flex: 1 }}>
              <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                <Text style={[styles.lbl, { color: '#4ade80' }]}>CASH RECEIVED</Text>
                <View style={{ flexDirection: 'row', gap: 4 }}>
                  <TouchableOpacity
                    onPress={() => setCashReceived(Math.round(nonMetalCharges * 100) / 100 > 0 ? (Math.round(nonMetalCharges * 100) / 100).toString() : '')}
                    style={{ backgroundColor: 'rgba(217,119,6,0.2)', paddingHorizontal: 6, paddingVertical: 2, borderRadius: 4, borderWidth: 1, borderColor: '#d97706' }}
                  >
                    <Text style={{ fontSize: 9, color: '#f59e0b', fontWeight: 'bold' }}>GST (₹{fmt(nonMetalCharges)})</Text>
                  </TouchableOpacity>
                  <TouchableOpacity
                    onPress={() => setCashReceived(Math.round(monetaryBeforeCash * 100) / 100 > 0 ? (Math.round(monetaryBeforeCash * 100) / 100).toString() : '')}
                    style={{ backgroundColor: 'rgba(34,197,94,0.2)', paddingHorizontal: 6, paddingVertical: 2, borderRadius: 4, borderWidth: 1, borderColor: '#22c55e' }}
                  >
                    <Text style={{ fontSize: 9, color: '#4ade80', fontWeight: 'bold' }}>Full (₹{fmt(monetaryBeforeCash)})</Text>
                  </TouchableOpacity>
                </View>
              </View>
              <TextInput
                style={styles.inputLarge}
                keyboardType="numeric"
                value={cashReceived}
                onChangeText={setCashReceived}
                placeholder="0"
                placeholderTextColor="#555"
              />
              
              <View style={styles.paymentMethods}>
                {(['Cash', 'UPI', 'Cheque'] as const).map(m => (
                  <TouchableOpacity
                    key={m}
                    style={[styles.payBtn, paymentMethod === m && styles.payBtnActive]}
                    onPress={() => setPaymentMethod(m)}
                  >
                    <Text style={[styles.payBtnText, paymentMethod === m && styles.payBtnTextActive]}>{m}</Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>
          </View>
        </View>

        {/* FINAL SETTLEMENT SUMMARY */}
        <View style={styles.summaryCard}>
          <Text style={styles.cardTitle}>FINAL SETTLEMENT SUMMARY</Text>
          <View style={styles.finalSummaryBox}>
            <View>
              <Text style={styles.lbl}>
                {finalBalanceAmount > 0 ? 'Amount Payable / Cash Due:' : finalBalanceAmount < 0 ? 'Refund to Customer:' : 'Amount Payable:'}
              </Text>
              <Text style={[styles.finalCashText, { color: finalBalanceAmount > 0 ? '#ef4444' : '#4ade80' }]}>
                {finalBalanceAmount < 0 ? '(Refund) ' : ''}₹ {fmt(Math.abs(finalBalanceAmount))}{finalBalanceAmount === 0 ? ' ✓ (Paid)' : ''}
              </Text>
            </View>
            <View style={{ alignItems: 'flex-end' }}>
              <Text style={styles.lbl}>Metal to Ledger:</Text>
              {hasGold && (
                <Text style={{ color: finalGoldDebt > 0.001 ? '#d4af37' : '#4ade80', fontWeight: '800', fontSize: 13 }}>
                  {finalGoldDebt > 0.001 ? `+${finalGoldDebt.toFixed(3)} g Gold Due` : '0.000 g Gold (Settled)'}
                </Text>
              )}
              {hasSilver && (
                <Text style={{ color: finalSilverDebt > 0.001 ? '#cbd5e1' : '#4ade80', fontWeight: '800', fontSize: 13 }}>
                  {finalSilverDebt > 0.001 ? `+${finalSilverDebt.toFixed(3)} g Silver Due` : '0.000 g Silver (Settled)'}
                </Text>
              )}
            </View>
          </View>

          {(remGoldReq > 0.001 || remSilverReq > 0.001 || cashBalanceDue > 0) && (
            <View style={{ marginTop: 14 }}>
              <Text style={styles.settlePrompt}>HOW TO SETTLE THE REMAINING BALANCE?</Text>

              {/* Option 1: All Cash */}
              <TouchableOpacity
                style={[styles.actionBtn, cashBalanceAction === 'cash' && styles.actionBtnActive]}
                onPress={() => setCashBalanceAction('cash')}
              >
                <View style={[styles.radioCircle, cashBalanceAction === 'cash' && styles.radioCircleActive]}>
                  {cashBalanceAction === 'cash' && <View style={styles.radioInner} />}
                </View>
                <View style={{ flex: 1 }}>
                  <Text style={styles.actionBtnText}>1. Keep as Cash Due — pay all in cash</Text>
                  <Text style={styles.actionSubText}>
                    Cash Due: ₹ {fmt(opt1CashDue)} (No metal ledger change)
                  </Text>
                </View>
              </TouchableOpacity>

              {/* Option 2: Gold Ledger */}
              {hasGold && (
                <TouchableOpacity
                  style={[styles.actionBtn, cashBalanceAction === 'metal_gold' && styles.actionBtnActive]}
                  onPress={() => setCashBalanceAction('metal_gold')}
                >
                  <View style={[styles.radioCircle, cashBalanceAction === 'metal_gold' && styles.radioCircleActive]}>
                    {cashBalanceAction === 'metal_gold' && <View style={styles.radioInner} />}
                  </View>
                  <View style={{ flex: 1 }}>
                    <Text style={styles.actionBtnText}>2. Convert Metal to Gold Ledger</Text>
                    <Text style={styles.actionSubText}>
                      +{opt2GoldToLedger.toFixed(3)} g Gold to Ledger | ₹ {fmt(opt2CashDue)} Cash Due
                      {opt2GoldRupeesPaid > 0 ? ` (₹${fmt(opt2GoldRupeesPaid)} cash applied to Gold)` : ''}
                    </Text>
                  </View>
                </TouchableOpacity>
              )}

              {/* Option 3: Silver Ledger */}
              {hasSilver && (
                <TouchableOpacity
                  style={[styles.actionBtn, cashBalanceAction === 'metal_silver' && styles.actionBtnActive]}
                  onPress={() => setCashBalanceAction('metal_silver')}
                >
                  <View style={[styles.radioCircle, cashBalanceAction === 'metal_silver' && styles.radioCircleActive]}>
                    {cashBalanceAction === 'metal_silver' && <View style={styles.radioInner} />}
                  </View>
                  <View style={{ flex: 1 }}>
                    <Text style={styles.actionBtnText}>3. Convert Metal to Silver Ledger</Text>
                    <Text style={styles.actionSubText}>
                      +{opt3SilverToLedger.toFixed(3)} g Silver to Ledger | ₹ {fmt(opt3CashDue)} Cash Due
                      {opt3SilverRupeesPaid > 0 ? ` (₹${fmt(opt3SilverRupeesPaid)} cash applied to Silver)` : ''}
                    </Text>
                  </View>
                </TouchableOpacity>
              )}

              {/* Option 4: Both Metals */}
              {(hasGold || hasSilver) && (
                <TouchableOpacity
                  style={[styles.actionBtn, cashBalanceAction === 'metal_both' && styles.actionBtnActive]}
                  onPress={() => setCashBalanceAction('metal_both')}
                >
                  <View style={[styles.radioCircle, cashBalanceAction === 'metal_both' && styles.radioCircleActive]}>
                    {cashBalanceAction === 'metal_both' && <View style={styles.radioInner} />}
                  </View>
                  <View style={{ flex: 1 }}>
                    <Text style={styles.actionBtnText}>4. Convert Both Metals to Ledgers</Text>
                    <Text style={styles.actionSubText}>
                      {hasGold ? `Gold: +${opt4GoldToLedger.toFixed(3)} g ${opt4GoldRupeesPaid > 0 ? `(₹${fmt(opt4GoldRupeesPaid)} pd)` : ''}` : ''}
                      {hasGold && hasSilver ? ' | ' : ''}
                      {hasSilver ? `Silver: +${opt4SilverToLedger.toFixed(3)} g ${opt4SilverRupeesPaid > 0 ? `(₹${fmt(opt4SilverRupeesPaid)} pd)` : ''}` : ''}
                      {opt4CashDue > 0 ? ` | ₹${fmt(opt4CashDue)} Cash Due` : ' | ₹0 Cash Due'}
                    </Text>
                  </View>
                </TouchableOpacity>
              )}
            </View>
          )}
        </View>

        {/* Action Buttons */}
        <View style={{ flexDirection: 'row', gap: 12, marginTop: 8 }}>
          <TouchableOpacity 
            style={[styles.saveButton, { flex: 1, backgroundColor: '#222', borderWidth: 1, borderColor: '#d4af37' }, loading && styles.saveButtonDisabled]} 
            onPress={() => handleGenerate(false)}
            disabled={loading}
          >
            {loading ? <ActivityIndicator color="#d4af37" /> : <Text style={[styles.saveButtonText, { color: '#d4af37', fontSize: 15 }]}>SAVE INVOICE</Text>}
          </TouchableOpacity>

          <TouchableOpacity 
            style={[styles.saveButton, { flex: 1 }, loading && styles.saveButtonDisabled]} 
            onPress={() => handleGenerate(true)}
            disabled={loading}
          >
            {loading ? <ActivityIndicator color="#000" /> : <Text style={[styles.saveButtonText, { fontSize: 15 }]}>SAVE & PRINT ⎙</Text>}
          </TouchableOpacity>
        </View>
        
        <View style={{ height: 40 }} />
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0a0a0a' },
  headerTitle: { color: '#d4af37', fontSize: 22, fontWeight: 'bold', marginBottom: 14 },
  card: { backgroundColor: '#141414', borderWidth: 1, borderColor: '#333', padding: 14, borderRadius: 8, marginBottom: 14 },
  cardTitle: { color: '#fff', fontSize: 13, fontWeight: 'bold', textTransform: 'uppercase', marginBottom: 10 },
  metalBlock: { marginBottom: 12 },
  metalReq: { color: '#d4af37', fontSize: 12, fontWeight: 'bold', marginBottom: 8 },
  row: { flexDirection: 'row', gap: 8 },
  col: { flex: 1 },
  lbl: { color: '#888', fontSize: 10, textTransform: 'uppercase', marginBottom: 4, fontWeight: 'bold' },
  inputSmall: { backgroundColor: '#0a0a0a', color: '#fff', borderWidth: 1, borderColor: '#333', padding: 8, borderRadius: 6, fontVariant: ['tabular-nums'] },
  valText: { color: '#fff', fontSize: 13, fontVariant: ['tabular-nums'] },
  valTextGreen: { color: '#4ade80', fontSize: 13, fontWeight: 'bold', fontVariant: ['tabular-nums'] },
  cashSectionRow: { flexDirection: 'row', gap: 12 },
  monetaryBal: { color: '#fff', fontSize: 22, fontWeight: 'bold', fontVariant: ['tabular-nums'] },
  inputLarge: { backgroundColor: '#0a0a0a', color: '#4ade80', borderWidth: 1, borderColor: '#166534', padding: 10, borderRadius: 8, fontSize: 18, fontVariant: ['tabular-nums'] },
  paymentMethods: { flexDirection: 'row', gap: 6, marginTop: 8 },
  payBtn: { flex: 1, paddingVertical: 8, borderWidth: 1, borderColor: '#333', borderRadius: 6, alignItems: 'center' },
  payBtnActive: { backgroundColor: '#166534', borderColor: '#4ade80' },
  payBtnText: { color: '#888', fontSize: 11, fontWeight: 'bold' },
  payBtnTextActive: { color: '#4ade80' },

  sectionHeaderTitle: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#d4af37',
    textTransform: 'uppercase',
    letterSpacing: 1,
    marginBottom: 10
  },
  gstOptionsRow: { gap: 8 },
  gstOptionBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 10,
    paddingHorizontal: 12,
    backgroundColor: '#1e1e1e',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#2d2d2d'
  },
  gstOptionBtnActive: {
    borderColor: '#d4af37',
    backgroundColor: 'rgba(212, 175, 55, 0.1)'
  },
  radioCircle: {
    width: 18,
    height: 18,
    borderRadius: 9,
    borderWidth: 2,
    borderColor: '#666',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 10
  },
  radioCircleActive: { borderColor: '#d4af37' },
  radioInner: { width: 9, height: 9, borderRadius: 4.5, backgroundColor: '#d4af37' },
  gstOptionText: { color: '#aaa', fontSize: 13, fontWeight: '500' },
  gstOptionTextActive: { color: '#fff', fontWeight: 'bold' },

  summaryCard: { backgroundColor: '#181510', borderWidth: 1, borderColor: '#854d0e', padding: 14, borderRadius: 8, marginBottom: 14 },
  finalSummaryBox: {
    backgroundColor: '#0a0a0a',
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#333',
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  finalCashText: { fontSize: 20, fontWeight: 'bold', fontVariant: ['tabular-nums'] },
  settlePrompt: { color: '#d4af37', fontSize: 11, fontWeight: 'bold', textTransform: 'uppercase', marginBottom: 8 },
  actionBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    borderWidth: 1,
    borderColor: '#333',
    borderRadius: 8,
    marginTop: 8,
    backgroundColor: '#121212'
  },
  actionBtnActive: { backgroundColor: 'rgba(212, 175, 55, 0.1)', borderColor: '#d4af37' },
  actionBtnText: { color: '#fff', fontSize: 13, fontWeight: 'bold' },
  actionSubText: { color: '#9ca3af', fontSize: 11, marginTop: 2 },

  saveButton: { backgroundColor: '#d4af37', padding: 14, borderRadius: 8, alignItems: 'center' },
  saveButtonDisabled: { opacity: 0.5 },
  saveButtonText: { color: '#000', fontSize: 16, fontWeight: 'bold' },
});
