import { create } from 'zustand';

export interface OldItem {
  id: string;
  itemName: string;
  metal: 'Gold' | 'Silver';
  purity: string;
  touch: number;
  grossWeight: number;
  stoneWeight: number;
  netWeight: number;
  wastage: number;
  fineWeight: number;
  labourCharge: number;
  testingMeltingCharge: number;
  hallmarkCharge: number;
  otherCharges: number;
  discount: number;
  rateApplied: number;
  calculatedValue: number;
}

export interface NewItem {
  id: string; // Used to uniquely identify manual or stock items in cart
  stockItemId: number | null;
  itemCode: string;
  itemName: string;
  metal: string;
  grossWeight: number;
  stoneWeight: number;
  netWeight: number;
  touchPurity: number;
  wastage: number;
  fineWeight: number;
  rateApplied: number;
  makingChargeType: string;
  makingChargeRate: number;
  makingCharges: number;
  hallmark: number;
  otherCharges: number;
  discount: number;
  finalPrice: number;
}

interface ExchangeStoreState {
  customerId: number | null;
  gstState: 'same_state' | 'different_state' | 'none';
  
  oldItems: OldItem[];
  newItems: NewItem[];
  
  setCustomerId: (id: number | null) => void;
  setGstState: (state: 'same_state' | 'different_state' | 'none') => void;
  
  addOldItem: (item: OldItem) => void;
  removeOldItem: (id: string) => void;
  
  addNewItem: (item: NewItem) => void;
  removeNewItem: (id: string) => void;
  
  editingOldItem: OldItem | null;
  setEditingOldItem: (item: OldItem | null) => void;
  updateOldItem: (id: string, item: OldItem) => void;

  editingNewItem: NewItem | null;
  setEditingNewItem: (item: NewItem | null) => void;
  updateNewItem: (id: string, item: NewItem) => void;

  clearExchange: () => void;
}

export const useExchangeStore = create<ExchangeStoreState>((set) => ({
  customerId: null,
  gstState: 'same_state',
  oldItems: [],
  newItems: [],
  
  setCustomerId: (id) => set({ customerId: id }),
  setGstState: (val) => set({ gstState: val }),
  
  addOldItem: (item) => set((state) => ({ oldItems: [...state.oldItems, item] })),
  removeOldItem: (id) => set((state) => ({ oldItems: state.oldItems.filter(i => i.id !== id) })),
  
  addNewItem: (item) => set((state) => ({ newItems: [...state.newItems, item] })),
  removeNewItem: (id) => set((state) => ({ newItems: state.newItems.filter(i => i.id !== id) })),
  
  editingOldItem: null,
  setEditingOldItem: (item) => set({ editingOldItem: item }),
  updateOldItem: (id, item) => set((state) => ({
    oldItems: state.oldItems.map(i => i.id === id ? item : i),
    editingOldItem: null
  })),

  editingNewItem: null,
  setEditingNewItem: (item) => set({ editingNewItem: item }),
  updateNewItem: (id, item) => set((state) => ({
    newItems: state.newItems.map(i => i.id === id ? item : i),
    editingNewItem: null
  })),

  clearExchange: () => set({ customerId: null, oldItems: [], newItems: [], gstState: 'same_state', editingOldItem: null, editingNewItem: null })
}));
