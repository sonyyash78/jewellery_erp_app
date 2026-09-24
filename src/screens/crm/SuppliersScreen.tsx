import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, TextInput, ActivityIndicator } from 'react-native';
import { axiosClient } from '../../api/axiosClient';

export default function SuppliersScreen({ navigation }: any) {
  const [Suppliers, setSuppliers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  const fetchSuppliers = async (searchQuery = '') => {
    try {
      setLoading(true);
      const url = searchQuery ? `/sellers/?search=${searchQuery}` : '/sellers/';
      const response = await axiosClient.get(url);
      setSuppliers(response.data.items || []);
    } catch (error) {
      console.log('Failed to fetch Suppliers', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSuppliers();
  }, []);

  const handleSearch = (text: string) => {
    setSearch(text);
    // In a real app, use debounce. For now, we fetch immediately.
    fetchSuppliers(text);
  };

  const renderItem = ({ item }: { item: any }) => (
    <TouchableOpacity 
      style={styles.card} 
      onPress={() => navigation.navigate('SupplierProfile', { SupplierId: item.id, SupplierName: `${item.first_name} ${item.last_name || ""}`.trim() })}
    >
      <View style={styles.cardHeader}>
        <Text style={styles.name}>{item.first_name} {item.last_name || ""}</Text>
        <Text style={styles.balance}>₹{item.outstanding_balance || 0}</Text>
      </View>
      <View style={styles.cardBody}>
        <Text style={styles.detail}>{item.phone_number}</Text>
        <Text style={styles.detail}>{item.city}</Text>
      </View>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <TextInput
        style={styles.searchInput}
        placeholder="Search Suppliers..."
        placeholderTextColor="#888"
        value={search}
        onChangeText={handleSearch}
      />
      
      {loading ? (
        <ActivityIndicator size="large" color="#d4af37" style={{ marginTop: 20 }} />
      ) : (
        <FlatList
          data={Suppliers}
          keyExtractor={(item) => item.id.toString()}
          renderItem={renderItem}
          contentContainerStyle={{ paddingBottom: 20 }}
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
    width: 60,
    height: 60,
    alignItems: 'center',
    justifyContent: 'center',
    right: 20,
    bottom: 20,
    backgroundColor: '#d4af37',
    borderRadius: 30,
    elevation: 8,
    shadowColor: '#000',
    shadowOpacity: 0.3,
    shadowOffset: { width: 0, height: 2 },
    shadowRadius: 4,
  },
  fabText: {
    fontSize: 32,
    color: '#0a0a0a',
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
  },
  balance: {
    color: '#d4af37',
    fontSize: 16,
    fontWeight: 'bold',
  },
  cardBody: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  detail: {
    color: '#888',
    fontSize: 14,
  },
  emptyText: {
    color: '#888',
    textAlign: 'center',
    marginTop: 20,
  }
});
