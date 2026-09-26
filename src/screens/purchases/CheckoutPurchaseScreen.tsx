import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity, ScrollView, Alert, ActivityIndicator, Modal, FlatList, KeyboardAvoidingView, Platform } from 'react-native';
import { axiosClient } from '../../api/axiosClient';
import * as Print from 'expo-print';
import { generateInvoiceHtml } from '../../utils/invoicePdfUtils';

export default function CheckoutPurchaseScreen({ route, navigation }: any) {
  const { selectedSeller: initialSeller, seller, items = [] } = route.params || {};

  // Supplier state
  const [selectedSeller, setSelectedSeller] = useState<any>(initialSeller || seller || null);
  const [sellers, setSellers] = useState<any[]>([]);
  const [sellerSearch, setSellerSearch] = useState('');
  const [showSellerModal, setShowSellerModal] = useState(false);
  const [showAddSellerModal, setShowAddSellerModal] = useState(false);
  const [newSellerName, setNewSellerName] = useState('');
  const [newSellerPhone, setNewSellerPhone] = useState('');

  useEffect(() => {
    fetchSellers();
  }, []);

  const fetchSellers = async () => {
    try {
      const response = await axiosClient.get('/sellers/');
      setSellers(response.data.items || response.data || []);
    } catch (error) {
      console.log('Failed to fetch suppliers', error);
    }
  };

  const handleAddNewSeller = async () => {
    if (!newSellerName) {
      Alert.alert('Error', 'Please enter supplier name');
      return;
    }
    const cleanedPhone = newSellerPhone.replace(/\D/g, '');
    if (cleanedPhone.length !== 10 && cleanedPhone.length !== 12) {
      Alert.alert('Error', 'Mobile number must be exactly 10 digits');
      return;
    }
    try {
      const response = await axiosClient.post('/sellers/', { name: newSellerName, mobile: cleanedPhone });
      const newS = response.data;
      setSellers([newS, ...sellers]);
      setSelectedSeller(newS);
      setShowAddSellerModal(false);
      setShowSellerModal(false);
      setNewSellerName('');
      setNewSellerPhone('');
    } catch (error) {
      Alert.alert('Error', 'Failed to add supplier');
    }
  };

  const total_taxable = items.reduce((sum: number, item: any) => sum + item.taxable_amount, 0);
  
  const [gstType, setGstType] = useState<'same' | 'inter' | 'none'>('same');
  let gstAmount = 0;
  let cgst = 0;
  let sgst = 0;
  let igst = 0;

  if (gstType === 'same') {
    gstAmount = total_taxable * 0.03;
    cgst = gstAmount / 2;
    sgst = gstAmount / 2;
  } else if (gstType === 'inter') {
    gstAmount = total_taxable * 0.03;
    igst = gstAmount;
  }
  const grand_total = Math.round(total_taxable + gstAmount);

  // Compute metal totals from cart
  const goldItems = items.filter((i: any) => i.metal_type === 'Gold');
  const silverItems = items.filter((i: any) => i.metal_type === 'Silver');
  
  const totalGoldBilled = goldItems.reduce((sum: number, i: any) => sum + (Number(i.fine_weight || i.pure_weight || (i.net_weight && i.touch_purity ? (i.net_weight * i.touch_purity / 100) : i.net_weight)) || 0), 0);
  const totalSilverBilled = silverItems.reduce((sum: number, i: any) => sum + (Number(i.fine_weight || i.pure_weight || (i.net_weight && i.touch_purity ? (i.net_weight * i.touch_purity / 100) : i.net_weight)) || 0), 0);
  
  const goldRate = goldItems.length > 0 ? Number(goldItems[0].metal_rate) : 72500;
  const silverRate = silverItems.length > 0 ? Number(silverItems[0].metal_rate) : 90000;

  const hasGold = totalGoldBilled > 0;
  const hasSilver = totalSilverBilled > 0;

  // User Inputs
  const [goldGiven, setGoldGiven] = useState('');
  const [goldGivenTanch, setGoldGivenTanch] = useState('100');
  const [silverGiven, setSilverGiven] = useState('');
  const [silverGivenTanch, setSilverGivenTanch] = useState('100');
  const [cashPaid, setCashPaid] = useState('');
  const [paymentMethod, setPaymentMethod] = useState<'Cash' | 'UPI' | 'Cheque'>('Cash');
  const [cashBalanceAction, setCashBalanceAction] = useState<'cash' | 'metal_gold' | 'metal_silver' | 'metal_both'>('cash');

  const [submitting, setSubmitting] = useState(false);

  // Metal Given Logic
  const parsedGoldGiven = parseFloat(goldGiven) || 0;
  const parsedGoldTanch = parseFloat(goldGivenTanch) || 100;
  const fineGoldGiven = parsedGoldGiven * (parsedGoldTanch / 100);
  const goldValueReceived = fineGoldGiven * (goldRate / 10);

  const parsedSilverGiven = parseFloat(silverGiven) || 0;
  const parsedSilverTanch = parseFloat(silverGivenTanch) || 100;
  const fineSilverGiven = parsedSilverGiven * (parsedSilverTanch / 100);
  const silverValueReceived = fineSilverGiven * (silverRate / 1000);

  const totalMetalValueReceived = goldValueReceived + silverValueReceived;

  // Remaining metal required
  const remGoldReq = Math.max(0, totalGoldBilled - fineGoldGiven);
  const remSilverReq = Math.max(0, totalSilverBilled - fineSilverGiven);

  const goldLeftRupees = goldRate > 0 ? remGoldReq * (goldRate / 10) : 0;
  const silverLeftRupees = silverRate > 0 ? remSilverReq * (silverRate / 1000) : 0;
  const totalMetalRupeesDue = goldLeftRupees + silverLeftRupees;

  const totalCharges = items.reduce((sum: number, item: any) => {
    return sum + Number(item.labour_charge || 0) + Number(item.hallmark_charge || 0) + Number(item.other_charges || 0);
  }, 0) + gstAmount;

  const monetaryBeforeCash = totalMetalRupeesDue + totalCharges;
  const parsedCash = parseFloat(cashPaid) || 0;
  const cashBalanceDue = Math.max(0, monetaryBeforeCash - parsedCash);

  // Settlement Logic
  const opt1CashDue = Math.max(0, monetaryBeforeCash - parsedCash);

  const opt4CashDue = Math.max(0, totalCharges - parsedCash);
  const opt4CashForMetal = Math.max(0, parsedCash - totalCharges);
  const opt4SilverPaid = Math.min(silverLeftRupees, opt4CashForMetal);
  const opt4CashRemGold = opt4CashForMetal - opt4SilverPaid;
  const opt4GoldPaid = Math.min(goldLeftRupees, opt4CashRemGold);

  const opt4RemSilver = Math.max(0, silverLeftRupees - opt4SilverPaid);
  const opt4RemGold = Math.max(0, goldLeftRupees - opt4GoldPaid);

  const opt4GoldToLedger = (goldRate > 0 && opt4RemGold > 0) ? (opt4RemGold / (goldRate / 10)) : 0;
  const opt4SilverToLedger = (silverRate > 0 && opt4RemSilver > 0) ? (opt4RemSilver / (silverRate / 1000)) : 0;

  const opt2ReqCash = totalCharges + silverLeftRupees;
  const opt2CashDue = Math.max(0, opt2ReqCash - parsedCash);
  const opt2CashForGold = Math.max(0, parsedCash - opt2ReqCash);
  const opt2GoldPaid = Math.min(goldLeftRupees, opt2CashForGold);
  const opt2RemGold = Math.max(0, goldLeftRupees - opt2GoldPaid);
  const opt2GoldToLedger = (goldRate > 0 && opt2RemGold > 0) ? (opt2RemGold / (goldRate / 10)) : 0;

  const opt3ReqCash = totalCharges + goldLeftRupees;
  const opt3CashDue = Math.max(0, opt3ReqCash - parsedCash);
  const opt3CashForSilver = Math.max(0, parsedCash - opt3ReqCash);
  const opt3SilverPaid = Math.min(silverLeftRupees, opt3CashForSilver);
  const opt3RemSilver = Math.max(0, silverLeftRupees - opt3SilverPaid);
  const opt3SilverToLedger = (silverRate > 0 && opt3RemSilver > 0) ? (opt3RemSilver / (silverRate / 1000)) : 0;

  let finalGoldDebt = 0;
  let finalSilverDebt = 0;
  let displayCashDue = opt1CashDue;

  if (cashBalanceAction === 'cash') {
    displayCashDue = opt1CashDue;
  } else if (cashBalanceAction === 'metal_gold') {
    finalGoldDebt = opt2GoldToLedger;
    displayCashDue = opt2CashDue;
  } else if (cashBalanceAction === 'metal_silver') {
    finalSilverDebt = opt3SilverToLedger;
    displayCashDue = opt3CashDue;
  } else if (cashBalanceAction === 'metal_both') {
    finalGoldDebt = opt4GoldToLedger;
    finalSilverDebt = opt4SilverToLedger;
    displayCashDue = opt4CashDue;
  }

  const fmt = (n: number) => n.toLocaleString('en-IN', { maximumFractionDigits: 2 });

  const isFullySettled = displayCashDue <= 0.01 && finalGoldDebt <= 0.001 && finalSilverDebt <= 0.001;

  const handleSettle = async (andPrint: boolean = false) => {
    try {
      if (parsedCash < 0 || parsedGoldGiven < 0 || parsedSilverGiven < 0) {
        Alert.alert('Error', 'Payments/deposits cannot be negative.');
        return;
      }

      if (!isFullySettled && !selectedSeller) {
        Alert.alert('Error', 'A supplier must be selected for outstanding balances.');
        return;
      }
      
      setSubmitting(true);
      
      let updatedItems = [...items];
      
      if (parsedGoldGiven > 0) {
        updatedItems.push({
          item_name: 'Metal Given (Gold)', 
          metal_type: 'Gold', 
          category: 'Deposit',
          gross_weight: parsedGoldGiven, 
          stone_weight: 0,
          net_weight: parsedGoldGiven,
          touch_purity: parsedGoldTanch, 
          wastage: 0, 
          fine_weight: fineGoldGiven,
          metal_rate: goldRate,
          metal_value: goldValueReceived,
          labour_charge: 0,
          other_charges: 0,
          discount: 0,
          taxable_amount: 0
        });
      }
      if (parsedSilverGiven > 0) {
        updatedItems.push({
          item_name: 'Metal Given (Silver)', 
          metal_type: 'Silver', 
          category: 'Deposit',
          gross_weight: parsedSilverGiven, 
          stone_weight: 0,
          net_weight: parsedSilverGiven,
          touch_purity: parsedSilverTanch, 
          wastage: 0, 
          fine_weight: fineSilverGiven,
          metal_rate: silverRate,
          metal_value: silverValueReceived,
          labour_charge: 0,
          other_charges: 0,
          discount: 0,
          taxable_amount: 0
        });
      }

      let backendSettlementType = 'Cash';
      if (cashBalanceAction !== 'cash') {
        if (cashBalanceAction === 'metal_both') backendSettlementType = 'Hybrid';
        else backendSettlementType = 'Metal';
      }

      let backendBillType = 'Cash';
      if (hasGold && hasSilver) backendBillType = 'Hybrid';
      else if (totalMetalValueReceived > 0 || finalGoldDebt > 0 || finalSilverDebt > 0) backendBillType = 'Metal';

      const payload = {
        seller_id: selectedSeller?.id || seller?.id || null,
        items: updatedItems,
        total_taxable,
        cgst,
        sgst,
        igst,
        grand_total,
        amount_paid: parsedCash,
        payment_method: paymentMethod,
        bill_type: backendBillType,
        settlement_type: backendSettlementType,
        settlement_metal_type: cashBalanceAction === 'metal_gold' ? 'Gold' : cashBalanceAction === 'metal_silver' ? 'Silver' : cashBalanceAction === 'metal_both' ? 'Both' : null,
        metal_given_value: totalMetalValueReceived,
        cash_paid: parsedCash,
        balance_amount: displayCashDue,
        balance_metal_weight: 0,
        gold_balance_metal_weight: finalGoldDebt,
        silver_balance_metal_weight: finalSilverDebt,
        status: (displayCashDue <= 0 && finalGoldDebt === 0 && finalSilverDebt === 0) ? 'Paid' : 'Completed'
      };

      const res = await axiosClient.post('/purchases/', payload);
      const purchaseId = res.data.id;

      if (andPrint) {
        try {
          const [pdfRes, settingsRes] = await Promise.all([
            axiosClient.get(`/purchases/${purchaseId}/pdf-data`),
            axiosClient.get('/settings/').catch(() => ({ data: {} })),
          ]);
          const fullPdfData = {
            ...pdfRes.data,
            settings: { ...(pdfRes.data?.settings || {}), ...(settingsRes.data || {}) },
          };
          if (fullPdfData.invoice) {
            fullPdfData.invoice.amount_paid = parsedCash;
            fullPdfData.invoice.cash_paid = parsedCash;
            fullPdfData.invoice.balance_due = displayCashDue;
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

      Alert.alert('Success', `Purchase ${res.data.purchase_number || res.data.id} recorded!`);
      navigation.navigate('Purchases');
    } catch (e: any) {
      console.log('Purchase settlement error:', e.response?.data || e);
      Alert.alert('Error', e.response?.data?.detail || 'Failed to record purchase');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <View style={styles.container}>
      <ScrollView contentContainerStyle={{ padding: 16, paddingBottom: 60 }}>
        <Text style={styles.headerTitle}>Checkout Settlement</Text>

        {/* TOP SUMMARY BANNER */}
        <View style={styles.topSummaryRow}>
          <View style={styles.topSummaryCol}>
            <Text style={styles.topSummaryLbl}>Purchase Bill</Text>
            <Text style={styles.topSummaryVal}>₹ {fmt(grand_total)}</Text>
          </View>
          <View style={styles.topSummaryCol}>
            <Text style={styles.topSummaryLbl}>Metal Given</Text>
            <Text style={[styles.topSummaryVal, { color: '#ef4444' }]}>− ₹ {fmt(totalMetalValueReceived)}</Text>
          </View>
          <View style={styles.topSummaryCol}>
            <Text style={[styles.topSummaryLbl, { color: '#d4af37' }]}>Net Due</Text>
            <Text style={[styles.topSummaryVal, { color: '#d4af37' }]}>₹ {fmt(monetaryBeforeCash)}</Text>
          </View>
        </View>

        {/* GST OPTIONS */}
        <View style={styles.card}>
          <Text style={styles.sectionHeaderTitle}>GST OPTIONS</Text>
          <View style={styles.gstOptionsRow}>
            {[
              { label: 'Same State (CGST + SGST 3%)', val: 'same' },
              { label: 'Diff State (IGST 3%)', val: 'inter' },
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

        {/* METAL GIVEN TO SUPPLIER */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Counter Metal Given to Supplier (Optional)</Text>
          
          {hasGold && (
            <View style={styles.metalBlock}>
              <Text style={styles.metalReq}>Gold Required @ ₹{goldRate}/10g: {totalGoldBilled.toFixed(3)}g</Text>
              <View style={styles.row}>
                <View style={styles.col}>
                  <Text style={styles.lbl}>Gross Given</Text>
                  <TextInput
                    style={styles.inputSmall}
                    keyboardType="numeric"
                    value={goldGiven}
                    onChangeText={setGoldGiven}
                    placeholder="0.000"
                    placeholderTextColor="#555"
                  />
                </View>
                <View style={styles.col}>
                  <Text style={styles.lbl}>Tanch %</Text>
                  <TextInput
                    style={styles.inputSmall}
                    keyboardType="numeric"
                    value={goldGivenTanch}
                    onChangeText={setGoldGivenTanch}
                  />
                </View>
                <View style={styles.col}>
                  <Text style={styles.lbl}>Fine / Value</Text>
                  <Text style={styles.valText}>{fineGoldGiven.toFixed(3)}g</Text>
                  <Text style={styles.valTextGreen}>₹{fmt(goldValueReceived)}</Text>
                </View>
              </View>
              {remGoldReq > 0.001 ? (
                <Text style={styles.remText}>Remaining: +{remGoldReq.toFixed(3)}g Due (₹{fmt(goldLeftRupees)})</Text>
              ) : (
                <Text style={[styles.remText, { color: '#4ade80' }]}>Gold Settled</Text>
              )}
            </View>
          )}

          {hasSilver && (
            <View style={[styles.metalBlock, hasGold && { borderTopWidth: 1, borderTopColor: '#333', paddingTop: 16 }]}>
              <Text style={styles.metalReq}>Silver Required @ ₹{silverRate}/kg: {totalSilverBilled.toFixed(3)}g</Text>
              <View style={styles.row}>
                <View style={styles.col}>
                  <Text style={styles.lbl}>Gross Given</Text>
                  <TextInput
                    style={styles.inputSmall}
                    keyboardType="numeric"
                    value={silverGiven}
                    onChangeText={setSilverGiven}
                    placeholder="0.000"
                    placeholderTextColor="#555"
                  />
                </View>
                <View style={styles.col}>
                  <Text style={styles.lbl}>Tanch %</Text>
                  <TextInput
                    style={styles.inputSmall}
                    keyboardType="numeric"
                    value={silverGivenTanch}
                    onChangeText={setSilverGivenTanch}
                  />
                </View>
                <View style={styles.col}>
                  <Text style={styles.lbl}>Fine / Value</Text>
                  <Text style={styles.valText}>{fineSilverGiven.toFixed(3)}g</Text>
                  <Text style={styles.valTextGreen}>₹{fmt(silverValueReceived)}</Text>
                </View>
              </View>
              {remSilverReq > 0.001 ? (
                <Text style={styles.remText}>Remaining: +{remSilverReq.toFixed(3)}g Due (₹{fmt(silverLeftRupees)})</Text>
              ) : (
                <Text style={[styles.remText, { color: '#4ade80' }]}>Silver Settled</Text>
              )}
            </View>
          )}

          <View style={styles.cashSectionContainer}>
            <View style={styles.payableBox}>
              <Text style={styles.lbl}>TOTAL PAYABLE TO SUPPLIER (IF 100% CASH)</Text>
              <Text style={styles.monetaryVal}>₹ {fmt(monetaryBeforeCash)}</Text>
              <Text style={styles.subtext}>Metal: ₹{fmt(totalMetalRupeesDue)} + Charges: ₹{fmt(totalCharges)}</Text>
            </View>
            <View style={styles.cashPaidBox}>
              <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                <Text style={[styles.lbl, { color: '#4ade80', marginBottom: 0 }]}>CASH PAID</Text>
                <TouchableOpacity
                  onPress={() => setCashPaid(Math.round(monetaryBeforeCash * 100) / 100 > 0 ? (Math.round(monetaryBeforeCash * 100) / 100).toString() : '')}
                  style={styles.quickFillBtn}
                >
                  <Text style={styles.quickFillText}>Full (₹{fmt(monetaryBeforeCash)})</Text>
                </TouchableOpacity>
              </View>
              <TextInput
                style={styles.inputLarge}
                keyboardType="numeric"
                value={cashPaid}
                onChangeText={setCashPaid}
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
                {displayCashDue > 0 ? 'This Bill Payable Due:' : displayCashDue < 0 ? 'Refund from Supplier:' : 'This Bill Payable Due:'}
              </Text>
              <Text style={[styles.finalCashText, { color: displayCashDue > 0 ? '#ef4444' : '#4ade80' }]}>
                {displayCashDue < 0 ? '(Refund) ' : ''}₹ {fmt(Math.abs(displayCashDue))}{displayCashDue === 0 ? ' ✓ (Paid)' : ''}
              </Text>
            </View>
            <View style={{ alignItems: 'flex-end' }}>
              <Text style={styles.lbl}>Metal to Ledger:</Text>
              {hasGold && (
                <Text style={{ color: finalGoldDebt > 0.001 ? '#d4af37' : '#4ade80', fontWeight: '800', fontSize: 13 }}>
                  {finalGoldDebt > 0.001 ? `+${finalGoldDebt.toFixed(3)} g Gold` : '0.000 g Gold (Settled)'}
                </Text>
              )}
              {hasSilver && (
                <Text style={{ color: finalSilverDebt > 0.001 ? '#cbd5e1' : '#4ade80', fontWeight: '800', fontSize: 13 }}>
                  {finalSilverDebt > 0.001 ? `+${finalSilverDebt.toFixed(3)} g Silver` : '0.000 g Silver (Settled)'}
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
                      {hasGold ? `Gold: +${opt4GoldToLedger.toFixed(3)} g` : ''}
                      {hasGold && hasSilver ? ' | ' : ''}
                      {hasSilver ? `Silver: +${opt4SilverToLedger.toFixed(3)} g` : ''}
                      {opt4CashDue > 0 ? ` | ₹${fmt(opt4CashDue)} Cash Due` : ' | ₹0 Cash Due'}
                    </Text>
                  </View>
                </TouchableOpacity>
              )}
            </View>
          )}
        </View>

        {/* SELECT SUPPLIER */}
        <View style={styles.card}>
          <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
            <Text style={styles.sectionHeaderTitle}>SELECT SUPPLIER</Text>
            <TouchableOpacity style={styles.newCustBtn} onPress={() => setShowAddSellerModal(true)}>
              <Text style={styles.newCustBtnText}>+ New</Text>
            </TouchableOpacity>
          </View>

          <TouchableOpacity style={styles.customerSelector} onPress={() => setShowSellerModal(true)}>
            <Text style={styles.customerSelectorText}>
              {selectedSeller
                ? `${selectedSeller.name} (${selectedSeller.mobile})`
                : '-- Select Supplier / Walk-in --'}
            </Text>
            <Text style={{ color: '#d4af37', fontSize: 14 }}>▼</Text>
          </TouchableOpacity>
          <Text style={styles.custWarningText}>* A supplier must be selected for outstanding balances.</Text>
        </View>

        <View style={{ flexDirection: 'row', gap: 12, marginTop: 8 }}>
          <TouchableOpacity
            style={[styles.submitButton, { flex: 1, backgroundColor: '#222', borderWidth: 1, borderColor: '#d4af37' }, submitting && { opacity: 0.7 }]}
            onPress={() => handleSettle(false)}
            disabled={submitting}
          >
            {submitting ? <ActivityIndicator color="#d4af37" /> : <Text style={[styles.submitButtonText, { color: '#d4af37', fontSize: 15 }]}>SAVE PURCHASE</Text>}
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.submitButton, { flex: 1 }, submitting && { opacity: 0.7 }]}
            onPress={() => handleSettle(true)}
            disabled={submitting}
          >
            {submitting ? <ActivityIndicator color="#000" /> : <Text style={[styles.submitButtonText, { fontSize: 15 }]}>SAVE & PRINT ⎙</Text>}
          </TouchableOpacity>
        </View>

        <View style={{ height: 40 }} />
      </ScrollView>

      {/* Supplier Picker Modal */}
      <Modal visible={showSellerModal} transparent animationType="slide">
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Select Supplier</Text>
              <TouchableOpacity onPress={() => setShowSellerModal(false)}>
                <Text style={styles.modalCloseText}>✕</Text>
              </TouchableOpacity>
            </View>

            <View style={{ paddingHorizontal: 16, paddingTop: 12, paddingBottom: 8 }}>
              <TextInput
                style={styles.modalSearchInput}
                placeholder="Search by name or phone..."
                placeholderTextColor="#666"
                value={sellerSearch}
                onChangeText={setSellerSearch}
              />
            </View>

            <FlatList
              data={sellers.filter((s: any) => {
                if (!sellerSearch) return true;
                const q = sellerSearch.toLowerCase();
                const name = (s.name || '').toLowerCase();
                const phone = (s.mobile || '').toLowerCase();
                return name.includes(q) || phone.includes(q);
              })}
              keyExtractor={(item) => String(item.id)}
              renderItem={({ item }) => (
                <TouchableOpacity
                  style={[
                    styles.customerItem,
                    selectedSeller?.id === item.id && styles.customerItemActive
                  ]}
                  onPress={() => {
                    setSelectedSeller(item);
                    setShowSellerModal(false);
                  }}
                >
                  <Text style={styles.customerName}>
                    {item.name}
                  </Text>
                  <Text style={styles.customerPhone}>{item.mobile}</Text>
                </TouchableOpacity>
              )}
            />
          </View>
        </View>
      </Modal>

      {/* Add New Supplier Modal */}
      <Modal visible={showAddSellerModal} transparent animationType="slide">
        <KeyboardAvoidingView
          behavior={Platform.OS === 'ios' ? 'padding' : undefined}
          style={styles.modalOverlay}
        >
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Add New Supplier</Text>
              <TouchableOpacity onPress={() => setShowAddSellerModal(false)}>
                <Text style={styles.modalCloseText}>✕</Text>
              </TouchableOpacity>
            </View>

            <View style={{ padding: 16 }}>
              <Text style={styles.inputLabel}>Supplier Name *</Text>
              <TextInput
                style={styles.modalInput}
                value={newSellerName}
                onChangeText={setNewSellerName}
                placeholder="Enter supplier name"
                placeholderTextColor="#666"
              />

              <Text style={[styles.inputLabel, { marginTop: 12 }]}>Mobile Number *</Text>
              <TextInput
                style={styles.modalInput}
                keyboardType="phone-pad"
                value={newSellerPhone}
                onChangeText={setNewSellerPhone}
                placeholder="10-digit mobile number"
                placeholderTextColor="#666"
                maxLength={10}
              />

              <TouchableOpacity
                style={styles.addCustomerSubmitBtn}
                onPress={handleAddNewSeller}
              >
                <Text style={styles.addCustomerSubmitBtnText}>Add & Select Supplier</Text>
              </TouchableOpacity>
            </View>
          </View>
        </KeyboardAvoidingView>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0a0a0a' },
  headerTitle: { color: '#d4af37', fontSize: 18, fontWeight: 'bold', marginBottom: 16 },
  
  topSummaryRow: {
    flexDirection: 'row',
    backgroundColor: '#141414',
    borderWidth: 1,
    borderColor: '#262626',
    borderRadius: 8,
    padding: 12,
    marginBottom: 16
  },
  topSummaryCol: { flex: 1, alignItems: 'center' },
  topSummaryLbl: { color: '#888', fontSize: 10, textTransform: 'uppercase', marginBottom: 2 },
  topSummaryVal: { color: '#fff', fontSize: 15, fontWeight: 'bold', fontVariant: ['tabular-nums'] },

  card: { backgroundColor: '#141414', padding: 16, borderRadius: 8, borderWidth: 1, borderColor: '#262626', marginBottom: 16 },
  cardTitle: { color: '#d4af37', fontSize: 14, fontWeight: 'bold', textTransform: 'uppercase', marginBottom: 12 },
  sectionHeaderTitle: { color: '#888', fontSize: 11, fontWeight: 'bold', textTransform: 'uppercase', marginBottom: 10 },
  
  gstOptionsRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  gstOptionBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    backgroundColor: '#1a1a1a',
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#333'
  },
  gstOptionBtnActive: { borderColor: '#d4af37', backgroundColor: 'rgba(212, 175, 55, 0.1)' },
  gstOptionText: { color: '#888', fontSize: 12 },
  gstOptionTextActive: { color: '#fff', fontWeight: 'bold' },

  metalBlock: { marginBottom: 16 },
  metalReq: { color: '#fff', fontSize: 13, fontWeight: 'bold', marginBottom: 8 },
  row: { flexDirection: 'row', gap: 8 },
  col: { flex: 1 },
  lbl: { color: '#888', fontSize: 10, textTransform: 'uppercase', marginBottom: 4, fontWeight: 'bold' },
  inputSmall: {
    backgroundColor: '#0a0a0a',
    color: '#d4af37',
    borderWidth: 1,
    borderColor: '#333',
    borderRadius: 6,
    paddingVertical: 6,
    paddingHorizontal: 8,
    fontSize: 14,
    fontVariant: ['tabular-nums']
  },
  valText: { color: '#fff', fontSize: 13, fontVariant: ['tabular-nums'] },
  valTextGreen: { color: '#4ade80', fontSize: 13, fontWeight: 'bold', fontVariant: ['tabular-nums'] },
  remText: { color: '#ef4444', fontSize: 11, marginTop: 4, fontVariant: ['tabular-nums'] },

  cashReceivedSection: {
    marginTop: 16,
    borderTopWidth: 1,
    borderTopColor: '#262626',
    paddingTop: 16,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start'
  },
  monetaryVal: { color: '#fff', fontSize: 18, fontWeight: 'bold', fontVariant: ['tabular-nums'] },
  subtext: { color: '#666', fontSize: 10, marginTop: 2 },
  quickFillBtn: {
    backgroundColor: 'rgba(34,197,94,0.2)',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
    borderWidth: 1,
    borderColor: '#22c55e'
  },
  quickFillText: { fontSize: 9, color: '#4ade80', fontWeight: 'bold' },
  inputLarge: {
    backgroundColor: '#0a0a0a',
    color: '#4ade80',
    borderWidth: 1,
    borderColor: '#166534',
    borderRadius: 6,
    paddingVertical: 8,
    paddingHorizontal: 10,
    fontSize: 18,
    fontWeight: 'bold',
    fontVariant: ['tabular-nums']
  },
  paymentMethods: { flexDirection: 'row', gap: 6, marginTop: 8 },
  payBtn: {
    flex: 1,
    paddingVertical: 6,
    alignItems: 'center',
    borderRadius: 4,
    borderWidth: 1,
    borderColor: '#333',
    backgroundColor: '#1a1a1a'
  },
  payBtnActive: { borderColor: '#4ade80', backgroundColor: 'rgba(74, 222, 128, 0.1)' },
  payBtnText: { color: '#888', fontSize: 11 },
  payBtnTextActive: { color: '#4ade80', fontWeight: 'bold' },

  summaryCard: {
    backgroundColor: '#141414',
    padding: 16,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: 'rgba(212, 175, 55, 0.3)',
    marginBottom: 16
  },
  finalSummaryBox: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#1a1a1a',
    padding: 12,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#333'
  },
  finalCashText: { fontSize: 18, fontWeight: 'bold', fontVariant: ['tabular-nums'] },
  settlePrompt: { color: '#888', fontSize: 10, textTransform: 'uppercase', fontWeight: 'bold', marginBottom: 8 },

  actionBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    backgroundColor: '#1a1a1a',
    padding: 12,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#333',
    marginBottom: 8
  },
  actionBtnActive: { borderColor: '#d4af37', backgroundColor: 'rgba(212, 175, 55, 0.08)' },
  actionBtnText: { color: '#fff', fontSize: 13, fontWeight: 'bold' },
  actionSubText: { color: '#888', fontSize: 11, marginTop: 2 },

  radioCircle: {
    width: 18,
    height: 18,
    borderRadius: 9,
    borderWidth: 2,
    borderColor: '#555',
    alignItems: 'center',
    justifyContent: 'center'
  },
  radioCircleActive: { borderColor: '#d4af37' },
  radioInner: { width: 10, height: 10, borderRadius: 5, backgroundColor: '#d4af37' },

  submitButton: { backgroundColor: '#d4af37', padding: 16, borderRadius: 8, alignItems: 'center' },
  submitButtonText: { color: '#000', fontSize: 16, fontWeight: 'bold' },

  cashSectionContainer: {
    marginTop: 16,
    borderTopWidth: 1,
    borderTopColor: '#262626',
    paddingTop: 16,
    gap: 12
  },
  payableBox: {
    backgroundColor: '#0d0d10',
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#222',
  },
  cashPaidBox: {
    backgroundColor: '#0d0d10',
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#166534',
  },
  newCustBtn: {
    backgroundColor: 'rgba(212, 175, 55, 0.15)',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 4,
    borderWidth: 1,
    borderColor: '#d4af37',
  },
  newCustBtnText: {
    color: '#d4af37',
    fontSize: 10,
    fontWeight: '700',
  },
  customerSelector: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#18181f',
    borderWidth: 1,
    borderColor: '#333',
    borderRadius: 6,
    padding: 10,
  },
  customerSelectorText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
  },
  custWarningText: {
    color: '#777',
    fontSize: 9,
    marginTop: 4,
    fontStyle: 'italic',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.7)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: '#121216',
    borderTopLeftRadius: 16,
    borderTopRightRadius: 16,
    maxHeight: '80%',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#222',
  },
  modalTitle: {
    color: '#d4af37',
    fontSize: 15,
    fontWeight: '800',
  },
  modalCloseText: {
    color: '#aaa',
    fontSize: 16,
    fontWeight: '700',
  },
  modalSearchInput: {
    backgroundColor: '#1c1c24',
    borderWidth: 1,
    borderColor: '#333',
    borderRadius: 8,
    color: '#fff',
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 13,
  },
  customerItem: {
    padding: 14,
    borderBottomWidth: 1,
    borderBottomColor: '#1a1a22',
  },
  customerItemActive: {
    backgroundColor: 'rgba(212, 175, 55, 0.1)',
  },
  customerName: {
    color: '#fff',
    fontSize: 13,
    fontWeight: '700',
  },
  customerPhone: {
    color: '#777',
    fontSize: 11,
    marginTop: 2,
  },
  inputLabel: {
    color: '#aaa',
    fontSize: 11,
    fontWeight: '700',
    marginBottom: 4,
  },
  modalInput: {
    backgroundColor: '#1c1c24',
    borderWidth: 1,
    borderColor: '#333',
    borderRadius: 6,
    color: '#fff',
    paddingHorizontal: 12,
    paddingVertical: 8,
    fontSize: 13,
  },
  addCustomerSubmitBtn: {
    backgroundColor: '#d4af37',
    borderRadius: 6,
    paddingVertical: 12,
    alignItems: 'center',
    marginTop: 18,
  },
  addCustomerSubmitBtnText: {
    color: '#000',
    fontWeight: '800',
    fontSize: 13,
  },
});
