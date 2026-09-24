import React, { useEffect, useState, useCallback } from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, TextInput, ActivityIndicator } from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { axiosClient } from '../../api/axiosClient';

export default function SuppliersScreen({ navigation }: any) {
  const [suppliers, setSuppliers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  const fetchSuppliers = async (searchQuery = '') => {
    try {
      setLoading(true);
      const url = searchQuery ? `/sellers/?search=${searchQuery}` : '/sellers/';
      const response = await axiosClient.get(url);
      setSuppliers(response.data.items || response.data || []);
    } catch (error) {
      console.log('Failed to fetch Suppliers', error);
    } finally {
      setLoading(false);
    }
  };

  useFocusEffect(
    useCallback(() => {
      fetchSuppliers(search);
    }, [])
  );

  const handleSearch = (text: string) => {
    setSearch(text);
    fetchSuppliers(text);
  };

  const formatAmount = (num: number) => {
    if (!num) return '0.00';
    return Math.abs(num).toLocaleString('en-IN', { minimumFractionDigits: 2 });
  };

  const renderItem = ({ item }: { item: any }) => {
    const sName = item.name || `${item.first_name || ''} ${item.last_name || ''}`.trim() || 'Supplier';
    const sPhone = item.mobile || item.phone_number || 'N/A';
    const sBalance = Number(item.outstanding_balance || 0);

    return (
      <TouchableOpacity 
        style={styles.card} 
        onPress={() => navigation.navigate('SupplierProfile', { 
          supplierId: item.id, 
          supplierName: sName,
          item: item 
        })}
      >
        <View style={styles.cardHeader}>
          <Text style={styles.name}>{sName}</Text>
          <Text style={[styles.balance, { color: sBalance > 0 ? '#ef4444' : '#10b981' }]}>
            ₹ {formatAmount(sBalance)} {sBalance > 0 ? '(Cr)' : (sBalance < 0 ? '(Dr)' : '')}
          </Text>
        </View>
        <View style={styles.cardBody}>
          <Text style={styles.detail}>📱 {sPhone}</Text>
          <Text style={styles.detail}>{item.city || item.address || 'N/A'}</Text>
        </View>
      </TouchableOpacity>
    );
  };

  return (
    <View style={styles.container}>
      <TextInput
        style={styles.searchInput}
        placeholder="Search Suppliers by name or phone..."
        placeholderTextColor="#888"
        value={search}
        onChangeText={handleSearch}
      />
      
      {loading ? (
        <ActivityIndicator size="large" color="#d4af37" style={{ marginTop: 20 }} />
      ) : (
        <FlatList
          data={suppliers}
          keyExtractor={(item) => item.id.toString()}
          renderItem={renderItem}
          contentContainerStyle={{ paddingBottom: 80 }}
          ListEmptyComponent={<Text style={styles.emptyText}>No Suppliers found.</Text>}
        />
      )}
      
      <TouchableOpacity 
        style={styles.fab} 
        onPress={() => navigation.navigate('CreateCRM', { type: 'Supplier' })}
      >
        <Text style={styles.fabText}>+</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a0a0a',
    padding: 16,
  },
  fab: {
    position: 'absolute',
    width: 56,
    height: 56,
    alignItems: 'center',
    justifyContent: 'center',
    right: 20,
    bottom: 24,
    backgroundColor: '#d4af37',
    borderRadius: 28,
    elevation: 8,
    shadowColor: '#000',
    shadowOpacity: 0.3,
    shadowOffset: { width: 0, height: 2 },
    shadowRadius: 4,
  },
  fabText: {
    fontSize: 30,
    color: '#0a0a0a',
    fontWeight: 'bold',
    lineHeight: 34,
  },
  searchInput: {
    backgroundColor: '#141414',
    color: '#fff',
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#333',
    marginBottom: 16,
  },
  card: {
    backgroundColor: '#141414',
    padding: 16,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#333',
    marginBottom: 12,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  name: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    flex: 1,
  },
  balance: {
    fontSize: 14,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  cardBody: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  detail: {
    color: '#888',
    fontSize: 13,
  },
  emptyText: {
    color: '#888',
    textAlign: 'center',
    marginTop: 40,
  }
});
