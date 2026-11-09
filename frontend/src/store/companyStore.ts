import { create } from 'zustand';
import { axiosClient, clearApiCache } from '../api/axiosClient';

export interface Company {
  id: number;
  code: string;
  name: string;
  address?: string;
  city?: string;
  state?: string;
  state_code?: string;
  gstin?: string;
  pan?: string;
  phone?: string;
  email?: string;
  gst_enabled: boolean;
  diamond_enabled: boolean;
  invoice_prefix: string;
  invoice_series: string;
  bank_name?: string;
  bank_account_no?: string;
  bank_ifsc?: string;
  bank_branch?: string;
  upi_id?: string;
  upi_name?: string;
  logo_url?: string;
  declaration?: string;
  jurisdiction_city?: string;
  tax_label_style: string;
  computer_generated_note: string;
  financial_year_start: number;
  rounding_mode: string;
  is_active: boolean;
}

interface CompanyState {
  currentCompanyId: number;
  currentCompany: Company | null;
  companies: Company[];
  isLoading: boolean;
  fetchCompanies: () => Promise<void>;
  selectCompany: (companyId: number) => void;
  updateCurrentCompany: (partial: Partial<Company>) => void;
}

const DEFAULT_COMPANY_ID = 1;

export const useCompanyStore = create<CompanyState>((set, get) => ({
  currentCompanyId: Number(localStorage.getItem('erp_company_id')) || DEFAULT_COMPANY_ID,
  currentCompany: null,
  companies: [],
  isLoading: false,

  fetchCompanies: async () => {
    set({ isLoading: true });
    try {
      const res = await axiosClient.get('/companies');
      const list: Company[] = res.data || [];
      const storedId = Number(localStorage.getItem('erp_company_id')) || DEFAULT_COMPANY_ID;
      const matched = list.find((c) => c.id === storedId) || list.find((c) => c.id === 1) || list[0] || null;
      const activeId = matched ? matched.id : DEFAULT_COMPANY_ID;

      localStorage.setItem('erp_company_id', String(activeId));
      set({
        companies: list,
        currentCompanyId: activeId,
        currentCompany: matched,
        isLoading: false
      });
    } catch (err) {
      console.error('Failed to load companies:', err);
      set({ isLoading: false });
    }
  },

  selectCompany: (companyId: number) => {
    const { companies } = get();
    const target = companies.find((c) => c.id === companyId);
    if (!target) return;

    clearApiCache();
    localStorage.setItem('erp_company_id', String(companyId));
    set({
      currentCompanyId: companyId,
      currentCompany: target
    });

    // Optional event dispatch for listeners to refresh their local states
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('company-switched', { detail: { companyId } }));
    }
  },

  updateCurrentCompany: (partial) => {
    const { currentCompany, companies } = get();
    if (!currentCompany) return;
    const updated = { ...currentCompany, ...partial };
    const updatedList = companies.map((c) => (c.id === updated.id ? updated : c));
    set({ currentCompany: updated, companies: updatedList });
  }
}));
