import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, ActivityIndicator, TouchableOpacity, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { axiosClient } from '../../api/axiosClient';
import * as Print from 'expo-print';
import * as Sharing from 'expo-sharing';
import * as FileSystem from 'expo-file-system/legacy';
import { generateInvoiceHtml } from '../../utils/invoicePdfUtils';

export default function InvoiceDetailScreen({ route, navigation }: any) {
  const { invoiceId } = route.params;
  const [pdfData, setPdfData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    fetchInvoice();
  }, [invoiceId]);

  const fetchInvoice = async () => {
    try {
      const response = await axiosClient.get(`/invoices/${invoiceId}/pdf-data`);
      setPdfData(response.data);
    } catch (error) {
      console.log('Failed to fetch invoice pdf data', error);
      Alert.alert('Error', 'Failed to load invoice details');
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
    Alert.alert('Cancel Bill', 'Are you sure you want to cancel this bill? This will mark it as Cancelled and reverse inventory.', [
      { text: 'No', style: 'cancel' },
      { text: 'Yes, Cancel', style: 'destructive', onPress: async () => {
        try {
          await axiosClient.delete(`/invoices/${invoiceId}`);
          Alert.alert('Success', 'Bill cancelled successfully');
          navigation.goBack();
        } catch (error) {
          console.error('Failed to cancel', error);
          Alert.alert('Error', 'Failed to cancel bill');
        }
      }}
    ]);
  };

  const handlePreview = async () => {
    try {
      setProcessing(true);
      const html = generateInvoiceHtml(pdfData);
      await Print.printAsync({ html });
    } catch (err) {
      console.error(err);
      Alert.alert('Error', 'Failed to open invoice preview');
    } finally {
      setProcessing(false);
    }
  };

  const handleShare = async () => {
    try {
      setProcessing(true);
      const html = generateInvoiceHtml(pdfData);
      const { base64 } = await Print.printToFileAsync({ html, base64: true });
      
      const pdfName = `Invoice_${pdfData.invoice.invoice_number.replace(/[^a-zA-Z0-9-]/g, '_')}.pdf`;
      const newUri = FileSystem.documentDirectory + pdfName;
      
      if (base64) {
        await FileSystem.writeAsStringAsync(newUri, base64, {
          encoding: FileSystem.EncodingType.Base64,
        });
      }

      if (await Sharing.isAvailableAsync()) {
        await Sharing.shareAsync(newUri, { UTI: '.pdf', mimeType: 'application/pdf', dialogTitle: 'Share Invoice' });
      } else {
        Alert.alert('Success', `Invoice saved at: ${newUri}`);
      }
    } catch (err) {
      console.error(err);
      Alert.alert('Error', 'Failed to share PDF');
    } finally {
      setProcessing(false);
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

        {/* Action Buttons Top Bar */}
        <View style={styles.topActionsRow}>
          <TouchableOpacity 
            style={styles.previewButton} 
            onPress={handlePreview}
            disabled={processing}
          >
            <Ionicons name="eye-outline" size={18} color="#000" />
            <Text style={styles.previewButtonText}>Preview Invoice</Text>
          </TouchableOpacity>

          <TouchableOpacity 
            style={styles.shareButton} 
            onPress={handleShare}
            disabled={processing}
          >
            <Ionicons name="share-social-outline" size={18} color="#fff" />
            <Text style={styles.shareButtonText}>Share PDF</Text>
          </TouchableOpacity>
        </View>

        {processing && (
          <View style={styles.processingBanner}>
            <ActivityIndicator size="small" color="#d4af37" />
            <Text style={styles.processingText}>Preparing invoice preview/PDF...</Text>
          </View>
        )}

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Customer Details</Text>
          <Text style={styles.customerName}>{pdfData.customer?.name || 'Walk-in Customer'}</Text>
          <Text style={styles.detailText}>Phone: {pdfData.customer?.phone || '-'}</Text>
          <Text style={styles.detailText}>Address: {pdfData.customer?.address || '-'}</Text>
          {pdfData.customer?.gstin && <Text style={styles.detailText}>GSTIN: {pdfData.customer.gstin}</Text>}
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Items ({items.length})</Text>
          {items.map((item: any, idx: number) => (
            <View key={idx} style={styles.itemRow}>
              <View style={{ flex: 1 }}>
                <Text style={styles.itemName}>{item.item_name}</Text>
                <Text style={styles.itemSub}>
                  {item.metal_type} | Net: {(item.net_weight || 0).toFixed(3)}g | Tanch: {item.touch_purity || item.tanch_percentage || '-'}%
                </Text>
              </View>
              <Text style={styles.itemPrice}>₹ {fmt(item.final_price)}</Text>
            </View>
          ))}
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Payment Breakdown</Text>
          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Taxable Amount</Text>
            <Text style={styles.detailValue}>₹ {fmt(invoice.subtotal)}</Text>
          </View>
          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>GST Amount</Text>
            <Text style={styles.detailValue}>₹ {fmt(invoice.tax_amount)}</Text>
          </View>
          <View style={styles.grandTotalRow}>
            <Text style={styles.grandTotalLabel}>Grand Total</Text>
            <Text style={styles.grandTotalValue}>₹ {fmt(invoice.grand_total)}</Text>
          </View>
        </View>

        <View style={styles.settlementCard}>
          <Text style={styles.sectionTitle}>Settlement Details</Text>
          
          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Bill Type</Text>
            <Text style={styles.detailValue}>{invoice.bill_type}</Text>
          </View>
          
          {invoice.metal_received_value > 0 && (
            <View style={styles.detailRow}>
              <Text style={styles.detailLabel}>Metal Received Value</Text>
              <Text style={[styles.detailValue, { color: '#4ade80' }]}>₹ {fmt(invoice.metal_received_value)}</Text>
            </View>
          )}
          
          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Cash Received</Text>
            <Text style={[styles.detailValue, { color: '#4ade80' }]}>₹ {fmt(invoice.cash_received || invoice.amount_paid)}</Text>
          </View>
          
          {invoice.balance_amount > 0 && (
            <View style={styles.detailRow}>
              <Text style={styles.detailLabel}>Cash Balance Due</Text>
              <Text style={[styles.detailValue, { color: '#ef4444' }]}>₹ {fmt(invoice.balance_amount)}</Text>
            </View>
          )}
        </View>

        <View style={{ flexDirection: 'row', gap: 12, marginTop: 8 }}>
          <TouchableOpacity 
            style={[styles.cancelButton, { flex: 1 }]} 
            onPress={handleCancel}
          >
            <Text style={styles.cancelButtonText}>Cancel Bill</Text>
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
  headerCard: { alignItems: 'center', marginBottom: 16 },
  title: { color: '#d4af37', fontSize: 24, fontWeight: 'bold', fontFamily: 'monospace' },
  date: { color: '#888', fontSize: 14, marginTop: 4 },
  statusBadge: { backgroundColor: 'rgba(74, 222, 128, 0.1)', borderColor: '#4ade80', borderWidth: 1, paddingHorizontal: 12, paddingVertical: 4, borderRadius: 12, marginTop: 8 },
  statusText: { color: '#4ade80', fontSize: 12, fontWeight: 'bold', textTransform: 'uppercase' },
  
  topActionsRow: { flexDirection: 'row', gap: 10, marginBottom: 16 },
  previewButton: { flex: 1, backgroundColor: '#d4af37', flexDirection: 'row', alignItems: 'center', justifyContent: 'center', paddingVertical: 14, borderRadius: 8, gap: 6 },
  previewButtonText: { color: '#000', fontSize: 15, fontWeight: 'bold' },
  shareButton: { flex: 1, backgroundColor: '#222', borderWidth: 1, borderColor: '#444', flexDirection: 'row', alignItems: 'center', justifyContent: 'center', paddingVertical: 14, borderRadius: 8, gap: 6 },
  shareButtonText: { color: '#fff', fontSize: 15, fontWeight: 'bold' },

  processingBanner: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', backgroundColor: '#141414', borderWidth: 1, borderColor: '#d4af37', padding: 8, borderRadius: 6, marginBottom: 12, gap: 8 },
  processingText: { color: '#d4af37', fontSize: 12, fontWeight: '600' },

  card: { backgroundColor: '#141414', borderWidth: 1, borderColor: '#333', borderRadius: 8, padding: 16, marginBottom: 16 },
  settlementCard: { backgroundColor: '#141414', borderWidth: 1, borderColor: '#333', borderRadius: 8, padding: 16, marginBottom: 16 },
  sectionTitle: { color: '#d4af37', fontSize: 14, fontWeight: 'bold', textTransform: 'uppercase', marginBottom: 12 },
  customerName: { color: '#fff', fontSize: 18, fontWeight: 'bold', marginBottom: 4 },
  detailText: { color: '#888', fontSize: 14, marginTop: 2 },
  itemRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingVertical: 8, borderBottomWidth: 1, borderBottomColor: '#222' },
  itemName: { color: '#fff', fontSize: 15, fontWeight: 'bold' },
  itemSub: { color: '#888', fontSize: 12, marginTop: 2 },
  itemPrice: { color: '#d4af37', fontSize: 15, fontWeight: 'bold' },
  detailRow: { flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 4 },
  detailLabel: { color: '#888', fontSize: 14 },
  detailValue: { color: '#fff', fontSize: 14, fontWeight: 'bold' },
  grandTotalRow: { flexDirection: 'row', justifyContent: 'space-between', borderTopWidth: 1, borderTopColor: '#333', paddingTop: 8, marginTop: 8 },
  grandTotalLabel: { color: '#fff', fontSize: 16, fontWeight: 'bold' },
  grandTotalValue: { color: '#d4af37', fontSize: 18, fontWeight: 'bold' },
  
  cancelButton: { backgroundColor: 'rgba(239, 68, 68, 0.1)', borderWidth: 1, borderColor: '#ef4444', padding: 14, borderRadius: 8, alignItems: 'center' },
  cancelButtonText: { color: '#ef4444', fontSize: 14, fontWeight: 'bold' },
});
