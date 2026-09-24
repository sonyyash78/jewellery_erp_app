import React, { useState, useCallback } from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, ActivityIndicator, Alert } from 'react-native';
import { axiosClient } from '../../api/axiosClient';
import { useFocusEffect } from '@react-navigation/native';

export default function ExchangeScreen({ navigation }: any) {
  const [exchanges, setExchanges] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchExchanges = async () => {
    try {
      setLoading(true);
      const response = await axiosClient.get('/exchanges/');
      setExchanges(response.data.items || []);
    } catch (error) {
      console.log('Failed to fetch exchanges', error);
    } finally {
      setLoading(false);
    }
  };

  useFocusEffect(
    useCallback(() => {
      fetchExchanges();
    }, [])
  );

  const formatDate = (dateString?: string) => {
    if (!dateString) return '-';
    try {
      const d = new Date(dateString);
      if (isNaN(d.getTime())) return String(dateString);
      return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
    } catch {
      return String(dateString);
    }
  };

  const fmt = (n?: any) => {
    const num = Number(n);
    if (isNaN(num)) return '0.00';
    return num.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  };

  const renderItem = ({ item }: any) => {
    const oldVal = Number(item.total_old_value || 0);
    const newVal = Number(item.total_new_value || item.grand_total || 0);
    const diff = Number(item.difference_amount || 0);
    const custName = item.customer 
      ? `${item.customer.first_name || ''} ${item.customer.last_name || ''}`.trim() || 'Walk-in Customer'
      : 'Walk-in Customer';

    return (
      <TouchableOpacity 
        style={styles.card} 
        onPress={() => navigation.navigate('InvoiceDetail', { invoiceId: item.id, isExchange: true })}
      >
        <View style={styles.cardHeader}>
          <Text style={styles.invoiceNo}>{item.exchange_no || item.invoice_number || `EXC-${item.id}`}</Text>
          <Text style={styles.date}>{formatDate(item.invoice_date || item.created_at)}</Text>
        </View>
        <View style={styles.customerRow}>
          <Text>👤</Text>
          <Text style={styles.customerName}>{custName}</Text>
        </View>
        <View style={styles.amountsRow}>
          <View>
            <Text style={styles.amountLabel}>Old Metal Value</Text>
            <Text style={styles.amountValue}>₹ {fmt(oldVal)}</Text>
          </View>
          <View style={{ alignItems: 'flex-end' }}>
            <Text style={styles.amountLabel}>New Items Value</Text>
            <Text style={styles.amountValue}>₹ {fmt(newVal)}</Text>
          </View>
        </View>
        <View style={styles.statusRow}>
          <Text style={styles.statusLabel}>Difference ({diff >= 0 ? 'Customer Pays' : 'Shop Owes'}):</Text>
          <Text style={[styles.statusText, { color: diff >= 0 ? '#ef4444' : '#4ade80' }]}>
            ₹ {fmt(Math.abs(diff))}
          </Text>
        </View>
      </TouchableOpacity>
    );
  };

  return (
    <View style={styles.container}>
      {loading ? (
        <ActivityIndicator size="large" color="#d4af37" style={{ marginTop: 20 }} />
      ) : (
        <FlatList
          data={exchanges}
          keyExtractor={(item) => item.id.toString()}
          renderItem={renderItem}
          contentContainerStyle={{ paddingBottom: 80 }}
          ListEmptyComponent={<Text style={styles.emptyText}>No exchanges found.</Text>}
        />
      )}

      <TouchableOpacity 
        style={styles.fab} 
        onPress={() => navigation.navigate('CreateExchange')}
      >
        <Text style={{fontSize: 24, fontWeight: 'bold'}}>+</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0a0a0a', padding: 16 },
  card: { backgroundColor: '#141414', padding: 16, borderRadius: 8, marginBottom: 12, borderWidth: 1, borderColor: '#333' },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 12 },
  invoiceNo: { color: '#d4af37', fontSize: 16, fontWeight: 'bold' },
  date: { color: '#888', fontSize: 14 },
  customerRow: { flexDirection: 'row', alignItems: 'center', marginBottom: 12, gap: 8 },
  customerName: { color: '#fff', fontSize: 16, fontWeight: '500' },
  amountsRow: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 12, backgroundColor: '#1a1a1a', padding: 10, borderRadius: 6 },
  amountLabel: { color: '#888', fontSize: 12, marginBottom: 4 },
  amountValue: { color: '#fff', fontSize: 16, fontWeight: 'bold' },
  statusRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', borderTopWidth: 1, borderTopColor: '#333', paddingTop: 12 },
  statusLabel: { color: '#888', fontSize: 14 },
  statusText: { fontSize: 16, fontWeight: 'bold' },
  emptyText: { color: '#888', textAlign: 'center', marginTop: 40 },
  fab: { position: 'absolute', bottom: 20, right: 20, backgroundColor: '#d4af37', width: 56, height: 56, borderRadius: 28, justifyContent: 'center', alignItems: 'center', elevation: 5 },
});
