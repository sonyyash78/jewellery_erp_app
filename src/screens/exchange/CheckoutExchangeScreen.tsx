import React, { useState, useMemo, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  ScrollView,
  Alert,
  ActivityIndicator,
  Modal,
  FlatList,
  KeyboardAvoidingView,
  Platform
} from 'react-native';
import { axiosClient } from '../../api/axiosClient';
import * as Print from 'expo-print';
import { generateInvoiceHtml } from '../../utils/invoicePdfUtils';

export default function CheckoutExchangeScreen({ route, navigation }: any) {
  const { selectedCustomer: initialCustomer, items } = route.params;

  // Customers state for picker modal
  const [selectedCustomer, setSelectedCustomer] = useState<any>(initialCustomer || null);
  const [customers, setCustomers] = useState<any[]>([]);
  const [showCustomerModal, setShowCustomerModal] = useState(false);
  const [showAddCustomerModal, setShowAddCustomerModal] = useState(false);
  const [newCustomerFirstName, setNewCustomerFirstName] = useState('');
  const [newCustomerPhone, setNewCustomerPhone] = useState('');

  useEffect(() => {
    fetchCustomers();
  }, []);

  const fetchCustomers = async () => {
    try {
      const response = await axiosClient.get('/customers/');
      setCustomers(response.data.items || response.data || []);
    } catch (error) {
      console.log('Failed to fetch customers', error);
    }
  };

  const handleAddNewCustomer = async () => {
    if (!newCustomerFirstName) {
      Alert.alert('Error', 'Please enter a name');
      return;
    }
    const cleanedPhone = newCustomerPhone.replace(/\D/g, '');
    if (cleanedPhone.length !== 10 && cleanedPhone.length !== 12) {
      Alert.alert('Error', 'Mobile number must be exactly 10 digits');
      return;
    }
    try {
      const response = await axiosClient.post('/customers/', {
        first_name: newCustomerFirstName,
        phone_number: cleanedPhone
      });
      const newCust = response.data;
      setCustomers([newCust, ...customers]);
      setSelectedCustomer(newCust);
      setShowAddCustomerModal(false);
      setShowCustomerModal(false);
      setNewCustomerFirstName('');
      setNewCustomerPhone('');
    } catch (error) {
      Alert.alert('Error', 'Failed to add customer');
    }
  };

  // Split items
  const oldItemsRaw = useMemo(() => (items || []).filter((i: any) => i.direction === 'Old'), [items]);
  const newItemsRaw = useMemo(() => (items || []).filter((i: any) => i.direction === 'New'), [items]);

  const total_old_value = useMemo(() => oldItemsRaw.reduce((sum: number, i: any) => sum + (Number(i.final_price) || 0), 0), [oldItemsRaw]);
  const total_new_value = useMemo(() => newItemsRaw.reduce((sum: number, i: any) => sum + (Number(i.final_price) || 0), 0), [newItemsRaw]);

  // GST options
  const [gstType, setGstType] = useState<'same' | 'inter' | 'none'>('same');
  let gstAmount = 0;
  if (gstType === 'same' || gstType === 'inter') {
    gstAmount = total_new_value * 0.03;
  }
  const grand_total = total_new_value + gstAmount;

  // Fine metal calculations from new and old carts
  const { totalNewGoldFine, totalNewSilverFine, totalOldGoldFine, totalOldSilverFine, goldRate, silverRate } = useMemo(() => {
    let tgNew = 0, tsNew = 0, tgOld = 0, tsOld = 0, gr = 0, sr = 0;

    newItemsRaw.forEach((item: any) => {
      if (item.item_type === 'Gold') {
        tgNew += (item.gold_calculation?.fine_weight || item.net_weight || 0);
        if (!gr) gr = item.gold_calculation?.applied_rate || 0;
      } else if (item.item_type === 'Silver') {
        tsNew += (item.silver_calculation?.pure_weight || item.net_weight || 0);
        if (!sr) sr = item.silver_calculation?.applied_rate || 0;
      }
    });

    oldItemsRaw.forEach((item: any) => {
      if (item.item_type === 'Gold') {
        tgOld += (item.gold_calculation?.fine_weight || item.net_weight || 0);
        if (!gr) gr = item.gold_calculation?.applied_rate || 0;
      } else if (item.item_type === 'Silver') {
        tsOld += (item.silver_calculation?.pure_weight || item.net_weight || 0);
        if (!sr) sr = item.silver_calculation?.applied_rate || 0;
      }
    });

    return {
      totalNewGoldFine: tgNew,
      totalNewSilverFine: tsNew,
      totalOldGoldFine: tgOld,
      totalOldSilverFine: tsOld,
      goldRate: gr || 72500,
      silverRate: sr || 90000
    };
  }, [newItemsRaw, oldItemsRaw]);

  // Required metal from customer
  const goldRequired = Math.max(0, totalNewGoldFine - totalOldGoldFine);
  const silverRequired = Math.max(0, totalNewSilverFine - totalOldSilverFine);

  const hasGold = totalNewGoldFine > 0 || totalOldGoldFine > 0 || goldRequired > 0;
  const hasSilver = totalNewSilverFine > 0 || totalOldSilverFine > 0 || silverRequired > 0;

  // Additional Metal Given by customer in Checkout
  const [goldGiven, setGoldGiven] = useState('');
  const [goldGivenTanch, setGoldGivenTanch] = useState('100');
  const [silverGiven, setSilverGiven] = useState('');
  const [silverGivenTanch, setSilverGivenTanch] = useState('100');

  const [cashReceived, setCashReceived] = useState('');
  const [paymentMethod, setPaymentMethod] = useState<'CASH' | 'UPI' | 'CHEQUE'>('CASH');
  const [cashBalanceAction, setCashBalanceAction] = useState<'cash' | 'metal_gold' | 'metal_silver' | 'metal_both'>('cash');

  const [submitting, setSubmitting] = useState(false);

  // Compute additional metal values
  const parsedGoldGiven = parseFloat(goldGiven) || 0;
  const parsedGoldTanch = parseFloat(goldGivenTanch) || 100;
  const fineGoldGiven = parsedGoldGiven * (parsedGoldTanch / 100);
  const goldValueGiven = fineGoldGiven * (goldRate / 10);

  const parsedSilverGiven = parseFloat(silverGiven) || 0;
  const parsedSilverTanch = parseFloat(silverGivenTanch) || 100;
  const fineSilverGiven = parsedSilverGiven * (parsedSilverTanch / 100);
  const silverValueGiven = fineSilverGiven * (silverRate / 1000);

  const totalAdditionalMetalValue = goldValueGiven + silverValueGiven;

  // Net monetary balance before cash
  // Grand Total (New Items + GST) - Old Items Total - Additional Metal Given
  const monetaryBeforeCash = grand_total - total_old_value - totalAdditionalMetalValue;
  const parsedCash = parseFloat(cashReceived) || 0;
  const cashBalanceDue = Math.max(0, monetaryBeforeCash - parsedCash);

  // Settlement Options (How to settle cash due)
  // Option 2: Convert entire remaining cash balance to Gold Ledger
  const cashToGoldGrams = goldRate > 0 ? (cashBalanceDue / (goldRate / 10)) : 0;
  const cashDueAfterGold = 0;

  // Option 3: Convert entire remaining cash balance to Silver Ledger
  const cashToSilverGrams = silverRate > 0 ? (cashBalanceDue / (silverRate / 1000)) : 0;
  const cashDueAfterSilver = 0;

  // Option 4: Convert both metals (satisfy gold required first if any, remainder to silver)
  let bothGoldGrams = 0;
  let bothSilverGrams = 0;
  if (goldRequired > 0 && goldRate > 0) {
    const goldReqVal = goldRequired * (goldRate / 10);
    if (cashBalanceDue <= goldReqVal) {
      bothGoldGrams = cashBalanceDue / (goldRate / 10);
      bothSilverGrams = 0;
    } else {
      bothGoldGrams = goldRequired;
      const remCash = cashBalanceDue - goldReqVal;
      bothSilverGrams = silverRate > 0 ? (remCash / (silverRate / 1000)) : 0;
    }
  } else {
    // 50/50 split if no specific gold requirement
    const halfCash = cashBalanceDue / 2;
    bothGoldGrams = goldRate > 0 ? (halfCash / (goldRate / 10)) : 0;
    bothSilverGrams = silverRate > 0 ? (halfCash / (silverRate / 1000)) : 0;
  }
  const cashDueAfterBoth = 0;

  let finalGoldDebt = 0;
  let finalSilverDebt = 0;
  let finalBalanceAmount = cashBalanceDue;

  if (cashBalanceAction === 'metal_gold') {
    finalGoldDebt = cashToGoldGrams;
    finalSilverDebt = 0;
    finalBalanceAmount = cashDueAfterGold;
  } else if (cashBalanceAction === 'metal_silver') {
    finalGoldDebt = 0;
    finalSilverDebt = cashToSilverGrams;
    finalBalanceAmount = cashDueAfterSilver;
  } else if (cashBalanceAction === 'metal_both') {
    finalGoldDebt = bothGoldGrams;
    finalSilverDebt = bothSilverGrams;
    finalBalanceAmount = cashDueAfterBoth;
  } else {
    finalGoldDebt = 0;
    finalSilverDebt = 0;
    finalBalanceAmount = cashBalanceDue;
  }

  const isFullySettled = finalBalanceAmount < 0.01 && finalGoldDebt === 0 && finalSilverDebt === 0;

  const fmt = (n?: any) => {
    const num = Number(n);
    if (isNaN(num)) return '0.00';
    return num.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  };

  const executeSettle = async (andPrint: boolean = false) => {
    if (!isFullySettled && !selectedCustomer) {
      Alert.alert('Error', 'A customer must be selected for outstanding balances.');
      return;
    }

    try {
      setSubmitting(true);

      const oldItemsPayload = oldItemsRaw.map((i: any) => {
        const isGold = i.item_type === 'Gold';
        const calc = isGold ? i.gold_calculation : i.silver_calculation;
        return {
          item_name: i.item_name,
          metal: i.item_type,
          purity: String(calc?.touch_purity || calc?.tanch_percentage || '100'),
          touch: Number(calc?.touch_purity || calc?.tanch_percentage || 100),
          gross_weight: Number(calc?.gross_weight || i.gross_weight || 0),
          stone_weight: Number(calc?.stone_weight || 0),
          net_weight: Number(calc?.net_weight || 0),
          wastage: Number(calc?.wastage || 0),
          fine_weight: Number(calc?.fine_weight || calc?.pure_weight || 0),
          labour_charge: Number(calc?.making_charges_amount || 0),
          testing_melting_charge: 0,
          hallmark_charge: Number(calc?.hallmark_charges || 0),
          other_charges: Number(calc?.other_charges || 0),
          discount: Number(calc?.discount || 0),
          rate_applied: Number(calc?.applied_rate || (isGold ? goldRate : silverRate) || 0),
          calculated_value: Number(i.final_price || 0)
        };
      });

      // If additional metal given in checkout, append to old items
      if (parsedGoldGiven > 0) {
        oldItemsPayload.push({
          item_name: 'Metal Given (Gold)',
          metal: 'Gold',
          purity: String(parsedGoldTanch),
          touch: parsedGoldTanch,
          gross_weight: parsedGoldGiven,
          stone_weight: 0,
          net_weight: parsedGoldGiven,
          wastage: 0,
          fine_weight: fineGoldGiven,
          labour_charge: 0,
          testing_melting_charge: 0,
          hallmark_charge: 0,
          other_charges: 0,
          discount: 0,
          rate_applied: goldRate,
          calculated_value: goldValueGiven
        });
      }

      if (parsedSilverGiven > 0) {
        oldItemsPayload.push({
          item_name: 'Metal Given (Silver)',
          metal: 'Silver',
          purity: String(parsedSilverTanch),
          touch: parsedSilverTanch,
          gross_weight: parsedSilverGiven,
          stone_weight: 0,
          net_weight: parsedSilverGiven,
          wastage: 0,
          fine_weight: fineSilverGiven,
          labour_charge: 0,
          testing_melting_charge: 0,
          hallmark_charge: 0,
          other_charges: 0,
          discount: 0,
          rate_applied: silverRate,
          calculated_value: silverValueGiven
        });
      }

      const newItemsPayload = newItemsRaw.map((i: any) => {
        const isGold = i.item_type === 'Gold';
        const calc = isGold ? i.gold_calculation : i.silver_calculation;
        return {
          item_name: i.item_name,
          metal: i.item_type,
          stock_item_id: i.stock_item_id || null,
          gross_weight: Number(calc?.gross_weight || i.gross_weight || 0),
          stone_weight: Number(calc?.stone_weight || 0),
          net_weight: Number(calc?.net_weight || 0),
          touch_purity: Number(calc?.touch_purity || calc?.tanch_percentage || 100),
          wastage: Number(calc?.wastage || 0),
          fine_weight: Number(calc?.fine_weight || calc?.pure_weight || 0),
          making_charge_type: calc?.making_charge_type || 'flat',
          making_charge_rate: Number(calc?.making_charge_rate || 0),
          making_charges_amount: Number(calc?.making_charges_amount || 0),
          hallmark_charges: Number(calc?.hallmark_charges || 0),
          other_charges: Number(calc?.other_charges || 0),
          discount: Number(calc?.discount || 0),
          rate_applied: Number(calc?.applied_rate || (isGold ? goldRate : silverRate) || 0),
          final_price: Number(i.final_price || 0)
        };
      });

      const backendSettlementType = cashBalanceAction !== 'cash' ? 'Metal' : 'Cash';

      const payload = {
        customer_id: selectedCustomer?.id || null,
        amount_paid: parsedCash,
        total_old_value: total_old_value + totalAdditionalMetalValue,
        total_new_value: total_new_value,
        gst_amount: gstAmount,
        grand_total: grand_total,
        difference_amount: monetaryBeforeCash,

        settlement_type: backendSettlementType,
        balance_amount: Math.max(0, finalBalanceAmount),
        gold_balance_metal_weight: finalGoldDebt,
        silver_balance_metal_weight: finalSilverDebt,

        old_items: oldItemsPayload,
        new_items: newItemsPayload
      };

      const response = await axiosClient.post('/exchanges/', payload);
      const exchangeId = response.data.id;

      if (andPrint) {
        try {
          const [pdfRes, settingsRes] = await Promise.all([
            axiosClient.get(`/exchanges/${exchangeId}/pdf-data`),
            axiosClient.get('/settings/').catch(() => ({ data: {} })),
          ]);
          const fullPdfData = {
            ...pdfRes.data,
            settings: { ...(pdfRes.data?.settings || {}), ...(settingsRes.data || {}) },
          };
          const html = generateInvoiceHtml(fullPdfData);
          await Print.printAsync({ html });
        } catch (printErr) {
          console.error('Print failed', printErr);
        }
      }

      Alert.alert('Success', `Exchange EXC-${exchangeId} recorded successfully!`);
      navigation.popToTop();
      navigation.navigate('Exchange');
    } catch (error: any) {
      console.log('Checkout failed', error?.response?.data || error);
      Alert.alert('Error', error?.response?.data?.detail || 'Failed to submit exchange');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <View style={styles.container}>
      <ScrollView contentContainerStyle={{ padding: 16, paddingBottom: 100 }}>
        
        {/* Top Summary Accordion / Card */}
        <View style={styles.card}>
          <Text style={styles.cardHeaderTitle}>EXCHANGE SUMMARY</Text>
          <View style={styles.summaryRow}>
            <Text style={styles.summaryLabel}>New Items Value (To Customer):</Text>
            <Text style={styles.summaryValue}>₹ {fmt(total_new_value)}</Text>
          </View>
          <View style={styles.summaryRow}>
            <Text style={styles.summaryLabel}>GST on New Items (3%):</Text>
            <Text style={styles.summaryValue}>₹ {fmt(gstAmount)}</Text>
          </View>
          <View style={styles.summaryRow}>
            <Text style={styles.summaryLabel}>Total Old Value (Trade-in):</Text>
            <Text style={[styles.summaryValue, { color: '#f97316' }]}>- ₹ {fmt(total_old_value)}</Text>
          </View>
          <View style={[styles.summaryRow, styles.dividerRow]}>
            <Text style={styles.grandTotalLabel}>Net Difference:</Text>
            <Text style={[styles.grandTotalValue, { color: (grand_total - total_old_value) >= 0 ? '#d4af37' : '#4ade80' }]}>
              ₹ {fmt(grand_total - total_old_value)}
            </Text>
          </View>
        </View>

        {/* GST Options */}
        <View style={styles.card}>
          <Text style={styles.sectionHeaderTitle}>GST OPTIONS</Text>
          <View style={styles.gstOptionsRow}>
            {[
              { label: 'Same State (3%)', val: 'same' },
              { label: 'Interstate (3%)', val: 'inter' },
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
          <Text style={styles.sectionHeaderTitle}>METAL RECEIVED FROM CUSTOMER</Text>

          {oldItemsRaw.length > 0 && (
            <View style={{ backgroundColor: '#18181b', padding: 10, borderRadius: 6, marginBottom: 12, borderWidth: 1, borderColor: '#333' }}>
              <Text style={{ color: '#d4af37', fontSize: 11, fontWeight: '700', marginBottom: 4 }}>
                ✓ OLD ITEMS DEPOSITED IN CART ({oldItemsRaw.length} Items):
              </Text>
              <Text style={{ color: '#aaa', fontSize: 10 }}>
                Gold Fine: <Text style={{ color: '#eab308', fontWeight: '700' }}>{totalOldGoldFine.toFixed(3)}g</Text> | Silver Fine: <Text style={{ color: '#e2e8f0', fontWeight: '700' }}>{totalOldSilverFine.toFixed(3)}g</Text> | Trade-in Value: <Text style={{ color: '#4ade80', fontWeight: '700' }}>₹ {fmt(total_old_value)}</Text>
              </Text>
            </View>
          )}

          <Text style={{ color: '#888', fontSize: 10, marginBottom: 8, fontStyle: 'italic' }}>
            Enter below only if customer is handing over additional metal right now at checkout:
          </Text>

          {/* Gold Row */}
          <View style={styles.metalItemBlock}>
            <View style={styles.metalHeaderLine}>
              <Text style={styles.metalRequiredTitle}>
                GOLD REQUIRED @ ₹{goldRate.toLocaleString('en-IN')}/10G
              </Text>
              <Text style={styles.metalRequiredGrams}>{goldRequired.toFixed(3)} g</Text>
            </View>

            <View style={styles.gridRow}>
              <View style={styles.gridCol}>
                <Text style={styles.gridLabel}>GROSS GIVEN</Text>
                <TextInput
                  style={styles.gridInput}
                  keyboardType="numeric"
                  value={goldGiven}
                  onChangeText={setGoldGiven}
                  placeholder="0.000"
                  placeholderTextColor="#666"
                />
              </View>
              <View style={styles.gridCol}>
                <Text style={styles.gridLabel}>TANCH %</Text>
                <TextInput
                  style={styles.gridInput}
                  keyboardType="numeric"
                  value={goldGivenTanch}
                  onChangeText={setGoldGivenTanch}
                  placeholder="100"
                  placeholderTextColor="#666"
                />
              </View>
              <View style={styles.gridCol}>
                <Text style={styles.gridLabel}>FINE METAL</Text>
                <Text style={styles.gridValGold}>{fineGoldGiven.toFixed(3)} g</Text>
              </View>
              <View style={styles.gridCol}>
                <Text style={styles.gridLabel}>VALUE</Text>
                <Text style={styles.gridValGreen}>₹ {fmt(goldValueGiven)}</Text>
              </View>
            </View>
          </View>

          {/* Silver Row */}
          <View style={[styles.metalItemBlock, { borderTopWidth: 1, borderTopColor: '#222', paddingTop: 12, marginTop: 12 }]}>
            <View style={styles.metalHeaderLine}>
              <Text style={styles.metalRequiredTitle}>
                SILVER REQUIRED @ ₹{silverRate.toLocaleString('en-IN')}/KG
              </Text>
              <Text style={styles.metalRequiredGrams}>{silverRequired.toFixed(3)} g</Text>
            </View>

            <View style={styles.gridRow}>
              <View style={styles.gridCol}>
                <Text style={styles.gridLabel}>GROSS GIVEN</Text>
                <TextInput
                  style={styles.gridInput}
                  keyboardType="numeric"
                  value={silverGiven}
                  onChangeText={setSilverGiven}
                  placeholder="0.000"
                  placeholderTextColor="#666"
                />
              </View>
              <View style={styles.gridCol}>
                <Text style={styles.gridLabel}>TANCH %</Text>
                <TextInput
                  style={styles.gridInput}
                  keyboardType="numeric"
                  value={silverGivenTanch}
                  onChangeText={setSilverGivenTanch}
                  placeholder="100"
                  placeholderTextColor="#666"
                />
              </View>
              <View style={styles.gridCol}>
                <Text style={styles.gridLabel}>FINE METAL</Text>
                <Text style={styles.gridValSilver}>{fineSilverGiven.toFixed(3)} g</Text>
              </View>
              <View style={styles.gridCol}>
                <Text style={styles.gridLabel}>VALUE</Text>
                <Text style={styles.gridValGreen}>₹ {fmt(silverValueGiven)}</Text>
              </View>
            </View>
          </View>

          {/* Monetary Balance & Cash Received */}
          <View style={styles.cashSectionRow}>
            <View style={{ flex: 1 }}>
              <Text style={styles.gridLabel}>MONETARY BALANCE (AFTER METAL)</Text>
              <Text style={styles.monetaryAmountText}>₹ {fmt(monetaryBeforeCash)}</Text>
              <Text style={styles.monetarySubText}>
                ₹{fmt(grand_total - total_old_value)} − ₹{fmt(totalAdditionalMetalValue)} metal
              </Text>
            </View>

            <View style={{ flex: 1 }}>
              <Text style={[styles.gridLabel, { color: '#4ade80' }]}>CASH RECEIVED</Text>
              <TextInput
                style={styles.cashInput}
                keyboardType="numeric"
                value={cashReceived}
                onChangeText={setCashReceived}
                placeholder="0"
                placeholderTextColor="#666"
              />
              <View style={styles.paymentMethodPills}>
                {(['CASH', 'UPI', 'CHEQUE'] as const).map(mode => (
                  <TouchableOpacity
                    key={mode}
                    style={[styles.pillBtn, paymentMethod === mode && styles.pillBtnActive]}
                    onPress={() => setPaymentMethod(mode)}
                  >
                    <View style={[styles.pillRadio, paymentMethod === mode && styles.pillRadioActive]} />
                    <Text style={[styles.pillText, paymentMethod === mode && styles.pillTextActive]}>
                      {mode}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>
          </View>
        </View>

        {/* FINAL SETTLEMENT SUMMARY */}
        <View style={styles.settlementSummaryCard}>
          <Text style={styles.settlementSummaryTitle}>FINAL SETTLEMENT SUMMARY</Text>

          <View style={styles.finalCashDueBox}>
            <Text style={styles.finalCashDueLabel}>Final Cash Due:</Text>
            <Text style={[styles.finalCashDueValue, { color: finalBalanceAmount > 0 ? '#ef4444' : '#4ade80' }]}>
              ₹ {fmt(Math.abs(finalBalanceAmount))}
            </Text>
          </View>

          {cashBalanceDue > 0 && (
            <View style={{ marginTop: 12 }}>
              <Text style={styles.settleChoicePrompt}>
                HOW TO SETTLE THE ₹ {fmt(cashBalanceDue)} CASH DUE?
              </Text>

              {/* Option 1 */}
              <TouchableOpacity
                style={[styles.settleOptionBox, cashBalanceAction === 'cash' && styles.settleOptionBoxActive]}
                onPress={() => setCashBalanceAction('cash')}
              >
                <View style={[styles.radioCircle, cashBalanceAction === 'cash' && styles.radioCircleActive]}>
                  {cashBalanceAction === 'cash' && <View style={styles.radioInner} />}
                </View>
                <Text style={styles.settleOptionText}>
                  Keep as Cash Due — pay ₹ {fmt(cashBalanceDue)} later
                </Text>
              </TouchableOpacity>

              {/* Option 2 (Gold) */}
              <TouchableOpacity
                style={[styles.settleOptionBox, cashBalanceAction === 'metal_gold' && styles.settleOptionBoxActive]}
                onPress={() => setCashBalanceAction('metal_gold')}
              >
                <View style={[styles.radioCircle, cashBalanceAction === 'metal_gold' && styles.radioCircleActive]}>
                  {cashBalanceAction === 'metal_gold' && <View style={styles.radioInner} />}
                </View>
                <View>
                  <Text style={styles.settleOptionText}>Convert Metal to Gold Ledger</Text>
                  <Text style={styles.settleOptionSubGold}>
                    +{cashToGoldGrams.toFixed(3)} g Gold | ₹ {fmt(cashDueAfterGold)} Cash Due
                  </Text>
                </View>
              </TouchableOpacity>

              {/* Option 3 (Silver) */}
              <TouchableOpacity
                style={[styles.settleOptionBox, cashBalanceAction === 'metal_silver' && styles.settleOptionBoxActive]}
                onPress={() => setCashBalanceAction('metal_silver')}
              >
                <View style={[styles.radioCircle, cashBalanceAction === 'metal_silver' && styles.radioCircleActive]}>
                  {cashBalanceAction === 'metal_silver' && <View style={styles.radioInner} />}
                </View>
                <View>
                  <Text style={styles.settleOptionText}>Convert Metal to Silver Ledger</Text>
                  <Text style={styles.settleOptionSubSilver}>
                    +{cashToSilverGrams.toFixed(3)} g Silver | ₹ {fmt(cashDueAfterSilver)} Cash Due
                  </Text>
                </View>
              </TouchableOpacity>

              {/* Option 4 (Both) */}
              <TouchableOpacity
                style={[styles.settleOptionBox, cashBalanceAction === 'metal_both' && styles.settleOptionBoxActive]}
                onPress={() => setCashBalanceAction('metal_both')}
              >
                <View style={[styles.radioCircle, cashBalanceAction === 'metal_both' && styles.radioCircleActive]}>
                  {cashBalanceAction === 'metal_both' && <View style={styles.radioInner} />}
                </View>
                <View>
                  <Text style={styles.settleOptionText}>Convert Both Metals to Ledgers</Text>
                  <Text style={styles.settleOptionSubGold}>
                    Gold: +{bothGoldGrams.toFixed(3)} g | Silver: +{bothSilverGrams.toFixed(3)} g | ₹ {fmt(cashDueAfterBoth)} Cash Due
                  </Text>
                </View>
              </TouchableOpacity>
            </View>
          )}
        </View>

        {/* SELECT CUSTOMER */}
        <View style={styles.card}>
          <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
            <Text style={styles.sectionHeaderTitle}>SELECT CUSTOMER</Text>
            <TouchableOpacity style={styles.newCustBtn} onPress={() => setShowAddCustomerModal(true)}>
              <Text style={styles.newCustBtnText}>+ New</Text>
            </TouchableOpacity>
          </View>

          <TouchableOpacity style={styles.customerSelector} onPress={() => setShowCustomerModal(true)}>
            <Text style={styles.customerSelectorText}>
              {selectedCustomer
                ? `${selectedCustomer.first_name} ${selectedCustomer.last_name || ''} (${selectedCustomer.phone_number})`
                : '-- Walk-in Customer --'}
            </Text>
            <Text style={{ color: '#d4af37', fontSize: 14 }}>▼</Text>
          </TouchableOpacity>
          <Text style={styles.custWarningText}>* A customer must be selected for outstanding balances.</Text>
        </View>

        {/* Bottom Action Buttons */}
        <View style={styles.actionButtonsRow}>
          <TouchableOpacity
            style={styles.cancelBtn}
            onPress={() => navigation.goBack()}
            disabled={submitting}
          >
            <Text style={styles.cancelBtnText}>Cancel</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.saveOnlyBtn, submitting && { opacity: 0.6 }]}
            onPress={() => executeSettle(false)}
            disabled={submitting}
          >
            {submitting ? (
              <ActivityIndicator color="#d4af37" size="small" />
            ) : (
              <Text style={styles.saveOnlyBtnText}>SAVE ONLY</Text>
            )}
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.savePrintBtn, submitting && { opacity: 0.6 }]}
            onPress={() => executeSettle(true)}
            disabled={submitting}
          >
            {submitting ? (
              <ActivityIndicator color="#000" size="small" />
            ) : (
              <Text style={styles.savePrintBtnText}>✓ SAVE & PRINT</Text>
            )}
          </TouchableOpacity>
        </View>

      </ScrollView>

      {/* Customer Picker Modal */}
      <Modal visible={showCustomerModal} animationType="slide" transparent={true}>
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Select Customer</Text>
            <TouchableOpacity style={styles.addNewCustModalBtn} onPress={() => { setShowCustomerModal(false); setShowAddCustomerModal(true); }}>
              <Text style={styles.addNewCustModalBtnText}>+ Add New Customer</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.customerOptionItem} onPress={() => { setSelectedCustomer(null); setShowCustomerModal(false); }}>
              <Text style={styles.customerOptionText}>-- Walk-in Customer --</Text>
            </TouchableOpacity>
            <FlatList
              data={customers}
              keyExtractor={(item) => item.id.toString()}
              renderItem={({ item }) => (
                <TouchableOpacity
                  style={styles.customerOptionItem}
                  onPress={() => {
                    setSelectedCustomer(item);
                    setShowCustomerModal(false);
                  }}
                >
                  <Text style={styles.customerOptionText}>
                    {item.first_name} {item.last_name || ''} ({item.phone_number})
                  </Text>
                </TouchableOpacity>
              )}
            />
            <TouchableOpacity style={styles.modalCloseBtn} onPress={() => setShowCustomerModal(false)}>
              <Text style={styles.modalCloseText}>Cancel</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>

      {/* Add New Customer Modal */}
      <Modal visible={showAddCustomerModal} animationType="fade" transparent={true}>
        <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Add New Customer</Text>
            <TextInput
              style={styles.inputModal}
              placeholder="First Name"
              placeholderTextColor="#888"
              value={newCustomerFirstName}
              onChangeText={setNewCustomerFirstName}
            />
            <TextInput
              style={styles.inputModal}
              placeholder="Mobile Number (10 digits)"
              placeholderTextColor="#888"
              keyboardType="phone-pad"
              value={newCustomerPhone}
              onChangeText={setNewCustomerPhone}
            />
            <View style={{ flexDirection: 'row', gap: 12, marginTop: 16 }}>
              <TouchableOpacity style={[styles.modalActionBtn, { backgroundColor: '#333' }]} onPress={() => setShowAddCustomerModal(false)}>
                <Text style={styles.modalActionBtnText}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity style={[styles.modalActionBtn, { backgroundColor: '#d4af37' }]} onPress={handleAddNewCustomer}>
                <Text style={[styles.modalActionBtnText, { color: '#000' }]}>Save</Text>
              </TouchableOpacity>
            </View>
          </View>
        </KeyboardAvoidingView>
      </Modal>

    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0e1017' },
  card: {
    backgroundColor: '#151922',
    borderRadius: 8,
    padding: 14,
    marginBottom: 14,
    borderWidth: 1,
    borderColor: '#222a38'
  },
  cardHeaderTitle: { color: '#d4af37', fontSize: 13, fontWeight: '800', letterSpacing: 0.5, marginBottom: 10 },
  sectionHeaderTitle: { color: '#cbd5e1', fontSize: 11.5, fontWeight: '800', letterSpacing: 0.5, marginBottom: 10 },
  
  summaryRow: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 6 },
  summaryLabel: { color: '#94a3b8', fontSize: 13 },
  summaryValue: { color: '#f8fafc', fontSize: 13, fontWeight: '700' },
  dividerRow: { borderTopWidth: 1, borderTopColor: '#222a38', paddingTop: 8, marginTop: 4 },
  grandTotalLabel: { color: '#d4af37', fontSize: 15, fontWeight: '800' },
  grandTotalValue: { fontSize: 16, fontWeight: '900' },

  gstOptionsRow: { flexDirection: 'row', gap: 8 },
  gstOptionBtn: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    backgroundColor: '#10141d',
    paddingVertical: 10,
    paddingHorizontal: 8,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#222a38'
  },
  gstOptionBtnActive: { borderColor: '#d4af37', backgroundColor: '#1c2331' },
  gstOptionText: { color: '#94a3b8', fontSize: 10.5, fontWeight: '600' },
  gstOptionTextActive: { color: '#f8fafc', fontWeight: '700' },

  radioCircle: {
    width: 14,
    height: 14,
    borderRadius: 7,
    borderWidth: 1.5,
    borderColor: '#64748b',
    alignItems: 'center',
    justifyContent: 'center'
  },
  radioCircleActive: { borderColor: '#d4af37' },
  radioInner: { width: 7, height: 7, borderRadius: 3.5, backgroundColor: '#d4af37' },

  metalItemBlock: { marginBottom: 6 },
  metalHeaderLine: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 },
  metalRequiredTitle: { color: '#fbbf24', fontSize: 11, fontWeight: '800', letterSpacing: 0.5 },
  metalRequiredGrams: { color: '#f8fafc', fontSize: 13, fontWeight: '900' },

  gridRow: { flexDirection: 'row', gap: 8, marginTop: 4 },
  gridCol: { flex: 1 },
  gridLabel: { color: '#64748b', fontSize: 9.5, fontWeight: '700', letterSpacing: 0.5, marginBottom: 4 },
  gridInput: {
    backgroundColor: '#0a0d14',
    color: '#f8fafc',
    borderWidth: 1,
    borderColor: '#2b3548',
    borderRadius: 5,
    paddingVertical: 6,
    paddingHorizontal: 8,
    fontSize: 13,
    fontWeight: '700'
  },
  gridValGold: { color: '#fbbf24', fontSize: 13, fontWeight: '800', paddingTop: 6 },
  gridValSilver: { color: '#e2e8f0', fontSize: 13, fontWeight: '800', paddingTop: 6 },
  gridValGreen: { color: '#4ade80', fontSize: 13, fontWeight: '800', paddingTop: 6 },

  cashSectionRow: {
    flexDirection: 'row',
    gap: 12,
    marginTop: 14,
    borderTopWidth: 1,
    borderTopColor: '#222a38',
    paddingTop: 12
  },
  monetaryAmountText: { color: '#f8fafc', fontSize: 19, fontWeight: '900', marginTop: 2 },
  monetarySubText: { color: '#64748b', fontSize: 10, marginTop: 2 },
  cashInput: {
    backgroundColor: '#0a0d14',
    color: '#4ade80',
    borderWidth: 1,
    borderColor: '#22c55e',
    borderRadius: 6,
    paddingVertical: 8,
    paddingHorizontal: 10,
    fontSize: 16,
    fontWeight: '800'
  },
  paymentMethodPills: { flexDirection: 'row', gap: 6, marginTop: 6 },
  pillBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    backgroundColor: '#10141d',
    paddingVertical: 4,
    paddingHorizontal: 6,
    borderRadius: 4,
    borderWidth: 1,
    borderColor: '#222a38'
  },
  pillBtnActive: { borderColor: '#4ade80', backgroundColor: '#13281c' },
  pillRadio: { width: 8, height: 8, borderRadius: 4, borderWidth: 1, borderColor: '#64748b' },
  pillRadioActive: { borderColor: '#4ade80', backgroundColor: '#4ade80' },
  pillText: { color: '#94a3b8', fontSize: 9.5, fontWeight: '700' },
  pillTextActive: { color: '#4ade80' },

  settlementSummaryCard: {
    backgroundColor: '#161922',
    borderRadius: 8,
    padding: 14,
    marginBottom: 14,
    borderWidth: 1,
    borderColor: '#4d3d18'
  },
  settlementSummaryTitle: { color: '#fbbf24', fontSize: 12, fontWeight: '800', letterSpacing: 0.5, marginBottom: 8 },
  finalCashDueBox: {
    backgroundColor: '#1c1c1a',
    borderWidth: 1,
    borderColor: '#38321e',
    borderRadius: 6,
    padding: 10,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  finalCashDueLabel: { color: '#94a3b8', fontSize: 13, fontWeight: '600' },
  finalCashDueValue: { fontSize: 17, fontWeight: '900' },

  settleChoicePrompt: { color: '#64748b', fontSize: 10.5, fontWeight: '700', letterSpacing: 0.5, marginBottom: 8 },
  settleOptionBox: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    backgroundColor: '#10141d',
    borderWidth: 1,
    borderColor: '#222a38',
    borderRadius: 6,
    padding: 10,
    marginBottom: 6
  },
  settleOptionBoxActive: { borderColor: '#d4af37', backgroundColor: '#1e2417' },
  settleOptionText: { color: '#f8fafc', fontSize: 12, fontWeight: '700' },
  settleOptionSubGold: { color: '#fbbf24', fontSize: 10.5, fontWeight: '700', marginTop: 2 },
  settleOptionSubSilver: { color: '#cbd5e1', fontSize: 10.5, fontWeight: '700', marginTop: 2 },

  newCustBtn: {
    backgroundColor: 'rgba(212, 175, 55, 0.15)',
    borderWidth: 1,
    borderColor: '#d4af37',
    paddingVertical: 3,
    paddingHorizontal: 8,
    borderRadius: 4
  },
  newCustBtnText: { color: '#d4af37', fontSize: 11, fontWeight: '800' },
  customerSelector: {
    backgroundColor: '#0a0d14',
    borderWidth: 1,
    borderColor: '#2b3548',
    borderRadius: 6,
    padding: 12,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  customerSelectorText: { color: '#f8fafc', fontSize: 13, fontWeight: '600' },
  custWarningText: { color: '#ef4444', fontSize: 10, marginTop: 4, fontStyle: 'italic' },

  actionButtonsRow: {
    flexDirection: 'row',
    gap: 8,
    marginTop: 8,
    marginBottom: 20
  },
  cancelBtn: {
    flex: 1,
    backgroundColor: '#1e2533',
    paddingVertical: 14,
    borderRadius: 6,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: '#334155'
  },
  cancelBtnText: { color: '#cbd5e1', fontSize: 13, fontWeight: '700' },
  saveOnlyBtn: {
    flex: 1.2,
    backgroundColor: '#2b2a1a',
    paddingVertical: 14,
    borderRadius: 6,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: '#785b1a'
  },
  saveOnlyBtnText: { color: '#fbbf24', fontSize: 13, fontWeight: '800' },
  savePrintBtn: {
    flex: 1.5,
    backgroundColor: '#d4af37',
    paddingVertical: 14,
    borderRadius: 6,
    alignItems: 'center',
    justifyContent: 'center'
  },
  savePrintBtnText: { color: '#000', fontSize: 13, fontWeight: '900' },

  modalOverlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.85)', justifyContent: 'center', padding: 20 },
  modalContent: { backgroundColor: '#141822', borderRadius: 10, padding: 18, maxHeight: '80%', borderWidth: 1, borderColor: '#2b3548' },
  modalTitle: { color: '#d4af37', fontSize: 18, fontWeight: '800', marginBottom: 12 },
  addNewCustModalBtn: { backgroundColor: 'rgba(212, 175, 55, 0.15)', borderWidth: 1, borderColor: '#d4af37', padding: 10, borderRadius: 6, marginBottom: 10, alignItems: 'center' },
  addNewCustModalBtnText: { color: '#d4af37', fontWeight: '800', fontSize: 13 },
  customerOptionItem: { paddingVertical: 14, borderBottomWidth: 1, borderBottomColor: '#222a38' },
  customerOptionText: { color: '#f8fafc', fontSize: 14 },
  modalCloseBtn: { marginTop: 14, padding: 14, alignItems: 'center', backgroundColor: '#222a38', borderRadius: 6 },
  modalCloseText: { color: '#fff', fontWeight: '700' },
  inputModal: { backgroundColor: '#0a0d14', color: '#fff', borderWidth: 1, borderColor: '#2b3548', padding: 12, borderRadius: 6, marginBottom: 12 },
  modalActionBtn: { flex: 1, padding: 12, borderRadius: 6, alignItems: 'center' },
  modalActionBtnText: { color: '#fff', fontWeight: '800' }
});
