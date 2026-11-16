import { axiosClient } from './axiosClient';

export interface DashboardMetrics {
  today_sales: number;
  today_bills: number;
  today_purchases: number;
  today_profit: number;
  total_customers: number;
  inventory_value: number;
  low_stock_count: number;
}

export interface RecentActivity {
  recent_bills: any[];
  recent_purchases: any[];
}

export const getMetrics = async (): Promise<DashboardMetrics> => {
  const res = await axiosClient.get(`/dashboard/metrics?t=${new Date().getTime()}`);
  return res.data;
};

export const getRecentActivity = async (): Promise<RecentActivity> => {
  const res = await axiosClient.get('/dashboard/recent-activity');
  return res.data;
};

export interface LiveRatesMap {
  gold24k: number;
  gold22k: number;
  gold20k: number;
  gold18k: number;
  gold14k: number;
  silver: number;
}

export interface CustomRateItem {
  id: string;
  name: string;
  metal_type: 'Gold' | 'Silver';
  purity_percent: number;
  rate: number;
  unit: string;
}

export interface MarketRatesMeta {
  xau_usd?: number | null;
  xag_usd?: number | null;
  usd_inr?: number | null;
  source?: string;
  fetched_at?: string;
  error?: string | null;
}

export interface LiveRatesStatusResponse {
  auto_sync_live: boolean;
  is_offline_fallback: boolean;
  market_rates: LiveRatesMap;
  market_meta: MarketRatesMeta;
  active_rates: LiveRatesMap;
  custom_rates: CustomRateItem[];
  updated_at?: string | null;
}

export interface LiveRatesConfigPayload {
  auto_sync_live?: boolean;
  active_rates?: Partial<LiveRatesMap>;
  custom_rates?: CustomRateItem[];
}

export const getMetalRates = async () => {
  const res = await axiosClient.get('/metal-rates/latest');
  return res.data;
};

export const getLiveRatesStatus = async (force = false): Promise<LiveRatesStatusResponse> => {
  const res = await axiosClient.get(`/metal-rates/live-status?force=${force}&t=${Date.now()}`);
  return res.data;
};

export const saveLiveRatesConfig = async (
  payload: LiveRatesConfigPayload
): Promise<LiveRatesStatusResponse> => {
  const res = await axiosClient.post('/metal-rates/config', payload);
  return res.data;
};

export interface ChartData {
  sales_trend: { name: string; sales: number }[];
  top_categories: { name: string; qty: number }[];
}

export const getChartData = async (): Promise<ChartData> => {
  const res = await axiosClient.get(`/dashboard/chart-data?t=${new Date().getTime()}`);
  return res.data;
};
