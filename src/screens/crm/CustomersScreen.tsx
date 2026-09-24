import React, { useEffect, useState, useCallback } from 'react';
import { Alert, View, Text, StyleSheet, FlatList, TouchableOpacity, TextInput, ActivityIndicator } from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { Ionicons } from '@expo/vector-icons';
import { axiosClient } from '../../api/axiosClient';

export default function CustomersScreen({ route, navigation }: any) {
  const initialTab = route.params?.initialTab || 'customers';
  const [activeTab, setActiveTab] = useState(initialTab);
  
  const [customers, setCustomers] = useState<any[]>([]);
  const [suppliers, setSuppliers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  const fetchCRMData = async (searchQuery = '') => {
    try {
      setLoading(true);
      const custUrl = searchQuery ? `/customers/?search=${searchQuery}` : '/customers/';
      const suppUrl = searchQuery ? `/suppliers/?search=${searchQuery}` : '/suppliers/';
      
      const [custRes, suppRes] = await Promise.all([
        axiosClient.get(custUrl),
        axiosClient.get(suppUrl)
      ]);
      
      setCustomers(custRes.data.items || []);
      setSuppliers(suppRes.data.items || []);
    } catch (error) {
      console.log('Failed to fetch CRM data', error);
    } finally {
      setLoading(false);
    }
  };

  useFocusEffect(
    useCallback(() => {
      fetchCRMData(search);
    }, [])
  );

  const handleSearch = (text: string) => {
    setSearch(text);
    fetchCRMData(text);
  };


  const formatAmount = (num: number) => {
    if (!num) return '0';
    const absNum = Math.abs(parseFloat(num as any) || 0);
    let formatted = '';
    if (absNum >= 10000000) {
      formatted = (absNum / 10000000).toFixed(2) + 'Cr';
    } else if (absNum >= 100000) {
      formatted = (absNum / 100000).toFixed(2) + 'L';
    } else if (absNum >= 1000) {
      formatted = (absNum / 1000).toFixed(2) + 'K';
    } else {
      formatted = absNum.toFixed(2);
    }
    formatted = formatted.replace(/\.00([a-zA-Z]*)$/, '$1'); // clean up trailing .00
    return (num < 0 ? '-' : '') + formatted;
  };

  const totalCustomers = customers.length;
  const totalSuppliers = suppliers.length;
  const netOutstanding = customers.reduce((acc, c) => acc + (parseFloat(c.outstanding_balance as any) || 0), 0);

  
  const handleDelete = (id: number, type: string) => {
    Alert.alert(
      `Delete ${type}`,
      `Are you sure you want to delete this ${type.toLowerCase()}?`,
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Delete', 
          style: 'destructive',
          onPress: async () => {
            try {
              const endpoint = type === 'Customer' ? `/customers/${id}` : `/suppliers/${id}`;
              await axiosClient.delete(endpoint);
              fetchCRMData(search); // refresh list
            } catch (error) {
              Alert.alert('Error', `Failed to delete ${type.toLowerCase()}`);
            }
          }
        }
      ]
    );
  };

  const currentData = activeTab === 'customers' ? customers : suppliers;

  const renderItem = ({ item }: { item: any }) => {
    const isCustomer = activeTab === 'customers';
    
    return (
      <View style={styles.rowCard}>
        <View style={styles.cardHeader}>
          <View style={styles.nameRow}>
            <Ionicons name="person-circle" size={24} color="#888" style={{ marginRight: 8 }} />
            <Text style={styles.itemName}>{isCustomer ? `${item.first_name} ${item.last_name || ''}` : item.name}</Text>
          </View>
          <Text style={styles.outstandingValue}>
            ₹ {formatAmount(item.outstanding_balance || 0)}
          </Text>
        </View>

        <View style={styles.detailsGrid}>
          <View style={styles.detailCol}>
            <Text style={styles.detailLabel}>CONTACT</Text>
            <Text style={styles.detailValue}>{item.phone_number || item.mobile || 'N/A'}</Text>
          </View>
          <View style={styles.detailCol}>
            <Text style={styles.detailLabel}>CITY</Text>
            <Text style={styles.detailValue}>{item.city || 'N/A'}</Text>
          </View>
          <View style={styles.detailCol}>
            <Text style={styles.detailLabel}>GST / ID</Text>
            <Text style={styles.detailValue}>{item.gst_number || 'N/A'}</Text>
          </View>
          <View style={styles.detailCol}>
            <Text style={styles.detailLabel}>CREDIT LIMIT</Text>
            <Text style={styles.detailValue}>₹ {formatAmount(item.credit_limit || 0)}</Text>
          </View>
        </View>

        <View style={styles.actionsRow}>
          <TouchableOpacity 
            style={[styles.actionBtn, styles.editBtn]}
            onPress={() => {
              // Wait, we don't have EditCRMScreen yet, but we will make it, or just use CreateCRM with item.
              navigation.navigate('CreateCRM', { type: isCustomer ? 'Customer' : 'Supplier', item });
            }}
          >
            <Text style={[styles.actionBtnText, {color: "#d4af37"}]}>EDIT</Text>
          </TouchableOpacity>
          <TouchableOpacity 
            style={[styles.actionBtn, styles.ledgerBtn]}
            onPress={() => navigation.navigate(isCustomer ? 'CustomerProfile' : 'SupplierProfile', { 
              customerId: item.id, 
              supplierId: item.id, 
              customerName: isCustomer ? `${item.first_name} ${item.last_name || ""}`.trim() : item.name, item: item,
              supplierName: isCustomer ? `${item.first_name} ${item.last_name || ""}`.trim() : item.name
            })}
          >
            <Text style={[styles.actionBtnText, {color: "#d4af37"}]}>LEDGER</Text>
          </TouchableOpacity>
          <TouchableOpacity style={[styles.actionBtn, styles.deleteBtn]} onPress={() => handleDelete(item.id, isCustomer ? "Customer" : "Supplier")}>
            <Text style={[styles.actionBtnText, {color: "#f87171"}]}>DELETE</Text>
          </TouchableOpacity>
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
            <Ionicons name="people" size={16} color="#d4af37" />
          </View>
          <View style={{ flex: 1 }}>
            <Text style={styles.summaryLabel} numberOfLines={1} adjustsFontSizeToFit>TOTAL CUSTOMERS</Text>
            <Text style={styles.summaryValue}>{totalCustomers}</Text>
          </View>
        </View>
        
        <View style={styles.summaryCard}>
          <View style={styles.summaryIconBox}>
            <Ionicons name="business" size={16} color="#d4af37" />
          </View>
          <View style={{ flex: 1 }}>
            <Text style={styles.summaryLabel} numberOfLines={1} adjustsFontSizeToFit>TOTAL SUPPLIERS</Text>
            <Text style={styles.summaryValue}>{totalSuppliers}</Text>
          </View>
        </View>
      </View>

      <View style={styles.summaryContainer}>
        <View style={styles.summaryCardLarge}>
          <View style={styles.summaryIconBox}>
            <Ionicons name="wallet" size={20} color="#d4af37" />
          </View>
          <View style={{ flex: 1 }}>
            <Text style={styles.summaryLabel}>NET OUTSTANDING</Text>
            <Text style={styles.summaryValueBig} numberOfLines={1} adjustsFontSizeToFit>₹ {formatAmount(netOutstanding)}</Text>
          </View>
        </View>
        
        <TouchableOpacity 
          style={styles.addButton}
          onPress={() => navigation.navigate('CreateCRM', { type: activeTab === 'customers' ? 'Customer' : 'Supplier' })}
        >
          <Ionicons name="add-circle-outline" size={20} color="#000" />
          <Text style={styles.addButtonText}>ADD {activeTab === 'customers' ? 'CUSTOMER' : 'SUPPLIER'}</Text>
        </TouchableOpacity>
      </View>

      {/* Tabs */}
      <View style={styles.tabsContainer}>
        <TouchableOpacity 
          style={[styles.tab, activeTab === 'customers' && styles.activeTab]}
          onPress={() => setActiveTab('customers')}
        >
          <Text style={[styles.tabText, activeTab === 'customers' && styles.activeTabText]}>CUSTOMERS DIRECTORY</Text>
        </TouchableOpacity>
        <TouchableOpacity 
          style={[styles.tab, activeTab === 'suppliers' && styles.activeTab]}
          onPress={() => setActiveTab('suppliers')}
        >
          <Text style={[styles.tabText, activeTab === 'suppliers' && styles.activeTabText]}>SUPPLIERS DIRECTORY</Text>
        </TouchableOpacity>
      </View>

      {/* Search Bar */}
      <View style={styles.searchContainer}>
        <Ionicons name="search" size={20} color="#888" style={{ marginRight: 8 }} />
        <TextInput
          style={styles.searchInput}
          placeholder={`Search ${activeTab}...`}
          placeholderTextColor="#888"
          value={search}
          onChangeText={handleSearch}
        />
      </View>
      
      {/* List */}
      {loading ? (
        <ActivityIndicator size="large" color="#d4af37" style={{ marginTop: 20 }} />
      ) : (
        <FlatList
          data={currentData}
          keyExtractor={(item) => item.id.toString()}
          renderItem={renderItem}
          contentContainerStyle={{ paddingBottom: 20 }}
          ListEmptyComponent={<Text style={styles.emptyText}>No {activeTab} found.</Text>}
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
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#333',
    flexDirection: 'row',
    alignItems: 'center',
  },
  summaryCardLarge: {
    flex: 1.5,
    backgroundColor: '#141414',
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#333',
    flexDirection: 'row',
    alignItems: 'center',
  },
  summaryIconBox: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: 'rgba(212, 175, 55, 0.1)',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 8,
  },
  summaryLabel: {
    color: '#888',
    fontSize: 10,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  summaryValue: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  summaryValueBig: {
    color: '#ffb74d',
    fontSize: 16,
    fontWeight: 'bold',
  },
  addButton: {
    flex: 1,
    backgroundColor: '#ffcc00',
    flexDirection: 'row',
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 8,
  },
  addButtonText: {
    color: '#0a0a0a',
    fontWeight: 'bold',
    fontSize: 12,
    marginLeft: 4,
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
    fontSize: 11,
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
  rowCard: {
    backgroundColor: '#141414',
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#333',
    marginBottom: 12,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#222',
    paddingBottom: 8,
  },
  nameRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  itemName: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  outstandingValue: {
    color: '#ffb74d',
    fontSize: 14,
    fontWeight: 'bold',
  },
  detailsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 12,
  },
  detailCol: {
    width: '50%',
    marginBottom: 8,
  },
  detailLabel: {
    color: '#666',
    fontSize: 10,
    fontWeight: 'bold',
    marginBottom: 2,
  },
  detailValue: {
    color: '#ccc',
    fontSize: 12,
  },
  actionsRow: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    gap: 8,
    borderTopWidth: 1,
    borderTopColor: '#222',
    paddingTop: 12,
  },
  actionBtn: {
    paddingVertical: 4,
    paddingHorizontal: 12,
    borderRadius: 4,
  },
  actionBtnText: {
    fontSize: 10,
    fontWeight: 'bold',
  },
  editBtn: {
    backgroundColor: 'rgba(212, 175, 55, 0.2)',
  },
  ledgerBtn: {
    backgroundColor: 'rgba(212, 175, 55, 0.2)',
  },
  deleteBtn: {
    backgroundColor: 'rgba(239, 68, 68, 0.2)',
  },
  emptyText: {
    color: '#888',
    textAlign: 'center',
    marginTop: 20,
  }
});

