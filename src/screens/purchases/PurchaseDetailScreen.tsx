import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, ActivityIndicator, TouchableOpacity, Alert } from 'react-native';
import { axiosClient } from '../../api/axiosClient';
import * as Print from 'expo-print';
import * as Sharing from 'expo-sharing';
import * as FileSystem from 'expo-file-system/legacy';
import { generateInvoiceHtml } from '../../utils/invoicePdfUtils';

export default function PurchaseDetailScreen({ route, navigation }: any) {
  const { purchaseId } = route.params;
  const [pdfData, setPdfData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPurchase();
  }, [purchaseId]);

  const fetchPurchase = async () => {
    try {
      // Fetch the full rich PDF JSON data structure from the backend
      const response = await axiosClient.get(`/purchases/${purchaseId}/pdf-data`);
      setPdfData(response.data);
    } catch (error) {
      console.log('Failed to fetch purchase pdf data', error);
      Alert.alert('Error', 'Failed to load purchase details');
      navigation.goBack();
    } finally {
      setLoading(false);
    }
  };

  const fmt = (n: number | undefined | null) => {
    if (n == null) return '0.00';
    return Number(n).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  };

  const handleCancel = () => {
    Alert.alert('Cancel Purchase', 'Are you sure you want to cancel this purchase? This will mark it as Cancelled and reverse inventory.', [
      { text: 'No', style: 'cancel' },
      { text: 'Yes, Cancel', style: 'destructive', onPress: async () => {
        try {
          await axiosClient.delete(`/purchases/${purchaseId}`);
          Alert.alert('Success', 'Purchase cancelled successfully');
          navigation.goBack();
        } catch (error) {
          console.error('Failed to cancel', error);
          Alert.alert('Error', 'Failed to cancel purchase');
        }
      }}
    ]);
  };

  const handlePrint = async () => {
    try {
      // Generate the premium HTML exactly like the web app
      const html = generateInvoiceHtml(pdfData);

      const { base64 } = await Print.printToFileAsync({ html, base64: true });
      
      const pdfName = `Purchase_${pdfData.invoice.invoice_number.replace(/[^a-zA-Z0-9-]/g, '_')}.pdf`;
      const newUri = FileSystem.documentDirectory + pdfName;
      
      if (base64) {
        await FileSystem.writeAsStringAsync(newUri, base64, {
          encoding: FileSystem.EncodingType.Base64,
        });
      }

      if (await Sharing.isAvailableAsync()) {
        await Sharing.shareAsync(newUri, { UTI: '.pdf', mimeType: 'application/pdf', dialogTitle: 'Share Purchase Invoice' });
      } else {
        Alert.alert('Success', `Invoice saved at: ${newUri}`);
      }
    } catch (err) {
      console.error(err);
      Alert.alert('Error', 'Failed to share PDF');
    }
  };

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#d4af37" />
      </View>
    );
  }

  if (!pdfData) return null;
  const invoice = pdfData.invoice;
  const items = pdfData.items || [];

  return (
    <View style={styles.container}>
      <ScrollView contentContainerStyle={styles.scroll}>
        
        <View style={styles.headerCard}>
          <Text style={styles.title}>{invoice.invoice_number}</Text>
          <Text style={styles.date}>{new Date(invoice.invoice_date).toLocaleString('en-IN')}</Text>
          <View style={styles.statusBadge}>
            <Text style={styles.statusText}>{invoice.status}</Text>
          </View>
        </View>

        <View style={styles.customerCard}>
          <Text style={styles.sectionTitle}>Supplier Details</Text>
          {pdfData.customer ? (
            <>
              <Text style={styles.textValue}>{pdfData.customer.name}</Text>
              <Text style={styles.textLabel}>Phone: {pdfData.customer.phone}</Text>
            </>
          ) : (
            <Text style={styles.textValue}>Unknown Supplier</Text>
          )}
        </View>

        <View style={styles.itemsCard}>
          <Text style={styles.sectionTitle}>Purchased Items ({items.length})</Text>
          {items.map((item: any, idx: number) => (
            <View key={idx} style={styles.itemRow}>
              <View style={{ flex: 1 }}>
                <Text style={styles.itemName}>{item.item_name}</Text>
                <Text style={styles.itemMeta}>
                  {item.item_type} 
                  {item.gold_calculation && ` | Net: ${item.gold_calculation.net_weight}g`}
                  {item.silver_calculation && ` | Net: ${item.silver_calculation.pure_weight}g`}
                </Text>
              </View>
              <Text style={styles.itemPrice}>₹ {fmt(item.final_price)}</Text>
            </View>
          ))}
          
          <View style={styles.divider} />
          
          <View style={styles.totalRow}>
            <Text style={styles.totalLabel}>Subtotal</Text>
            <Text style={styles.totalValue}>₹ {fmt(invoice.subtotal)}</Text>
          </View>
          <View style={styles.totalRow}>
            <Text style={styles.totalLabel}>Tax Amount</Text>
            <Text style={styles.totalValue}>₹ {fmt(invoice.tax_amount)}</Text>
          </View>
          <View style={styles.grandTotalRow}>
            <Text style={styles.grandTotalLabel}>Grand Total</Text>
            <Text style={styles.grandTotalValue}>₹ {fmt(invoice.grand_total)}</Text>
          </View>
        </View>

        <View style={styles.settlementCard}>
          <Text style={styles.sectionTitle}>Settlement Details</Text>
          
          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Cash Paid</Text>
            <Text style={[styles.detailValue, { color: '#4ade80' }]}>₹ {fmt(invoice.cash_paid)}</Text>
          </View>
          
          {invoice.metal_given_value > 0 && (
            <View style={styles.detailRow}>
              <Text style={styles.detailLabel}>Metal Given to Supplier</Text>
              <Text style={[styles.detailValue, { color: '#4ade80' }]}>₹ {fmt(invoice.metal_given_value)}</Text>
            </View>
          )}
          
          {invoice.balance_amount > 0 && (
            <View style={styles.detailRow}>
              <Text style={styles.detailLabel}>Balance Owed</Text>
              <Text style={[styles.detailValue, { color: '#ef4444' }]}>₹ {fmt(invoice.balance_amount)}</Text>
            </View>
          )}
        </View>
        <View style={{ flexDirection: 'row', gap: 12 }}>
          <TouchableOpacity style={[styles.printButton, { flex: 1 }]} onPress={handlePrint}>
            <Text style={styles.printButtonText}>Print / Share</Text>
          </TouchableOpacity>
          <TouchableOpacity style={[styles.printButton, { flex: 1, backgroundColor: 'rgba(239, 68, 68, 0.1)', borderColor: '#ef4444' }]} onPress={handleCancel}>
            <Text style={[styles.printButtonText, { color: '#ef4444' }]}>Cancel Purchase</Text>
          </TouchableOpacity>
        </View>
        
        <View style={{ height: 40 }} />
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0a0a0a' },
  centerContainer: { flex: 1, backgroundColor: '#0a0a0a', justifyContent: 'center', alignItems: 'center' },
  scroll: { padding: 16 },
  headerCard: { alignItems: 'center', marginBottom: 24 },
  title: { color: '#d4af37', fontSize: 24, fontWeight: 'bold', fontFamily: 'monospace' },
  date: { color: '#888', fontSize: 14, marginTop: 4 },
  statusBadge: { backgroundColor: 'rgba(34, 197, 94, 0.2)', paddingHorizontal: 12, paddingVertical: 4, borderRadius: 16, marginTop: 8, borderWidth: 1, borderColor: 'rgba(34, 197, 94, 0.5)' },
  statusText: { color: '#4ade80', fontSize: 12, fontWeight: 'bold', textTransform: 'uppercase' },
  customerCard: { backgroundColor: '#141414', padding: 16, borderRadius: 8, borderWidth: 1, borderColor: '#333', marginBottom: 16 },
  sectionTitle: { color: '#d4af37', fontSize: 14, fontWeight: 'bold', textTransform: 'uppercase', marginBottom: 12, borderBottomWidth: 1, borderBottomColor: '#333', paddingBottom: 8 },
  textValue: { color: '#fff', fontSize: 18, fontWeight: 'bold' },
  textLabel: { color: '#888', fontSize: 14, marginTop: 4 },
  itemsCard: { backgroundColor: '#141414', padding: 16, borderRadius: 8, borderWidth: 1, borderColor: '#333', marginBottom: 16 },
  itemRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  itemName: { color: '#fff', fontSize: 16, fontWeight: 'bold' },
  itemMeta: { color: '#888', fontSize: 12, marginTop: 2 },
  itemPrice: { color: '#d4af37', fontSize: 16, fontWeight: 'bold' },
  divider: { height: 1, backgroundColor: '#333', marginVertical: 12 },
  totalRow: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 8 },
  totalLabel: { color: '#888', fontSize: 14 },
  totalValue: { color: '#fff', fontSize: 14, fontVariant: ['tabular-nums'] },
  grandTotalRow: { flexDirection: 'row', justifyContent: 'space-between', marginTop: 8, paddingTop: 12, borderTopWidth: 1, borderTopColor: '#333' },
  grandTotalLabel: { color: '#d4af37', fontSize: 18, fontWeight: 'bold' },
  grandTotalValue: { color: '#d4af37', fontSize: 18, fontWeight: 'bold', fontVariant: ['tabular-nums'] },
  settlementCard: { backgroundColor: '#141414', padding: 16, borderRadius: 8, borderWidth: 1, borderColor: '#333', marginBottom: 24 },
  detailRow: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 8 },
  detailLabel: { color: '#888', fontSize: 14 },
  detailValue: { color: '#fff', fontSize: 14, fontWeight: 'bold' },
  printButton: { backgroundColor: '#333', padding: 16, borderRadius: 8, alignItems: 'center', borderWidth: 1, borderColor: '#444' },
  printButtonText: { color: '#fff', fontSize: 16, fontWeight: 'bold' },
});
