import React, { useState } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity, ScrollView, Alert, ActivityIndicator } from 'react-native';
import { axiosClient } from '../../api/axiosClient';
import { Ionicons } from '@expo/vector-icons';

export default function CreateSettlementScreen({ route, navigation }: any) {
  const { id, type, name } = route.params; // type: 'Customer' or 'Supplier'
  
  const [formData, setFormData] = useState({
    voucher_type: 'Payment',
    voucher_number: '',
    description: '',
    debit: '0',
    credit: '0',
    gold_debit: '0',
    gold_credit: '0',
    silver_debit: '0',
    silver_credit: '0'
  });
  
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    try {
      setLoading(true);
      const payload = {
        voucher_type: formData.voucher_type,
        voucher_number: formData.voucher_number || undefined,
        description: formData.description || undefined,
        debit: parseFloat(formData.debit) || 0,
        credit: parseFloat(formData.credit) || 0,
        gold_debit: parseFloat(formData.gold_debit) || 0,
        gold_credit: parseFloat(formData.gold_credit) || 0,
        silver_debit: parseFloat(formData.silver_debit) || 0,
        silver_credit: parseFloat(formData.silver_credit) || 0,
      };

      const endpoint = type === 'Customer' ? `/customers/${id}/ledger` : `/suppliers/${id}/ledger`;
      await axiosClient.post(endpoint, payload);
      
      Alert.alert('Success', 'Settlement recorded successfully!');
      navigation.goBack();
    } catch (error: any) {
      console.log('Failed to save settlement', error.response?.data || error.message);
      Alert.alert('Error', 'Failed to save settlement.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.card}>
        <View style={styles.header}>
          <Text style={styles.title}>RECORD {type.toUpperCase()} SETTLEMENT</Text>
        </View>

        <View style={styles.row}>
          <View style={styles.col}>
            <Text style={styles.label}>VOUCHER TYPE</Text>
            <View style={styles.typeGroup}>
              <TouchableOpacity 
                style={[styles.typeBtn, formData.voucher_type === 'Payment' && styles.typeBtnActive]}
                onPress={() => setFormData({...formData, voucher_type: 'Payment'})}
              >
                <Text style={[styles.typeBtnText, formData.voucher_type === 'Payment' && styles.typeBtnTextActive]}>Payment</Text>
              </TouchableOpacity>
              <TouchableOpacity 
                style={[styles.typeBtn, formData.voucher_type === 'Receipt' && styles.typeBtnActive]}
                onPress={() => setFormData({...formData, voucher_type: 'Receipt'})}
              >
                <Text style={[styles.typeBtnText, formData.voucher_type === 'Receipt' && styles.typeBtnTextActive]}>Receipt</Text>
              </TouchableOpacity>
            </View>
          </View>
          <View style={styles.col}>
            <Text style={styles.label}>REF / VOUCHER NO.</Text>
            <TextInput
              style={styles.input}
              placeholder="e.g. PAY-123"
              placeholderTextColor="#555"
              value={formData.voucher_number}
              onChangeText={(t) => setFormData({...formData, voucher_number: t})}
            />
          </View>
        </View>

        <Text style={styles.label}>REMARKS / DESCRIPTION</Text>
        <TextInput
          style={styles.input}
          placeholder="e.g. Received Cash for Due Bill"
          placeholderTextColor="#555"
          value={formData.description}
          onChangeText={(t) => setFormData({...formData, description: t})}
        />

        {/* Dual columns for Debit and Credit */}
        <View style={styles.financeContainer}>
          <View style={styles.financeCol}>
            <Text style={[styles.financeTitle, { color: '#ef4444' }]}>Debit (They Owe Us)</Text>
            
            <Text style={styles.financeLabel}>Amount (₹)</Text>
            <TextInput
              style={styles.financeInput}
              keyboardType="numeric"
              value={formData.debit}
              onChangeText={(t) => setFormData({...formData, debit: t})}
            />
            
            <Text style={styles.financeLabel}>Gold (g)</Text>
            <TextInput
              style={styles.financeInput}
              keyboardType="numeric"
              value={formData.gold_debit}
              onChangeText={(t) => setFormData({...formData, gold_debit: t})}
            />

            <Text style={styles.financeLabel}>Silver (g)</Text>
            <TextInput
              style={styles.financeInput}
              keyboardType="numeric"
              value={formData.silver_debit}
              onChangeText={(t) => setFormData({...formData, silver_debit: t})}
            />
          </View>

          <View style={styles.financeCol}>
            <Text style={[styles.financeTitle, { color: '#10b981' }]}>Credit (They Paid Us)</Text>
            
            <Text style={styles.financeLabel}>Amount (₹)</Text>
            <TextInput
              style={styles.financeInput}
              keyboardType="numeric"
              value={formData.credit}
              onChangeText={(t) => setFormData({...formData, credit: t})}
            />
            
            <Text style={styles.financeLabel}>Gold (g)</Text>
            <TextInput
              style={styles.financeInput}
              keyboardType="numeric"
              value={formData.gold_credit}
              onChangeText={(t) => setFormData({...formData, gold_credit: t})}
            />

            <Text style={styles.financeLabel}>Silver (g)</Text>
            <TextInput
              style={styles.financeInput}
              keyboardType="numeric"
              value={formData.silver_credit}
              onChangeText={(t) => setFormData({...formData, silver_credit: t})}
            />
          </View>
        </View>

        <View style={styles.footer}>
          <TouchableOpacity style={styles.cancelBtn} onPress={() => navigation.goBack()}>
            <Text style={styles.cancelBtnText}>Cancel</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.saveBtn} onPress={handleSubmit} disabled={loading}>
            {loading ? <ActivityIndicator color="#000" /> : <Text style={styles.saveBtnText}>Save Record</Text>}
          </TouchableOpacity>
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a0a0a',
    padding: 16,
  },
  card: {
    backgroundColor: '#141414',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#333',
    padding: 16,
    marginBottom: 40,
  },
  header: {
    borderBottomWidth: 1,
    borderBottomColor: '#222',
    paddingBottom: 16,
    marginBottom: 16,
  },
  title: {
    color: '#d4af37',
    fontSize: 18,
    fontWeight: 'bold',
    textTransform: 'uppercase',
  },
  row: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 16,
  },
  col: {
    flex: 1,
  },
  label: {
    color: '#888',
    fontSize: 10,
    fontWeight: 'bold',
    marginBottom: 6,
  },
  input: {
    backgroundColor: '#0a0a0a',
    borderWidth: 1,
    borderColor: '#333',
    borderRadius: 6,
    color: '#fff',
    padding: 10,
    fontSize: 14,
    marginBottom: 12,
  },
  typeGroup: {
    flexDirection: 'row',
    backgroundColor: '#0a0a0a',
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#333',
    overflow: 'hidden',
  },
  typeBtn: {
    flex: 1,
    paddingVertical: 10,
    alignItems: 'center',
  },
  typeBtnActive: {
    backgroundColor: '#333',
  },
  typeBtnText: {
    color: '#888',
    fontSize: 12,
    fontWeight: 'bold',
  },
  typeBtnTextActive: {
    color: '#fff',
  },
  financeContainer: {
    flexDirection: 'row',
    gap: 16,
    backgroundColor: '#0f0f0f',
    padding: 12,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#222',
    marginBottom: 20,
  },
  financeCol: {
    flex: 1,
  },
  financeTitle: {
    fontSize: 12,
    fontWeight: 'bold',
    marginBottom: 12,
    paddingBottom: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#222',
  },
  financeLabel: {
    color: '#d4af37',
    fontSize: 10,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  financeInput: {
    backgroundColor: '#000',
    borderWidth: 1,
    borderColor: '#222',
    borderRadius: 6,
    color: '#fff',
    padding: 8,
    fontSize: 14,
    marginBottom: 12,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    alignItems: 'center',
    gap: 12,
    borderTopWidth: 1,
    borderTopColor: '#222',
    paddingTop: 16,
  },
  cancelBtn: {
    padding: 12,
  },
  cancelBtnText: {
    color: '#ccc',
    fontWeight: 'bold',
  },
  saveBtn: {
    backgroundColor: '#ffcc00',
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 6,
  },
  saveBtnText: {
    color: '#000',
    fontWeight: 'bold',
  }
});
