import { create } from 'zustand';

export type MakingChargeType = 'percent' | 'per_gm' | 'flat';
export type GSTState = 'same_state' | 'different_state' | 'none';
export type ItemType = 'Gold' | 'Silver';

export interface BaseCalcForm {
  itemName: string;
  category: string;
  hsn: string;
  grossWeight: number;
  makingChargeType: MakingChargeType;
  makingChargeValue: number;
  otherCharges: number;
  discount: number;
}

export interface GoldForm extends BaseCalcForm {
  purity: string;
  touch: number;
  wastage: number;
  stoneWeight: number;
  ratePerGm: number;
  hallmark: number;
}

export interface SilverForm extends BaseCalcForm {
  tanch: number;
  wastage: number;
  stoneWeight: number;
  silverPurity: string;
  ratePerKg: number;
}

export interface BillItem {
  id: string;
  itemType: ItemType;
  stockItemId?: number; // Added for QR Billing
  
  // Display fields
  itemName: string;
  purityDisplay: string;
  touchDisplay: number;
  wastageDisplay: number;
  grossWeight: number;
  stoneWeight: number;
  netWeight: number;
  fineWeight: number;
  rateDisplay: number;
  
  // Math fields
  metalValue: number;
  makingAmount: number;
  hallmark: number;
  otherCharges: number;
  discount: number;
  taxableAmount: number;
  
  // Store the raw form for re-editing/API payload
  rawGold?: GoldForm;
  rawSilver?: SilverForm;
}

export interface LiveRates {
  gold24k: number;
  gold22k: number;
  gold20k: number;
  gold18k: number;
  gold14k: number;
  silver: number;
}

interface BillingStoreState {
  cart: BillItem[];
  gstState: GSTState;
  recentScans: string[];
  selectedCustomerId: number | null;
  globalDiscount: number;
  
  liveRates: LiveRates;
  
  goldForm: GoldForm;
  silverForm: SilverForm;
  
  editingItemId: string | null;
  setEditingItemId: (id: string | null) => void;
  
  setSelectedCustomerId: (id: number | null) => void;
  setGlobalDiscount: (amount: number) => void;
  setGstState: (val: GSTState) => void;
  updateLiveRates: (rates: Partial<LiveRates>) => void;
  updateGoldForm: (field: keyof GoldForm, value: any) => void;
  updateSilverForm: (field: keyof SilverForm, value: any) => void;
  resetGoldForm: () => void;
  resetSilverForm: () => void;
  addToCart: (item: BillItem) => void;
  removeFromCart: (id: string) => void;
  clearCart: () => void;
  addRecentScan: (code: string) => void;
}

const initialGoldForm: GoldForm = {
  itemName: '', category: '', hsn: '', purity: '22K Gold', touch: 91.6, wastage: 0,
  grossWeight: 0, stoneWeight: 0, ratePerGm: 72500,
  makingChargeType: 'per_gm', makingChargeValue: 650,
  hallmark: 120, otherCharges: 0, discount: 0
};

const initialSilverForm: SilverForm = {
  itemName: '', category: '', hsn: '',
  grossWeight: 0, stoneWeight: 0, tanch: 65, wastage: 0, silverPurity: 'Fine', ratePerKg: 90000,
  makingChargeType: 'per_gm', makingChargeValue: 30,
  otherCharges: 0, discount: 0
};

export const useBillingStore = create<BillingStoreState>((set) => ({
  cart: [],
  gstState: 'same_state',
  recentScans: [],
  selectedCustomerId: null,
  globalDiscount: 0,
  
  liveRates: {
    gold24k: 79100.0,
    gold22k: 72500.0,
    gold20k: 65900.0,
    gold18k: 59300.0,
    gold14k: 46100.0,
    silver: 90000.0 // per kg
  },
  
  goldForm: initialGoldForm,
  silverForm: initialSilverForm,
  
  editingItemId: null,
  setEditingItemId: (id) => set({ editingItemId: id }),
  
  setSelectedCustomerId: (id) => set({ selectedCustomerId: id }),
  setGlobalDiscount: (amount) => set({ globalDiscount: amount }),
  setGstState: (val) => set({ gstState: val }),
  updateLiveRates: (rates) => set((state) => ({ liveRates: { ...state.liveRates, ...rates } })),
  updateGoldForm: (field, value) => set((state) => ({ goldForm: { ...state.goldForm, [field]: value } })),
  updateSilverForm: (field, value) => set((state) => ({ silverForm: { ...state.silverForm, [field]: value } })),
  
  resetGoldForm: () => set({ goldForm: initialGoldForm }),
  resetSilverForm: () => set({ silverForm: initialSilverForm }),
  
  addToCart: (item) => set((state) => ({ 
    cart: state.editingItemId 
      ? state.cart.map(i => i.id === state.editingItemId ? item : i) 
      : [...state.cart, item],
    editingItemId: null
  })),
  removeFromCart: (id) => set((state) => ({ cart: state.cart.filter(i => i.id !== id) })),
  clearCart: () => set({ cart: [], recentScans: [], globalDiscount: 0, editingItemId: null }),
  addRecentScan: (code) => set((state) => ({ recentScans: [code, ...state.recentScans] }))
}));

