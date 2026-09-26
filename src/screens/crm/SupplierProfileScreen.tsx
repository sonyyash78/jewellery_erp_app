import React, { useEffect, useState, useCallback } from 'react';
import { useFocusEffect } from '@react-navigation/native';
import { View, Text, Alert, StyleSheet, FlatList, ActivityIndicator, TouchableOpacity, ScrollView } from 'react-native';
import { Ionicons, MaterialCommunityIcons } from '@expo/vector-icons';
import { axiosClient } from '../../api/axiosClient';
import * as Print from 'expo-print';
import * as Sharing from 'expo-sharing';
import * as FileSystem from 'expo-file-system/legacy';
import { generateLedgerVoucherHtml, generateLedgerStatementHtml } from '../../utils/ledgerPdfUtils';
import { generateInvoiceHtml } from '../../utils/invoicePdfUtils';

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

export default function SupplierProfileScreen({ route, navigation }: any) {
  const params = route.params || {};
  const supplierId = params.supplierId || params.id || params.SupplierId || params.item?.id;
  const supplierName = params.supplierName || params.SupplierName || params.item?.name || (params.item?.first_name ? `${params.item.first_name} ${params.item.last_name || ''}`.trim() : '') || 'Supplier';
  const item = params.item;

  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [pdfGenerating, setPdfGenerating] = useState(false);

  useFocusEffect(
    useCallback(() => {
      if (supplierId) fetchProfile();
    }, [supplierId])
  );

  useEffect(() => {
    navigation.setOptions({ title: `${supplierName} - Ledger` });
    if (supplierId) fetchProfile();
  }, [supplierId, supplierName]);

  const fetchProfile = async () => {
    if (!supplierId) {
      setLoading(false);
      return;
    }
    try {
      setLoading(true);
      const response = await axiosClient.get(`/sellers/${supplierId}/bills`);
      setData(response.data);
    } catch (error) {
      console.log('Failed to fetch profile', error);
    } finally {
      setLoading(false);
    }
  };

  const outstanding = data?.outstanding_balance || 0;
  const isCr = outstanding > 0;

  const getVoucherHtml = async (bill: any) => {
    let html = '';
    try {
      if (bill.bill_no && bill.bill_no !== '-') {
        // Try purchase PDF endpoint first
        try {
          const res = await axiosClient.get(`/purchases/pdf-by-voucher/${bill.bill_no}`);
          if (res.data) {
            html = generateInvoiceHtml(res.data);
          }
        } catch (e) {
          // If not purchase, try invoice endpoint
          try {
            const res = await axiosClient.get(`/invoices/pdf-by-voucher/${bill.bill_no}`);
            if (res.data) {
              html = generateInvoiceHtml(res.data);
            }
          } catch (e2) {
            // fallback
          }
        }
      }
    } catch (e) {
      // fallback
    }
    if (!html) {
      const party = item || { name: supplierName, first_name: supplierName };
      html = generateLedgerVoucherHtml('Supplier', party, bill);
    }
    return html;
  };

  const handlePreviewVoucher = async (bill: any) => {
    try {
      setPdfGenerating(true);
      const html = await getVoucherHtml(bill);
      await Print.printAsync({ html });
    } catch (error: any) {
      console.error('Error previewing voucher:', error);
      Alert.alert('Error', 'Failed to open preview');
    } finally {
      setPdfGenerating(false);
    }
  };

  const handleDownloadVoucherPdf = async (bill: any) => {
    try {
      setPdfGenerating(true);
      const html = await getVoucherHtml(bill);
      
      const { base64 } = await Print.printToFileAsync({ html, base64: true });
      const sanitizedBillNo = (bill?.bill_no || `VOUCHER_${bill?.id || Date.now()}`).replace(/[^a-zA-Z0-9_-]/g, '_');
      const pdfName = `Supplier_Voucher_${sanitizedBillNo}.pdf`;
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
          dialogTitle: `Share Voucher ${bill?.bill_no || ''}`,
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

  const getStatementHtml = async () => {
    let company: any = null;
    try {
      const sRes = await axiosClient.get('/settings/');
      company = sRes.data;
    } catch {}
    const party = item || { name: supplierName, first_name: supplierName };
    return generateLedgerStatementHtml('Supplier', party, data, company);
  };

  const handlePreviewStatement = async () => {
    try {
      setPdfGenerating(true);
      const html = await getStatementHtml();
      await Print.printAsync({ html });
    } catch (error: any) {
      console.error('Error previewing statement:', error);
      Alert.alert('Error', 'Failed to open statement preview');
    } finally {
      setPdfGenerating(false);
    }
  };

  const handleDownloadStatementPdf = async () => {
    try {
      setPdfGenerating(true);
      const html = await getStatementHtml();
      
      const { base64 } = await Print.printToFileAsync({ html, base64: true });
      const sanitizedName = (supplierName || 'Supplier').replace(/[^a-zA-Z0-9_-]/g, '_');
      const pdfName = `Supplier_Statement_${sanitizedName}_${Date.now()}.pdf`;
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
          dialogTitle: `Download Supplier Statement - ${supplierName || ''}`,
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
    let typeColor = '#3b82f6';
    if (bill.type === 'EXCHANGE') typeColor = '#a855f7';
    else if (bill.type === 'PURCHASE') typeColor = '#f59e0b';
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
        
        {/* Row 2: Details & Actions (Preview + PDF) */}
        <View style={styles.detailsRow}>
          <Text style={styles.billSummary} numberOfLines={2}>{bill.summary}</Text>
          <View style={styles.billActions}>
            <TouchableOpacity 
              style={styles.previewBtn} 
              onPress={() => handlePreviewVoucher(bill)}
              disabled={pdfGenerating}
            >
              <Ionicons name="eye-outline" size={13} color="#fff" />
              <Text style={styles.previewBtnText}>Preview</Text>
            </TouchableOpacity>
            <TouchableOpacity 
              style={styles.pdfBtn} 
              onPress={() => handleDownloadVoucherPdf(bill)}
              disabled={pdfGenerating}
            >
              <Ionicons name="download-outline" size={13} color="#d4af37" />
              <Text style={styles.pdfBtnText}>PDF</Text>
            </TouchableOpacity>
          </View>
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
            ₹ {Math.abs(bill.balance).toLocaleString('en-IN')} {bill.balance > 0 ? '(Cr)' : (bill.balance < 0 ? '(Dr)' : '')}
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
        <Text style={styles.customerName}>{supplierName?.toUpperCase()}</Text>
        
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
            <Text style={styles.sumLabel}>PENDING PAYABLE ₹</Text>
            <Text style={[styles.sumValBig, {color: isCr ? '#ef4444' : '#10b981'}]} numberOfLines={1} adjustsFontSizeToFit>
              ₹ {formatAmount(outstanding)} {isCr ? '(Cr)' : (outstanding < 0 ? '(Dr)' : '')}
            </Text>
          </View>
        </View>
      </View>

      {/* Ledger Header Bar - Fitted with no text cut off */}
      <View style={styles.ledgerHeader}>
        <View style={styles.ledgerTitleRow}>
          <Ionicons name="document-text" size={16} color="#d4af37" />
          <Text style={styles.sectionTitle}>LEDGER</Text>
        </View>
        <View style={styles.actionBtns}>
          <TouchableOpacity 
            style={styles.statementBtn} 
            onPress={handleDownloadStatementPdf}
            disabled={pdfGenerating}
          >
            <Ionicons name="download-outline" size={13} color="#d4af37" />
            <Text style={styles.statementBtnText}>Statement</Text>
          </TouchableOpacity>
          <TouchableOpacity 
            style={styles.settleBtn} 
            onPress={() => navigation.navigate('CreateSettlement', { id: supplierId, type: 'Supplier' })}
          >
            <Ionicons name="add" size={14} color="#000" />
            <Text style={styles.settleBtnText}>Settle</Text>
          </TouchableOpacity>
        </View>
      </View>

      {pdfGenerating && (
        <View style={styles.generatingBanner}>
          <ActivityIndicator size="small" color="#d4af37" />
          <Text style={styles.generatingText}>Preparing preview/PDF...</Text>
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
    marginBottom: 12,
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
    marginBottom: 14,
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
    paddingTop: 14,
  },
  sumBox: {
    flex: 1,
    borderRightWidth: 1,
    borderRightColor: '#333',
    paddingHorizontal: 6,
    alignItems: 'center',
  },
  sumLabel: {
    color: '#888',
    fontSize: 9.5,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  sumVal: {
    fontSize: 13,
    fontWeight: 'bold',
    marginBottom: 2,
  },
  sumSub: {
    color: '#666',
    fontSize: 8.5,
  },
  sumValBig: {
    fontSize: 13,
    fontWeight: 'bold',
  },
  ledgerHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#141414',
    paddingVertical: 10,
    paddingHorizontal: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#333',
    marginBottom: 10,
  },
  ledgerTitleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    flexShrink: 1,
  },
  sectionTitle: {
    color: '#d4af37',
    fontSize: 13,
    fontWeight: 'bold',
    marginLeft: 5,
  },
  actionBtns: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    flexShrink: 0,
  },
  statementBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(212, 175, 55, 0.1)',
    borderWidth: 1,
    borderColor: '#d4af37',
    paddingVertical: 5,
    paddingHorizontal: 8,
    borderRadius: 5,
    gap: 4,
  },
  statementBtnText: {
    color: '#d4af37',
    fontWeight: 'bold',
    fontSize: 11,
  },
  settleBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#d4af37',
    paddingVertical: 5,
    paddingHorizontal: 8,
    borderRadius: 5,
    gap: 2,
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
    backgroundColor: '#141414',
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
    gap: 8,
  },
  billSummary: {
    color: '#ccc',
    fontSize: 12,
    flex: 1,
  },
  billActions: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    flexShrink: 0,
  },
  previewBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#444',
    backgroundColor: '#262626',
    paddingHorizontal: 7,
    paddingVertical: 4,
    borderRadius: 4,
    gap: 3,
  },
  previewBtnText: {
    color: '#fff',
    fontSize: 10.5,
    fontWeight: 'bold',
  },
  pdfBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#d4af37',
    backgroundColor: 'rgba(212, 175, 55, 0.1)',
    paddingHorizontal: 7,
    paddingVertical: 4,
    borderRadius: 4,
    gap: 3,
  },
  pdfBtnText: {
    color: '#d4af37',
    fontSize: 10.5,
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
