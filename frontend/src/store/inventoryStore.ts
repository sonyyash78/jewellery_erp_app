import { create } from 'zustand';

export interface StockItem {
  id: number;
  item_code: string;
  item_name: string;
  metal: string;
  category: string;
  hsn: string | null;
  purity: string | null;
  tanch: number | null;
  wastage: number | null;
  gross_weight: number;
  stone_weight: number;
  net_weight: number;
  making_type: string | null;
  making_charge: number;
  hallmark: number;
  other_charges: number;
  location: string | null;
  shelf: string | null;
  image_path: string | null;
  qr_code_path: string | null;
  description: string | null;
  status: string;
  created_at: string;
}

interface InventoryStoreState {
  items: StockItem[];
  totalItems: number;
  totalWeight: number;
  searchQuery: string;
  categoryFilter: string;
  metalFilter: string;
  statusFilter: string;
  
  setItems: (items: StockItem[], total: number, weight: number) => void;
  setSearchQuery: (query: string) => void;
  setFilters: (category: string, metal: string, status: string) => void;
}

export const useInventoryStore = create<InventoryStoreState>((set) => ({
  items: [],
  totalItems: 0,
  totalWeight: 0,
  searchQuery: '',
  categoryFilter: '',
  metalFilter: '',
  statusFilter: '',
  
  setItems: (items, total, weight) => set({ items, totalItems: total, totalWeight: weight }),
  setSearchQuery: (searchQuery) => set({ searchQuery }),
  setFilters: (categoryFilter, metalFilter, statusFilter) => set({ categoryFilter, metalFilter, statusFilter })
}));
