import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, FlatList, TextInput, ActivityIndicator, TouchableOpacity } from 'react-native';
import { axiosClient } from '../../api/axiosClient';

export default function BillingScreen({ navigation }: any) {
  const [invoices, setInvoices] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  const fetchInvoices = async (searchQuery = '') => {
    try {
      setLoading(true);
      const url = searchQuery ? `/invoices/?search=${searchQuery}&skip=0&limit=50` : '/invoices/?skip=0&limit=50';
      const response = await axiosClient.get(url);
      setInvoices(response.data.items || response.data || []);
    } catch (error) {
      console.log('Failed to fetch invoices', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Refresh when screen comes into focus
    const unsubscribe = navigation.addListener('focus', () => {
      fetchInvoices(search);
    });
    return unsubscribe;
  }, [navigation, search]);

  const handleSearch = (text: string) => {
    setSearch(text);
    fetchInvoices(text);
  };

  const renderItem = ({ item }: { item: any }) => (
    <TouchableOpacity 
      style={styles.card}
      onPress={() => navigation.navigate('InvoiceDetail', { invoiceId: item.id })}
    >
      <View style={styles.cardHeader}>
        <Text style={styles.invoiceNumber}>{item.invoice_number}</Text>
        <Text style={styles.date}>{new Date(item.invoice_date).toLocaleDateString('en-IN')}</Text>
      </View>
      
      <View style={styles.cardBody}>
        <View>
          <Text style={styles.customerName}>
            {item.customer ? `${item.customer.first_name} ${item.customer.last_name || ''}`.trim() : 'Walk-in'}
          </Text>
          <Text style={styles.phone}>{item.customer?.phone_number || '-'}</Text>
        </View>
        <View style={styles.amountContainer}>
          <Text style={styles.amount}>₹{Number(item.grand_total).toLocaleString('en-IN')}</Text>
          <View style={[styles.statusBadge, item.status === 'Paid' ? styles.statusPaid : styles.statusDraft]}>
            <Text style={item.status === 'Paid' ? styles.statusTextPaid : styles.statusTextDraft}>{item.status}</Text>
          </View>
        </View>
      </View>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <TouchableOpacity 
        style={styles.createButton}
        onPress={() => navigation.navigate('CreateInvoice')}
      >
        <Text style={styles.createButtonText}>+ Create New Invoice</Text>
      </TouchableOpacity>

      <TextInput
        style={styles.searchInput}
        placeholder="Search Invoice Number or Customer..."
        placeholderTextColor="#888"
        value={search}
        onChangeText={handleSearch}
      />
      
      {loading ? (
        <ActivityIndicator size="large" color="#d4af37" style={{ marginTop: 20 }} />
      ) : (
        <FlatList
          data={invoices}
          keyExtractor={(item) => item.id.toString()}
          renderItem={renderItem}
          contentContainerStyle={{ paddingBottom: 20 }}
          ListEmptyComponent={<Text style={styles.emptyText}>No invoices found.</Text>}
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
  createButton: {
    backgroundColor: '#d4af37',
    padding: 14,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 16,
  },
  createButtonText: {
    color: '#000',
    fontWeight: 'bold',
    fontSize: 16,
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
    marginBottom: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#333',
    paddingBottom: 8,
  },
  invoiceNumber: {
    color: '#d4af37',
    fontSize: 14,
    fontWeight: 'bold',
    fontFamily: 'monospace',
  },
  date: {
    color: '#888',
    fontSize: 12,
  },
  cardBody: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  customerName: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  phone: {
    color: '#888',
    fontSize: 12,
    marginTop: 2,
  },
  amountContainer: {
    alignItems: 'flex-end',
  },
  amount: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 4,
    borderWidth: 1,
  },
  statusPaid: {
    backgroundColor: 'rgba(34, 197, 94, 0.2)',
    borderColor: 'rgba(34, 197, 94, 0.5)',
  },
  statusDraft: {
    backgroundColor: 'rgba(234, 179, 8, 0.2)',
    borderColor: 'rgba(234, 179, 8, 0.5)',
  },
  statusTextPaid: {
    color: '#4ade80',
    fontSize: 10,
    fontWeight: 'bold',
    textTransform: 'uppercase',
  },
  statusTextDraft: {
    color: '#eab308',
    fontSize: 10,
    fontWeight: 'bold',
    textTransform: 'uppercase',
  },
  emptyText: {
    color: '#888',
    textAlign: 'center',
    marginTop: 20,
  }
});
