import React, { useState } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity, ScrollView, Alert, ActivityIndicator } from 'react-native';
import { axiosClient } from '../../api/axiosClient';

export default function CheckoutPurchaseScreen({ route, navigation }: any) {
  const { seller, items } = route.params;

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
  const grand_total = total_taxable + gstAmount;

  // Compute metal totals from cart
  const goldItems = items.filter((i: any) => i.metal_type === 'Gold');
  const silverItems = items.filter((i: any) => i.metal_type === 'Silver');
  
  const totalGoldBilled = goldItems.reduce((sum: number, i: any) => sum + i.fine_weight, 0);
  const totalSilverBilled = silverItems.reduce((sum: number, i: any) => sum + i.fine_weight, 0);
  
  const goldRate = goldItems.length > 0 ? goldItems[0].metal_rate : 72500;
  const silverRate = silverItems.length > 0 ? silverItems[0].metal_rate : 90000;

  const hasGold = totalGoldBilled > 0;
  const hasSilver = totalSilverBilled > 0;

  // User Inputs
  const [goldGiven, setGoldGiven] = useState('');
  const [goldGivenTanch, setGoldGivenTanch] = useState('100');
  const [silverGiven, setSilverGiven] = useState('');
  const [silverGivenTanch, setSilverGivenTanch] = useState('100');
  const [cashPaid, setCashPaid] = useState('');
  
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
  const monetaryBeforeCash = grand_total - totalMetalValueReceived;
  
  const parsedCash = parseFloat(cashPaid) || 0;
  const cashBalanceDue = Math.max(0, monetaryBeforeCash - parsedCash);

  // Settlement Logic (like web)
  const maxGoldMetalGrams = hasGold ? Math.max(0, totalGoldBilled - fineGoldGiven) : 0;
  const maxSilverMetalGrams = hasSilver ? Math.max(0, totalSilverBilled - fineSilverGiven) : 0;

  const cashToGoldGrams = Math.min(maxGoldMetalGrams, goldRate > 0 ? (Math.max(0, cashBalanceDue) / (goldRate / 10)) : 0);
  const cashDueAfterGold = cashBalanceDue - (cashToGoldGrams * (goldRate / 10));

  const cashToSilverGrams = Math.min(maxSilverMetalGrams, silverRate > 0 ? (Math.max(0, cashBalanceDue) / (silverRate / 1000)) : 0);
  const cashDueAfterSilver = cashBalanceDue - (cashToSilverGrams * (silverRate / 1000));

  const bothGoldGrams = maxGoldMetalGrams;
  const bothSilverGrams = Math.min(maxSilverMetalGrams, silverRate > 0 ? (Math.max(0, cashBalanceDue - (bothGoldGrams * (goldRate / 10))) / (silverRate / 1000)) : 0);
  const cashDueAfterBoth = cashBalanceDue - (bothGoldGrams * (goldRate / 10)) - (bothSilverGrams * (silverRate / 1000));

  let finalGoldDebt = 0;
  let finalSilverDebt = 0;
  if (cashBalanceAction === 'metal_gold') finalGoldDebt = cashToGoldGrams;
  if (cashBalanceAction === 'metal_silver') finalSilverDebt = cashToSilverGrams;
  if (cashBalanceAction === 'metal_both') {
    finalGoldDebt = bothGoldGrams;
    finalSilverDebt = bothSilverGrams;
  }

  const fmt = (n: number) => n.toLocaleString('en-IN', { maximumFractionDigits: 2 });

  const handleSettle = async () => {
    try {
      if (parsedCash < 0 || parsedGoldGiven < 0 || parsedSilverGiven < 0) {
        Alert.alert('Error', 'Deposits cannot be negative.');
        return;
      }
      
      setSubmitting(true);
      
      let updatedItems = [...items];
      
      // Inject Metal Given entries just like web
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
      
      const payload = {
        seller_id: seller?.id || null,
        seller: seller?.id ? null : seller,
        amount_paid: parsedCash,
        total_taxable: total_taxable,
        cgst: cgst,
        sgst: sgst,
        igst: igst,
        grand_total: grand_total,
        status: (cashBalanceDue > 0 && cashBalanceAction === 'cash') ? 'Pending' : 'Completed',
        
        bill_type: 'Cash',
        settlement_type: cashBalanceAction !== 'cash' ? 'Metal' : 'Cash',
        settlement_metal_type: cashBalanceAction === 'cash' ? null : cashBalanceAction.replace('metal_', '').replace('both', 'Both').replace('gold', 'Gold').replace('silver', 'Silver'),
        metal_given_value: totalMetalValueReceived,
        cash_paid: parsedCash,
        balance_amount: cashBalanceAction === 'cash' ? cashBalanceDue : (cashBalanceAction === 'metal_gold' ? cashDueAfterGold : (cashBalanceAction === 'metal_silver' ? cashDueAfterSilver : cashDueAfterBoth)),
        gold_balance_metal_weight: finalGoldDebt,
        silver_balance_metal_weight: finalSilverDebt,
        
        items: updatedItems
      };

      const response = await axiosClient.post('/purchases/', payload);
      Alert.alert('Success', 'Purchase recorded successfully!');
      navigation.popToTop();
      navigation.navigate('Purchases');
    } catch (error: any) {
      console.log('Checkout failed', error?.response?.data || error);
      Alert.alert('Error', error?.response?.data?.detail || 'Failed to submit purchase');
    } finally {
      setSubmitting(false);
    }
  };

  let displayCashDue = cashBalanceDue;
  if (cashBalanceDue > 0) {
    if (cashBalanceAction === 'metal_gold') displayCashDue = cashDueAfterGold;
    if (cashBalanceAction === 'metal_silver') displayCashDue = cashDueAfterSilver;
    if (cashBalanceAction === 'metal_both') displayCashDue = cashDueAfterBoth;
  }

  return (
    <ScrollView style={styles.container}>
      
      <View style={styles.card}>
        <Text style={styles.sectionTitle}>GST Options</Text>
        {[
          {label: 'Same State (3%)', val: 'same'},
          {label: 'Interstate (3%)', val: 'inter'},
          {label: 'Without GST (0%)', val: 'none'}
        ].map(opt => (
          <TouchableOpacity key={opt.val} style={styles.gstBox} onPress={() => setGstType(opt.val as any)}>
            <View style={[styles.gstRadio, gstType === opt.val && styles.gstRadioActive]}>
              {gstType === opt.val && <View style={styles.gstRadioInner} />}
            </View>
            <Text style={styles.gstText}>{opt.label}</Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* METAL GIVEN TO SUPPLIER */}
      <View style={styles.card}>
        <Text style={styles.sectionTitle}>METAL GIVEN TO SUPPLIER</Text>
        
        {hasGold && (
          <View style={styles.metalRow}>
            <View style={{ flex: 1.5 }}>
              <Text style={styles.lbl}>GOLD REQ @ ₹{goldRate}/10G</Text>
              <Text style={styles.reqVal}>{totalGoldBilled.toFixed(3)} g</Text>
            </View>
            <View style={{ flex: 1 }}>
              <Text style={styles.lbl}>GROSS GIVEN</Text>
              <TextInput style={styles.inputSmall} keyboardType="numeric" value={goldGiven} onChangeText={setGoldGiven} placeholder="0.000" placeholderTextColor="#555" />
            </View>
            <View style={{ flex: 1 }}>
              <Text style={styles.lbl}>TANCH %</Text>
              <TextInput style={styles.inputSmall} keyboardType="numeric" value={goldGivenTanch} onChangeText={setGoldGivenTanch} />
            </View>
            <View style={{ flex: 1 }}>
              <Text style={styles.lbl}>FINE METAL</Text>
              <Text style={styles.valGreen}>{fineGoldGiven.toFixed(3)} g</Text>
            </View>
            <View style={{ flex: 1.2 }}>
              <Text style={styles.lbl}>VALUE</Text>
              <Text style={styles.valGreen}>₹ {fmt(goldValueReceived)}</Text>
            </View>
          </View>
        )}

        {hasSilver && (
          <View style={[styles.metalRow, hasGold && { borderTopWidth: 1, borderTopColor: '#333', paddingTop: 16 }]}>
            <View style={{ flex: 1.5 }}>
              <Text style={styles.lbl}>SILVER REQ @ ₹{silverRate}/KG</Text>
              <Text style={styles.reqVal}>{totalSilverBilled.toFixed(3)} g</Text>
            </View>
            <View style={{ flex: 1 }}>
              <Text style={styles.lbl}>GROSS GIVEN</Text>
              <TextInput style={styles.inputSmall} keyboardType="numeric" value={silverGiven} onChangeText={setSilverGiven} placeholder="0.000" placeholderTextColor="#555" />
            </View>
            <View style={{ flex: 1 }}>
              <Text style={styles.lbl}>TANCH %</Text>
              <TextInput style={styles.inputSmall} keyboardType="numeric" value={silverGivenTanch} onChangeText={setSilverGivenTanch} />
            </View>
            <View style={{ flex: 1 }}>
              <Text style={styles.lbl}>FINE METAL</Text>
              <Text style={styles.valGreen}>{fineSilverGiven.toFixed(3)} g</Text>
            </View>
            <View style={{ flex: 1.2 }}>
              <Text style={styles.lbl}>VALUE</Text>
              <Text style={styles.valGreen}>₹ {fmt(silverValueReceived)}</Text>
            </View>
          </View>
        )}

        <View style={styles.monetaryBox}>
          <View>
            <Text style={styles.lbl}>MONETARY BALANCE (AFTER METAL)</Text>
            <Text style={styles.monetaryVal}>₹ {fmt(monetaryBeforeCash)}</Text>
            <Text style={styles.subtext}>₹{fmt(grand_total)} - ₹{fmt(totalMetalValueReceived)} metal</Text>
          </View>
          <View style={{ width: '40%' }}>
            <Text style={[styles.lbl, { color: '#4ade80' }]}>CASH PAID</Text>
            <TextInput style={[styles.inputSmall, { borderColor: '#4ade80', color: '#4ade80', fontSize: 16 }]} keyboardType="numeric" value={cashPaid} onChangeText={setCashPaid} placeholder="0" placeholderTextColor="#225533" />
          </View>
        </View>
      </View>

      {/* FINAL SETTLEMENT SUMMARY */}
      <View style={styles.card}>
        <Text style={styles.sectionTitle}>FINAL SETTLEMENT SUMMARY</Text>
        
        <View style={styles.finalRow}>
          <Text style={styles.finalLabel}>Final Cash Due:</Text>
          <Text style={styles.finalVal}>₹ {fmt(displayCashDue)}</Text>
        </View>
        
        {cashBalanceDue > 0 && (
          <View style={{ marginTop: 16 }}>
            <Text style={styles.lbl}>HOW TO SETTLE THE ₹{fmt(cashBalanceDue)} CASH DUE?</Text>
            
            <TouchableOpacity style={[styles.optionBox, cashBalanceAction === 'cash' && styles.optionBoxActive]} onPress={() => setCashBalanceAction('cash')}>
              <Text style={[styles.optionTitle, cashBalanceAction === 'cash' && styles.optionTitleActive]}>Keep as Cash Due — pay ₹{fmt(cashBalanceDue)} later</Text>
            </TouchableOpacity>

            {hasGold && (
              <TouchableOpacity style={[styles.optionBox, cashBalanceAction === 'metal_gold' && styles.optionBoxActive]} onPress={() => setCashBalanceAction('metal_gold')}>
                <Text style={[styles.optionTitle, cashBalanceAction === 'metal_gold' && styles.optionTitleActive]}>Convert Metal to Gold Ledger</Text>
                <Text style={styles.optionSub}>+{cashToGoldGrams.toFixed(3)} g Gold | ₹{fmt(cashDueAfterGold)} Cash Due</Text>
              </TouchableOpacity>
            )}

            {hasSilver && (
              <TouchableOpacity style={[styles.optionBox, cashBalanceAction === 'metal_silver' && styles.optionBoxActive]} onPress={() => setCashBalanceAction('metal_silver')}>
                <Text style={[styles.optionTitle, cashBalanceAction === 'metal_silver' && styles.optionTitleActive]}>Convert Metal to Silver Ledger</Text>
                <Text style={styles.optionSub}>+{cashToSilverGrams.toFixed(3)} g Silver | ₹{fmt(cashDueAfterSilver)} Cash Due</Text>
              </TouchableOpacity>
            )}

            {(hasGold && hasSilver) && (
              <TouchableOpacity style={[styles.optionBox, cashBalanceAction === 'metal_both' && styles.optionBoxActive]} onPress={() => setCashBalanceAction('metal_both')}>
                <Text style={[styles.optionTitle, cashBalanceAction === 'metal_both' && styles.optionTitleActive]}>Convert Both Metals to Ledgers</Text>
                <Text style={styles.optionSub}>Gold: +{bothGoldGrams.toFixed(3)} g | Silver: +{bothSilverGrams.toFixed(3)} g | ₹{fmt(cashDueAfterBoth)} Cash Due</Text>
              </TouchableOpacity>
            )}
          </View>
        )}
      </View>

      <TouchableOpacity style={[styles.submitButton, submitting && { opacity: 0.7 }]} onPress={handleSettle} disabled={submitting}>
        {submitting ? <ActivityIndicator color="#000" /> : <Text style={styles.submitButtonText}>CONFIRM & GENERATE</Text>}
      </TouchableOpacity>
      
      <View style={{ height: 40 }} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0a0a0a', padding: 16 },
  card: { backgroundColor: '#141414', padding: 16, borderRadius: 8, borderWidth: 1, borderColor: '#333', marginBottom: 16 },
  sectionTitle: { color: '#d4af37', fontSize: 14, fontWeight: 'bold', textTransform: 'uppercase', marginBottom: 16 },
  
  metalRow: { flexDirection: 'row', gap: 8, marginBottom: 16, alignItems: 'flex-start' },
  lbl: { color: '#888', fontSize: 9, fontWeight: 'bold', marginBottom: 4, textTransform: 'uppercase' },
  reqVal: { color: '#fff', fontSize: 14, fontWeight: 'bold', fontVariant: ['tabular-nums'] },
  inputSmall: { backgroundColor: '#0a0a0a', color: '#d4af37', borderWidth: 1, borderColor: '#333', borderRadius: 4, paddingVertical: 4, paddingHorizontal: 6, fontSize: 13, fontVariant: ['tabular-nums'], minHeight: 32 },
  valGreen: { color: '#4ade80', fontSize: 14, fontWeight: 'bold', fontVariant: ['tabular-nums'] },
  
  gstBox: { flexDirection: 'row', alignItems: 'center', marginBottom: 12, gap: 8 },
  gstRadio: { width: 16, height: 16, borderRadius: 8, borderWidth: 2, borderColor: '#888', alignItems: 'center', justifyContent: 'center' },
  gstRadioActive: { borderColor: '#d4af37' },
  gstRadioInner: { width: 8, height: 8, borderRadius: 4, backgroundColor: '#d4af37' },
  gstText: { color: '#fff', fontSize: 14 },
  
  monetaryBox: { marginTop: 16, borderTopWidth: 1, borderTopColor: '#333', paddingTop: 16, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  monetaryVal: { color: '#fff', fontSize: 20, fontWeight: 'bold' },
  subtext: { color: '#555', fontSize: 12 },
  
  finalRow: { flexDirection: 'row', justifyContent: 'space-between', backgroundColor: '#1a1a1a', padding: 12, borderRadius: 8, borderWidth: 1, borderColor: '#333' },
  finalLabel: { color: '#888', fontSize: 16 },
  finalVal: { color: '#ef4444', fontSize: 18, fontWeight: 'bold' },
  
  optionBox: { backgroundColor: '#1a1a1a', padding: 12, borderRadius: 8, borderWidth: 1, borderColor: '#333', marginTop: 8 },
  optionBoxActive: { borderColor: '#d4af37', backgroundColor: 'rgba(212, 175, 55, 0.1)' },
  optionTitle: { color: '#fff', fontSize: 14, fontWeight: 'bold' },
  optionTitleActive: { color: '#d4af37' },
  optionSub: { color: '#888', fontSize: 12, marginTop: 4 },
  
  submitButton: { backgroundColor: '#d4af37', padding: 16, borderRadius: 8, alignItems: 'center' },
  submitButtonText: { color: '#000', fontSize: 16, fontWeight: 'bold' }
});
