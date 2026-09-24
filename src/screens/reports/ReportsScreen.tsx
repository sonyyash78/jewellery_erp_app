import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, ActivityIndicator, TouchableOpacity } from 'react-native';
import { axiosClient } from '../../api/axiosClient';

export default function ReportsScreen() {
  const [loading, setLoading] = useState(true);
  const [profitData, setProfitData] = useState<any>(null);
  const [metalFlowData, setMetalFlowData] = useState<any>(null);

  useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async () => {
    try {
      setLoading(true);
      const [profitRes, metalRes] = await Promise.all([
        axiosClient.get('/reports/profit'),
        axiosClient.get('/reports/metal-flow')
      ]);
      setProfitData(profitRes.data);
      setMetalFlowData(metalRes.data);
    } catch (error) {
      console.log('Failed to fetch reports', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#d4af37" />
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      
      {/* PROFIT REPORT */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Profit & Loss (Cash Flow)</Text>
        
        <View style={styles.row}>
          <Text style={styles.label}>Total Sales Amount (Invoices)</Text>
          <Text style={styles.valueGreen}>?{(profitData?.sales?.total_sales_amount || 0).toLocaleString('en-IN')}</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Exchange Sales Amount</Text>
          <Text style={styles.valueGreen}>?{(profitData?.sales?.total_exchange_sales_amount || 0).toLocaleString('en-IN')}</Text>
        </View>
        
        <View style={styles.divider} />
        
        <View style={styles.row}>
          <Text style={styles.label}>Total Purchase Amount</Text>
          <Text style={styles.valueRed}>?{(profitData?.purchases?.total_purchases_amount || 0).toLocaleString('en-IN')}</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Exchange Purchase Amount</Text>
          <Text style={styles.valueRed}>?{(profitData?.purchases?.total_exchange_purchases_amount || 0).toLocaleString('en-IN')}</Text>
        </View>

        <View style={styles.divider} />

        <View style={styles.row}>
          <Text style={styles.labelBold}>Net Cash Profit</Text>
          <Text style={[styles.valueBold, (profitData?.net_cash_profit || 0) >= 0 ? {color: '#4ade80'} : {color: '#f87171'}]}>
            ?{(profitData?.net_cash_profit || 0).toLocaleString('en-IN')}
          </Text>
        </View>
      </View>

      {/* METAL FLOW REPORT */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Metal Flow (Gold)</Text>
        <View style={styles.row}>
          <Text style={styles.label}>Total Fine Sold (Invoices)</Text>
          <Text style={styles.value}>{(metalFlowData?.gold?.sales?.total_fine_sold || 0).toFixed(3)} g</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Exchange Fine Sold</Text>
          <Text style={styles.value}>{(metalFlowData?.gold?.sales?.exchange_fine_sold || 0).toFixed(3)} g</Text>
        </View>

        <View style={styles.divider} />
        
        <View style={styles.row}>
          <Text style={styles.label}>Total Fine Purchased</Text>
          <Text style={styles.value}>{(metalFlowData?.gold?.purchases?.total_fine_purchased || 0).toFixed(3)} g</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Exchange Fine Purchased</Text>
          <Text style={styles.value}>{(metalFlowData?.gold?.purchases?.exchange_fine_purchased || 0).toFixed(3)} g</Text>
        </View>

        <View style={styles.divider} />

        <View style={styles.row}>
          <Text style={styles.labelBold}>Net Gold Balance</Text>
          <Text style={[styles.valueBold, (metalFlowData?.gold?.net_balance || 0) >= 0 ? {color: '#4ade80'} : {color: '#f87171'}]}>
            {(metalFlowData?.gold?.net_balance || 0).toFixed(3)} g
          </Text>
        </View>
      </View>

      <View style={[styles.card, { marginBottom: 40 }]}>
        <Text style={styles.cardTitle}>Metal Flow (Silver)</Text>
        <View style={styles.row}>
          <Text style={styles.label}>Total Fine Sold (Invoices)</Text>
          <Text style={styles.value}>{(metalFlowData?.silver?.sales?.total_fine_sold || 0).toFixed(3)} g</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Exchange Fine Sold</Text>
          <Text style={styles.value}>{(metalFlowData?.silver?.sales?.exchange_fine_sold || 0).toFixed(3)} g</Text>
        </View>

        <View style={styles.divider} />
        
        <View style={styles.row}>
          <Text style={styles.label}>Total Fine Purchased</Text>
          <Text style={styles.value}>{(metalFlowData?.silver?.purchases?.total_fine_purchased || 0).toFixed(3)} g</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Exchange Fine Purchased</Text>
          <Text style={styles.value}>{(metalFlowData?.silver?.purchases?.exchange_fine_purchased || 0).toFixed(3)} g</Text>
        </View>

        <View style={styles.divider} />

        <View style={styles.row}>
          <Text style={styles.labelBold}>Net Silver Balance</Text>
          <Text style={[styles.valueBold, (metalFlowData?.silver?.net_balance || 0) >= 0 ? {color: '#4ade80'} : {color: '#f87171'}]}>
            {(metalFlowData?.silver?.net_balance || 0).toFixed(3)} g
          </Text>
        </View>
      </View>

    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a0a0a',
    padding: 16,
  },
  center: {
    flex: 1,
    backgroundColor: '#0a0a0a',
    justifyContent: 'center',
    alignItems: 'center',
  },
  card: {
    backgroundColor: '#141414',
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: '#333',
    marginBottom: 16,
  },
  cardTitle: {
    color: '#d4af37',
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
  },
  label: {
    color: '#888',
    fontSize: 14,
  },
  labelBold: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  value: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  valueGreen: {
    color: '#4ade80',
    fontSize: 14,
    fontWeight: '600',
  },
  valueRed: {
    color: '#f87171',
    fontSize: 14,
    fontWeight: '600',
  },
  valueBold: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  divider: {
    height: 1,
    backgroundColor: '#333',
    marginVertical: 8,
  },
});
