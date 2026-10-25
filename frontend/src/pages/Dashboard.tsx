import { useState, useEffect } from 'react';
import { getMetrics, getChartData, getRecentActivity } from '../api/dashboardApi';
import type { DashboardMetrics, ChartData } from '../api/dashboardApi';
import StatCard from '../components/dashboard/StatCard';
import MetalRatesWidget from '../components/dashboard/MetalRatesWidget';
import QuickShortcuts from '../components/dashboard/QuickShortcuts';
import AiAssistantCard from '../components/dashboard/AiAssistantCard';
import { SalesTrendChart, TopSellingChart } from '../components/dashboard/DashboardCharts';
import RecentTables from '../components/dashboard/RecentTables';
import { IndianRupee, ShoppingBag, TrendingUp, Users, PackageOpen, RefreshCw } from 'lucide-react';
import toast from 'react-hot-toast';
import { useAuthStore } from '../store/authStore';

export default function Dashboard() {
  const user = useAuthStore(state => state.user);
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [chartData, setChartData] = useState<ChartData | null>(null);
  const [recentData, setRecentData] = useState<{recent_bills: any[], recent_purchases: any[]} | null>(null);
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  const fetchDashboardData = async (showRefreshIndicator = false, retryCount = 0) => {
    if (showRefreshIndicator) setIsRefreshing(true);
    try {
      const [metricsData, chartsData, activityData] = await Promise.all([
        getMetrics(),
        getChartData(),
        getRecentActivity()
      ]);
      setMetrics(metricsData);
      setChartData(chartsData);
      setRecentData(activityData);
      setLastUpdated(new Date());
    } catch (err: any) {
      // Auto-retry up to 5 times with exponential backoff (handles backend startup delays)
      if (retryCount < 5) {
        const delay = Math.min(3000 * (retryCount + 1), 15000);
        setTimeout(() => fetchDashboardData(false, retryCount + 1), delay);
      } else {
        console.error(err);
        if (!metrics) toast.error('Failed to load dashboard data. Please refresh the page.');
      }
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  };

  // Initial load & Polling setup (every 60 seconds, throttled focus)
  useEffect(() => {
    fetchDashboardData();
    const intervalId = setInterval(() => {
      fetchDashboardData(true);
    }, 60000);
    
    let lastFocusTime = Date.now();
    const onFocus = () => {
      const now = Date.now();
      // Only refetch if more than 45 seconds have passed since last fetch
      if (now - lastFocusTime > 45000) {
        lastFocusTime = now;
        fetchDashboardData(true);
      }
    };
    window.addEventListener('focus', onFocus);
    
    return () => {
      clearInterval(intervalId);
      window.removeEventListener('focus', onFocus);
    };
  }, []);

  const formatCurrency = (val: number) => `₹ ${val.toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;

  return (
    <div className="space-y-6 sm:space-y-8 pb-12 animate-in fade-in duration-500">
      
      {/* Header & Live Update Status */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-end gap-3 sm:gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-400 tracking-tight">Dashboard Overview</h1>
          <p className="text-xs sm:text-sm text-primary mt-1 font-semibold flex flex-wrap items-center gap-1.5 sm:gap-2">
            <span>{user?.store_name || 'Jewellery Store'}</span>
            <span className="text-gray-500">•</span>
            <span className="text-gray-400 font-normal">Real-time insights and business metrics</span>
          </p>
        </div>
        <div className="flex items-center gap-2.5 sm:gap-3 bg-surface/50 border border-gray-800 px-3 sm:px-4 py-1.5 sm:py-2 rounded-full shadow-inner self-start sm:self-auto">
          <div className="flex items-center gap-2 text-xs font-semibold text-gray-400">
            <span className="relative flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-green-500"></span>
            </span>
            Live Updates On
          </div>
          <div className="w-px h-4 bg-gray-700"></div>
          <button onClick={() => fetchDashboardData(true)} className="flex items-center gap-1.5 text-xs font-semibold text-primary hover:text-white transition-colors">
            <RefreshCw size={12} className={isRefreshing ? "animate-spin" : ""} />
            {lastUpdated.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </button>
        </div>
      </div>

      {/* Top Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 sm:gap-6">
        <StatCard 
          title="Today's Sales" 
          value={loading || !metrics ? '…' : formatCurrency(metrics.today_sales)} 
          icon={<IndianRupee size={24} />} 
          subtitle={metrics ? `${metrics.today_bills} Bills generated` : undefined}
          trend={metrics ? "up" : undefined}
        />
        <StatCard 
          title="Today's Purchases" 
          value={loading || !metrics ? '…' : formatCurrency(metrics.today_purchases)} 
          icon={<ShoppingBag size={24} />} 
        />
        <StatCard 
          title="Today's Profit" 
          value={loading || !metrics ? '…' : formatCurrency(metrics.today_profit)} 
          icon={<TrendingUp size={24} />} 
          trend={metrics && metrics.today_profit >= 0 ? 'up' : metrics ? 'down' : undefined}
        />
        <StatCard 
          title="Total Customers" 
          value={loading || !metrics ? '…' : metrics.total_customers.toLocaleString()} 
          icon={<Users size={24} />} 
        />
      </div>

      {/* Middle Row: Charts & AI */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">
        <div className="lg:col-span-2">
          {chartData ? <SalesTrendChart data={chartData.sales_trend} /> : (
            <div className="bg-surface rounded-xl border border-gray-800 p-6 h-96 flex items-center justify-center">
              <RefreshCw className="animate-spin text-primary opacity-50" size={32} />
            </div>
          )}
        </div>
        <div className="flex flex-col space-y-4 sm:space-y-6">
          <div className="flex-1">
            <AiAssistantCard />
          </div>
          <div className="flex-1">
            <MetalRatesWidget />
          </div>
        </div>
      </div>

      {/* Lower Row: Inventory & Shortcuts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">
        <div className="lg:col-span-1 flex flex-col space-y-6">
          <StatCard 
            title="Inventory Value (Est)" 
            value={loading ? '...' : formatCurrency(metrics?.inventory_value || 0)} 
            icon={<PackageOpen size={24} />} 
          />
          <QuickShortcuts />
        </div>
        <div className="lg:col-span-2">
          {chartData ? <TopSellingChart data={chartData.top_categories} /> : (
            <div className="bg-surface rounded-xl border border-gray-800 p-6 h-96 flex items-center justify-center">
              <RefreshCw className="animate-spin text-primary opacity-50" size={32} />
            </div>
          )}
        </div>
      </div>

      {/* Tables Row */}
      {recentData && <RecentTables data={recentData} />}
    </div>
  );
}
