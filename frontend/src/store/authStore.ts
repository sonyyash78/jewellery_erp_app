import { create } from 'zustand';
import { clearApiCache } from '../api/axiosClient';

interface AuthState {
  token: string | null;
  user: any | null;
  setAuth: (token: string, user: any) => void;
  updateUser: (partialUser: any) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: localStorage.getItem('erp_token'),
  user: JSON.parse(localStorage.getItem('erp_user') || 'null'),
  setAuth: (token, user) => {
    clearApiCache();
    localStorage.setItem('erp_token', token);
    localStorage.setItem('erp_user', JSON.stringify(user));
    set({ token, user });
  },
  updateUser: (partialUser) => {
    clearApiCache();
    const current = useAuthStore.getState().user || {};
    const updated = { ...current, ...partialUser };
    localStorage.setItem('erp_user', JSON.stringify(updated));
    set({ user: updated });
  },
  logout: () => {
    clearApiCache();
    localStorage.removeItem('erp_token');
    localStorage.removeItem('erp_user');
    set({ token: null, user: null });
  }
}));
