import { useCompanyStore } from '../../store/companyStore';
import { useState, useEffect } from 'react';
import { axiosClient } from '../../api/axiosClient';
import { exportReportToPDF } from '../../utils/exportUtils';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, LineChart, Line } from 'recharts';
import { FileText, Printer, AlertCircle, RotateCcw } from 'lucide-react';
import toast from 'react-hot-toast';


interface WastageData {
  company_id?: number;
  summary?: {
    gold_net_wastage_profit_g: number;
    silver_net_wastage_profit_g: number;
    diamond_carats_sold: number;
    total_making_profit_rs: number;
    total_value_profit_rs: number;
  };
  gold?: {
    sold_fine_g: number;
    sold_wastage_g: number;
    sold_making_rs: number;
    sold_total_val_rs: number;
    purchased_fine_g: number;
    purchased_wastage_g: number;
    purchased_labour_rs: number;
    purchased_total_val_rs: number;
    net_wastage_profit_g: number;
    net_labour_profit_rs: number;
    net_val_profit_rs: number;
  };
  silver?: {
    sold_pure_g: number;
    sold_wastage_g: number;
    sold_making_rs: number;
    sold_total_val_rs: number;
    purchased_pure_g: number;
    purchased_wastage_g: number;
    purchased_labour_rs: number;
    purchased_total_val_rs: number;
    net_wastage_profit_g: number;
    net_labour_profit_rs: number;
    net_val_profit_rs: number;
  };
  diamond?: {
    sold_carats: number;
    sold_weight_g: number;
    sold_making_rs: number;
    sold_total_val_rs: number;
    purchased_labour_rs: number;
    purchased_total_val_rs: number;
    net_making_profit_rs: number;
    net_val_profit_rs: number;
  };
  transactions?: Array<{
    date: string;
    type: string;
    bill_no: string;
    item_name: string;
    metal: string;
    weight_g: number;
    touch_pct: number;
    wastage_pct: number;
    wastage_g: number;
    fine_weight_g: number;
    making_charges: number;
    total_amount: number;
  }>;
}

function WastageProfitView({ data }: { data: WastageData }) {
  const sum = data.summary || {
    gold_net_wastage_profit_g: 0,
    silver_net_wastage_profit_g: 0,
    diamond_carats_sold: 0,
    total_making_profit_rs: 0,
    total_value_profit_rs: 0,
  };
  const g = data.gold || {} as any;
  const s = data.silver || {} as any;
  const d = data.diamond || {} as any;
  const txs = data.transactions || [];

  return (
    <div className="space-y-6">
      {/* 1. TOP HIGHLIGHT SUMMARY BANNER */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 p-4 bg-gradient-to-r from-amber-950/40 via-gray-900/60 to-purple-950/40 border border-gray-800 rounded-2xl shadow-xl">
        <div className="p-2 border-r border-gray-800/80">
          <div className="text-[11px] font-bold text-amber-400 uppercase tracking-widest flex items-center gap-1">
            <span>🪙 Gold Wastage Profit</span>
          </div>
          <div className={`text-xl sm:text-2xl font-black font-mono mt-1 ${sum.gold_net_wastage_profit_g >= 0 ? 'text-amber-400' : 'text-red-400'}`}>
            {sum.gold_net_wastage_profit_g >= 0 ? '+' : ''}{sum.gold_net_wastage_profit_g.toFixed(3)} g
          </div>
          <div className="text-[10px] text-gray-400 mt-0.5">Sold Wst − Pur Wst</div>
        </div>

        <div className="p-2 border-r border-gray-800/80">
          <div className="text-[11px] font-bold text-cyan-300 uppercase tracking-widest flex items-center gap-1">
            <span>🥈 Silver Wastage Profit</span>
          </div>
          <div className={`text-xl sm:text-2xl font-black font-mono mt-1 ${sum.silver_net_wastage_profit_g >= 0 ? 'text-cyan-300' : 'text-red-400'}`}>
            {sum.silver_net_wastage_profit_g >= 0 ? '+' : ''}{sum.silver_net_wastage_profit_g.toFixed(3)} g
          </div>
          <div className="text-[10px] text-gray-400 mt-0.5">Sold Wst − Pur Wst</div>
        </div>

        <div className="p-2 border-r border-gray-800/80">
          <div className="text-[11px] font-bold text-purple-300 uppercase tracking-widest flex items-center gap-1">
            <span>💎 Diamond Sold</span>
          </div>
          <div className="text-xl sm:text-2xl font-black font-mono mt-1 text-purple-300">
            {sum.diamond_carats_sold.toFixed(4)} cts
          </div>
          <div className="text-[10px] text-gray-400 mt-0.5">Total Carats Traded</div>
        </div>

        <div className="p-2 border-r border-gray-800/80">
          <div className="text-[11px] font-bold text-emerald-400 uppercase tracking-widest flex items-center gap-1">
            <span>🔨 Making/Labour Profit</span>
          </div>
          <div className={`text-xl sm:text-2xl font-black font-mono mt-1 ${sum.total_making_profit_rs >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
            ₹ {sum.total_making_profit_rs.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </div>
          <div className="text-[10px] text-gray-400 mt-0.5">Making Earned − Paid</div>
        </div>

        <div className="p-2 col-span-2 sm:col-span-1">
          <div className="text-[11px] font-bold text-yellow-400 uppercase tracking-widest flex items-center gap-1">
            <span>💰 Net Trading Profit</span>
          </div>
          <div className={`text-xl sm:text-2xl font-black font-mono mt-1 ${sum.total_value_profit_rs >= 0 ? 'text-yellow-400' : 'text-red-400'}`}>
            ₹ {sum.total_value_profit_rs.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </div>
          <div className="text-[10px] text-gray-400 mt-0.5">Sales Val − Pur Cost</div>
        </div>
      </div>

      {/* 2. THREE DEDICATED METAL ANALYSIS CARDS */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* GOLD CARD */}
        <div className="bg-surface border border-amber-500/30 rounded-2xl p-4 sm:p-5 shadow-lg flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-gray-800">
              <h3 className="text-sm font-bold text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
                <span>🪙 Gold (स्वर्ण) Wastage & Profit</span>
              </h3>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 font-mono font-bold">Gold Analysis</span>
            </div>

            <div className="mt-3 space-y-2 text-xs">
              <div className="flex justify-between py-1 border-b border-gray-800/60">
                <span className="text-gray-400">Customer Wastage Charged (Sell):</span>
                <span className="font-mono font-bold text-white">{(g.sold_wastage_g || 0).toFixed(3)} g</span>
              </div>
              <div className="flex justify-between py-1 border-b border-gray-800/60">
                <span className="text-gray-400">Supplier Wastage Paid (Purchase):</span>
                <span className="font-mono font-bold text-red-300">− {(g.purchased_wastage_g || 0).toFixed(3)} g</span>
              </div>
              <div className="flex justify-between py-1.5 bg-amber-500/10 px-2 rounded-lg border border-amber-500/20">
                <span className="font-bold text-amber-400">Net Gold Wastage Profit:</span>
                <span className="font-mono font-black text-amber-400 text-sm">
                  {(g.net_wastage_profit_g || 0) >= 0 ? '+' : ''}{(g.net_wastage_profit_g || 0).toFixed(3)} g
                </span>
              </div>
              <div className="flex justify-between py-1 border-b border-gray-800/60 pt-2">
                <span className="text-gray-400">Fine Gold Sold:</span>
                <span className="font-mono text-gray-200">{(g.sold_fine_g || 0).toFixed(3)} g</span>
              </div>
              <div className="flex justify-between py-1 border-b border-gray-800/60">
                <span className="text-gray-400">Fine Gold Purchased:</span>
                <span className="font-mono text-gray-200">{(g.purchased_fine_g || 0).toFixed(3)} g</span>
              </div>
              <div className="flex justify-between py-1 border-b border-gray-800/60">
                <span className="text-gray-400">Customer Making Earned:</span>
                <span className="font-mono text-emerald-400">₹ {(g.sold_making_rs || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-gray-800/60">
                <span className="text-gray-400">Supplier Labour Paid:</span>
                <span className="font-mono text-red-300">₹ {(g.purchased_labour_rs || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
              </div>
              <div className="flex justify-between py-1.5 bg-gray-900 px-2 rounded-lg font-bold">
                <span className="text-gray-300">Gold Labour Profit:</span>
                <span className="font-mono text-emerald-400">₹ {(g.net_labour_profit_rs || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
              </div>
            </div>
          </div>
        </div>

        {/* SILVER CARD */}
        <div className="bg-surface border border-cyan-500/30 rounded-2xl p-4 sm:p-5 shadow-lg flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-gray-800">
              <h3 className="text-sm font-bold text-cyan-300 uppercase tracking-wider flex items-center gap-1.5">
                <span>🥈 Silver (रजत) Wastage & Profit</span>
              </h3>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 font-mono font-bold">Silver Analysis</span>
            </div>

            <div className="mt-3 space-y-2 text-xs">
              <div className="flex justify-between py-1 border-b border-gray-800/60">
                <span className="text-gray-400">Customer Wastage Charged (Sell):</span>
                <span className="font-mono font-bold text-white">{(s.sold_wastage_g || 0).toFixed(3)} g</span>
              </div>
              <div className="flex justify-between py-1 border-b border-gray-800/60">
                <span className="text-gray-400">Supplier Wastage Paid (Purchase):</span>
                <span className="font-mono font-bold text-red-300">− {(s.purchased_wastage_g || 0).toFixed(3)} g</span>
              </div>
              <div className="flex justify-between py-1.5 bg-cyan-500/10 px-2 rounded-lg border border-cyan-500/20">
                <span className="font-bold text-cyan-300">Net Silver Wastage Profit:</span>
                <span className="font-mono font-black text-cyan-300 text-sm">
                  {(s.net_wastage_profit_g || 0) >= 0 ? '+' : ''}{(s.net_wastage_profit_g || 0).toFixed(3)} g
                </span>
              </div>
              <div className="flex justify-between py-1 border-b border-gray-800/60 pt-2">
                <span className="text-gray-400">Pure Silver Sold:</span>
                <span className="font-mono text-gray-200">{(s.sold_pure_g || 0).toFixed(3)} g</span>
              </div>
              <div className="flex justify-between py-1 border-b border-gray-800/60">
                <span className="text-gray-400">Pure Silver Purchased:</span>
                <span className="font-mono text-gray-200">{(s.purchased_pure_g || 0).toFixed(3)} g</span>
              </div>
              <div className="flex justify-between py-1 border-b border-gray-800/60">
                <span className="text-gray-400">Customer Making Earned:</span>
                <span className="font-mono text-emerald-400">₹ {(s.sold_making_rs || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-gray-800/60">
                <span className="text-gray-400">Supplier Labour Paid:</span>
                <span className="font-mono text-red-300">₹ {(s.purchased_labour_rs || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
              </div>
              <div className="flex justify-between py-1.5 bg-gray-900 px-2 rounded-lg font-bold">
                <span className="text-gray-300">Silver Labour Profit:</span>
                <span className="font-mono text-emerald-400">₹ {(s.net_labour_profit_rs || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
              </div>
            </div>
          </div>
        </div>

        {/* DIAMOND CARD */}
        <div className="bg-surface border border-purple-500/30 rounded-2xl p-4 sm:p-5 shadow-lg flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-gray-800">
              <h3 className="text-sm font-bold text-purple-300 uppercase tracking-wider flex items-center gap-1.5">
                <span>💎 Diamond (हीरा) Margin & Profit</span>
              </h3>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300 font-mono font-bold">Diamond Analysis</span>
            </div>

            <div className="mt-3 space-y-2 text-xs">
              <div className="flex justify-between py-1 border-b border-gray-800/60">
                <span className="text-gray-400">Total Carats Sold:</span>
                <span className="font-mono font-bold text-purple-300">{(d.sold_carats || 0).toFixed(4)} cts</span>
              </div>
              <div className="flex justify-between py-1 border-b border-gray-800/60">
                <span className="text-gray-400">Gold/Mounting Weight:</span>
                <span className="font-mono font-bold text-white">{(d.sold_weight_g || 0).toFixed(3)} g</span>
              </div>
              <div className="flex justify-between py-1 border-b border-gray-800/60">
                <span className="text-gray-400">Setting/Making Charges Earned:</span>
                <span className="font-mono text-emerald-400">₹ {(d.sold_making_rs || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-gray-800/60">
                <span className="text-gray-400">Setting/Labour Charges Paid:</span>
                <span className="font-mono text-red-300">₹ {(d.purchased_labour_rs || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
              </div>
              <div className="flex justify-between py-1.5 bg-purple-500/10 px-2 rounded-lg border border-purple-500/20">
                <span className="font-bold text-purple-300">Net Setting Profit:</span>
                <span className="font-mono font-black text-purple-300 text-sm">
                  ₹ {(d.net_making_profit_rs || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </span>
              </div>
              <div className="flex justify-between py-1 border-b border-gray-800/60 pt-2">
                <span className="text-gray-400">Diamond Sales Value:</span>
                <span className="font-mono text-gray-200">₹ {(d.sold_total_val_rs || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-gray-800/60">
                <span className="text-gray-400">Diamond Purchase Cost:</span>
                <span className="font-mono text-gray-200">₹ {(d.purchased_total_val_rs || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
              </div>
              <div className="flex justify-between py-1.5 bg-gray-900 px-2 rounded-lg font-bold">
                <span className="text-gray-300">Diamond Net Margin:</span>
                <span className="font-mono text-yellow-400">₹ {(d.net_val_profit_rs || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 3. TRANSACTION AUDIT TABLE */}
      <div className="bg-surface border border-gray-800 rounded-2xl p-4 sm:p-5 shadow-lg">
        <h4 className="text-xs sm:text-sm font-bold text-primary uppercase tracking-wider mb-3 flex items-center justify-between">
          <span>Detailed Itemized Wastage & Weight Breakdown ({txs.length} Transactions)</span>
          <span className="text-[10px] text-gray-400 font-normal">Audit Trail (Sales & Purchases)</span>
        </h4>

        {txs.length === 0 ? (
          <div className="py-8 text-center text-xs text-gray-500">No transactions recorded in this date range.</div>
        ) : (
          <div className="overflow-x-auto whitespace-nowrap custom-scrollbar">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-gray-800 text-gray-400 uppercase text-[10px] font-bold">
                  <th className="py-2 px-3">Date</th>
                  <th className="py-2 px-3">Type</th>
                  <th className="py-2 px-3">Bill No.</th>
                  <th className="py-2 px-3">Item Name</th>
                  <th className="py-2 px-3">Metal</th>
                  <th className="py-2 px-3 text-right">Gross Wt</th>
                  <th className="py-2 px-3 text-right">Touch</th>
                  <th className="py-2 px-3 text-right text-amber-400">Wastage (gm)</th>
                  <th className="py-2 px-3 text-right">Fine Wt (g)</th>
                  <th className="py-2 px-3 text-right">Making (₹)</th>
                  <th className="py-2 px-3 text-right">Total (₹)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800/60 font-mono">
                {txs.map((tx, idx) => (
                  <tr key={idx} className="hover:bg-gray-800/30 transition-colors">
                    <td className="py-2 px-3 text-gray-400 font-sans">{tx.date}</td>
                    <td className="py-2 px-3 font-sans">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${tx.type === 'Sale' ? 'bg-emerald-500/20 text-emerald-300' : 'bg-amber-500/20 text-amber-300'}`}>
                        {tx.type}
                      </span>
                    </td>
                    <td className="py-2 px-3 font-bold text-white">{tx.bill_no}</td>
                    <td className="py-2 px-3 font-sans text-gray-300">{tx.item_name}</td>
                    <td className="py-2 px-3 font-sans">
                      <span className={tx.metal === 'Gold' ? 'text-amber-400 font-bold' : tx.metal === 'Silver' ? 'text-cyan-300 font-bold' : 'text-purple-300 font-bold'}>
                        {tx.metal}
                      </span>
                    </td>
                    <td className="py-2 px-3 text-right">{tx.weight_g.toFixed(3)}</td>
                    <td className="py-2 px-3 text-right">{((tx as any).touch ?? tx.touch_pct ?? 0).toFixed(2)}</td>
                    <td className="py-2 px-3 text-right text-amber-400 font-bold">{(tx.wastage_g || 0).toFixed(3)} g</td>
                    <td className="py-2 px-3 text-right text-gray-200">{tx.fine_weight_g.toFixed(3)}</td>
                    <td className="py-2 px-3 text-right text-emerald-400">₹ {tx.making_charges.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</td>
                    <td className="py-2 px-3 text-right font-bold text-white">₹ {tx.total_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default function ReportViewer({ reportType }: { reportType: string }) {
  const { currentCompanyId, currentCompany } = useCompanyStore();
  const [timeFilter, setTimeFilter] = useState('Last30Days');
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [dateRange, setDateRange] = useState<{ start?: string; end?: string }>({});
  
  // Custom date picker state
  const [customStart, setCustomStart] = useState('');
  const [customEnd, setCustomEnd] = useState('');

  const formatLocalDate = (d: Date): string => {
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };

  useEffect(() => {
    if (timeFilter !== 'Custom') {
      fetchReport();
    }
  }, [reportType, timeFilter, currentCompanyId]);

  const fetchReport = async (overrideStart?: string, overrideEnd?: string) => {
    setLoading(true);
    setHasError(false);
    try {
      const today = new Date();
      let startDate: string | undefined;
      let endDate: string | undefined;

      switch (timeFilter) {
        case 'Daily':
          startDate = endDate = formatLocalDate(today);
          break;
        case 'Weekly': {
          const weekAgo = new Date(today);
          weekAgo.setDate(weekAgo.getDate() - 7);
          startDate = formatLocalDate(weekAgo);
          endDate = formatLocalDate(today);
          break;
        }
        case 'Last30Days': {
          const thirtyAgo = new Date(today);
          thirtyAgo.setDate(thirtyAgo.getDate() - 30);
          startDate = formatLocalDate(thirtyAgo);
          endDate = formatLocalDate(today);
          break;
        }
        case 'ThisMonth': {
          const firstOfMonth = new Date(today.getFullYear(), today.getMonth(), 1);
          startDate = formatLocalDate(firstOfMonth);
          endDate = formatLocalDate(today);
          break;
        }
        case 'LastMonth': {
          const firstOfLastMonth = new Date(today.getFullYear(), today.getMonth() - 1, 1);
          const lastOfLastMonth = new Date(today.getFullYear(), today.getMonth(), 0);
          startDate = formatLocalDate(firstOfLastMonth);
          endDate = formatLocalDate(lastOfLastMonth);
          break;
        }
        case 'Yearly': {
          const firstOfYear = new Date(today.getFullYear(), 0, 1);
          startDate = formatLocalDate(firstOfYear);
          endDate = formatLocalDate(today);
          break;
        }
        case 'Custom':
          startDate = overrideStart || customStart || undefined;
          endDate = overrideEnd || customEnd || undefined;
          break;
        case 'All':
        default:
          startDate = endDate = undefined;
      }

      setDateRange({ start: startDate, end: endDate });

      const params = new URLSearchParams();
      params.append('company_id', String(currentCompanyId || 1));
      if (startDate) params.append('start_date', startDate);
      if (endDate) params.append('end_date', endDate);

      const endpoint = reportType.toLowerCase().replace(' ', '-');
      const res = await axiosClient.get(`/reports/${endpoint}?${params.toString()}`);
      setData(res.data);
    } catch (e: any) {
      setHasError(true);
      const isTimeout = e?.code === 'ECONNABORTED' || Boolean(e?.message && e.message.toLowerCase().includes('timeout'));
      if (isTimeout) {
        toast.error('Backend is waking up. Please retry shortly.', { duration: 5000 });
      } else {
        toast.error(`Failed to load ${reportType} report`);
      }
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleApplyCustomDates = (e: React.FormEvent) => {
    e.preventDefault();
    if (!customStart || !customEnd) {
      toast.error('Please select both Start and End dates');
      return;
    }
    fetchReport(customStart, customEnd);
  };

  const handlePrint = () => {
    window.print();
  };

  const handleExportPDF = () => {
    if (!data) {
      toast.error("No data to export");
      return;
    }
    
    const toastId = 'pdf-export';
    try {
      toast.loading('Generating PDF...', { id: toastId });
      exportReportToPDF(data, `${reportType} Report`, dateRange);
      toast.success("PDF downloaded successfully", { id: toastId });
    } catch (error: any) {
      console.error('PDF export error:', error);
      const errorMessage = error.message || 'Unknown error occurred';
      toast.error(`Failed to generate PDF: ${errorMessage}`, { id: toastId, duration: 5000 });
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[350px] p-12 bg-surface border border-gray-800 rounded-xl text-center space-y-4">
        <div className="w-10 h-10 border-3 border-primary border-t-transparent rounded-full animate-spin" />
        <div className="text-sm font-bold text-primary tracking-wide">
          Calculating {reportType} Analytics...
        </div>
        <p className="text-xs text-textMuted max-w-sm">
          Compiling transactions and calculating metal flows. If the server was idle, it may take a few seconds to spin up.
        </p>
      </div>
    );
  }

  if (hasError || !data) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[350px] p-12 bg-surface border border-gray-800 rounded-xl text-center space-y-4">
        <div className="w-12 h-12 rounded-full bg-red-500/10 text-red-400 flex items-center justify-center">
          <AlertCircle size={28} />
        </div>
        <div>
          <h3 className="text-base font-bold text-textMain">Unable to Load {reportType} Report</h3>
          <p className="text-xs text-textMuted max-w-md mt-1">
            The server may be waking up from sleep or reconnecting. Please click below to reload.
          </p>
        </div>
        <button
          onClick={() => fetchReport()}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-black font-bold text-xs rounded-lg hover:bg-primary-dark transition-colors cursor-pointer shadow-md"
        >
          <RotateCcw size={14} /> Retry Report
        </button>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6 h-full print-safe">
      
      {/* Header and Controls */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-surface p-4 rounded-xl border border-gray-800 shadow-lg print:hidden">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider border ${
              currentCompany?.gst_enabled
                ? 'bg-cyan-500/15 border-cyan-500/30 text-cyan-400'
                : 'bg-amber-500/15 border-amber-500/30 text-amber-300'
            }`}>
              {currentCompany?.name || 'Saideep Jewellers'} {currentCompany?.gst_enabled ? '• GST Tax Analytics' : '• Normal Retail Analytics'}
            </span>
          </div>
          <h2 className="text-xl font-bold text-primary uppercase tracking-widest">{reportType} Report</h2>
          <div className="flex items-center gap-2 mt-1">
            <span className="text-xs text-textMuted">Active Period:</span>
            <span className="text-xs font-semibold text-primary bg-primary/10 border border-primary/20 px-2.5 py-0.5 rounded-full">
              {dateRange.start && dateRange.end 
                ? `${dateRange.start}  ➔  ${dateRange.end}` 
                : 'All Time Records'}
            </span>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {timeFilter === 'Custom' && (
            <form onSubmit={handleApplyCustomDates} className="flex items-center gap-2">
              <input 
                type="date" 
                value={customStart} 
                onChange={e => setCustomStart(e.target.value)} 
                className="bg-background border border-gray-700 text-xs rounded px-2.5 py-1.5 text-textMain outline-none focus:border-primary"
              />
              <span className="text-xs text-gray-500">to</span>
              <input 
                type="date" 
                value={customEnd} 
                onChange={e => setCustomEnd(e.target.value)} 
                className="bg-background border border-gray-700 text-xs rounded px-2.5 py-1.5 text-textMain outline-none focus:border-primary"
              />
              <button 
                type="submit" 
                className="bg-primary text-black text-xs font-bold px-3 py-1.5 rounded hover:bg-primary-dark transition-colors"
              >
                Apply
              </button>
            </form>
          )}

          <select 
            value={timeFilter} 
            onChange={e => setTimeFilter(e.target.value)}
            className="bg-background border border-gray-700 text-sm rounded px-3 py-2 outline-none text-textMain focus:border-primary"
          >
            <option value="Last30Days">Last 30 Days (Rolling Month)</option>
            <option value="ThisMonth">This Month (Current)</option>
            <option value="LastMonth">Last Month (Previous)</option>
            <option value="Weekly">Last 7 Days</option>
            <option value="Daily">Today (Daily)</option>
            <option value="Yearly">This Year</option>
            <option value="All">All Time</option>
            <option value="Custom">Custom Date Range...</option>
          </select>

          <div className="flex bg-background border border-gray-700 rounded overflow-hidden">
            <button 
              onClick={handleExportPDF} 
              className="px-3 py-2 hover:bg-gray-800 text-red-400 flex items-center gap-2 border-r border-gray-700 transition-colors text-sm font-semibold"
            >
              <FileText size={16} /> PDF
            </button>
            <button 
              onClick={handlePrint} 
              className="px-3 py-2 hover:bg-gray-800 text-blue-400 flex items-center gap-2 transition-colors text-sm font-semibold"
            >
              <Printer size={16} /> Print
            </button>
          </div>
        </div>
      </div>

      {reportType === 'Wastage Profit' ? (
        <WastageProfitView data={data} />
      ) : (
        <>
      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
        {Object.entries(data).filter(([k]) => k !== 'chart').map(([key, value]) => (
          <div key={key} className="bg-surface border border-gray-800 rounded-xl p-4 sm:p-6 shadow-lg flex flex-col justify-center">
            <div className="text-[11px] sm:text-xs font-bold text-gray-500 uppercase tracking-wider mb-1.5 sm:mb-2">{key.replace(/_/g, ' ')}</div>
            <div className="text-xl sm:text-2xl lg:text-3xl font-bold font-mono text-textMain">
              {typeof value === 'object' && value !== null ? (
                <div className="flex flex-col gap-1 mt-2">
                  {Object.entries(value).map(([k, v]) => {
                    const isTotal = k.toLowerCase().includes('total');
                    const isNet = k.toLowerCase().includes('net');
                    let rowClass = 'text-xs sm:text-sm font-normal text-gray-400';
                    let valClass = '';
                    if (isNet) {
                        rowClass = 'text-sm sm:text-base font-black text-white mt-3 border-t border-gray-600 pt-2 pb-2 bg-gray-800/30 px-2 rounded-lg';
                        valClass = 'text-green-400';
                    } else if (isTotal) {
                        rowClass = 'text-xs sm:text-sm font-bold text-gray-200 mt-2 border-t pt-1 border-gray-700';
                        valClass = 'text-primary';
                    }
                    return (
                      <div key={k} className={`flex justify-between border-b border-gray-800/50 pb-1 ${rowClass}`}>
                        <span className="capitalize">{k}</span>
                        <span className={valClass}>{k.toLowerCase().includes('(g)') || k.toLowerCase().includes('weight') ? '' : 'Rs. '}{Number(v).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}{k.toLowerCase().includes('(g)') || k.toLowerCase().includes('weight') ? ' g' : ''}</span>
                      </div>
                    );
                  })}
                </div>
              ) : typeof value === 'number' && !key.toLowerCase().includes('count') && !key.toLowerCase().includes('item') && !key.toLowerCase().includes('margin') && !key.toLowerCase().includes('weight') && !key.toLowerCase().includes('(g)') && key !== 'total' ? 
                `Rs. ${value.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : 
                (typeof value === 'number' && (key.toLowerCase().includes('weight') || key.toLowerCase().includes('(g)')) ? `${value.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} g` : String(value))}
            </div>
          </div>
        ))}
      </div>

      {/* Charting Area - Only if chart data exists */}
      {data.chart && data.chart.length > 0 && (
        <div className="flex-1 bg-surface border border-gray-800 rounded-xl p-4 sm:p-6 shadow-lg min-h-[320px] sm:min-h-[400px]">
          <ResponsiveContainer width="100%" height="100%">
            {reportType === 'Inventory' ? (
              <BarChart data={data.chart}>
                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                <XAxis dataKey="metal" stroke="#888" />
                <YAxis yAxisId="left" stroke="#888" />
                <YAxis yAxisId="right" orientation="right" stroke="#d4af37" />
                <Tooltip contentStyle={{ backgroundColor: '#111', borderColor: '#333' }} />
                <Bar yAxisId="left" dataKey="count" fill="#8884d8" name="Item Count" />
                <Bar yAxisId="right" dataKey="weight" fill="#d4af37" name="Total Weight (g)" />
              </BarChart>
            ) : (
              <LineChart data={data.chart}>
                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                <XAxis dataKey="date" stroke="#888" tickFormatter={t => t.split('-').slice(1).join('/')} />
                <YAxis stroke="#888" />
                <Tooltip contentStyle={{ backgroundColor: '#111', borderColor: '#333' }} />
                <Line type="monotone" dataKey="amount" stroke="#d4af37" strokeWidth={3} dot={{ fill: '#d4af37', r: 4 }} activeDot={{ r: 8 }} />
              </LineChart>
            )}
          </ResponsiveContainer>
        </div>
      )}

      {/* Grid Fallback for Print */}
      {data.chart && data.chart.length > 0 && (
        <div className="hidden print:block mt-8">
          <table className="w-full text-left text-sm border-collapse border border-gray-800">
            <thead>
              <tr className="bg-gray-100 text-black">
                {Object.keys(data.chart[0]).map(k => (
                  <th key={k} className="p-2 border border-gray-300 uppercase">{k}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.chart.map((row: any, i: number) => (
                <tr key={i}>
                  {Object.values(row).map((v: any, j: number) => (
                    <td key={j} className="p-2 border border-gray-300 text-black">{v}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      </>
      )}

    </div>
  );
}
