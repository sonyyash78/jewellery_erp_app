import React, { useEffect, useState } from 'react';
import { NavigationContainer, DefaultTheme, DarkTheme } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { ActivityIndicator, View } from 'react-native';

// Import Screens
import LoginScreen from '../screens/auth/LoginScreen';
import DashboardScreen from '../screens/dashboard/DashboardScreen';
import CustomersScreen from '../screens/crm/CustomersScreen';
import CustomerProfileScreen from '../screens/crm/CustomerProfileScreen';
import SuppliersScreen from '../screens/crm/SuppliersScreen';
import SupplierProfileScreen from '../screens/crm/SupplierProfileScreen';
import InventoryScreen from '../screens/inventory/InventoryScreen';
import SettingsScreen from '../screens/settings/SettingsScreen';
import ReportsScreen from '../screens/reports/ReportsScreen';
import BillingScreen from '../screens/billing/BillingScreen';
import CreateInvoiceScreen from '../screens/billing/CreateInvoiceScreen';
import CheckoutScreen from '../screens/billing/CheckoutScreen';
import InvoiceDetailScreen from '../screens/billing/InvoiceDetailScreen';

import PurchasesScreen from '../screens/purchases/PurchasesScreen';
import CreatePurchaseScreen from '../screens/purchases/CreatePurchaseScreen';
import CheckoutPurchaseScreen from '../screens/purchases/CheckoutPurchaseScreen';
import PurchaseDetailScreen from '../screens/purchases/PurchaseDetailScreen';

import ExchangeScreen from '../screens/exchange/ExchangeScreen';
import CreateExchangeScreen from '../screens/exchange/CreateExchangeScreen';
import CheckoutExchangeScreen from '../screens/exchange/CheckoutExchangeScreen';

import { useAuthStore } from '../store/authStore';

const Stack = createNativeStackNavigator();

const AppDarkTheme = {
  ...DarkTheme,
  colors: {
    ...DarkTheme.colors,
    background: '#0a0a0a',
    card: '#141414',
    text: '#ffffff',
    primary: '#d4af37', // Gold color
  },
};

export default function AppNavigator() {
  const { userToken, isLoading, restoreToken } = useAuthStore();

  useEffect(() => {
    restoreToken();
  }, []);

  if (isLoading) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#0a0a0a' }}>
        <ActivityIndicator size="large" color="#d4af37" />
      </View>
    );
  }

  return (
    <NavigationContainer theme={AppDarkTheme}>
      <Stack.Navigator
        screenOptions={{
          headerStyle: { backgroundColor: '#141414' },
          headerTintColor: '#d4af37',
          headerTitleStyle: { fontWeight: 'bold' },
        }}
      >
        {userToken == null ? (
          // No token found, user isn't signed in
          <Stack.Screen 
            name="Login" 
            component={LoginScreen} 
            options={{ headerShown: false }} 
          />
        ) : (
          // User is signed in
          <>
            <Stack.Screen 
              name="MainDrawer" 
              component={DashboardScreen} 
              options={{ title: 'Jewellery ERP' }} 
            />
            <Stack.Screen name="Customers" component={CustomersScreen} options={{ title: 'Customers' }} />
            <Stack.Screen name="CustomerProfile" component={CustomerProfileScreen} options={{ title: 'Customer Profile' }} />
            <Stack.Screen name="Suppliers" component={SuppliersScreen} options={{ title: 'Suppliers' }} />
            <Stack.Screen name="SupplierProfile" component={SupplierProfileScreen} options={{ title: 'Supplier Profile' }} />
            <Stack.Screen name="Inventory" component={InventoryScreen} options={{ title: 'Inventory Stock' }} />
            <Stack.Screen name="Billing" component={BillingScreen} options={{ title: 'Billing & Invoices' }} />
            <Stack.Screen name="CreateInvoice" component={CreateInvoiceScreen} options={{ title: 'Create Invoice' }} />
            <Stack.Screen name="Checkout" component={CheckoutScreen} options={{ title: 'Checkout & Settle' }} />
            <Stack.Screen name="InvoiceDetail" component={InvoiceDetailScreen} options={{ title: 'Invoice Detail' }} />

            <Stack.Screen name="Purchases" component={PurchasesScreen} options={{ title: 'Purchases History' }} />
            <Stack.Screen name="CreatePurchase" component={CreatePurchaseScreen} options={{ title: 'Add Purchase' }} />
            <Stack.Screen name="CheckoutPurchase" component={CheckoutPurchaseScreen} options={{ title: 'Checkout Purchase' }} />
            <Stack.Screen name="PurchaseDetail" component={PurchaseDetailScreen} options={{ title: 'Purchase Detail' }} />

            <Stack.Screen name="Exchange" component={ExchangeScreen} options={{ title: 'Exchange History' }} />
            <Stack.Screen name="CreateExchange" component={CreateExchangeScreen} options={{ title: 'New Exchange' }} />
            <Stack.Screen name="CheckoutExchange" component={CheckoutExchangeScreen} options={{ title: 'Checkout Exchange' }} />

            <Stack.Screen name="Settings" component={SettingsScreen} options={{ title: 'Settings' }} />
            <Stack.Screen name="Reports" component={ReportsScreen} options={{ title: 'Reports' }} />
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}
