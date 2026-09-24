import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, FlatList, ActivityIndicator, TouchableOpacity } from 'react-native';
import { axiosClient } from '../../api/axiosClient';

export default function SupplierProfileScreen({ route, navigation }: any) {
  const { SupplierId, SupplierName } = route.params;
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    navigation.setOptions({ title: SupplierName });
    fetchProfile();
  }, [SupplierId]);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      const response = await axiosClient.get(`/Suppliers/${SupplierId}/bills`);
      setData(response.data);
    } catch (error) {
      console.log('Failed to fetch profile', error);
    } finally {
      setLoading(false);
    }
  };

  const renderBill = ({ item }: { item: any }) => (
    <View style={styles.billCard}>
      <View style={styles.billHeader}>
        <Text style={styles.billDate}>{new Date(item.date).toLocaleDateString()}</Text>
        <Text style={styles.billType}>{item.type}</Text>
      </View>
      <View style={styles.billBody}>
        <Text style={styles.billSummary}>{item.summary}</Text>
        <Text style={styles.billAmount}>
          {item.debit > 0 ? `+ ₹${item.debit}` : ''}
          {item.credit > 0 ? `- ₹${item.credit}` : ''}
        </Text>
      </View>
    </View>
  );

  if (loading) {
    return (
      <View style={[styles.container, { justifyContent: 'center' }]}>
        <ActivityIndicator size="large" color="#d4af37" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Balances */}
      <View style={styles.balancesContainer}>
        <View style={styles.balanceCard}>
          <Text style={styles.balanceLabel}>₹ Balance</Text>
          <Text style={styles.balanceValue}>₹{data?.outstanding_balance || 0}</Text>
        </View>
        <View style={styles.balanceCard}>
          <Text style={styles.balanceLabel}>Gold (g)</Text>
          <Text style={styles.balanceValue}>{data?.fine_gold_balance || 0}g</Text>
        </View>
        <View style={styles.balanceCard}>
          <Text style={styles.balanceLabel}>Silver (g)</Text>
          <Text style={styles.balanceValue}>{data?.fine_silver_balance || 0}g</Text>
        </View>
      </View>

      {/* Action Buttons */}
      <TouchableOpacity style={styles.actionButton}>
        <Text style={styles.actionButtonText}>Record Settlement</Text>
      </TouchableOpacity>

      {/* Ledger */}
      <Text style={styles.sectionTitle}>Ledger History</Text>
      <FlatList
        data={data?.bills || []}
        keyExtractor={(item) => item.id.toString()}
        renderItem={renderBill}
        contentContainerStyle={{ paddingBottom: 20 }}
        ListEmptyComponent={<Text style={styles.emptyText}>No history found.</Text>}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a0a0a',
    padding: 16,
  },
  balancesContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  balanceCard: {
    flex: 0.31,
    backgroundColor: '#141414',
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#333',
    alignItems: 'center',
  },
  balanceLabel: {
    color: '#888',
    fontSize: 12,
    textTransform: 'uppercase',
    marginBottom: 4,
    fontWeight: 'bold',
  },
  balanceValue: {
    color: '#d4af37',
    fontSize: 16,
    fontWeight: 'bold',
  },
  actionButton: {
    backgroundColor: '#d4af37',
    padding: 14,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 20,
  },
  actionButtonText: {
    color: '#000',
    fontWeight: 'bold',
    fontSize: 16,
  },
  sectionTitle: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 12,
  },
  billCard: {
    backgroundColor: '#141414',
    padding: 16,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#333',
    marginBottom: 12,
  },
  billHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  billDate: {
    color: '#d4af37',
    fontSize: 12,
    fontWeight: 'bold',
  },
  billType: {
    color: '#888',
    fontSize: 12,
  },
  billBody: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  billSummary: {
    color: '#fff',
    fontSize: 14,
    flex: 1,
  },
  billAmount: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
  },
  emptyText: {
    color: '#888',
    textAlign: 'center',
    marginTop: 20,
  }
});
