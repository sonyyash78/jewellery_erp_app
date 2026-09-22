import React, { useEffect, useState } from 'react';
import { NavigationContainer, DefaultTheme, DarkTheme } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { ActivityIndicator, View } from 'react-native';

// Import Screens
import LoginScreen from '../screens/auth/LoginScreen';
import DashboardScreen from '../screens/dashboard/DashboardScreen';
// import CustomerProfileScreen from '../screens/crm/CustomerProfileScreen';
// import BillingScreen from '../screens/billing/BillingScreen';

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
  const [isLoading, setIsLoading] = useState(true);
  const [userToken, setUserToken] = useState<string | null>(null);

  useEffect(() => {
    // Check for existing token
    const bootstrapAsync = async () => {
      let token;
      try {
        token = await AsyncStorage.getItem('token');
      } catch (e) {
        // Restoring token failed
      }
      setUserToken(token || null);
      setIsLoading(false);
    };

    bootstrapAsync();
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
            {/* 
            <Stack.Screen name="CustomerProfile" component={CustomerProfileScreen} options={{ title: 'Customer Ledger' }} />
            <Stack.Screen name="Billing" component={BillingScreen} options={{ title: 'Create Invoice' }} /> 
            */}
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}
