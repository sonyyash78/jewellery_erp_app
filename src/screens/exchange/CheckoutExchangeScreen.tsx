import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Alert, ActivityIndicator } from 'react-native';
import { axiosClient } from '../../api/axiosClient';

export default function CheckoutExchangeScreen({ route, navigation }: any) {
  const { customer, items } = route.params;

  // Split items
  const oldItemsRaw = items.filter((i: any) => i.direction === 'Old');
  const newItemsRaw = items.filter((i: any) => i.direction === 'New');

  const total_old_value = oldItemsRaw.reduce((sum: number, i: any) => sum + i.final_price, 0);
  const total_new_value = newItemsRaw.reduce((sum: number, i: any) => sum + i.final_price, 0);
  
  const gstAmount = total_new_value * 0.03;
  const grand_total = total_new_value + gstAmount;
  const difference_amount = grand_total - total_old_value;

  const [submitting, setSubmitting] = useState(false);

  const handleSettle = async () => {
    try {
      if (!customer) {
        Alert.alert('Error', 'Customer required');
        return;
      }
      setSubmitting(true);
      
      const payload = {
        customer_id: customer.id,
        amount_paid: difference_amount > 0 ? difference_amount : 0,
        total_old_value,
        total_new_value,
        gst_amount: gstAmount,
        grand_total,
        difference_amount,
        
        settlement_type: "Cash",
        balance_amount: 0,
        gold_balance_metal_weight: 0,
        silver_balance_metal_weight: 0,
        
        old_items: oldItemsRaw.map((i: any) => ({
          item_name: i.item_name, metal: i.item_type, purity: '100', touch: 100,
          gross_weight: 0, stone_weight: 0, net_weight: 0,
          wastage: 0, fine_weight: 0,
          labour_charge: 0, testing_melting_charge: 0,
          hallmark_charge: 0, other_charges: 0,
          discount: 0, rate_applied: 0, calculated_value: i.final_price
        })),
        new_items: newItemsRaw.map((i: any) => ({
          item_name: i.item_name, metal: i.item_type,
          net_weight: 0, gross_weight: 0,
          stone_weight: 0, touch_purity: 100,
          wastage: 0, fine_weight: 0,
          making_charge_type: "flat", making_charge_rate: 0,
          making_charges_amount: 0,
          hallmark_charges: 0, other_charges: 0,
          discount: 0, rate_applied: 0, final_price: i.final_price
        }))
      };

      const response = await axiosClient.post('/exchanges/', payload);
      Alert.alert('Success', 'Exchange recorded successfully!');
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
    <ScrollView style={styles.container}>
      <View style={styles.summaryCard}>
        <Text style={styles.title}>Exchange Summary</Text>
        
        <View style={styles.row}>
          <Text style={styles.label}>Total Old Value (From Customer):</Text>
          <Text style={styles.value}>₹ {total_old_value.toFixed(2)}</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Total New Value (To Customer):</Text>
          <Text style={styles.value}>₹ {total_new_value.toFixed(2)}</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>GST on New Items (3%):</Text>
          <Text style={styles.value}>₹ {gstAmount.toFixed(2)}</Text>
        </View>
        <View style={[styles.row, styles.grandTotalRow]}>
          <Text style={styles.grandTotalLabel}>Grand Total (New):</Text>
          <Text style={styles.grandTotalValue}>₹ {grand_total.toFixed(2)}</Text>
        </View>
        
        <View style={[styles.row, {marginTop: 24}]}>
          <Text style={styles.diffLabel}>Difference Amount:</Text>
          <Text style={[styles.diffValue, { color: difference_amount > 0 ? '#ef4444' : '#4ade80' }]}>
            {difference_amount > 0 ? 'Customer Pays: ' : 'We Pay Customer: '}
            ₹ {Math.abs(difference_amount).toFixed(2)}
          </Text>
        </View>
      </View>

      <TouchableOpacity 
        style={[styles.submitButton, submitting && { opacity: 0.7 }]} 
        onPress={handleSettle}
        disabled={submitting}
      >
        {submitting ? (
          <ActivityIndicator color="#000" />
        ) : (
          <Text style={styles.submitButtonText}>Confirm Exchange</Text>
        )}
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0a0a0a', padding: 16 },
  summaryCard: { backgroundColor: '#141414', padding: 16, borderRadius: 8, borderWidth: 1, borderColor: '#333', marginBottom: 24 },
  title: { color: '#d4af37', fontSize: 20, fontWeight: 'bold', marginBottom: 16 },
  row: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 8 },
  label: { color: '#888', fontSize: 16 },
  value: { color: '#fff', fontSize: 16, fontWeight: 'bold' },
  grandTotalRow: { marginTop: 8, paddingTop: 12, borderTopWidth: 1, borderTopColor: '#333' },
  grandTotalLabel: { color: '#d4af37', fontSize: 18, fontWeight: 'bold' },
  grandTotalValue: { color: '#d4af37', fontSize: 18, fontWeight: 'bold' },
  diffLabel: { color: '#fff', fontSize: 16, fontWeight: 'bold' },
  diffValue: { fontSize: 16, fontWeight: 'bold' },
  submitButton: { backgroundColor: '#d4af37', padding: 16, borderRadius: 8, alignItems: 'center' },
  submitButtonText: { color: '#000', fontSize: 18, fontWeight: 'bold' }
});
