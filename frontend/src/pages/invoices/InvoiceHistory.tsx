import { useState, useEffect } from 'react';
import { axiosClient } from '../../api/axiosClient';
import { generateInvoicePDF, printInvoiceDirect } from '../../utils/invoicePdfUtils';
import {
  Search,
  Filter,
  Eye,
  Download,
  Printer,
  Trash2,
  MessageCircle,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import toast from 'react-hot-toast';

interface Invoice {
  id: number;
  invoice_number: string;
  invoice_date: string;
  customer?: {
    first_name: string;
    last_name?: string;
    phone_number: string;
  };
  grand_total: number;
  status: string;
}

export default function InvoiceHistory() {
  const [tab, setTab] = useState<'sales' | 'purchases' | 'exchanges'>('sales');
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedInvoice, setSelectedInvoice] = useState<any>(null);
  const [showViewModal, setShowViewModal] = useState(false);
  const itemsPerPage = 10;

  useEffect(() => {
    fetchInvoices();
  }, [searchTerm, statusFilter, currentPage, tab]);

  const fetchInvoices = async () => {
    setLoading(true);
    try {
      const skip = (currentPage - 1) * itemsPerPage;
      const params = new URLSearchParams();
      params.append('skip', skip.toString());
      params.append('limit', itemsPerPage.toString());
      
      if (searchTerm) params.append('search', searchTerm);
      if (statusFilter) params.append('status', statusFilter);

      const endpoint = 
        tab === 'sales' ? '/invoices/' :
        tab === 'purchases' ? '/purchases/history' : 
        '/exchanges/';
      const res = await axiosClient.get(`${endpoint}?${params.toString()}`);
      setInvoices(res.data.items || res.data);
    } catch (error: any) {
      console.error('Failed to fetch invoices:', error);
      toast.error(error?.response?.data?.detail || error.message || 'Failed to load invoice history', { id: 'invoice-history-fetch-error' });
    } finally {
      setLoading(false);
    }
  };

  const handleView = async (invoice: Invoice) => {
    try {
      const isExchange = invoice.invoice_number.startsWith('EXC-');
      const endpoint = isExchange ? `/exchanges/${invoice.id}` : `/invoices/${invoice.id}`;
      const res = await axiosClient.get(endpoint);
      setSelectedInvoice(res.data);
      setShowViewModal(true);
    } catch (error) {
      toast.error('Failed to load invoice details');
    }
  };

  const getPdfEndpoint = (invoice: Invoice) => {
    if (invoice.invoice_number.startsWith('PUR-')) return `/purchases/${invoice.id}/pdf-data`;
    if (invoice.invoice_number.startsWith('EXC-')) return `/exchanges/${invoice.id}/pdf-data`;
    return `/invoices/${invoice.id}/pdf-data`;
  };

  const handleDownloadPDF = async (invoice: Invoice) => {
    const toastId = 'pdf-gen';
    try {
      toast.loading('Generating PDF...', { id: toastId });
      const res = await axiosClient.get(getPdfEndpoint(invoice));
      
      // Use the centralized PDF generator which handles html2pdf logic
      await generateInvoicePDF(res.data);
      
      toast.success('PDF downloaded successfully', { id: toastId });
    } catch (error: any) {
      console.error('PDF generation error:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Unknown error';
      toast.error(`Failed to generate PDF: ${errorMessage}`, { id: toastId, duration: 5000 });
    }
  };

  const handlePrint = async (invoice: Invoice) => {
    try {
      const res = await axiosClient.get(getPdfEndpoint(invoice));
      await printInvoiceDirect(res.data);
    } catch (error) {
      toast.error('Failed to print invoice');
    }
  };

  const handleWhatsApp = async (invoice: Invoice) => {
    try {
      const res = await axiosClient.get(getPdfEndpoint(invoice));
      const phone = res.data.customer.phone?.replace(/[^0-9]/g, '');
      if (!phone) {
        toast.error('Customer phone number not available');
        return;
      }
      
      const isExchange = invoice.invoice_number.startsWith('EXC-');
      const isPurchase = invoice.invoice_number.startsWith('PUR-');
      const message = encodeURIComponent(
        `Hello ${res.data.customer.name},\n\nYour ${isPurchase ? 'purchase receipt' : isExchange ? 'exchange invoice' : 'invoice'} ${res.data.invoice.invoice_number} for Rs. ${res.data.totals.grand_total.toLocaleString('en-IN')} has been generated.\n\nThank you for your business!\n\n- ${res.data.company.name}`
      );
      
      window.open(`https://wa.me/91${phone}?text=${message}`, '_blank');
    } catch (error) {
      toast.error('Failed to open WhatsApp');
    }
  };

  const handleDelete = async (invoice: Invoice) => {
    if (!confirm(`Are you sure you want to cancel invoice ${invoice.invoice_number}?`)) {
      return;
    }

    try {
      const isExchange = invoice.invoice_number.startsWith('EXC-');
      const isPurchase = invoice.invoice_number.startsWith('PUR-');
      const endpoint = isPurchase ? `/purchases/${invoice.id}` : isExchange ? `/exchanges/${invoice.id}` : `/invoices/${invoice.id}`;
      await axiosClient.delete(endpoint);
      toast.success('Invoice cancelled successfully');
      fetchInvoices();
    } catch (error) {
      toast.error('Failed to cancel invoice');
    }
  };

  const getStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      'Paid': 'bg-green-500/20 text-green-400',
      'Partial': 'bg-blue-500/20 text-blue-400',
      'Draft': 'bg-yellow-500/20 text-yellow-400',
      'Cancelled': 'bg-red-500/20 text-red-400'
    };
    return colors[status] || 'bg-gray-500/20 text-gray-400';
  };

  return (
    <div className="p-3 sm:p-6 space-y-4 sm:space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-primary">Invoice History</h1>
          <p className="text-xs sm:text-sm text-textMuted mt-0.5 sm:mt-1">View and manage all generated invoices across categories</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-800 overflow-x-auto whitespace-nowrap custom-scrollbar">
        <button 
          onClick={() => { setTab('sales'); setCurrentPage(1); }}
          className={`px-4 sm:px-6 py-2.5 sm:py-3 font-bold uppercase tracking-wider text-xs sm:text-sm shrink-0 transition-colors ${tab === 'sales' ? 'text-primary border-b-2 border-primary' : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/50'}`}
        >
          Sales Invoices
        </button>
        <button 
          onClick={() => { setTab('purchases'); setCurrentPage(1); }}
          className={`px-4 sm:px-6 py-2.5 sm:py-3 font-bold uppercase tracking-wider text-xs sm:text-sm shrink-0 transition-colors ${tab === 'purchases' ? 'text-primary border-b-2 border-primary' : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/50'}`}
        >
          Purchases Invoices
        </button>
        <button 
          onClick={() => { setTab('exchanges'); setCurrentPage(1); }}
          className={`px-4 sm:px-6 py-2.5 sm:py-3 font-bold uppercase tracking-wider text-xs sm:text-sm shrink-0 transition-colors ${tab === 'exchanges' ? 'text-primary border-b-2 border-primary' : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/50'}`}
        >
          Exchange Invoices
        </button>
      </div>

      {/* Filters */}
      <div className="bg-surface p-3 sm:p-4 rounded-xl border border-gray-800 flex flex-col sm:flex-row gap-3 sm:gap-4 items-stretch sm:items-center">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" size={18} />
          <input
            type="text"
            placeholder="Search by invoice number or customer name..."
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              setCurrentPage(1);
            }}
            className="w-full bg-background border border-gray-700 rounded-lg pl-10 pr-4 py-2 text-sm text-textMain focus:outline-none focus:border-primary"
          />
        </div>

        <div className="flex items-center gap-2">
          <Filter size={18} className="text-gray-500 shrink-0" />
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setCurrentPage(1);
            }}
            className="w-full sm:w-auto bg-background border border-gray-700 rounded-lg px-4 py-2 text-sm text-textMain focus:outline-none focus:border-primary"
          >
            <option value="">All Status</option>
            <option value="Paid">Paid</option>
            <option value="Partial">Partial</option>
            <option value="Draft">Draft</option>
            <option value="Cancelled">Cancelled</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="bg-surface rounded-xl border border-gray-800 overflow-hidden">
        <div className="overflow-x-auto custom-scrollbar">
          <table className="w-full min-w-[700px]">
            <thead className="bg-background border-b border-gray-800">
              <tr>
                <th className="text-left p-4 text-xs font-bold text-gray-400 uppercase tracking-wider">Invoice #</th>
                <th className="text-left p-4 text-xs font-bold text-gray-400 uppercase tracking-wider">Date</th>
                <th className="text-left p-4 text-xs font-bold text-gray-400 uppercase tracking-wider">Customer</th>
                <th className="text-left p-4 text-xs font-bold text-gray-400 uppercase tracking-wider">Phone</th>
                <th className="text-right p-4 text-xs font-bold text-gray-400 uppercase tracking-wider">Amount</th>
                <th className="text-center p-4 text-xs font-bold text-gray-400 uppercase tracking-wider">Status</th>
                <th className="text-center p-4 text-xs font-bold text-gray-400 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={7} className="text-center p-8 text-textMuted">
                    Loading invoices...
                  </td>
                </tr>
              ) : invoices.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center p-8 text-textMuted">
                    No invoices found
                  </td>
                </tr>
              ) : (
                invoices.map((invoice) => (
                  <tr key={invoice.id} className="border-b border-gray-800 hover:bg-background/50 transition-colors">
                    <td className="p-4 text-sm font-mono text-primary">{invoice.invoice_number}</td>
                    <td className="p-4 text-sm text-textMain">
                      {new Date(invoice.invoice_date).toLocaleDateString('en-IN')}
                    </td>
                    <td className="p-4 text-sm text-textMain">{invoice.customer ? `${invoice.customer.first_name} ${invoice.customer.last_name || ''}`.trim() : 'Walk-in'}</td>
                    <td className="p-4 text-sm text-textMuted">{invoice.customer?.phone_number || '-'}</td>
                    <td className="p-4 text-sm font-semibold text-right text-textMain">
                      Rs. {Number(invoice.grand_total).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                    </td>
                    <td className="p-4">
                      <span className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${getStatusBadge(invoice.status)}`}>
                        {invoice.status}
                      </span>
                    </td>
                    <td className="p-4">
                      <div className="flex justify-center gap-2">
                        <button
                          onClick={() => handleView(invoice)}
                          className="p-2 hover:bg-blue-500/20 rounded text-blue-400 transition-colors"
                          title="View Details"
                        >
                          <Eye size={16} />
                        </button>
                        <button
                          onClick={() => handleDownloadPDF(invoice)}
                          className="p-2 hover:bg-green-500/20 rounded text-green-400 transition-colors"
                          title="Download PDF"
                        >
                          <Download size={16} />
                        </button>
                        <button
                          onClick={() => handlePrint(invoice)}
                          className="p-2 hover:bg-purple-500/20 rounded text-purple-400 transition-colors"
                          title="Print"
                        >
                          <Printer size={16} />
                        </button>
                        <button
                          onClick={() => handleWhatsApp(invoice)}
                          className="p-2 hover:bg-green-500/20 rounded text-green-400 transition-colors"
                          title="Share on WhatsApp"
                        >
                          <MessageCircle size={16} />
                        </button>
                        {invoice.status !== 'Cancelled' && tab === 'sales' && (
                          <button
                            onClick={() => handleDelete(invoice)}
                            className="p-2 hover:bg-red-500/20 rounded text-red-400 transition-colors"
                            title="Cancel Invoice"
                          >
                            <Trash2 size={16} />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {invoices.length > 0 && (
          <div className="flex flex-col sm:flex-row justify-between items-center gap-3 p-3 sm:p-4 border-t border-gray-800">
            <div className="text-xs sm:text-sm text-textMuted text-center sm:text-left">
              Showing {((currentPage - 1) * itemsPerPage) + 1} to {Math.min(currentPage * itemsPerPage, ((currentPage - 1) * itemsPerPage) + invoices.length)} invoices
            </div>
            <div className="flex gap-2 w-full sm:w-auto justify-center">
              <button
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="flex-1 sm:flex-initial px-3 sm:px-4 py-2 bg-background border border-gray-700 rounded-lg text-xs sm:text-sm text-textMain hover:border-primary disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
              >
                <ChevronLeft size={16} /> Previous
              </button>
              <button
                onClick={() => setCurrentPage(p => p + 1)}
                disabled={invoices.length < itemsPerPage}
                className="flex-1 sm:flex-initial px-3 sm:px-4 py-2 bg-background border border-gray-700 rounded-lg text-xs sm:text-sm text-textMain hover:border-primary disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
              >
                Next <ChevronRight size={16} />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* View Modal */}
      {showViewModal && selectedInvoice && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
          <div className="bg-surface rounded-xl border border-gray-800 max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-800 flex justify-between items-center sticky top-0 bg-surface">
              <div>
                <h2 className="text-xl font-bold text-primary">Invoice Details</h2>
                <p className="text-sm text-textMuted">{selectedInvoice.invoice_number}</p>
              </div>
              <button
                onClick={() => setShowViewModal(false)}
                className="text-gray-400 hover:text-white transition-colors"
              >
                ✕
              </button>
            </div>
            
            <div className="p-6 space-y-6">
              {/* Customer Info */}
              <div className="bg-background rounded-lg p-4">
                <h3 className="text-sm font-bold text-gray-400 uppercase mb-3">Customer Information</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-xs text-gray-500">Name</p>
                    <p className="text-sm text-textMain">{selectedInvoice.customer ? `${selectedInvoice.customer.first_name} ${selectedInvoice.customer.last_name || ''}`.trim() : 'Walk-in'}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Phone</p>
                    <p className="text-sm text-textMain">{selectedInvoice.customer?.phone_number || '-'}</p>
                  </div>
                </div>
              </div>

              {/* Items */}
              <div className="bg-background rounded-lg p-4">
                <h3 className="text-sm font-bold text-gray-400 uppercase mb-3">Items</h3>
                <div className="space-y-2">
                  {selectedInvoice.items?.map((item: any, i: number) => (
                    <div key={i} className="flex justify-between items-center p-3 bg-surface rounded border border-gray-800">
                      <div>
                        <p className="text-sm font-semibold text-textMain">{item.item_name}</p>
                        <p className="text-xs text-textMuted">{item.item_type}</p>
                      </div>
                      <p className="text-sm font-bold text-primary">
                        Rs. {item.final_price.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Totals */}
              <div className="bg-background rounded-lg p-4">
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-textMuted">Subtotal</span>
                    <span className="text-textMain">Rs. {selectedInvoice.subtotal.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-textMuted">Tax (GST)</span>
                    <span className="text-textMain">Rs. {selectedInvoice.tax_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
                  </div>
                  {selectedInvoice.discount_amount > 0 && (
                    <div className="flex justify-between text-sm">
                      <span className="text-textMuted">Discount</span>
                      <span className="text-textMain">- Rs. {Number(selectedInvoice.discount_amount).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
                    </div>
                  )}
                  <div className="flex justify-between font-bold text-lg mt-4 pt-4 border-t border-gray-800">
                    <span>Grand Total</span>
                    <span className="text-primary">Rs. {Number(selectedInvoice.grand_total).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
