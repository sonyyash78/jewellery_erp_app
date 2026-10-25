import { useState, useEffect } from 'react';
import { ArrowLeft, Download, FileText, RefreshCcw, Plus, Printer, Calendar, X } from 'lucide-react';
import { axiosClient } from '../../api/axiosClient';
import toast from 'react-hot-toast';
import * as XLSX from 'xlsx';
import { generateInvoicePDF, generatePaymentReceiptPDF, generateLedgerStatementPDF } from '../../utils/invoicePdfUtils';
import RecordPaymentModal from './RecordPaymentModal';

export default function CustomerProfile({ id, onBack }: { id: number, onBack: () => void }) {
  const [customer, setCustomer] = useState<any>(null);
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [isPaymentModalOpen, setIsPaymentModalOpen] = useState(false);
  const [generatingStatement, setGeneratingStatement] = useState(false);

  // Date Filter States
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [preset, setPreset] = useState<'all' | 'this_month' | 'last_month' | 'last_30_days' | 'custom'>('all');

  const fetchData = async () => {
    try {
      const [custRes, billsRes] = await Promise.all([
        axiosClient.get(`/customers/${id}`),
        axiosClient.get(`/customers/${id}/bills`)
      ]);
      setCustomer(custRes.data);
      setData(billsRes.data);
    } catch (e) {
      toast.error('Failed to fetch customer profile');
      onBack();
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [id]);

  const handlePresetChange = (p: 'all' | 'this_month' | 'last_month' | 'last_30_days' | 'custom') => {
    setPreset(p);
    const now = new Date();
    if (p === 'all') {
      setStartDate('');
      setEndDate('');
    } else if (p === 'this_month') {
      const firstDay = new Date(now.getFullYear(), now.getMonth(), 1);
      setStartDate(firstDay.toISOString().split('T')[0]);
      setEndDate(now.toISOString().split('T')[0]);
    } else if (p === 'last_month') {
      const firstDay = new Date(now.getFullYear(), now.getMonth() - 1, 1);
      const lastDay = new Date(now.getFullYear(), now.getMonth(), 0);
      setStartDate(firstDay.toISOString().split('T')[0]);
      setEndDate(lastDay.toISOString().split('T')[0]);
    } else if (p === 'last_30_days') {
      const past = new Date();
      past.setDate(past.getDate() - 30);
      setStartDate(past.toISOString().split('T')[0]);
      setEndDate(now.toISOString().split('T')[0]);
    }
  };

  const filteredBills = (data?.bills || []).filter((row: any) => {
    if (!startDate && !endDate) return true;
    const rowDate = new Date(row.date);
    if (isNaN(rowDate.getTime())) return true;
    if (startDate) {
      const s = new Date(startDate);
      s.setHours(0, 0, 0, 0);
      if (rowDate < s) return false;
    }
    if (endDate) {
      const e = new Date(endDate);
      e.setHours(23, 59, 59, 999);
      if (rowDate > e) return false;
    }
    return true;
  });

  const handleDownloadPDF = async (row: any) => {
    if (row.bill_no && row.bill_no !== '-') {
      try {
        const res = await axiosClient.get(`/invoices/pdf-by-voucher/${row.bill_no}`);
        await generateInvoicePDF(res.data);
      } catch (e: any) {
        try {
          await generatePaymentReceiptPDF(row, customer);
        } catch {
          toast.error('Failed to download PDF');
        }
      }
    } else {
      try {
        await generatePaymentReceiptPDF(row, customer);
      } catch {
        toast.error('Failed to download PDF');
      }
    }
  };

  const handlePrintStatement = async () => {
    if (!customer || !filteredBills) return;
    setGeneratingStatement(true);
    try {
      let dateRangeLabel = 'All Transactions';
      if (startDate && endDate) {
        dateRangeLabel = `${new Date(startDate).toLocaleDateString('en-GB')} to ${new Date(endDate).toLocaleDateString('en-GB')}`;
      } else if (startDate) {
        dateRangeLabel = `From ${new Date(startDate).toLocaleDateString('en-GB')}`;
      } else if (endDate) {
        dateRangeLabel = `Up to ${new Date(endDate).toLocaleDateString('en-GB')}`;
      }

      await generateLedgerStatementPDF({
        entity: customer,
        isSupplier: false,
        bills: filteredBills,
        dateRangeLabel,
        balances: {
          outstanding_balance: data?.outstanding_balance,
          fine_gold_balance: data?.fine_gold_balance,
          fine_silver_balance: data?.fine_silver_balance,
          current_gold_rate: data?.current_gold_rate,
          current_silver_rate: data?.current_silver_rate
        }
      });
      toast.success('Statement downloaded successfully!');
    } catch {
      toast.error('Failed to generate statement');
    } finally {
      setGeneratingStatement(false);
    }
  };

  const handleExportExcel = () => {
    if (!filteredBills || filteredBills.length === 0) {
      toast.error('No ledger entries to export');
      return;
    }
    const ws = XLSX.utils.json_to_sheet(filteredBills.map((row: any) => ({
      Date: new Date(row.date).toLocaleString(),
      Type: row.type,
      RefNo: row.bill_no,
      Summary: row.summary,
      GoldChange: row.gold_change,
      SilverChange: row.silver_change,
      Debit: row.debit,
      Credit: row.credit,
      Balance: row.balance
    })));
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Ledger");
    const dateSuffix = startDate || endDate ? `_${startDate || 'start'}_to_${endDate || 'now'}` : '';
    XLSX.writeFile(wb, `Customer_${customer.first_name}_Statement${dateSuffix}.xlsx`);
  };

  if (loading || !customer || !data) return <div className="p-8 text-primary font-bold">Loading...</div>;

  return (
    <div className="h-auto lg:h-[calc(100vh-6rem)] flex flex-col space-y-4 overflow-y-auto lg:overflow-hidden">
      
      {/* Header Panel */}
      <div className="bg-surface border border-gray-800 rounded-xl p-4 sm:p-6 shadow-lg flex flex-col lg:flex-row items-stretch lg:items-start justify-between gap-4">
        <div className="flex gap-3 sm:gap-4 items-start">
          <button onClick={onBack} className="text-gray-400 hover:text-white transition-colors h-fit mt-1"><ArrowLeft size={24} /></button>
          <div className="min-w-0">
            <h1 className="text-xl sm:text-2xl font-bold text-textMain uppercase tracking-widest truncate">{customer.first_name} {customer.last_name || ''}</h1>
            <div className="text-xs sm:text-sm text-textMuted mt-1 grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-1">
              <span>📱 {customer.phone_number}</span>
              <span>🏢 GST: {customer.gst_number || 'N/A'}</span>
              <span>💳 PAN: {customer.pan_card || 'N/A'}</span>
              <span>🆔 Aadhar: {customer.aadhar_card || 'N/A'}</span>
            </div>
          </div>
        </div>
        
        <div className="flex flex-col items-stretch lg:items-end gap-2">
          <div className="flex flex-wrap sm:flex-nowrap gap-3 sm:gap-6 items-center sm:items-end justify-between sm:justify-end bg-black/30 p-3 sm:p-4 rounded-lg border border-gray-800/50">
            <div>
              <div className="text-[10px] font-bold text-yellow-500/80 uppercase tracking-wider mb-1">Fine Gold</div>
              <div className="text-lg sm:text-xl font-bold font-mono text-yellow-400">{Number(data.fine_gold_balance || 0).toFixed(3)} g</div>
              <div className="text-[10px] text-gray-500 mt-0.5 sm:mt-1">@ ₹{data.current_gold_rate}/g</div>
            </div>
            <div className="hidden sm:block w-px h-10 bg-gray-800"></div>
            <div>
              <div className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1">Fine Silver</div>
              <div className="text-lg sm:text-xl font-bold font-mono text-gray-300">{Number(data.fine_silver_balance || 0).toFixed(3)} g</div>
              <div className="text-[10px] text-gray-500 mt-0.5 sm:mt-1">@ ₹{data.current_silver_rate}/g</div>
            </div>
            <div className="hidden sm:block w-px h-10 bg-gray-800"></div>
            <div className="text-right">
              <div className="text-[10px] font-bold text-textMuted uppercase tracking-wider mb-1">Outstanding ₹</div>
              <div className={`text-2xl sm:text-3xl font-bold font-mono ${data.outstanding_balance > 0 ? 'text-red-400' : 'text-green-400'}`}>
                ₹ {Math.abs(data.outstanding_balance).toLocaleString()} {data.outstanding_balance > 0 ? '(Dr)' : '(Cr)'}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Bills Table */}
      <div className="flex-1 bg-surface border border-gray-800 rounded-xl shadow-lg flex flex-col overflow-hidden min-h-[350px]">
        {/* Table Top Toolbar */}
        <div className="p-3 sm:p-4 border-b border-gray-800 flex flex-col lg:flex-row justify-between items-start lg:items-center gap-3 bg-black/20">
          <div className="flex items-center gap-2">
            <h2 className="text-base sm:text-lg font-bold text-primary uppercase tracking-widest flex items-center gap-2">
              <FileText size={18} /> Customer Ledger
            </h2>
            <span className="text-xs bg-gray-800 text-gray-400 px-2 py-0.5 rounded-full font-mono font-semibold">
              {filteredBills.length} {filteredBills.length === 1 ? 'bill' : 'bills'}
            </span>
          </div>

          <div className="flex flex-wrap gap-2 sm:gap-2.5 w-full lg:w-auto">
            <button 
              onClick={() => setIsPaymentModalOpen(true)} 
              className="flex-1 sm:flex-initial bg-primary text-black px-3 sm:px-4 py-2 rounded font-bold text-xs sm:text-sm hover:bg-primary/90 transition-colors flex items-center justify-center gap-1.5 shadow-[0_0_12px_rgba(212,175,55,0.2)]"
            >
              <Plus size={16} /> Record Settlement
            </button>
            <button 
              onClick={handlePrintStatement} 
              disabled={generatingStatement}
              className="flex-1 sm:flex-initial bg-primary/20 text-primary border border-primary/40 px-3 sm:px-4 py-2 rounded font-bold text-xs sm:text-sm hover:bg-primary/30 transition-colors flex items-center justify-center gap-1.5 shadow-[0_0_10px_rgba(212,175,55,0.1)]"
              title="Print or Download Full Ledger Statement PDF"
            >
              <Printer size={16} /> {generatingStatement ? 'Generating...' : 'Statement'}
            </button>
            <button 
              onClick={handleExportExcel} 
              className="flex-1 sm:flex-initial bg-background text-white border border-gray-700 px-3 sm:px-4 py-2 rounded font-bold text-xs sm:text-sm hover:border-gray-500 transition-colors flex items-center justify-center gap-1.5"
              title="Export Current Filtered Ledger to Excel"
            >
              <Download size={16} /> Export Excel
            </button>
          </div>
        </div>

        {/* Date Filter Bar */}
        <div className="px-3 sm:px-4 py-2.5 bg-gray-900/40 border-b border-gray-800 flex flex-wrap items-center justify-between gap-2.5 text-xs">
          {/* Quick Preset Buttons */}
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mr-1 flex items-center gap-1">
              <Calendar size={12} /> Filter:
            </span>
            <button
              onClick={() => handlePresetChange('all')}
              className={`px-2.5 py-1 rounded text-xs font-semibold transition-colors ${preset === 'all' ? 'bg-primary text-black font-bold' : 'bg-gray-800 text-gray-300 hover:bg-gray-700'}`}
            >
              All Time
            </button>
            <button
              onClick={() => handlePresetChange('this_month')}
              className={`px-2.5 py-1 rounded text-xs font-semibold transition-colors ${preset === 'this_month' ? 'bg-primary text-black font-bold' : 'bg-gray-800 text-gray-300 hover:bg-gray-700'}`}
            >
              This Month
            </button>
            <button
              onClick={() => handlePresetChange('last_month')}
              className={`px-2.5 py-1 rounded text-xs font-semibold transition-colors ${preset === 'last_month' ? 'bg-primary text-black font-bold' : 'bg-gray-800 text-gray-300 hover:bg-gray-700'}`}
            >
              Last Month
            </button>
            <button
              onClick={() => handlePresetChange('last_30_days')}
              className={`px-2.5 py-1 rounded text-xs font-semibold transition-colors ${preset === 'last_30_days' ? 'bg-primary text-black font-bold' : 'bg-gray-800 text-gray-300 hover:bg-gray-700'}`}
            >
              Last 30 Days
            </button>
          </div>

          {/* Custom Date Pickers */}
          <div className="flex flex-wrap items-center gap-2 ml-auto">
            <div className="flex items-center gap-1">
              <span className="text-gray-500 text-[11px]">From:</span>
              <input
                type="date"
                value={startDate}
                onChange={(e) => {
                  setStartDate(e.target.value);
                  setPreset('custom');
                }}
                className="bg-background border border-gray-700 rounded px-2 py-0.5 text-xs text-white [color-scheme:dark] outline-none focus:border-primary"
              />
            </div>
            <div className="flex items-center gap-1">
              <span className="text-gray-500 text-[11px]">To:</span>
              <input
                type="date"
                value={endDate}
                onChange={(e) => {
                  setEndDate(e.target.value);
                  setPreset('custom');
                }}
                className="bg-background border border-gray-700 rounded px-2 py-0.5 text-xs text-white [color-scheme:dark] outline-none focus:border-primary"
              />
            </div>
            {(startDate || endDate || preset !== 'all') && (
              <button
                onClick={() => handlePresetChange('all')}
                className="text-gray-400 hover:text-red-400 p-1 rounded hover:bg-gray-800 transition-colors"
                title="Clear date filter"
              >
                <X size={14} />
              </button>
            )}
          </div>
        </div>

        <RecordPaymentModal
          isOpen={isPaymentModalOpen}
          onClose={() => setIsPaymentModalOpen(false)}
          onSuccess={fetchData}
          entityId={id}
          isSupplier={false}
        />

        <div className="flex-1 overflow-x-auto custom-scrollbar">
          <table className="w-full text-left text-sm text-textMuted min-w-[750px]">
            <thead className="bg-background sticky top-0 border-b border-gray-800 z-10">
              <tr>
                <th className="py-3 px-4 font-bold uppercase tracking-wider text-xs">Date</th>
                <th className="py-3 px-4 font-bold uppercase tracking-wider text-xs">Type</th>
                <th className="py-3 px-4 font-bold uppercase tracking-wider text-xs">Ref No</th>
                <th className="py-3 px-4 font-bold uppercase tracking-wider text-xs">Details / Bill</th>
                <th className="py-3 px-4 font-bold uppercase tracking-wider text-xs text-right text-yellow-500">Gold (g)</th>
                <th className="py-3 px-4 font-bold uppercase tracking-wider text-xs text-right text-gray-300">Silver (g)</th>
                <th className="py-3 px-4 font-bold uppercase tracking-wider text-xs text-right text-red-400">Debit (₹)</th>
                <th className="py-3 px-4 font-bold uppercase tracking-wider text-xs text-right text-green-400">Credit (₹)</th>
                <th className="py-3 px-4 font-bold uppercase tracking-wider text-xs text-right text-primary">Balance (₹)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/50">
              {filteredBills.map((row: any) => (
                <tr key={row.id} className="hover:bg-gray-800/30 transition-colors">
                  <td className="py-3 px-4 whitespace-nowrap text-xs">{new Date(row.date).toLocaleString()}</td>
                  <td className="py-3 px-4">
                    <span className={`px-2 py-1 rounded text-[10px] font-bold uppercase tracking-wider ${row.type === 'Invoice' ? 'bg-blue-900/30 text-blue-400' : 'bg-purple-900/30 text-purple-400'}`}>
                      {row.type}
                    </span>
                  </td>
                  <td className="py-3 px-4 font-mono text-gray-300">{row.bill_no}</td>
                  <td className="py-3 px-4 text-xs">
                    <div className="flex items-center gap-2">
                      <span className="truncate max-w-[200px]" title={row.summary}>{row.summary}</span>
                      <button 
                        onClick={() => handleDownloadPDF(row)}
                        className="bg-primary/20 text-primary hover:bg-primary hover:text-black px-2 py-1 rounded transition-colors flex items-center gap-1 ml-auto"
                        title="Download PDF"
                      >
                        <Download size={14} /> <span className="hidden sm:inline">PDF</span>
                      </button>
                    </div>
                  </td>
                  
                  <td className="py-3 px-4 text-right font-mono text-yellow-500 bg-yellow-900/5">
                    {Number(row.gold_change) !== 0 ? (Number(row.gold_change) > 0 ? '+' : '') + Number(row.gold_change).toFixed(3) : '-'}
                  </td>
                  <td className="py-3 px-4 text-right font-mono text-gray-400 bg-gray-800/20">
                    {Number(row.silver_change) !== 0 ? (Number(row.silver_change) > 0 ? '+' : '') + Number(row.silver_change).toFixed(3) : '-'}
                  </td>
                  <td className="py-3 px-4 text-right font-mono font-bold text-red-400">
                    {Number(row.debit) > 0 ? Number(row.debit).toLocaleString() : '-'}
                  </td>
                  <td className="py-3 px-4 text-right font-mono font-bold text-green-400">
                    {Number(row.credit) > 0 ? Number(row.credit).toLocaleString() : '-'}
                  </td>
                  <td className="py-3 px-4 text-right font-mono font-bold text-primary">
                    {Number(row.balance).toLocaleString()} {Number(row.balance) > 0 ? '(Dr)' : (Number(row.balance) < 0 ? '(Cr)' : '')}
                  </td>
                </tr>
              ))}
              {filteredBills.length === 0 && (
                <tr>
                  <td colSpan={9} className="py-12 text-center text-gray-500 italic">
                    <div className="flex flex-col items-center gap-2">
                      <RefreshCcw size={24} className="opacity-20" />
                      <p>No ledger entries found for the selected period.</p>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
            {filteredBills.length > 0 && (
              <tfoot className="bg-gray-900/90 border-t-2 border-gray-800 sticky bottom-0 z-10 text-xs font-bold font-mono">
                <tr>
                  <td colSpan={4} className="py-2.5 px-4 text-gray-300 uppercase font-sans">
                    Period Total ({filteredBills.length} bills):
                  </td>
                  <td className="py-2.5 px-4 text-right text-yellow-400">
                    {(() => {
                      const sum = filteredBills.reduce((acc: number, r: any) => acc + (Number(r.gold_change) || 0), 0);
                      return sum !== 0 ? (sum > 0 ? '+' : '') + sum.toFixed(3) + 'g' : '-';
                    })()}
                  </td>
                  <td className="py-2.5 px-4 text-right text-gray-300">
                    {(() => {
                      const sum = filteredBills.reduce((acc: number, r: any) => acc + (Number(r.silver_change) || 0), 0);
                      return sum !== 0 ? (sum > 0 ? '+' : '') + sum.toFixed(3) + 'g' : '-';
                    })()}
                  </td>
                  <td className="py-2.5 px-4 text-right text-red-400">
                    ₹{filteredBills.reduce((acc: number, r: any) => acc + (Number(r.debit) || 0), 0).toLocaleString()}
                  </td>
                  <td className="py-2.5 px-4 text-right text-green-400">
                    ₹{filteredBills.reduce((acc: number, r: any) => acc + (Number(r.credit) || 0), 0).toLocaleString()}
                  </td>
                  <td className="py-2.5 px-4 text-right text-primary">
                    ₹{Math.abs(Number(data?.outstanding_balance || 0)).toLocaleString()} {Number(data?.outstanding_balance || 0) > 0 ? '(Dr)' : (Number(data?.outstanding_balance || 0) < 0 ? '(Cr)' : '')}
                  </td>
                </tr>
              </tfoot>
            )}
          </table>
        </div>
      </div>
    </div>
  );
}
