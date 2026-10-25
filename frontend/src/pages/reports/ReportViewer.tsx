import { useState, useEffect } from 'react';
import { axiosClient } from '../../api/axiosClient';
import { exportReportToPDF } from '../../utils/exportUtils';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, LineChart, Line } from 'recharts';
import { FileText, Printer, AlertCircle, RotateCcw } from 'lucide-react';
import toast from 'react-hot-toast';

export default function ReportViewer({ reportType }: { reportType: string }) {
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
  }, [reportType, timeFilter]);

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

    </div>
  );
}
