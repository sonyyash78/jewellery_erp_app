import { create } from 'zustand';
import {
  type CustomRateItem,
  type LiveRatesConfigPayload,
  type LiveRatesStatusResponse,
  type MarketRatesMeta,
  getLiveRatesStatus,
  saveLiveRatesConfig as saveLiveRatesConfigApi,
} from '../api/dashboardApi';

export type { CustomRateItem, MarketRatesMeta };

export type MakingChargeType = 'percent' | 'per_gm' | 'flat';
export type GSTState = 'same_state' | 'different_state' | 'none';
export type ItemType = 'Gold' | 'Silver' | 'Diamond';

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
  wastage: number | '';
  stoneWeight: number;
  ratePerGm: number;
  hallmark: number;
}


export interface DiamondForm {
  itemName: string;
  diamondType: 'NATURAL' | 'SYNTHETIC';
  diamondForm: 'CUT_AND_POLISHED' | 'UNWORKED' | 'MOUNTED';
  shape: string;
  weightGm: number;
  caratWeight?: number;
  pieces: number;
  colour: string;
  clarity: string;
  cut: string;
  certificateNo: string;
  ratePerGm: number;
  ratePerCarat?: number;
  makingCharges: number;
  otherCharges: number;
  discount: number;
}

export interface SilverForm extends BaseCalcForm {
  tanch: number;
  wastage: number | '';
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
  rawDiamond?: DiamondForm;
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
  marketRates: LiveRates;
  marketMeta: MarketRatesMeta | null;
  customRates: CustomRateItem[];
  autoSyncLive: boolean;
  isOfflineFallback: boolean;
  liveRatesLastUpdated: string | null;
  liveRatesSyncing: boolean;
  
  goldForm: GoldForm;
  silverForm: SilverForm;
  diamondForm: DiamondForm;
  
  editingItemId: string | null;
  setEditingItemId: (id: string | null) => void;
  
  setSelectedCustomerId: (id: number | null) => void;
  setGlobalDiscount: (amount: number) => void;
  setGstState: (val: GSTState) => void;
  updateLiveRates: (rates: Partial<LiveRates>) => void;
  fetchLiveRates: (force?: boolean) => Promise<LiveRatesStatusResponse | null>;
  saveLiveRatesConfig: (payload: LiveRatesConfigPayload) => Promise<LiveRatesStatusResponse>;
  updateGoldForm: (field: keyof GoldForm, value: any) => void;
  updateSilverForm: (field: keyof SilverForm, value: any) => void;
  resetGoldForm: () => void;
  resetSilverForm: () => void;
  updateDiamondForm: (field: keyof DiamondForm, value: any) => void;
  resetDiamondForm: () => void;
  addToCart: (item: BillItem) => void;
  removeFromCart: (id: string) => void;
  clearCart: () => void;
  addRecentScan: (code: string) => void;
}

const initialGoldForm: GoldForm = {
  itemName: '', category: '', hsn: '', purity: '22K Gold', touch: 91.6, wastage: '',
  grossWeight: 0, stoneWeight: 0, ratePerGm: 72500,
  makingChargeType: 'per_gm', makingChargeValue: 650,
  hallmark: 120, otherCharges: 0, discount: 0
};


const initialDiamondForm: DiamondForm = {
  itemName: '',
  diamondType: 'NATURAL',
  diamondForm: 'CUT_AND_POLISHED',
  shape: 'Round',
  weightGm: 0,
  caratWeight: 0,
  pieces: 1,
  colour: 'G',
  clarity: 'VS1',
  cut: 'Excellent',
  certificateNo: '',
  ratePerGm: 25000,
  ratePerCarat: 50000,
  makingCharges: 0,
  otherCharges: 0,
  discount: 0
};

const initialSilverForm: SilverForm = {
  itemName: '', category: '', hsn: '',
  grossWeight: 0, stoneWeight: 0, tanch: 65, wastage: '', silverPurity: 'Fine', ratePerKg: 90000,
  makingChargeType: 'per_gm', makingChargeValue: 30,
  otherCharges: 0, discount: 0
};

const defaultRatesSnapshot: LiveRates = {
  gold24k: 79100.0,
  gold22k: 72500.0,
  gold20k: 65900.0,
  gold18k: 59300.0,
  gold14k: 46100.0,
  silver: 90000.0 // per kg
};

const resolveGoldRateForPurity = (purity: string, rates: LiveRates): number => {
  const p = (purity || '').toUpperCase();
  if (p.includes('24')) return rates.gold24k;
  if (p.includes('20')) return rates.gold20k;
  if (p.includes('18')) return rates.gold18k;
  if (p.includes('14')) return rates.gold14k;
  return rates.gold22k || rates.gold24k;
};

const applyLiveRatesStatus = (
  state: BillingStoreState,
  data: LiveRatesStatusResponse
): Partial<BillingStoreState> => {
  const nextRates: LiveRates = { ...state.liveRates, ...(data.active_rates || {}) };
  const canUpdateGoldForm = !state.editingItemId && Number(state.goldForm.grossWeight || 0) === 0;
  const canUpdateSilverForm = !state.editingItemId && Number(state.silverForm.grossWeight || 0) === 0;

  return {
    liveRates: nextRates,
    marketRates: { ...state.marketRates, ...(data.market_rates || {}) },
    marketMeta: data.market_meta || null,
    customRates: Array.isArray(data.custom_rates) ? data.custom_rates : [],
    autoSyncLive: Boolean(data.auto_sync_live),
    isOfflineFallback: Boolean(data.is_offline_fallback),
    liveRatesLastUpdated: data.market_meta?.fetched_at || data.updated_at || new Date().toISOString(),
    liveRatesSyncing: false,
    ...(canUpdateGoldForm
      ? { goldForm: { ...state.goldForm, ratePerGm: resolveGoldRateForPurity(state.goldForm.purity, nextRates) } }
      : {}),
    ...(canUpdateSilverForm
      ? { silverForm: { ...state.silverForm, ratePerKg: nextRates.silver } }
      : {}),
  };
};

export const useBillingStore = create<BillingStoreState>((set) => ({
  cart: [],
  gstState: 'same_state',
  recentScans: [],
  selectedCustomerId: null,
  globalDiscount: 0,
  
  liveRates: { ...defaultRatesSnapshot },
  marketRates: { ...defaultRatesSnapshot },
  marketMeta: null,
  customRates: [],
  autoSyncLive: true,
  isOfflineFallback: false,
  liveRatesLastUpdated: null,
  liveRatesSyncing: false,
  
  goldForm: initialGoldForm,
  silverForm: initialSilverForm,
  diamondForm: initialDiamondForm,
  
  editingItemId: null,
  setEditingItemId: (id) => set({ editingItemId: id }),
  
  setSelectedCustomerId: (id) => set({ selectedCustomerId: id }),
  setGlobalDiscount: (amount) => set({ globalDiscount: amount }),
  setGstState: (val) => set({ gstState: val }),
  updateLiveRates: (rates) => set((state) => ({ liveRates: { ...state.liveRates, ...rates } })),
  fetchLiveRates: async (force = false) => {
    set({ liveRatesSyncing: true });
    try {
      const data = await getLiveRatesStatus(force);
      set((state) => applyLiveRatesStatus(state, data));
      return data;
    } catch {
      set({ liveRatesSyncing: false });
      return null;
    }
  },
  saveLiveRatesConfig: async (payload) => {
    set({ liveRatesSyncing: true });
    try {
      const data = await saveLiveRatesConfigApi(payload);
      set((state) => applyLiveRatesStatus(state, data));
      return data;
    } catch (err) {
      set({ liveRatesSyncing: false });
      throw err;
    }
  },
  updateGoldForm: (field, value) => set((state) => ({ goldForm: { ...state.goldForm, [field]: value } })),
  updateSilverForm: (field, value) => set((state) => ({ silverForm: { ...state.silverForm, [field]: value } })),
  
  resetGoldForm: () => set((state) => ({
    goldForm: {
      ...initialGoldForm,
      ratePerGm: resolveGoldRateForPurity(initialGoldForm.purity, state.liveRates),
    }
  })),
  resetSilverForm: () => set((state) => ({
    silverForm: {
      ...initialSilverForm,
      ratePerKg: state.liveRates.silver || initialSilverForm.ratePerKg,
    }
  })),
  updateDiamondForm: (field, value) => set((state) => ({ diamondForm: { ...state.diamondForm, [field]: value } })),
  resetDiamondForm: () => set({ diamondForm: initialDiamondForm }),
  
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

