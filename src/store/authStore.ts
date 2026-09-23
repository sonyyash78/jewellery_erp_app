import { create } from 'zustand';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface AuthState {
  userToken: string | null;
  isLoading: boolean;
  signIn: (token: string, user: any) => Promise<void>;
  signOut: () => Promise<void>;
  restoreToken: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  userToken: null,
  isLoading: true,
  
  signIn: async (token: string, user: any) => {
    await AsyncStorage.setItem('token', token);
    await AsyncStorage.setItem('user', JSON.stringify(user));
    set({ userToken: token });
  },
  
  signOut: async () => {
    await AsyncStorage.removeItem('token');
    await AsyncStorage.removeItem('user');
    set({ userToken: null });
  },
  
  restoreToken: async () => {
    try {
      const token = await AsyncStorage.getItem('token');
      set({ userToken: token, isLoading: false });
    } catch (e) {
      set({ userToken: null, isLoading: false });
    }
  },
}));
