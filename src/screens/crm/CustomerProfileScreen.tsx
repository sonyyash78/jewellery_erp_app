import React, { useEffect, useState, useCallback } from 'react';
import { useFocusEffect } from '@react-navigation/native';
import { View, Text, Alert, StyleSheet, FlatList, ActivityIndicator, TouchableOpacity, ScrollView } from 'react-native';
import { Ionicons, MaterialCommunityIcons } from '@expo/vector-icons';
import { axiosClient } from '../../api/axiosClient';
import * as Print from 'expo-print';
import * as Sharing from 'expo-sharing';
import * as FileSystem from 'expo-file-system/legacy';
import { generateLedgerVoucherHtml, generateLedgerStatementHtml } from '../../utils/ledgerPdfUtils';

const formatAmount = (num: number) => {
  if (!num) return '0';
  const absNum = Math.abs(num);
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
  formatted = formatted.replace(/\.00([a-zA-Z]*)$/, '$1');
  return formatted;
};

export default function CustomerProfileScreen({ route, navigation }: any) {
  const { customerId, customerName, item } = route.params || {};
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [pdfGenerating, setPdfGenerating] = useState(false);

  useFocusEffect(
    useCallback(() => {
      fetchProfile();
    }, [])
  );

  useEffect(() => {
    navigation.setOptions({ title: 'Customer Profile' });
    fetchProfile();
  }, [customerId]);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      const response = await axiosClient.get(`/customers/${customerId}/bills`);
      setData(response.data);
    } catch (error) {
      console.log('Failed to fetch profile', error);
    } finally {
      setLoading(false);
    }
  };

  const outstanding = data?.outstanding_balance || 0;
  const isDr = outstanding > 0;

  const handleDownloadVoucherPdf = async (bill: any) => {
    try {
      setPdfGenerating(true);
      const party = item || { first_name: customerName, name: customerName };
      const html = generateLedgerVoucherHtml('Customer', party, bill);
      
      const { base64 } = await Print.printToFileAsync({ html, base64: true });
      const sanitizedBillNo = (bill?.bill_no || `VOUCHER_${bill?.id || Date.now()}`).replace(/[^a-zA-Z0-9_-]/g, '_');
      const pdfName = `Customer_Voucher_${sanitizedBillNo}.pdf`;
      const newUri = FileSystem.documentDirectory + pdfName;

      if (base64) {
        await FileSystem.writeAsStringAsync(newUri, base64, {
          encoding: FileSystem.EncodingType.Base64,
        });
      }

      if (await Sharing.isAvailableAsync()) {
        await Sharing.shareAsync(newUri, {
          UTI: '.pdf',
          mimeType: 'application/pdf',
          dialogTitle: `Download Voucher ${bill?.bill_no || ''}`,
        });
      } else {
        Alert.alert('PDF Saved', `Voucher PDF saved to: ${newUri}`);
      }
    } catch (error: any) {
      console.error('Error generating voucher PDF:', error);
      Alert.alert('Error', 'Failed to generate voucher PDF. Please try again.');
    } finally {
      setPdfGenerating(false);
    }
  };

  const handleDownloadStatementPdf = async () => {
    try {
      setPdfGenerating(true);
      const party = item || { first_name: customerName, name: customerName };
      const html = generateLedgerStatementHtml('Customer', party, data);
      
      const { base64 } = await Print.printToFileAsync({ html, base64: true });
      const sanitizedName = (customerName || 'Customer').replace(/[^a-zA-Z0-9_-]/g, '_');
      const pdfName = `Customer_Statement_${sanitizedName}_${Date.now()}.pdf`;
      const newUri = FileSystem.documentDirectory + pdfName;

      if (base64) {
        await FileSystem.writeAsStringAsync(newUri, base64, {
          encoding: FileSystem.EncodingType.Base64,
        });
      }

      if (await Sharing.isAvailableAsync()) {
        await Sharing.shareAsync(newUri, {
          UTI: '.pdf',
          mimeType: 'application/pdf',
          dialogTitle: `Download Customer Statement - ${customerName || ''}`,
        });
      } else {
        Alert.alert('PDF Saved', `Statement PDF saved to: ${newUri}`);
      }
    } catch (error: any) {
      console.error('Error generating statement PDF:', error);
      Alert.alert('Error', 'Failed to generate statement PDF. Please try again.');
    } finally {
      setPdfGenerating(false);
    }
  };
  
  const renderBill = ({ item: bill }: { item: any }) => {
    let typeColor = '#3b82f6'; // INVOICE
    if (bill.type === 'EXCHANGE') typeColor = '#a855f7';
    else if (bill.type === 'SETTLEMENT' || bill.type === 'Payment' || bill.type === 'Receipt') typeColor = '#10b981';
    
    return (
      <View style={styles.billCard}>
        {/* Row 1: Date, Type, Ref */}
        <View style={styles.cardRow}>
          <Text style={styles.billDate}>{new Date(bill.date).toLocaleString([], { year: 'numeric', month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</Text>
          <View style={[styles.badge, { backgroundColor: `${typeColor}20` }]}>
            <Text style={[styles.badgeText, { color: typeColor }]}>{bill.type}</Text>
          </View>
        </View>
        <Text style={styles.refNo}>{bill.bill_no}</Text>
        
        {/* Row 2: Details */}
        <View style={styles.detailsRow}>
          <Text style={styles.billSummary} numberOfLines={2}>{bill.summary}</Text>
          <TouchableOpacity 
            style={styles.pdfBtn} 
            onPress={() => handleDownloadVoucherPdf(bill)}
            disabled={pdfGenerating}
          >
            <Ionicons name="download-outline" size={14} color="#d4af37" />
            <Text style={styles.pdfBtnText}>PDF</Text>
          </TouchableOpacity>
        </View>
        
        {/* Row 3: Metals */}
        {(bill.gold_change !== 0 || bill.silver_change !== 0) && (
          <View style={styles.metalRow}>
            {bill.gold_change !== 0 && (
              <View style={styles.metalCol}>
                <Text style={styles.metalLabel}>GOLD (G)</Text>
                <Text style={[styles.metalVal, { color: '#d4af37' }]}>{bill.gold_change > 0 ? '+' : ''}{bill.gold_change.toFixed(3)}</Text>
              </View>
            )}
            {bill.silver_change !== 0 && (
              <View style={styles.metalCol}>
                <Text style={styles.metalLabel}>SILVER (G)</Text>
                <Text style={[styles.metalVal, { color: '#e5e7eb' }]}>{bill.silver_change > 0 ? '+' : ''}{bill.silver_change.toFixed(3)}</Text>
              </View>
            )}
          </View>
        )}
        
        {/* Row 4: Finance */}
        <View style={styles.financeRow}>
          <View style={styles.financeCol}>
            <Text style={styles.financeLabel}>DEBIT (₹)</Text>
            <Text style={styles.debitVal}>{bill.debit > 0 ? bill.debit.toLocaleString('en-IN') : '-'}</Text>
          </View>
          <View style={styles.financeCol}>
            <Text style={styles.financeLabel}>CREDIT (₹)</Text>
            <Text style={styles.creditVal}>{bill.credit > 0 ? bill.credit.toLocaleString('en-IN') : '-'}</Text>
          </View>
        </View>
        
        {/* Footer: Balance */}
        <View style={styles.balanceRow}>
          <Text style={styles.balanceLabel}>BALANCE (₹)</Text>
          <Text style={styles.balanceAmt}>
            ₹ {Math.abs(bill.balance).toLocaleString('en-IN')} {bill.balance > 0 ? '(Dr)' : (bill.balance < 0 ? '(Cr)' : '')}
          </Text>
        </View>
      </View>
    );
  };

  if (loading) {
    return (
      <View style={[styles.container, { justifyContent: 'center' }]}>
        <ActivityIndicator size="large" color="#d4af37" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Header Profile Section */}
      <View style={styles.headerBlock}>
        <Text style={styles.customerName}>{customerName?.toUpperCase()}</Text>
        
        <View style={styles.infoGrid}>
          <View style={styles.infoItem}>
            <Ionicons name="call" size={14} color="#888" />
            <Text style={styles.infoText}>{item?.phone_number || item?.mobile || 'N/A'}</Text>
          </View>
          <View style={styles.infoItem}>
            <MaterialCommunityIcons name="card-account-details" size={14} color="#888" />
            <Text style={styles.infoText}>PAN: {item?.aadhaar_pan || 'N/A'}</Text>
          </View>
          <View style={styles.infoItem}>
            <MaterialCommunityIcons name="bank" size={14} color="#888" />
            <Text style={styles.infoText}>GST: {item?.gst_number || 'N/A'}</Text>
          </View>
          <View style={styles.infoItem}>
            <MaterialCommunityIcons name="fingerprint" size={14} color="#888" />
            <Text style={styles.infoText}>Aadhar: N/A</Text>
          </View>
        </View>
        
        <View style={styles.summaryBoxes}>
          <View style={styles.sumBox}>
            <Text style={styles.sumLabel}>FINE GOLD</Text>
            <Text style={[styles.sumVal, {color: '#d4af37'}]}>{data?.fine_gold_balance?.toFixed(3) || '0.000'} g</Text>
            <Text style={styles.sumSub}>@ ₹{data?.current_gold_rate || 7000}/g</Text>
          </View>
          <View style={styles.sumBox}>
            <Text style={styles.sumLabel}>FINE SILVER</Text>
            <Text style={[styles.sumVal, {color: '#e5e7eb'}]}>{data?.fine_silver_balance?.toFixed(3) || '0.000'} g</Text>
            <Text style={styles.sumSub}>@ ₹{data?.current_silver_rate || 85}/g</Text>
          </View>
          <View style={[styles.sumBox, { borderRightWidth: 0 }]}>
            <Text style={styles.sumLabel}>OUTSTANDING ₹</Text>
            <Text style={[styles.sumValBig, {color: isDr ? '#ef4444' : '#10b981'}]} numberOfLines={1} adjustsFontSizeToFit>
              ₹ {formatAmount(outstanding)} {isDr ? '(Dr)' : (outstanding < 0 ? '(Cr)' : '')}
            </Text>
          </View>
        </View>
      </View>

      {/* Ledger Header & Actions */}
      <View style={styles.ledgerHeader}>
        <View style={styles.ledgerTitleRow}>
          <Ionicons name="document-text" size={20} color="#d4af37" />
          <Text style={styles.sectionTitle}>CUSTOMER LEDGER</Text>
        </View>
        <View style={styles.actionBtns}>
          <TouchableOpacity 
            style={styles.statementBtn} 
            onPress={handleDownloadStatementPdf}
            disabled={pdfGenerating}
          >
            <Ionicons name="document-attach-outline" size={14} color="#fff" />
            <Text style={styles.statementBtnText}>Statement PDF</Text>
          </TouchableOpacity>
          <TouchableOpacity 
            style={styles.settleBtn} 
            onPress={() => navigation.navigate('CreateSettlement', { id: customerId, type: 'Customer' })}
          >
            <Text style={styles.settleBtnText}>+ Settlement</Text>
          </TouchableOpacity>
        </View>
      </View>

      {pdfGenerating && (
        <View style={styles.generatingBanner}>
          <ActivityIndicator size="small" color="#d4af37" />
          <Text style={styles.generatingText}>Generating & opening PDF...</Text>
        </View>
      )}

      {/* Ledger List */}
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
    padding: 12,
  },
  headerBlock: {
    backgroundColor: '#141414',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#333',
    padding: 16,
    marginBottom: 16,
  },
  customerName: {
    color: '#fff',
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 12,
  },
  infoGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 16,
    gap: 12,
  },
  infoItem: {
    flexDirection: 'row',
    alignItems: 'center',
    width: '45%',
  },
  infoText: {
    color: '#888',
    fontSize: 12,
    marginLeft: 6,
  },
  summaryBoxes: {
    flexDirection: 'row',
    borderTopWidth: 1,
    borderTopColor: '#333',
    paddingTop: 16,
  },
  sumBox: {
    flex: 1,
    borderRightWidth: 1,
    borderRightColor: '#333',
    paddingHorizontal: 8,
    alignItems: 'center',
  },
  sumLabel: {
    color: '#888',
    fontSize: 10,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  sumVal: {
    fontSize: 14,
    fontWeight: 'bold',
    marginBottom: 2,
  },
  sumSub: {
    color: '#666',
    fontSize: 9,
  },
  sumValBig: {
    fontSize: 14,
    fontWeight: 'bold',
  },
  ledgerHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#141414',
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#333',
    marginBottom: 12,
  },
  ledgerTitleRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  sectionTitle: {
    color: '#d4af37',
    fontSize: 13,
    fontWeight: 'bold',
    marginLeft: 6,
  },
  actionBtns: {
    flexDirection: 'row',
    gap: 8,
  },
  statementBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#262626',
    borderWidth: 1,
    borderColor: '#444',
    paddingVertical: 6,
    paddingHorizontal: 10,
    borderRadius: 6,
    gap: 4,
  },
  statementBtnText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 11,
  },
  settleBtn: {
    backgroundColor: '#ffcc00',
    paddingVertical: 6,
    paddingHorizontal: 10,
    borderRadius: 6,
  },
  settleBtnText: {
    color: '#000',
    fontWeight: 'bold',
    fontSize: 11,
  },
  generatingBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#1a1a1a',
    padding: 8,
    borderRadius: 6,
    marginBottom: 10,
    gap: 8,
    borderWidth: 1,
    borderColor: '#d4af37',
  },
  generatingText: {
    color: '#d4af37',
    fontSize: 12,
    fontWeight: '600',
  },
  billCard: {
    backgroundColor: '#141414',
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#333',
    marginBottom: 10,
  },
  cardRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  billDate: {
    color: '#888',
    fontSize: 11,
  },
  badge: {
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
  },
  badgeText: {
    fontSize: 10,
    fontWeight: 'bold',
  },
  refNo: {
    color: '#fff',
    fontSize: 13,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  detailsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#1a1a1a',
    padding: 8,
    borderRadius: 6,
    marginBottom: 12,
  },
  billSummary: {
    color: '#ccc',
    fontSize: 12,
    flex: 1,
    marginRight: 8,
  },
  pdfBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#d4af37',
    backgroundColor: 'rgba(212, 175, 55, 0.1)',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  pdfBtnText: {
    color: '#d4af37',
    fontSize: 11,
    marginLeft: 4,
    fontWeight: 'bold',
  },
  metalRow: {
    flexDirection: 'row',
    marginBottom: 12,
    gap: 16,
  },
  metalCol: {
    flex: 1,
  },
  metalLabel: {
    color: '#888',
    fontSize: 10,
    fontWeight: 'bold',
    marginBottom: 2,
  },
  metalVal: {
    fontSize: 13,
    fontWeight: 'bold',
  },
  financeRow: {
    flexDirection: 'row',
    borderTopWidth: 1,
    borderTopColor: '#222',
    paddingTop: 8,
    marginBottom: 8,
  },
  financeCol: {
    flex: 1,
  },
  financeLabel: {
    color: '#888',
    fontSize: 10,
    fontWeight: 'bold',
    marginBottom: 2,
  },
  debitVal: {
    color: '#ef4444',
    fontSize: 13,
    fontWeight: 'bold',
  },
  creditVal: {
    color: '#10b981',
    fontSize: 13,
    fontWeight: 'bold',
  },
  balanceRow: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    alignItems: 'center',
    borderTopWidth: 1,
    borderTopColor: '#222',
    paddingTop: 8,
  },
  balanceLabel: {
    color: '#888',
    fontSize: 10,
    fontWeight: 'bold',
    marginRight: 8,
  },
  balanceAmt: {
    color: '#f59e0b',
    fontSize: 13,
    fontWeight: 'bold',
  },
  emptyText: {
    color: '#888',
    textAlign: 'center',
    marginTop: 20,
  }
});
