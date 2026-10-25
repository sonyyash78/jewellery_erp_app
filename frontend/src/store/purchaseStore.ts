import { create } from 'zustand';

export interface PurchaseItem {
  id: string;
  metalType: 'Gold' | 'Silver';
  itemName: string;
  category: string;
  grossWeight: number;
  stoneWeight: number;
  netWeight: number;
  touchPurity: number;
  wastage: number;
  fineWeight: number;
  metalRate: number;
  metalValue: number;
  labourCharge: number;
  makingChargeType?: string;
  makingChargeValue?: number;
  testingMeltingCharge: number;
  hallmarkCharge: number;
  otherCharges: number;
  discount: number;
  taxableAmount: number;
}

interface PurchaseStoreState {
  items: PurchaseItem[];
  gstState: 'same_state' | 'different_state' | 'none';
  
  goldForm: {
    itemName: string;
    category: string;
    grossWeight: number;
    stoneWeight: number;
    touchPurity: number;
    wastage: number;
    metalRate: number;
    labourCharge: number;
    makingChargeType?: string;
    makingChargeValue?: number;
    hallmarkCharge: number;
    otherCharges: number;
    discount: number;
  };
  
  silverForm: {
    itemName: string;
    grossWeight: number;
    stoneWeight: number;
    tanch: number;
    wastage: number;
    metalRate: number;
    makingChargeType?: string;
    makingChargeValue?: number;
    testingMeltingCharge: number;
    otherCharges: number;
    discount: number;
  };

  editingItemId: string | null;
  setEditingItemId: (id: string | null) => void;
  
  updateGoldForm: (key: string, value: any) => void;
  updateSilverForm: (key: string, value: any) => void;
  setGstState: (val: 'same_state' | 'different_state' | 'none') => void;
  addItem: (item: PurchaseItem) => void;
  removeItem: (id: string) => void;
  resetForms: () => void;
  clearCart: () => void;
}

export const usePurchaseStore = create<PurchaseStoreState>((set) => ({
  items: [],
  gstState: 'same_state',
  
  goldForm: {
    itemName: '', category: '', grossWeight: 0, stoneWeight: 0, touchPurity: 91.6, wastage: 0,
    metalRate: 0, labourCharge: 0, makingChargeType: 'flat', makingChargeValue: 0, hallmarkCharge: 0, otherCharges: 0, discount: 0
  },
  
  silverForm: {
    itemName: '', grossWeight: 0, stoneWeight: 0, tanch: 99.9, wastage: 0,
    metalRate: 0, testingMeltingCharge: 0, makingChargeType: 'flat', makingChargeValue: 0, otherCharges: 0, discount: 0
  },

  editingItemId: null,
  setEditingItemId: (id) => set({ editingItemId: id }),

  updateGoldForm: (key, value) => set((state) => ({ goldForm: { ...state.goldForm, [key]: value } })),
  updateSilverForm: (key, value) => set((state) => ({ silverForm: { ...state.silverForm, [key]: value } })),
  setGstState: (val) => set({ gstState: val }),
  
  addItem: (item) => set((state) => ({
    items: state.editingItemId
      ? state.items.map(i => i.id === state.editingItemId ? item : i)
      : [...state.items, item],
    editingItemId: null
  })),
  removeItem: (id) => set((state) => ({ items: state.items.filter(i => i.id !== id) })),
  
  resetForms: () => set((state) => ({
    goldForm: { itemName: '', category: '', grossWeight: 0, stoneWeight: 0, touchPurity: 91.6, wastage: 0, metalRate: state.goldForm.metalRate, labourCharge: 0, makingChargeType: 'flat', makingChargeValue: 0, hallmarkCharge: 0, otherCharges: 0, discount: 0 },
    silverForm: { itemName: '', grossWeight: 0, stoneWeight: 0, tanch: 99.9, wastage: 0, metalRate: state.silverForm.metalRate, testingMeltingCharge: 0, makingChargeType: 'flat', makingChargeValue: 0, otherCharges: 0, discount: 0 },
    editingItemId: null
  })),
  
  clearCart: () => set({ items: [], editingItemId: null })
}));
