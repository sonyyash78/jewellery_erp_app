import React, { useState } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity, ScrollView, Alert, ActivityIndicator } from 'react-native';
import { axiosClient } from '../../api/axiosClient';
import { Ionicons } from '@expo/vector-icons';

export default function CreateSettlementScreen({ route, navigation }: any) {
  const { id, type, name } = route.params; // type: 'Customer' or 'Supplier'
  const isSupplier = type === 'Supplier';
  
  const [formData, setFormData] = useState({
    voucher_type: isSupplier ? 'Payment' : 'Receipt',
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
        description: formData.description || (isSupplier ? 'Supplier Settlement' : 'Customer Settlement'),
        debit: parseFloat(formData.debit) || 0,
        credit: parseFloat(formData.credit) || 0,
        gold_debit: parseFloat(formData.gold_debit) || 0,
        gold_credit: parseFloat(formData.gold_credit) || 0,
        silver_debit: parseFloat(formData.silver_debit) || 0,
        silver_credit: parseFloat(formData.silver_credit) || 0,
      };

      const endpoint = isSupplier ? `/sellers/${id}/ledger` : `/customers/${id}/ledger`;
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

  const voucherTypes = ['Payment', 'Receipt', 'Metal Settlement', 'Manual'];

  return (
    <ScrollView style={styles.container}>
      <View style={styles.card}>
        <View style={styles.header}>
          <Text style={styles.title}>RECORD {type.toUpperCase()} SETTLEMENT</Text>
          {name ? <Text style={styles.partyName}>{name}</Text> : null}
        </View>

        <View style={styles.row}>
          <View style={styles.col}>
            <Text style={styles.label}>VOUCHER TYPE</Text>
            <View style={styles.typeGroup}>
              {voucherTypes.map((vType) => (
                <TouchableOpacity 
                  key={vType}
                  style={[styles.typeBtn, formData.voucher_type === vType && styles.typeBtnActive]}
                  onPress={() => setFormData({...formData, voucher_type: vType})}
                >
                  <Text style={[styles.typeBtnText, formData.voucher_type === vType && styles.typeBtnTextActive]}>
                    {vType === 'Metal Settlement' ? 'Metal Settle' : vType}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        </View>

        <View style={styles.row}>
          <View style={styles.col}>
            <Text style={styles.label}>REF / VOUCHER NO. (OPTIONAL)</Text>
            <TextInput
              style={styles.input}
              placeholder={isSupplier ? "e.g. PAY-SUP-01" : "e.g. REC-CUST-01"}
              placeholderTextColor="#555"
              value={formData.voucher_number}
              onChangeText={(t) => setFormData({...formData, voucher_number: t})}
            />
          </View>
        </View>

        <Text style={styles.label}>REMARKS / DESCRIPTION</Text>
        <TextInput
          style={styles.input}
          placeholder={isSupplier ? "e.g. Payment for Gold Purchase" : "e.g. Received Cash / Gold Deposit"}
          placeholderTextColor="#555"
          value={formData.description}
          onChangeText={(t) => setFormData({...formData, description: t})}
        />

        {/* Dual columns for Debit and Credit */}
        <View style={styles.financeContainer}>
          {/* Debit Column */}
          <View style={styles.financeCol}>
            <Text style={[styles.financeTitle, { color: '#ef4444' }]}>
              {isSupplier ? 'Debit (We Pay Them)' : 'Debit (Customer Owes)'}
            </Text>
            
            <Text style={styles.financeLabel}>Amount (₹)</Text>
            <TextInput
              style={styles.financeInput}
              keyboardType="numeric"
              placeholder="0.00"
              placeholderTextColor="#444"
              value={formData.debit}
              onChangeText={(t) => setFormData({...formData, debit: t})}
            />
            
            <Text style={styles.financeLabel}>Gold (g)</Text>
            <TextInput
              style={styles.financeInput}
              keyboardType="numeric"
              placeholder="0.000"
              placeholderTextColor="#444"
              value={formData.gold_debit}
              onChangeText={(t) => setFormData({...formData, gold_debit: t})}
            />

            <Text style={styles.financeLabel}>Silver (g)</Text>
            <TextInput
              style={styles.financeInput}
              keyboardType="numeric"
              placeholder="0.000"
              placeholderTextColor="#444"
              value={formData.silver_debit}
              onChangeText={(t) => setFormData({...formData, silver_debit: t})}
            />
          </View>

          {/* Credit Column */}
          <View style={styles.financeCol}>
            <Text style={[styles.financeTitle, { color: '#10b981' }]}>
              {isSupplier ? 'Credit (They Billed Us)' : 'Credit (Customer Paid)'}
            </Text>
            
            <Text style={styles.financeLabel}>Amount (₹)</Text>
            <TextInput
              style={styles.financeInput}
              keyboardType="numeric"
              placeholder="0.00"
              placeholderTextColor="#444"
              value={formData.credit}
              onChangeText={(t) => setFormData({...formData, credit: t})}
            />
            
            <Text style={styles.financeLabel}>Gold (g)</Text>
            <TextInput
              style={styles.financeInput}
              keyboardType="numeric"
              placeholder="0.000"
              placeholderTextColor="#444"
              value={formData.gold_credit}
              onChangeText={(t) => setFormData({...formData, gold_credit: t})}
            />

            <Text style={styles.financeLabel}>Silver (g)</Text>
            <TextInput
              style={styles.financeInput}
              keyboardType="numeric"
              placeholder="0.000"
              placeholderTextColor="#444"
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
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#333',
    padding: 16,
    marginBottom: 40,
  },
  header: {
    borderBottomWidth: 1,
    borderBottomColor: '#222',
    paddingBottom: 12,
    marginBottom: 16,
  },
  title: {
    color: '#d4af37',
    fontSize: 16,
    fontWeight: 'bold',
    letterSpacing: 0.5,
  },
  partyName: {
    color: '#aaa',
    fontSize: 13,
    marginTop: 3,
    fontWeight: '600',
  },
  row: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 12,
  },
  col: {
    flex: 1,
  },
  label: {
    color: '#888',
    fontSize: 10,
    fontWeight: 'bold',
    marginBottom: 6,
    textTransform: 'uppercase',
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
    flexWrap: 'wrap',
  },
  typeBtn: {
    flex: 1,
    minWidth: 70,
    paddingVertical: 9,
    paddingHorizontal: 4,
    alignItems: 'center',
    justifyContent: 'center',
  },
  typeBtnActive: {
    backgroundColor: '#d4af37',
  },
  typeBtnText: {
    color: '#888',
    fontSize: 11,
    fontWeight: 'bold',
  },
  typeBtnTextActive: {
    color: '#000',
  },
  financeContainer: {
    flexDirection: 'row',
    gap: 12,
    backgroundColor: '#0f0f0f',
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#222',
    marginBottom: 20,
  },
  financeCol: {
    flex: 1,
  },
  financeTitle: {
    fontSize: 11,
    fontWeight: 'bold',
    marginBottom: 10,
    paddingBottom: 6,
    borderBottomWidth: 1,
    borderBottomColor: '#222',
    textTransform: 'uppercase',
  },
  financeLabel: {
    color: '#d4af37',
    fontSize: 9.5,
    fontWeight: 'bold',
    marginBottom: 3,
  },
  financeInput: {
    backgroundColor: '#000',
    borderWidth: 1,
    borderColor: '#262626',
    borderRadius: 6,
    color: '#fff',
    padding: 8,
    fontSize: 13,
    marginBottom: 10,
    fontFamily: 'System',
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
    paddingVertical: 10,
    paddingHorizontal: 16,
  },
  cancelBtnText: {
    color: '#888',
    fontWeight: 'bold',
    fontSize: 13,
  },
  saveBtn: {
    backgroundColor: '#d4af37',
    paddingVertical: 11,
    paddingHorizontal: 22,
    borderRadius: 6,
  },
  saveBtnText: {
    color: '#000',
    fontWeight: 'bold',
    fontSize: 13,
  }
});
