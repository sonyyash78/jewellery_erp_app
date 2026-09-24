import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, TextInput, ActivityIndicator } from 'react-native';
import { axiosClient } from '../../api/axiosClient';

export default function InventoryScreen({ navigation }: any) {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [metalFilter, setMetalFilter] = useState('');

  const fetchItems = async (searchQuery = '', metal = '') => {
    try {
      setLoading(true);
      const response = await axiosClient.get('/stock/', {
        params: { search: searchQuery, metal: metal }
      });
      setItems(response.data.items || []);
    } catch (error) {
      console.log('Failed to fetch inventory', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchItems(search, metalFilter);
  }, [metalFilter]);

  const handleSearch = (text: string) => {
    setSearch(text);
    // Real app should debounce
    fetchItems(text, metalFilter);
  };

  const renderItem = ({ item }: { item: any }) => (
    <View style={styles.card}>
      <View style={styles.cardHeader}>
        <Text style={styles.itemCode}>{item.item_code}</Text>
        <View style={[styles.statusBadge, item.status === 'Available' ? styles.statusAvailable : styles.statusSold]}>
          <Text style={item.status === 'Available' ? styles.statusTextAvailable : styles.statusTextSold}>
            {item.status}
          </Text>
        </View>
      </View>
      
      <Text style={styles.itemName}>{item.item_name}</Text>
      
      <View style={styles.cardBody}>
        <View style={styles.col}>
          <Text style={styles.detailLabel}>Category</Text>
          <Text style={styles.detailValue}>{item.category}</Text>
        </View>
        <View style={styles.col}>
          <Text style={styles.detailLabel}>Metal / Purity</Text>
          <Text style={styles.detailValue}>{item.metal} {item.purity && `• ${item.purity}`}</Text>
        </View>
        <View style={styles.colRight}>
          <Text style={styles.detailLabel}>Net Wt</Text>
          <Text style={styles.weightValue}>{item.net_weight}g</Text>
        </View>
      </View>
    </View>
  );

  return (
    <View style={styles.container}>
      {/* Tabs */}
      <View style={styles.tabsContainer}>
        {['', 'Gold', 'Silver'].map((metal) => (
          <TouchableOpacity 
            key={metal} 
            style={[styles.tab, metalFilter === metal && styles.activeTab]}
            onPress={() => setMetalFilter(metal)}
          >
            <Text style={[styles.tabText, metalFilter === metal && styles.activeTabText]}>
              {metal === '' ? 'All' : metal}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      <TextInput
        style={styles.searchInput}
        placeholder="Search Item Code or Name..."
        placeholderTextColor="#888"
        value={search}
        onChangeText={handleSearch}
      />
      
      {loading ? (
        <ActivityIndicator size="large" color="#d4af37" style={{ marginTop: 20 }} />
      ) : (
        <FlatList
          data={items}
          keyExtractor={(item) => item.id.toString()}
          renderItem={renderItem}
          contentContainerStyle={{ paddingBottom: 20 }}
          ListEmptyComponent={<Text style={styles.emptyText}>No inventory items found.</Text>}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a0a0a',
    padding: 16,
  },
  tabsContainer: {
    flexDirection: 'row',
    marginBottom: 16,
    backgroundColor: '#141414',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#333',
    overflow: 'hidden',
  },
  tab: {
    flex: 1,
    paddingVertical: 12,
    alignItems: 'center',
    borderRightWidth: 1,
    borderRightColor: '#333',
  },
  activeTab: {
    backgroundColor: '#d4af37',
  },
  tabText: {
    color: '#888',
    fontWeight: 'bold',
    textTransform: 'uppercase',
    fontSize: 12,
  },
  activeTabText: {
    color: '#000',
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
    marginBottom: 4,
  },
  itemCode: {
    color: '#d4af37',
    fontSize: 14,
    fontWeight: 'bold',
    fontFamily: 'monospace',
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 4,
    borderWidth: 1,
  },
  statusAvailable: {
    backgroundColor: 'rgba(34, 197, 94, 0.2)',
    borderColor: 'rgba(34, 197, 94, 0.5)',
  },
  statusSold: {
    backgroundColor: 'rgba(239, 68, 68, 0.2)',
    borderColor: 'rgba(239, 68, 68, 0.5)',
  },
  statusTextAvailable: {
    color: '#4ade80',
    fontSize: 10,
    fontWeight: 'bold',
    textTransform: 'uppercase',
  },
  statusTextSold: {
    color: '#f87171',
    fontSize: 10,
    fontWeight: 'bold',
    textTransform: 'uppercase',
  },
  itemName: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 12,
  },
  cardBody: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  col: {
    flex: 1,
  },
  colRight: {
    flex: 1,
    alignItems: 'flex-end',
  },
  detailLabel: {
    color: '#888',
    fontSize: 10,
    textTransform: 'uppercase',
    marginBottom: 2,
  },
  detailValue: {
    color: '#ccc',
    fontSize: 12,
  },
  weightValue: {
    color: '#d4af37',
    fontSize: 16,
    fontWeight: 'bold',
  },
  emptyText: {
    color: '#888',
    textAlign: 'center',
    marginTop: 20,
  }
});
