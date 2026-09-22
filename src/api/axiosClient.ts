import axios from 'axios';
import { ENV } from '../config/api';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Alert } from 'react-native';

export const axiosClient = axios.create({
  baseURL: ENV.API_BASE_URL,
  timeout: 10000, // 10 seconds timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor: Attach Token
axiosClient.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response Interceptor: Handle Errors & Formatting
axiosClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    // 1. No Internet / Network Error
    if (error.message === 'Network Error') {
      Alert.alert('Network Error', 'Unable to connect to ERP server. Please check your internet connection or Cloudflare Tunnel.');
      return Promise.reject(error);
    }
    
    // 2. Timeout
    if (error.code === 'ECONNABORTED') {
      Alert.alert('Timeout', 'The request to the ERP server timed out. Please try again.');
      return Promise.reject(error);
    }

    if (error.response) {
      // 3. Unauthorized / Session Expired
      if (error.response.status === 401) {
        Alert.alert('Session Expired', 'Your session has expired. Please log in again.');
        await AsyncStorage.removeItem('token');
        await AsyncStorage.removeItem('user');
        // Force navigation to Login (handled via App.tsx state or navigation ref in a real app)
      }
      
      // 4. Server Errors (500)
      if (error.response.status >= 500) {
        Alert.alert('Server Error', 'The ERP server encountered an error. Please try again later.');
      }
    } else {
      Alert.alert('Error', 'An unexpected error occurred connecting to the ERP API.');
    }

    return Promise.reject(error);
  }
);
