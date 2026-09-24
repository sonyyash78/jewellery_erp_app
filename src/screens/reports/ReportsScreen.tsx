import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  TouchableOpacity,
  RefreshControl,
  Alert
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { axiosClient } from '../../api/axiosClient';
import * as Print from 'expo-print';
import * as Sharing from 'expo-sharing';
import * as FileSystem from 'expo-file-system/legacy';

const REPORT_TABS = [
  { id: 'sales', label: 'Sales', icon: 'trending-up-outline', endpoint: '/reports/sales' },
  { id: 'purchases', label: 'Purchases', icon: 'cube-outline', endpoint: '/reports/purchases' },
  { id: 'profit', label: 'Profit', icon: 'cash-outline', endpoint: '/reports/profit' },
  { id: 'metal-flow', label: 'Metal Flow', icon: 'analytics-outline', endpoint: '/reports/metal-flow' },
  { id: 'inventory', label: 'Inventory', icon: 'grid-outline', endpoint: '/reports/inventory' },
  { id: 'gst', label: 'GST', icon: 'receipt-outline', endpoint: '/reports/gst' },
  { id: 'customers', label: 'Customers', icon: 'people-outline', endpoint: '/reports/customers' },
  { id: 'suppliers', label: 'Suppliers', icon: 'business-outline', endpoint: '/reports/suppliers' },
  { id: 'expenses', label: 'Expenses', icon: 'wallet-outline', endpoint: '/reports/expenses' },
];

const TIME_FILTERS = [
  { id: 'Daily', label: 'Today' },
  { id: 'Weekly', label: '7 Days' },
  { id: 'Monthly', label: 'This Month' },
  { id: 'Yearly', label: 'This Year' },
  { id: 'All', label: 'All Time' },
];

export default function ReportsScreen() {
  const [activeTab, setActiveTab] = useState('sales');
  const [timeFilter, setTimeFilter] = useState('Monthly');
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    fetchReport();
  }, [activeTab, timeFilter]);

  const getDateRangeParams = () => {
    const today = new Date();
    let startDate: string | undefined;
    let endDate: string | undefined;

    switch (timeFilter) {
      case 'Daily':
        startDate = endDate = today.toISOString().split('T')[0];
        break;
      case 'Weekly': {
        const weekAgo = new Date(today);
        weekAgo.setDate(weekAgo.getDate() - 7);
        startDate = weekAgo.toISOString().split('T')[0];
        endDate = today.toISOString().split('T')[0];
        break;
      }
      case 'Monthly':
        startDate = new Date(today.getFullYear(), today.getMonth(), 1).toISOString().split('T')[0];
        endDate = today.toISOString().split('T')[0];
        break;
      case 'Yearly':
        startDate = new Date(today.getFullYear(), 0, 1).toISOString().split('T')[0];
        endDate = today.toISOString().split('T')[0];
        break;
      default:
        startDate = endDate = undefined;
    }

    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    return params.toString();
  };

  const fetchReport = async () => {
    try {
      setLoading(true);
      const tabObj = REPORT_TABS.find(t => t.id === activeTab);
      if (!tabObj) return;

      const queryString = getDateRangeParams();
      const url = queryString ? `${tabObj.endpoint}?${queryString}` : tabObj.endpoint;
      const res = await axiosClient.get(url);
      setData(res.data);
    } catch (error) {
      console.log('Failed to fetch report', error);
      Alert.alert('Error', `Failed to load ${activeTab} report`);
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await fetchReport();
    setRefreshing(false);
  };

  const fmtCurrency = (n?: any) => {
    const num = Number(n);
    if (isNaN(num)) return '0.00';
    return num.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  };

  const fmtWeight = (n?: any) => {
    const num = Number(n);
    if (isNaN(num)) return '0.000 g';
    return `${num.toFixed(3)} g`;
  };

  // Generate Print / PDF HTML
  const generateReportHtml = () => {
    const currentTab = REPORT_TABS.find(t => t.id === activeTab)?.label || 'Report';
    const reportDate = new Date().toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });

    let rowsHtml = '';
    if (data && typeof data === 'object') {
      Object.entries(data).forEach(([key, val]) => {
        if (key === 'chart') return;
        const formattedKey = key.replace(/_/g, ' ').toUpperCase();
        let formattedVal = '';

        if (typeof val === 'object' && val !== null) {
          formattedVal = Object.entries(val)
            .map(([subKey, subVal]) => `${subKey.replace(/_/g, ' ')}: ${typeof subVal === 'number' ? fmtCurrency(subVal) : subVal}`)
            .join('<br>');
        } else if (typeof val === 'number') {
          if (key.toLowerCase().includes('count') || key === 'total') {
            formattedVal = String(val);
          } else if (key.toLowerCase().includes('weight') || key.toLowerCase().includes('(g)')) {
            formattedVal = fmtWeight(val);
          } else {
            formattedVal = `₹ ${fmtCurrency(val)}`;
          }
        } else {
          formattedVal = String(val ?? '-');
        }

        rowsHtml += `
          <tr>
            <td style="padding: 10px; border-bottom: 1px solid #ddd; font-weight: 700; color: #333;">${formattedKey}</td>
            <td style="padding: 10px; border-bottom: 1px solid #ddd; font-weight: 800; text-align: right; color: #111;">${formattedVal}</td>
          </tr>
        `;
      });
    }

    return `
      <!DOCTYPE html>
      <html>
        <head>
          <meta charset="utf-8">
          <style>
            body { font-family: 'Helvetica Neue', Arial, sans-serif; padding: 20px; color: #111; }
            .header { text-align: center; border-bottom: 2px solid #d4af37; padding-bottom: 12px; margin-bottom: 20px; }
            .company { font-size: 20px; font-weight: 900; color: #111; letter-spacing: 1px; }
            .title { font-size: 16px; font-weight: 800; color: #d4af37; margin-top: 4px; text-transform: uppercase; }
            .meta { font-size: 11px; color: #666; margin-top: 4px; }
            table { width: 100%; border-collapse: collapse; margin-top: 15px; }
            th { background: #f8f8f8; padding: 10px; text-align: left; font-size: 12px; border-bottom: 2px solid #ccc; }
            td { font-size: 13px; }
            .footer { margin-top: 30px; text-align: center; font-size: 10px; color: #999; border-top: 1px solid #eee; padding-top: 10px; }
          </style>
        </head>
        <body>
          <div class="header">
            <div class="company">SAIDEEP JEWELLERS</div>
            <div class="title">${currentTab} Report (${timeFilter})</div>
            <div class="meta">Generated on: ${reportDate}</div>
          </div>
          <table>
            <thead>
              <tr>
                <th>METRIC</th>
                <th style="text-align: right;">VALUE</th>
              </tr>
            </thead>
            <tbody>
              ${rowsHtml}
            </tbody>
          </table>
          <div class="footer">
            Generated via Jewellery ERP Analytics Engine
          </div>
        </body>
      </html>
    `;
  };

  const handlePrint = async () => {
    try {
      setExporting(true);
      const html = generateReportHtml();
      await Print.printAsync({ html });
    } catch (e) {
      console.error('Print failed', e);
      Alert.alert('Error', 'Failed to print report');
    } finally {
      setExporting(false);
    }
  };

  const handleSharePDF = async () => {
    try {
      setExporting(true);
      const html = generateReportHtml();
      const { uri } = await Print.printToFileAsync({ html });
      const currentTab = REPORT_TABS.find(t => t.id === activeTab)?.label || 'Report';
      const cleanName = `${currentTab}_Report_${timeFilter}_${Date.now()}.pdf`;
      const newUri = FileSystem.documentDirectory + cleanName;

      await FileSystem.copyAsync({ from: uri, to: newUri });

      if (await Sharing.isAvailableAsync()) {
        await Sharing.shareAsync(newUri, { UTI: '.pdf', mimeType: 'application/pdf', dialogTitle: `Share ${currentTab} Report` });
      } else {
        Alert.alert('Success', `Report saved at: ${newUri}`);
      }
    } catch (e) {
      console.error('PDF Share failed', e);
      Alert.alert('Error', 'Failed to generate report PDF');
    } finally {
      setExporting(false);
    }
  };

  const renderKPIs = () => {
    if (!data) {
      return (
        <View style={styles.emptyCard}>
          <Text style={styles.emptyText}>No data available for this timeframe</Text>
        </View>
      );
    }

    const entries = Object.entries(data).filter(([k]) => k !== 'chart');

    return (
      <View style={styles.kpiGrid}>
        {entries.map(([key, value]) => {
          const title = key.replace(/_/g, ' ').toUpperCase();

          // If nested object (e.g. profit metrics, metal breakdown)
          if (typeof value === 'object' && value !== null) {
            return (
              <View key={key} style={styles.nestedCard}>
                <Text style={styles.nestedCardTitle}>{title}</Text>
                {Object.entries(value).map(([subKey, subVal]) => {
                  const subTitle = subKey.replace(/_/g, ' ');
                  const isWeight = subKey.toLowerCase().includes('weight') || subKey.toLowerCase().includes('(g)') || subKey.toLowerCase().includes('fine');
                  const isPositive = Number(subVal) >= 0;
                  return (
                    <View key={subKey} style={styles.nestedRow}>
                      <Text style={styles.nestedLabel}>{subTitle}</Text>
                      <Text style={[styles.nestedValue, isWeight ? styles.weightColor : (isPositive ? styles.greenColor : styles.redColor)]}>
                        {isWeight ? fmtWeight(subVal) : `₹ ${fmtCurrency(subVal)}`}
                      </Text>
                    </View>
                  );
                })}
              </View>
            );
          }

          // Simple metric value
          const isCount = key.toLowerCase().includes('count') || key.toLowerCase().includes('total_items') || key === 'total';
          const isWeight = key.toLowerCase().includes('weight') || key.toLowerCase().includes('(g)') || key.toLowerCase().includes('fine');
          const isPositive = Number(value) >= 0;

          let displayVal = String(value);
          if (typeof value === 'number') {
            if (isCount) displayVal = String(value);
            else if (isWeight) displayVal = fmtWeight(value);
            else displayVal = `₹ ${fmtCurrency(value)}`;
          }

          return (
            <View key={key} style={styles.kpiCard}>
              <Text style={styles.kpiTitle}>{title}</Text>
              <Text style={[styles.kpiValue, isWeight ? styles.weightColor : (isCount ? styles.countColor : (isPositive ? styles.goldColor : styles.redColor))]}>
                {displayVal}
              </Text>
            </View>
          );
        })}
      </View>
    );
  };

  return (
    <View style={styles.container}>
      {/* Top Header Controls */}
      <View style={styles.topHeader}>
        <View style={{ flex: 1 }}>
          <Text style={styles.screenHeading}>Analytics Engine</Text>
          <Text style={styles.screenSubheading}>Real-time financial & metal reports</Text>
        </View>

        <View style={styles.actionButtons}>
          <TouchableOpacity 
            style={styles.actionBtn} 
            onPress={handleSharePDF}
            disabled={exporting}
          >
            <Ionicons name="document-text-outline" size={16} color="#ef4444" />
            <Text style={[styles.actionBtnText, { color: '#ef4444' }]}>PDF</Text>
          </TouchableOpacity>

          <TouchableOpacity 
            style={styles.actionBtn} 
            onPress={handlePrint}
            disabled={exporting}
          >
            <Ionicons name="print-outline" size={16} color="#38bdf8" />
            <Text style={[styles.actionBtnText, { color: '#38bdf8' }]}>Print</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Category Pills (Horizontal Scroll) */}
      <View style={styles.tabsContainer}>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{ paddingHorizontal: 12, gap: 8 }}>
          {REPORT_TABS.map(tab => {
            const isActive = activeTab === tab.id;
            return (
              <TouchableOpacity
                key={tab.id}
                style={[styles.tabChip, isActive && styles.tabChipActive]}
                onPress={() => setActiveTab(tab.id)}
              >
                <Ionicons 
                  name={tab.icon as any} 
                  size={14} 
                  color={isActive ? '#000' : '#888'} 
                />
                <Text style={[styles.tabChipText, isActive && styles.tabChipTextActive]}>
                  {tab.label}
                </Text>
              </TouchableOpacity>
            );
          })}
        </ScrollView>
      </View>

      {/* Time Filter Pills */}
      <View style={styles.timeFiltersContainer}>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{ paddingHorizontal: 12, gap: 6 }}>
          {TIME_FILTERS.map(f => {
            const isSelected = timeFilter === f.id;
            return (
              <TouchableOpacity
                key={f.id}
                style={[styles.timeChip, isSelected && styles.timeChipActive]}
                onPress={() => setTimeFilter(f.id)}
              >
                <Text style={[styles.timeChipText, isSelected && styles.timeChipTextActive]}>
                  {f.label}
                </Text>
              </TouchableOpacity>
            );
          })}
        </ScrollView>
      </View>

      {/* Body Content */}
      <ScrollView
        style={styles.scrollBody}
        contentContainerStyle={{ padding: 14, paddingBottom: 60 }}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#d4af37" />}
      >
        {loading ? (
          <View style={styles.loadingBox}>
            <ActivityIndicator size="large" color="#d4af37" />
            <Text style={styles.loadingText}>Fetching live analytics...</Text>
          </View>
        ) : (
          renderKPIs()
        )}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a0a0c',
  },
  topHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingTop: 12,
    paddingBottom: 8,
    backgroundColor: '#121216',
    borderBottomWidth: 1,
    borderBottomColor: '#222',
  },
  screenHeading: {
    color: '#d4af37',
    fontSize: 16,
    fontWeight: '800',
    letterSpacing: 0.5,
  },
  screenSubheading: {
    color: '#888',
    fontSize: 11,
    marginTop: 1,
  },
  actionButtons: {
    flexDirection: 'row',
    gap: 8,
  },
  actionBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    backgroundColor: '#1a1a22',
    borderWidth: 1,
    borderColor: '#333',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 6,
  },
  actionBtnText: {
    fontSize: 11,
    fontWeight: '700',
  },
  tabsContainer: {
    backgroundColor: '#121216',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#222',
  },
  tabChip: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    paddingHorizontal: 12,
    paddingVertical: 7,
    borderRadius: 20,
    backgroundColor: '#1a1a22',
    borderWidth: 1,
    borderColor: '#333',
  },
  tabChipActive: {
    backgroundColor: '#d4af37',
    borderColor: '#d4af37',
  },
  tabChipText: {
    color: '#aaa',
    fontSize: 12,
    fontWeight: '700',
  },
  tabChipTextActive: {
    color: '#000',
    fontWeight: '800',
  },
  timeFiltersContainer: {
    backgroundColor: '#0f0f13',
    paddingVertical: 6,
    borderBottomWidth: 1,
    borderBottomColor: '#1c1c24',
  },
  timeChip: {
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 14,
    backgroundColor: 'transparent',
  },
  timeChipActive: {
    backgroundColor: 'rgba(212, 175, 55, 0.15)',
    borderWidth: 1,
    borderColor: '#d4af37',
  },
  timeChipText: {
    color: '#777',
    fontSize: 11,
    fontWeight: '600',
  },
  timeChipTextActive: {
    color: '#d4af37',
    fontWeight: '700',
  },
  scrollBody: {
    flex: 1,
  },
  loadingBox: {
    paddingVertical: 60,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 12,
  },
  loadingText: {
    color: '#888',
    fontSize: 13,
  },
  emptyCard: {
    backgroundColor: '#141418',
    borderRadius: 10,
    padding: 30,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#222',
    marginTop: 20,
  },
  emptyText: {
    color: '#888',
    fontSize: 13,
  },
  kpiGrid: {
    gap: 12,
  },
  kpiCard: {
    backgroundColor: '#131318',
    borderRadius: 10,
    padding: 14,
    borderWidth: 1,
    borderColor: '#222',
  },
  kpiTitle: {
    color: '#888',
    fontSize: 11,
    fontWeight: '700',
    letterSpacing: 0.5,
    marginBottom: 6,
  },
  kpiValue: {
    fontSize: 20,
    fontWeight: '900',
    fontFamily: 'monospace',
  },
  goldColor: {
    color: '#d4af37',
  },
  greenColor: {
    color: '#4ade80',
  },
  redColor: {
    color: '#ef4444',
  },
  weightColor: {
    color: '#38bdf8',
  },
  countColor: {
    color: '#fff',
  },
  nestedCard: {
    backgroundColor: '#131318',
    borderRadius: 10,
    padding: 14,
    borderWidth: 1,
    borderColor: '#222',
  },
  nestedCardTitle: {
    color: '#d4af37',
    fontSize: 12,
    fontWeight: '800',
    letterSpacing: 0.5,
    borderBottomWidth: 1,
    borderBottomColor: '#222',
    paddingBottom: 6,
    marginBottom: 8,
  },
  nestedRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 5,
  },
  nestedLabel: {
    color: '#aaa',
    fontSize: 12,
    textTransform: 'capitalize',
  },
  nestedValue: {
    fontSize: 13,
    fontWeight: '800',
    fontFamily: 'monospace',
  },
});
