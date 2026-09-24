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

  const renderItem = ({ item }: any) => (
    <TouchableOpacity 
      style={styles.card} 
      onPress={() => Alert.alert('Notice', 'Exchange Details feature coming soon!')}
    >
      <View style={styles.cardHeader}>
        <Text style={styles.invoiceNo}>{item.exchange_no}</Text>
        <Text style={styles.date}>{new Date(item.created_at).toLocaleDateString()}</Text>
      </View>
      <View style={styles.customerRow}>
        <Text>👤</Text>
        <Text style={styles.customerName}>
          {item.customer?.first_name} {item.customer?.last_name || ''}
        </Text>
      </View>
      <View style={styles.amountsRow}>
        <View>
          <Text style={styles.amountLabel}>Old Metal Value</Text>
          <Text style={styles.amountValue}>₹ {item.total_old_value.toFixed(2)}</Text>
        </View>
        <View style={{ alignItems: 'flex-end' }}>
          <Text style={styles.amountLabel}>New Items Value</Text>
          <Text style={styles.amountValue}>₹ {item.grand_total.toFixed(2)}</Text>
        </View>
      </View>
      <View style={styles.statusRow}>
        <Text style={styles.statusLabel}>Difference (Customer Pays):</Text>
        <Text style={[styles.statusText, { color: item.difference_amount > 0 ? '#ef4444' : '#4ade80' }]}>
          ₹ {Math.abs(item.difference_amount).toFixed(2)}
        </Text>
      </View>
    </TouchableOpacity>
  );

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
