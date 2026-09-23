import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, RefreshControl } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { axiosClient } from '../../api/axiosClient';
import { useAuthStore } from '../../store/authStore';

export default function DashboardScreen({ navigation }: any) {
  const [data, setData] = useState<any>(null);
  const [refreshing, setRefreshing] = useState(false);

  const fetchDashboardData = async () => {
    try {
      const response = await axiosClient.get('/dashboard/metrics');
      setData(response.data);
    } catch (error) {
      console.log('Failed to fetch dashboard', error);
    }
  };

  const onRefresh = React.useCallback(() => {
    setRefreshing(true);
    fetchDashboardData().then(() => setRefreshing(false));
  }, []);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handleLogout = async () => {
    const { signOut } = useAuthStore.getState();
    await signOut();
  };

  return (
    <ScrollView 
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#d4af37" />}
    >
      <View style={styles.header}>
        <Text style={styles.title}>Dashboard</Text>
        <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
          <Text style={styles.logoutText}>Logout</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.ratesContainer}>
        <View style={styles.rateCard}>
          <Text style={styles.rateLabel}>Gold Rate (24K)</Text>
          <Text style={styles.rateValue}>₹ {data?.latest_gold_rate || '---'}</Text>
        </View>
        <View style={styles.rateCard}>
          <Text style={styles.rateLabel}>Silver Rate</Text>
          <Text style={styles.rateValue}>₹ {data?.latest_silver_rate || '---'}</Text>
        </View>
      </View>

      <View style={styles.grid}>
        <TouchableOpacity style={styles.gridItem} onPress={() => {}}>
          <Text style={styles.gridValue}>{data?.total_customers || 0}</Text>
          <Text style={styles.gridLabel}>Total Customers</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.gridItem} onPress={() => {}}>
          <Text style={styles.gridValue}>{data?.today_bills || 0}</Text>
          <Text style={styles.gridLabel}>Today's Bills</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.gridItem} onPress={() => {}}>
          <Text style={styles.gridValue}>₹{data?.today_sales?.toLocaleString('en-IN') || 0}</Text>
          <Text style={styles.gridLabel}>Today's Sales</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.gridItem} onPress={() => {}}>
          <Text style={styles.gridValue}>₹{data?.today_purchases?.toLocaleString('en-IN') || 0}</Text>
          <Text style={styles.gridLabel}>Today's Purchases</Text>
        </TouchableOpacity>
      </View>

      {/* Upcoming features list */}
      <View style={styles.menuList}>
        <Text style={styles.menuTitle}>Menu</Text>
        {['Customers', 'Inventory', 'Billing', 'Purchases', 'Exchange', 'Settings'].map((item) => (
          <TouchableOpacity 
            key={item} 
            style={styles.menuItem}
            onPress={() => {
              if (item === 'Customers') {
                navigation.navigate('Customers');
              } else if (item === 'Inventory') {
                navigation.navigate('Inventory');
              } else if (item === 'Billing') {
                navigation.navigate('Billing');
              } else if (item === 'Purchases') {
                navigation.navigate('Purchases');
              } else if (item === 'Exchange') {
                navigation.navigate('Exchange');
              }
            }}
          >
            <Text style={styles.menuItemText}>{item}</Text>
            <Text style={styles.menuItemArrow}>→</Text>
          </TouchableOpacity>
        ))}
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
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
  },
  logoutButton: {
    backgroundColor: '#1a1a1a',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#333',
  },
  logoutText: {
    color: '#d4af37',
    fontWeight: 'bold',
  },
  ratesContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  rateCard: {
    flex: 0.48,
    backgroundColor: '#141414',
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#333',
    alignItems: 'center',
  },
  rateLabel: {
    color: '#888',
    fontSize: 12,
    textTransform: 'uppercase',
    marginBottom: 8,
    fontWeight: 'bold',
  },
  rateValue: {
    color: '#d4af37',
    fontSize: 20,
    fontWeight: 'bold',
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  gridItem: {
    width: '48%',
    backgroundColor: '#141414',
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#333',
    marginBottom: 16,
    justifyContent: 'center',
  },
  gridValue: {
    color: '#fff',
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  gridLabel: {
    color: '#888',
    fontSize: 12,
    textTransform: 'uppercase',
    fontWeight: 'bold',
  },
  menuList: {
    backgroundColor: '#141414',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#333',
    overflow: 'hidden',
    marginBottom: 40,
  },
  menuTitle: {
    color: '#888',
    fontSize: 12,
    textTransform: 'uppercase',
    fontWeight: 'bold',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#333',
  },
  menuItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#333',
  },
  menuItemText: {
    color: '#fff',
    fontSize: 16,
  },
  menuItemArrow: {
    color: '#555',
    fontSize: 16,
  }
});
