import React, { useState, useCallback } from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, TextInput, ActivityIndicator } from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { Ionicons } from '@expo/vector-icons';
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

  useFocusEffect(
    useCallback(() => {
      fetchItems(search, metalFilter);
    }, [metalFilter])
  );

  const handleSearch = (text: string) => {
    setSearch(text);
    fetchItems(text, metalFilter);
  };

  const totalItems = items.length;
  const totalWeight = items.reduce((acc, item) => acc + (item.net_weight || 0), 0);

  const renderItem = ({ item }: { item: any }) => {
    const isAvailable = item.status === 'Available';
    const fineWt = (item.net_weight * (((item.tanch || 0) + (item.wastage || 0)) / 100)).toFixed(3);
    const purityText = item.purity ? `${item.metal} • ${item.purity}` : item.metal;

    return (
      <View style={styles.rowCard}>
        {/* QR Code Placeholder */}
        <View style={styles.qrBox}>
          <Ionicons name="qr-code" size={32} color="#000" />
        </View>

        {/* Info Container */}
        <View style={styles.infoContainer}>
          <View style={styles.rowHeader}>
            <Text style={styles.itemCode}>{item.item_code}</Text>
            <View style={[styles.statusBadge, isAvailable ? styles.statusAvailable : styles.statusSold]}>
              <Text style={isAvailable ? styles.statusTextAvailable : styles.statusTextSold}>
                {item.status}
              </Text>
            </View>
          </View>
          
          <View style={styles.detailsRow}>
            <View style={{ flex: 1 }}>
              <Text style={styles.itemName}>{item.item_name}</Text>
            </View>
            <View style={{ flex: 1 }}>
              <Text style={styles.categoryText}>{item.category}</Text>
              <Text style={styles.purityText}>{purityText}</Text>
            </View>
            <View style={{ flex: 1.2, alignItems: 'flex-end' }}>
              <Text style={styles.netWtText}>{item.net_weight}g</Text>
              <Text style={styles.fineWtText}>
                Fine: {fineWt}g ({item.tanch || 0}% + {item.wastage || 0}%)
              </Text>
            </View>
          </View>
        </View>
      </View>
    );
  };

  return (
    <View style={styles.container}>
      {/* Top Summary Cards */}
      <View style={styles.summaryContainer}>
        <View style={styles.summaryCard}>
          <View style={styles.summaryIconBox}>
            <Ionicons name="cube" size={20} color="#d4af37" />
          </View>
          <View>
            <Text style={styles.summaryLabel}>TOTAL ITEMS</Text>
            <Text style={styles.summaryValue}>{totalItems}</Text>
          </View>
        </View>
        <View style={styles.summaryCard}>
          <View style={styles.summaryIconBox}>
            <Ionicons name="cube" size={20} color="#d4af37" />
          </View>
          <View>
            <Text style={styles.summaryLabel}>TOTAL WEIGHT (NET)</Text>
            <Text style={styles.summaryValue}>{totalWeight.toFixed(3)}g</Text>
          </View>
        </View>
      </View>

      <TouchableOpacity 
        style={styles.addButton} 
        onPress={() => navigation.navigate('CreateInventory')}
      >
        <Ionicons name="add-circle-outline" size={20} color="#000" />
        <Text style={styles.addButtonText}>ADD NEW ITEM</Text>
      </TouchableOpacity>

      {/* Tabs */}
      <View style={styles.tabsContainer}>
        {['', 'Gold', 'Silver'].map((metal) => {
          const isActive = metalFilter === metal;
          return (
            <TouchableOpacity 
              key={metal} 
              style={[styles.tab, isActive && styles.activeTab]}
              onPress={() => setMetalFilter(metal)}
            >
              <Text style={[styles.tabText, isActive && styles.activeTabText]}>
                {metal === '' ? 'ALL INVENTORY' : `${metal.toUpperCase()} ITEMS`}
              </Text>
            </TouchableOpacity>
          );
        })}
      </View>

      {/* Search Bar */}
      <View style={styles.searchContainer}>
        <Ionicons name="search" size={20} color="#888" style={{ marginRight: 8 }} />
        <TextInput
          style={styles.searchInput}
          placeholder="Search by Item Code or Name..."
          placeholderTextColor="#888"
          value={search}
          onChangeText={handleSearch}
        />
      </View>
      
      {/* List */}
      <View style={styles.listHeaderRow}>
        <Text style={styles.listHeaderLabel}>INVENTORY LIST</Text>
      </View>

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
  summaryContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
    gap: 12,
  },
  summaryCard: {
    flex: 1,
    backgroundColor: '#141414',
    padding: 16,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#333',
    flexDirection: 'row',
    alignItems: 'center',
  },
  summaryIconBox: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: 'rgba(212, 175, 55, 0.1)',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  summaryLabel: {
    color: '#888',
    fontSize: 10,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  summaryValue: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  addButton: {
    backgroundColor: '#ffcc00',
    flexDirection: 'row',
    paddingVertical: 14,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
    gap: 8,
  },
  addButtonText: {
    color: '#0a0a0a',
    fontWeight: 'bold',
    fontSize: 14,
  },
  tabsContainer: {
    flexDirection: 'row',
    borderBottomWidth: 1,
    borderBottomColor: '#333',
    marginBottom: 16,
  },
  tab: {
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderBottomWidth: 2,
    borderBottomColor: 'transparent',
  },
  activeTab: {
    borderBottomColor: '#d4af37',
  },
  tabText: {
    color: '#888',
    fontWeight: 'bold',
    fontSize: 12,
  },
  activeTabText: {
    color: '#d4af37',
  },
  searchContainer: {
    flexDirection: 'row',
    backgroundColor: '#141414',
    borderWidth: 1,
    borderColor: '#333',
    borderRadius: 8,
    paddingHorizontal: 12,
    alignItems: 'center',
    marginBottom: 16,
  },
  searchInput: {
    flex: 1,
    color: '#fff',
    paddingVertical: 12,
    fontSize: 14,
  },
  listHeaderRow: {
    borderBottomWidth: 1,
    borderBottomColor: '#333',
    paddingBottom: 8,
    marginBottom: 12,
  },
  listHeaderLabel: {
    color: '#666',
    fontSize: 10,
    fontWeight: 'bold',
  },
  rowCard: {
    flexDirection: 'row',
    backgroundColor: '#141414',
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#333',
    marginBottom: 12,
  },
  qrBox: {
    width: 50,
    height: 50,
    backgroundColor: '#fff',
    borderRadius: 4,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  infoContainer: {
    flex: 1,
  },
  rowHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  itemCode: {
    color: '#fff',
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
    backgroundColor: 'rgba(34, 197, 94, 0.1)',
    borderColor: 'rgba(34, 197, 94, 0.3)',
  },
  statusSold: {
    backgroundColor: 'rgba(239, 68, 68, 0.1)',
    borderColor: 'rgba(239, 68, 68, 0.3)',
  },
  statusTextAvailable: {
    color: '#4ade80',
    fontSize: 10,
    fontWeight: 'bold',
  },
  statusTextSold: {
    color: '#f87171',
    fontSize: 10,
    fontWeight: 'bold',
  },
  detailsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  itemName: {
    color: '#ccc',
    fontSize: 12,
  },
  categoryText: {
    color: '#82b1ff',
    fontSize: 12,
  },
  purityText: {
    color: '#d4af37',
    fontSize: 10,
    marginTop: 2,
  },
  netWtText: {
    color: '#ffb74d',
    fontSize: 14,
    fontWeight: 'bold',
  },
  fineWtText: {
    color: '#4ade80',
    fontSize: 10,
    marginTop: 2,
  },
  emptyText: {
    color: '#888',
    textAlign: 'center',
    marginTop: 20,
  }
});
