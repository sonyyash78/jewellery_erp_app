import React, { useState, useMemo } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity, ScrollView, Alert, ActivityIndicator } from 'react-native';
import { axiosClient } from '../../api/axiosClient';
import { useAuthStore } from '../../store/authStore';

export default function CheckoutScreen({ route, navigation }: any) {
  const { items, subtotal, tax, grandTotal, selectedCustomer } = route.params;

  const [loading, setLoading] = useState(false);
  const [cashReceived, setCashReceived] = useState('');
  
  const [goldDeposited, setGoldDeposited] = useState('');
  const [goldDepositTanch, setGoldDepositTanch] = useState('100');
  
  const [silverDeposited, setSilverDeposited] = useState('');
  const [silverDepositTanch, setSilverDepositTanch] = useState('100');

  const [cashBalanceAction, setCashBalanceAction] = useState<'cash' | 'metal_gold' | 'metal_silver' | 'metal_both'>('cash');
  const [paymentMethod, setPaymentMethod] = useState<'Cash' | 'UPI' | 'Cheque'>('Cash');

  // STEP 1: Extract from payload
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
    return { totalGoldBilled: tg, totalSilverBilled: ts, goldRate: gr, silverRate: sr };
  }, [items]);

  const hasGold = totalGoldBilled > 0;
  const hasSilver = totalSilverBilled > 0;
  const isGoldFixed = goldRate > 0;
  const isSilverFixed = silverRate > 0;

  const conversionGoldRate = goldRate || 72500;
  const conversionSilverRate = silverRate || 90000;

  const cashRecNum = parseFloat(cashReceived) || 0;
  const goldDepNum = parseFloat(goldDeposited) || 0;
  const goldTanchNum = parseFloat(goldDepositTanch) || 0;
  const silverDepNum = parseFloat(silverDeposited) || 0;
  const silverTanchNum = parseFloat(silverDepositTanch) || 0;

  // STEP 3: Monetary settlement
  const fineGoldDeposited = goldDepNum * (goldTanchNum / 100);
  const fineSilverDeposited = silverDepNum * (silverTanchNum / 100);

  const goldValueReceived = fineGoldDeposited * (isGoldFixed ? goldRate : 0) / 10;
  const silverValueReceived = fineSilverDeposited * (isSilverFixed ? silverRate : 0) / 1000;
  const totalMetalValueReceived = goldValueReceived + silverValueReceived;
  const monetaryBeforeCash = grandTotal - totalMetalValueReceived;
  const cashBalanceDue = monetaryBeforeCash - cashRecNum;

  // STEP 4: Physical balance
  const physicalGoldDue = isGoldFixed ? 0 : Math.max(0, totalGoldBilled - fineGoldDeposited);
  const physicalSilverDue = isSilverFixed ? 0 : Math.max(0, totalSilverBilled - fineSilverDeposited);

  // STEP 5: Conversions
  const maxGoldMetalGrams = isGoldFixed ? Math.max(0, totalGoldBilled - fineGoldDeposited) : 0;
  const maxSilverMetalGrams = isSilverFixed ? Math.max(0, totalSilverBilled - fineSilverDeposited) : 0;
  const goldMetalValue = maxGoldMetalGrams * (conversionGoldRate / 10);
  const silverMetalValue = maxSilverMetalGrams * (conversionSilverRate / 1000);
  const totalMetalValue = goldMetalValue + silverMetalValue;

  const cashToGoldGrams = Math.min(maxGoldMetalGrams, conversionGoldRate > 0 ? Math.max(0, cashBalanceDue) / (conversionGoldRate / 10) : 0);
  const cashDueAfterGold = cashBalanceDue - (cashToGoldGrams * (conversionGoldRate / 10));

  const cashToSilverGrams = Math.min(maxSilverMetalGrams, conversionSilverRate > 0 ? (Math.max(0, cashBalanceDue) / (conversionSilverRate / 1000)) : 0);
  const cashDueAfterSilver = cashBalanceDue - (cashToSilverGrams * (conversionSilverRate / 1000));

  const goldValueProp = totalMetalValue > 0 ? goldMetalValue / totalMetalValue : 0;
  const silverValueProp = totalMetalValue > 0 ? silverMetalValue / totalMetalValue : 0;
  const allocatedToGold = Math.min(goldMetalValue, Math.max(0, cashBalanceDue) * goldValueProp);
  const allocatedToSilver = Math.min(silverMetalValue, Math.max(0, cashBalanceDue) * silverValueProp);
  
  const cashToGoldGramsGoldPortion = conversionGoldRate > 0 ? allocatedToGold / (conversionGoldRate / 10) : 0;
  const cashToSilverGramsSilverPortion = conversionSilverRate > 0 ? allocatedToSilver / (conversionSilverRate / 1000) : 0;
  const cashDueAfterBoth = cashBalanceDue - allocatedToGold - allocatedToSilver;

  const isFullySettled = cashBalanceDue <= 0 && physicalGoldDue === 0 && physicalSilverDue === 0;

  const handleGenerate = async () => {
    if (!isFullySettled && !selectedCustomer) {
      Alert.alert('Error', 'A customer must be selected for outstanding balances.');
      return;
    }
    
    setLoading(true);

    let updatedItems = [...items];
    if (goldDepNum > 0) {
      updatedItems.push({
        item_name: 'Gold Deposit', item_type: 'Gold', final_price: 0,
        gold_calculation: {
          applied_rate: isGoldFixed ? goldRate : 0, gross_weight: goldDepNum, net_weight: goldDepNum,
          stone_weight: 0, touch_purity: goldTanchNum, wastage: 0, fine_weight: fineGoldDeposited,
          making_charge_type: 'flat', making_charge_rate: 0, making_charges_amount: 0,
          hallmark_charges: 0, other_charges: 0, discount: 0, total_gold_value: goldValueReceived,
        }
      });
    }
    if (silverDepNum > 0) {
      updatedItems.push({
        item_name: 'Silver Deposit', item_type: 'Silver', final_price: 0,
        silver_calculation: {
          applied_rate: isSilverFixed ? silverRate : 0, gross_weight: silverDepNum, net_weight: silverDepNum,
          stone_weight: 0, tanch_percentage: silverTanchNum, wastage: 0, pure_weight: fineSilverDeposited,
          making_charge_type: 'flat', making_charge_rate: 0, making_charges_amount: 0,
          other_charges: 0, discount: 0, total_silver_value: silverValueReceived,
        }
      });
    }

    const isConvertingToMetal = cashBalanceDue > 0 && cashBalanceAction !== 'cash';
    const backendSettlementType = isConvertingToMetal ? 'Metal' : 'Cash';
    let goldBalMetal = 0, silverBalMetal = 0;
    let finalBalanceAmount = cashBalanceDue;

    if (cashBalanceDue > 0) {
      if (cashBalanceAction === 'metal_gold')   { goldBalMetal = cashToGoldGrams; finalBalanceAmount = cashDueAfterGold; }
      if (cashBalanceAction === 'metal_silver') { silverBalMetal = cashToSilverGrams; finalBalanceAmount = cashDueAfterSilver; }
      if (cashBalanceAction === 'metal_both') { 
        goldBalMetal = cashToGoldGramsGoldPortion; 
        silverBalMetal = cashToSilverGramsSilverPortion; 
        finalBalanceAmount = cashDueAfterBoth;
      }
    }

    let backendBillType = 'Cash';
    if (hasGold && hasSilver) backendBillType = 'Hybrid';
    else if (totalMetalValueReceived > 0 || physicalGoldDue > 0 || physicalSilverDue > 0) backendBillType = 'Metal';

    let recStrParts = [];
    if (fineGoldDeposited > 0) recStrParts.push(`${fineGoldDeposited.toFixed(3)}g Gold`);
    if (fineSilverDeposited > 0) recStrParts.push(`${fineSilverDeposited.toFixed(3)}g Silver`);
    const metalRecStr = recStrParts.join(' | ');

    const payload = {
      customer_id: selectedCustomer ? selectedCustomer.id : null,
      subtotal: subtotal,
      tax_amount: tax,
      discount_amount: 0,
      grand_total: grandTotal,
      status: isFullySettled ? 'Paid' : 'Completed',
      items: updatedItems,
      amount_paid: cashRecNum,
      payment_method: paymentMethod,
      bill_type: backendBillType,
      settlement_type: backendSettlementType,
      settlement_metal_type: cashBalanceAction === 'metal_gold' ? 'Gold' : cashBalanceAction === 'metal_silver' ? 'Silver' : null,
      metal_received_value: totalMetalValueReceived,
      metal_received_str: metalRecStr,
      cash_received: cashRecNum,
      balance_amount: finalBalanceAmount,
      balance_metal_weight: 0,
      gold_balance_metal_weight: goldBalMetal,
      silver_balance_metal_weight: silverBalMetal,
    };

    try {
      const res = await axiosClient.post('/invoices/', payload);
      Alert.alert('Success', `Invoice ${res.data.invoice_number} generated!`);
      navigation.navigate('Billing');
    } catch (e: any) {
      console.log('Checkout Error:', e.response?.data);
      Alert.alert('Error', e.response?.data?.detail || 'Failed to generate invoice');
    } finally {
      setLoading(false);
    }
  };

  let displayCashDue = cashBalanceDue;
  if (cashBalanceDue > 0) {
    if (cashBalanceAction === 'metal_gold') displayCashDue = cashDueAfterGold;
    if (cashBalanceAction === 'metal_silver') displayCashDue = cashDueAfterSilver;
    if (cashBalanceAction === 'metal_both') displayCashDue = cashDueAfterBoth;
  }

  const fmt = (n: number) => n.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

  return (
    <View style={styles.container}>
      <ScrollView contentContainerStyle={{ padding: 16 }}>
        <Text style={styles.headerTitle}>Checkout Settlement</Text>
        
        {/* Metal Received */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Metal Received from Customer</Text>
          
          {hasGold && (
            <View style={styles.metalBlock}>
              <Text style={styles.metalReq}>Gold Required {isGoldFixed ? `@ ₹${goldRate}/10g` : ''}: {totalGoldBilled.toFixed(3)}g</Text>
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
                  <Text style={styles.valText}>{fineGoldDeposited.toFixed(3)}g</Text>
                  <Text style={styles.valTextGreen}>{isGoldFixed ? `₹${fmt(goldValueReceived)}` : `${physicalGoldDue.toFixed(3)}g due`}</Text>
                </View>
              </View>
            </View>
          )}

          {hasSilver && (
            <View style={[styles.metalBlock, hasGold && { borderTopWidth: 1, borderTopColor: '#333', paddingTop: 16 }]}>
              <Text style={styles.metalReq}>Silver Required {isSilverFixed ? `@ ₹${silverRate}/kg` : ''}: {totalSilverBilled.toFixed(3)}g</Text>
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
                  <Text style={styles.valText}>{fineSilverDeposited.toFixed(3)}g</Text>
                  <Text style={styles.valTextGreen}>{isSilverFixed ? `₹${fmt(silverValueReceived)}` : `${physicalSilverDue.toFixed(3)}g due`}</Text>
                </View>
              </View>
            </View>
          )}
        </View>

        <View style={styles.card}>
          <Text style={styles.lbl}>Monetary Balance (after metal)</Text>
          <Text style={styles.monetaryBal}>₹ {fmt(monetaryBeforeCash)}</Text>
          <Text style={{color:'#666', fontSize:10}}>₹{fmt(grandTotal)} − ₹{fmt(totalMetalValueReceived)} metal</Text>

          <Text style={[styles.lbl, { marginTop: 16, color: '#4ade80' }]}>Cash Received</Text>
          <TextInput style={styles.inputLarge} keyboardType="numeric" value={cashReceived} onChangeText={setCashReceived} placeholder="0" placeholderTextColor="#555"/>
          
          <View style={styles.paymentMethods}>
            {(['Cash', 'UPI', 'Cheque'] as any[]).map(m => (
              <TouchableOpacity key={m} style={[styles.payBtn, paymentMethod === m && styles.payBtnActive]} onPress={() => setPaymentMethod(m)}>
                <Text style={[styles.payBtnText, paymentMethod === m && styles.payBtnTextActive]}>{m}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Final Settlement Summary */}
        <View style={styles.summaryCard}>
          <Text style={styles.cardTitle}>Final Settlement Summary</Text>
          <View style={styles.summaryBox}>
            {physicalGoldDue > 0 && <Text style={styles.summaryText}>Gold Due: {physicalGoldDue.toFixed(3)} g</Text>}
            {physicalSilverDue > 0 && <Text style={styles.summaryText}>Silver Due: {physicalSilverDue.toFixed(3)} g</Text>}
            <Text style={styles.summaryText}>
              {displayCashDue > 0 ? 'Final Cash Due:' : displayCashDue < 0 ? 'Refund to Customer:' : 'Cash:'} 
              <Text style={{color: displayCashDue > 0 ? '#ef4444' : '#4ade80', fontWeight: 'bold'}}>
                {' '}₹ {fmt(Math.abs(displayCashDue))}
              </Text>
            </Text>
          </View>

          {cashBalanceDue > 0 && (isGoldFixed || isSilverFixed) && (
            <View style={{ marginTop: 16 }}>
              <Text style={styles.lbl}>How to settle the ₹ {fmt(cashBalanceDue)} cash due?</Text>
              
              <TouchableOpacity style={[styles.actionBtn, cashBalanceAction === 'cash' && styles.actionBtnActive]} onPress={() => setCashBalanceAction('cash')}>
                <Text style={styles.actionBtnText}>Keep as Cash Due</Text>
              </TouchableOpacity>
              
              {isGoldFixed && !hasSilver && (
                <TouchableOpacity style={[styles.actionBtn, cashBalanceAction === 'metal_gold' && styles.actionBtnActive]} onPress={() => setCashBalanceAction('metal_gold')}>
                  <Text style={styles.actionBtnText}>Convert to Gold Ledger (+{cashToGoldGrams.toFixed(3)}g)</Text>
                </TouchableOpacity>
              )}
              {isSilverFixed && !hasGold && (
                <TouchableOpacity style={[styles.actionBtn, cashBalanceAction === 'metal_silver' && styles.actionBtnActive]} onPress={() => setCashBalanceAction('metal_silver')}>
                  <Text style={styles.actionBtnText}>Convert to Silver Ledger (+{cashToSilverGrams.toFixed(3)}g)</Text>
                </TouchableOpacity>
              )}
              {isGoldFixed && isSilverFixed && hasGold && hasSilver && (
                <>
                  <TouchableOpacity style={[styles.actionBtn, cashBalanceAction === 'metal_gold' && styles.actionBtnActive]} onPress={() => setCashBalanceAction('metal_gold')}>
                    <Text style={styles.actionBtnText}>Convert to Gold Ledger (+{cashToGoldGrams.toFixed(3)}g)</Text>
                  </TouchableOpacity>
                  <TouchableOpacity style={[styles.actionBtn, cashBalanceAction === 'metal_silver' && styles.actionBtnActive]} onPress={() => setCashBalanceAction('metal_silver')}>
                    <Text style={styles.actionBtnText}>Convert to Silver Ledger (+{cashToSilverGrams.toFixed(3)}g)</Text>
                  </TouchableOpacity>
                  <TouchableOpacity style={[styles.actionBtn, cashBalanceAction === 'metal_both' && styles.actionBtnActive]} onPress={() => setCashBalanceAction('metal_both')}>
                    <Text style={styles.actionBtnText}>Convert Both Metals to Ledgers (+{cashToGoldGramsGoldPortion.toFixed(3)}g Gold | +{cashToSilverGramsSilverPortion.toFixed(3)}g Silver)</Text>
                  </TouchableOpacity>
                </>
              )}
              {isGoldFixed && !isSilverFixed && hasGold && hasSilver && (
                <TouchableOpacity style={[styles.actionBtn, cashBalanceAction === 'metal_gold' && styles.actionBtnActive]} onPress={() => setCashBalanceAction('metal_gold')}>
                  <Text style={styles.actionBtnText}>Convert to Gold Ledger (+{cashToGoldGrams.toFixed(3)}g)</Text>
                </TouchableOpacity>
              )}
              {isSilverFixed && !isGoldFixed && hasGold && hasSilver && (
                <TouchableOpacity style={[styles.actionBtn, cashBalanceAction === 'metal_silver' && styles.actionBtnActive]} onPress={() => setCashBalanceAction('metal_silver')}>
                  <Text style={styles.actionBtnText}>Convert to Silver Ledger (+{cashToSilverGrams.toFixed(3)}g)</Text>
                </TouchableOpacity>
              )}
            </View>
          )}
        </View>

        <TouchableOpacity 
          style={[styles.saveButton, loading && styles.saveButtonDisabled]} 
          onPress={handleGenerate}
          disabled={loading}
        >
          {loading ? <ActivityIndicator color="#000" /> : <Text style={styles.saveButtonText}>SAVE INVOICE</Text>}
        </TouchableOpacity>
        
        <View style={{ height: 40 }} />
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0a0a0a' },
  headerTitle: { color: '#d4af37', fontSize: 24, fontWeight: 'bold', marginBottom: 16 },
  card: { backgroundColor: '#141414', borderWidth: 1, borderColor: '#333', padding: 16, borderRadius: 8, marginBottom: 16 },
  cardTitle: { color: '#fff', fontSize: 14, fontWeight: 'bold', textTransform: 'uppercase', marginBottom: 12 },
  metalBlock: { marginBottom: 16 },
  metalReq: { color: '#d4af37', fontSize: 12, fontWeight: 'bold', marginBottom: 8 },
  row: { flexDirection: 'row', gap: 8 },
  col: { flex: 1 },
  lbl: { color: '#888', fontSize: 10, textTransform: 'uppercase', marginBottom: 4, fontWeight: 'bold' },
  inputSmall: { backgroundColor: '#0a0a0a', color: '#fff', borderWidth: 1, borderColor: '#333', padding: 8, borderRadius: 6, fontVariant: ['tabular-nums'] },
  valText: { color: '#fff', fontSize: 14, fontVariant: ['tabular-nums'] },
  valTextGreen: { color: '#4ade80', fontSize: 14, fontWeight: 'bold', fontVariant: ['tabular-nums'] },
  monetaryBal: { color: '#fff', fontSize: 24, fontWeight: 'bold', fontVariant: ['tabular-nums'] },
  inputLarge: { backgroundColor: '#0a0a0a', color: '#4ade80', borderWidth: 1, borderColor: '#166534', padding: 12, borderRadius: 8, fontSize: 20, fontVariant: ['tabular-nums'] },
  paymentMethods: { flexDirection: 'row', gap: 8, marginTop: 12 },
  payBtn: { flex: 1, padding: 10, borderWidth: 1, borderColor: '#333', borderRadius: 6, alignItems: 'center' },
  payBtnActive: { backgroundColor: '#166534', borderColor: '#4ade80' },
  payBtnText: { color: '#888', fontSize: 12, fontWeight: 'bold' },
  payBtnTextActive: { color: '#4ade80' },
  summaryCard: { backgroundColor: '#1e1b14', borderWidth: 1, borderColor: '#713f12', padding: 16, borderRadius: 8, marginBottom: 16 },
  summaryBox: { backgroundColor: '#000', padding: 12, borderRadius: 6, borderWidth: 1, borderColor: '#333' },
  summaryText: { color: '#d1d5db', fontSize: 14, marginBottom: 4 },
  actionBtn: { padding: 12, borderWidth: 1, borderColor: '#333', borderRadius: 6, marginTop: 8 },
  actionBtnActive: { backgroundColor: '#713f12', borderColor: '#d4af37' },
  actionBtnText: { color: '#fff', fontSize: 12, fontWeight: 'bold' },
  saveButton: { backgroundColor: '#d4af37', padding: 16, borderRadius: 8, alignItems: 'center', marginTop: 8 },
  saveButtonDisabled: { opacity: 0.5 },
  saveButtonText: { color: '#000', fontSize: 18, fontWeight: 'bold' },
});
