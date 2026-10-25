import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { 
  ShieldCheck, 
  Search, 
  Calendar, 
  CheckCircle2, 
  XCircle, 
  Loader2, 
  Award,
  Phone,
  MapPin,
  ArrowLeft,
  Sparkles,
  AlertCircle,
  QrCode,
  Lock
} from 'lucide-react';

export default function VerifyInvoice() {
  const { invoiceNumber } = useParams<{ invoiceNumber?: string }>();
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState(invoiceNumber || '');
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchVerification = async (voucher: string) => {
    if (!voucher.trim()) return;
    setLoading(true);
    setError(null);
    setData(null);
    try {
      const res = await axios.get(`/api/v1/verification/verify/${encodeURIComponent(voucher.trim())}`);
      setData(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || `No authentic record found for voucher "${voucher}".`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (invoiceNumber) {
      setSearchQuery(invoiceNumber);
      fetchVerification(invoiceNumber);
    }
  }, [invoiceNumber]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/verify/${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-gray-100 flex flex-col items-center py-10 px-4 sm:px-6 lg:px-8">
      {/* Top Banner */}
      <div className="w-full max-w-4xl flex items-center justify-between mb-8 pb-4 border-b border-gray-800">
        <Link to="/login" className="flex items-center gap-2 text-sm text-yellow-500 hover:text-yellow-400 transition">
          <ArrowLeft className="w-4 h-4" /> Back to Portal
        </Link>
        <div className="flex items-center gap-2 text-xs text-gray-400 bg-gray-900 border border-gray-800 px-3 py-1.5 rounded-full">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <span>Official Public Verification Gateway</span>
        </div>
      </div>

      {/* Header */}
      <div className="text-center max-w-2xl mb-8">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-tr from-yellow-600/30 to-amber-500/10 border border-yellow-500/30 text-yellow-400 mb-4 shadow-lg shadow-yellow-500/10">
          <Award className="w-8 h-8" />
        </div>
        <h1 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
          Certificate of <span className="text-yellow-500">Authenticity</span>
        </h1>
        <p className="mt-2 text-sm text-gray-400">
          Verify genuine hallmarked jewellery bills, purchase memos, and exchange vouchers issued by verified jewellers.
        </p>
      </div>

      {/* Search Input Bar */}
      <div className="w-full max-w-xl mb-10">
        <form onSubmit={handleSearch} className="relative flex items-center">
          <input
            type="text"
            placeholder="Enter Bill / Voucher No. (e.g. INV-20260924-0001 or EXC-1)"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-[#141414] border border-gray-700 rounded-xl pl-12 pr-28 py-3.5 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-yellow-500 focus:ring-1 focus:ring-yellow-500 transition shadow-inner"
          />
          <Search className="absolute left-4 w-5 h-5 text-gray-400" />
          <button
            type="submit"
            disabled={loading || !searchQuery.trim()}
            className="absolute right-2 px-5 py-2 bg-yellow-500 hover:bg-yellow-400 text-black font-semibold text-xs rounded-lg transition disabled:opacity-50"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Verify'}
          </button>
        </form>
      </div>

      {/* Loading state */}
      {loading && (
        <div className="flex flex-col items-center justify-center py-16 text-gray-400">
          <Loader2 className="w-10 h-10 animate-spin text-yellow-500 mb-3" />
          <p className="text-sm">Verifying digital certificate with registry...</p>
        </div>
      )}

      {/* Error / Not Found */}
      {error && !loading && (
        <div className="w-full max-w-2xl bg-red-950/40 border border-red-800/60 rounded-2xl p-6 text-center shadow-xl">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-red-900/40 text-red-400 mb-3">
            <XCircle className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-red-300 mb-1">Verification Failed</h3>
          <p className="text-sm text-red-200/80 mb-4">{error}</p>
          <p className="text-xs text-gray-400">
            Please make sure the voucher number is correct as printed on your bill receipt.
          </p>
        </div>
      )}

      {/* Legacy Registry Notice Card (Minimal Safe Verification) */}
      {data && !loading && (data.status === 'LEGACY_VERIFICATION_REQUIRED' || data.requires_secure_token) && (
        <div className="w-full max-w-3xl bg-[#141414] border-2 border-amber-500/40 rounded-2xl shadow-2xl overflow-hidden relative">
          <div className="h-2 bg-gradient-to-r from-amber-600 via-amber-400 to-amber-600" />

          {/* Verification Badge Header */}
          <div className="bg-amber-950/40 border-b border-amber-800/40 px-6 py-4 flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <ShieldCheck className="w-6 h-6 text-amber-400" />
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-amber-400">Registry Status</span>
                <h4 className="text-sm font-semibold text-white">Document Confirmed in Official Store Registry</h4>
              </div>
            </div>
            <div className="flex items-center gap-2 bg-black/40 border border-amber-500/30 px-3 py-1 rounded-full text-xs text-amber-300">
              <Lock className="w-3.5 h-3.5 text-amber-400" />
              <span>Legacy Verification</span>
            </div>
          </div>

          <div className="p-6 sm:p-8 space-y-6">
            {/* Store & Voucher Header */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center pb-6 border-b border-gray-800 gap-4">
              <div>
                <h2 className="text-2xl font-black text-amber-400 tracking-wide uppercase">
                  {data.company?.name || 'JEWELLERY STORE'}
                </h2>
                <p className="text-xs text-gray-400 mt-1 flex items-center gap-1.5">
                  <MapPin className="w-3.5 h-3.5 text-amber-400/80" />
                  {data.company?.address || 'Certified Store'}
                </p>
                {data.company?.phone && (
                  <p className="text-xs text-gray-400 mt-0.5 flex items-center gap-1.5">
                    <Phone className="w-3.5 h-3.5 text-amber-400/80" />
                    +91 {data.company.phone}
                  </p>
                )}
                {data.company?.gstin && (
                  <p className="text-xs text-gray-300 mt-1 font-mono">
                    <span className="text-gray-500 font-normal">GSTIN:</span> {data.company.gstin}
                  </p>
                )}
              </div>

              <div className="bg-[#1c1c1c] border border-gray-800 rounded-xl p-4 sm:text-right min-w-[200px]">
                <span className="text-[10px] uppercase font-bold text-amber-400 tracking-wider">Voucher / Bill No.</span>
                <p className="text-base font-mono font-bold text-white mt-0.5">{data.voucher_number}</p>
                <div className="mt-2 flex sm:justify-end items-center gap-1 text-xs text-gray-400">
                  <Calendar className="w-3.5 h-3.5 text-gray-500" />
                  <span>{data.document_date || 'N/A'}</span>
                </div>
              </div>
            </div>

            {/* Privacy & Anti-Scraping Security Callout */}
            <div className="bg-amber-950/20 border border-amber-800/40 rounded-xl p-5 space-y-3">
              <div className="flex items-center gap-2.5 text-amber-300">
                <AlertCircle className="w-5 h-5 text-amber-400 flex-shrink-0" />
                <h4 className="text-sm font-semibold">Security & Customer Privacy Protection</h4>
              </div>
              <p className="text-xs text-gray-300 leading-relaxed">
                This document reference was queried without an unguessable digital verification token. To safeguard customer confidentiality and prevent automated public data harvesting, detailed item-level hallmark weights and financial values are restricted from plain voucher queries.
              </p>
              <div className="pt-2 border-t border-amber-900/30 grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs text-gray-300">
                <div className="flex items-start gap-2 bg-black/30 p-3 rounded-lg border border-gray-800">
                  <QrCode className="w-4 h-4 text-amber-400 mt-0.5 flex-shrink-0" />
                  <div>
                    <span className="font-semibold text-white block">Scan Official QR Code</span>
                    <span className="text-gray-400 text-[11px]">Scan the secure QR code printed directly on the physical bill invoice for instant hallmark certificate verification.</span>
                  </div>
                </div>
                <div className="flex items-start gap-2 bg-black/30 p-3 rounded-lg border border-gray-800">
                  <ShieldCheck className="w-4 h-4 text-emerald-400 mt-0.5 flex-shrink-0" />
                  <div>
                    <span className="font-semibold text-white block">In-Store Verification</span>
                    <span className="text-gray-400 text-[11px]">Present this bill memo at any authorized store branch for full manual verification and hallmark re-certification.</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Trust Footer */}
            <div className="pt-4 border-t border-gray-800 flex flex-wrap items-center justify-between text-[11px] text-gray-500 gap-2">
              <div className="flex items-center gap-2">
                <Award className="w-4 h-4 text-amber-400" />
                <span>BIS 916 & 925 Hallmark Certified Guarantee • Saideep Jewellers</span>
              </div>
              <span className="font-mono">Reference: {data.voucher_number}</span>
            </div>
          </div>
        </div>
      )}

      {/* Verified Certificate Card (Token-Authenticated) */}
      {data && !loading && data.status !== 'LEGACY_VERIFICATION_REQUIRED' && !data.requires_secure_token && (
        <div className="w-full max-w-3xl bg-[#141414] border-2 border-yellow-500/40 rounded-2xl shadow-2xl overflow-hidden relative">
          {/* Top Gold Accent Ribbon */}
          <div className="h-2 bg-gradient-to-r from-yellow-600 via-yellow-400 to-yellow-600" />

          {/* Verification Badge Header */}
          <div className="bg-emerald-950/40 border-b border-emerald-800/40 px-6 py-4 flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <CheckCircle2 className="w-6 h-6 text-emerald-400" />
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-emerald-400">Official Status</span>
                <h4 className="text-sm font-semibold text-white">Genuine & Verified Authentic Record</h4>
              </div>
            </div>
            <div className="flex items-center gap-2 bg-black/40 border border-emerald-500/30 px-3 py-1 rounded-full text-xs text-emerald-300">
              <Sparkles className="w-3.5 h-3.5 text-yellow-400" />
              <span>Registry Verified</span>
            </div>
          </div>

          {/* Body Content */}
          <div className="p-6 sm:p-8 space-y-6">
            {/* Store & Voucher Header */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center pb-6 border-b border-gray-800 gap-4">
              <div>
                <h2 className="text-2xl font-black text-yellow-500 tracking-wide uppercase">
                  {data.company?.name || 'JEWELLERY STORE'}
                </h2>
                <p className="text-xs text-gray-400 mt-1 flex items-center gap-1.5">
                  <MapPin className="w-3.5 h-3.5 text-yellow-500/80" />
                  {data.company?.address || 'Certified Store'}
                </p>
                {data.company?.phone && (
                  <p className="text-xs text-gray-400 mt-0.5 flex items-center gap-1.5">
                    <Phone className="w-3.5 h-3.5 text-yellow-500/80" />
                    +91 {data.company.phone}
                  </p>
                )}
                {data.company?.gstin && (
                  <p className="text-xs text-gray-300 mt-1 font-mono">
                    <span className="text-gray-500 font-normal">GSTIN:</span> {data.company.gstin}
                  </p>
                )}
              </div>

              <div className="bg-[#1c1c1c] border border-gray-800 rounded-xl p-4 sm:text-right min-w-[200px]">
                <span className="text-[10px] uppercase font-bold text-yellow-500 tracking-wider">Voucher / Bill No.</span>
                <p className="text-base font-mono font-bold text-white mt-0.5">{data.voucher_number}</p>
                <div className="mt-2 flex sm:justify-end items-center gap-1 text-xs text-gray-400">
                  <Calendar className="w-3.5 h-3.5 text-gray-500" />
                  <span>{data.document_date || data.invoice?.invoice_date || 'N/A'}</span>
                </div>
              </div>
            </div>

            {/* Document Verification Overview */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 bg-[#181818] p-4 rounded-xl border border-gray-800">
              <div>
                <span className="text-xs text-gray-500 block">Verification Integrity</span>
                <p className="text-sm font-semibold text-emerald-400 mt-0.5">Verified Hallmark Authenticity</p>
                <p className="text-xs text-gray-400 mt-0.5">Official ERP Store Registry Record</p>
              </div>
              <div>
                <span className="text-xs text-gray-500 block">Settlement / Bill Type</span>
                <p className="text-sm font-semibold text-yellow-400 mt-0.5">
                  {data.bill_type || data.invoice?.bill_type || data.invoice?.settlement_type || 'Standard Bill'}
                </p>
              </div>
            </div>

            {/* Itemized Summary */}
            <div>
              <h4 className="text-xs uppercase font-bold text-gray-400 tracking-wider mb-3">Item Details</h4>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-gray-300">
                  <thead className="bg-[#1e1e1e] text-gray-400 uppercase font-semibold">
                    <tr>
                      <th className="p-2.5 rounded-l-lg">Item</th>
                      <th className="p-2.5">Metal</th>
                      <th className="p-2.5 text-right">Net Wt. (g)</th>
                      <th className="p-2.5 text-right rounded-r-lg">Purity / Touch</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-800/60">
                    {data.items?.map((item: any, idx: number) => (
                      <tr key={idx} className="hover:bg-white/[0.02]">
                        <td className="p-2.5 font-medium text-white">{item.item_name}</td>
                        <td className="p-2.5 text-yellow-500 font-semibold">{item.metal_type || 'Gold'}</td>
                        <td className="p-2.5 text-right font-mono">{Number(item.net_weight || item.gross_weight || 0).toFixed(3)}g</td>
                        <td className="p-2.5 text-right font-mono">{item.touch_purity || item.tanch_percentage || '91.60'}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Totals Summary */}
            <div className="bg-[#1c1c1c] border border-gray-800 rounded-xl p-5 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
              <div className="space-y-1 text-xs text-gray-400">
                <p>Total Items: <span className="text-white font-semibold">{data.totals?.total_items || data.items?.length || 1}</span></p>
                <p>Total Weight: <span className="text-white font-semibold font-mono">{Number(data.totals?.total_weight || 0).toFixed(3)}g</span></p>
              </div>
              <div className="text-left sm:text-right space-y-1">
                <span className="text-xs text-gray-400 block">Grand Total</span>
                <p className="text-2xl font-black font-mono text-yellow-400">
                  ₹{Number(data.totals?.grand_total || data.invoice?.grand_total || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </p>
              </div>
            </div>

            {/* Hallmark / Trust Seal Footer */}
            <div className="pt-4 border-t border-gray-800 flex flex-wrap items-center justify-between text-[11px] text-gray-500 gap-2">
              <div className="flex items-center gap-2">
                <Award className="w-4 h-4 text-yellow-500" />
                <span>BIS 916 & 925 Hallmark Certified Guarantee</span>
              </div>
              <span className="font-mono">Verification ID: {data.voucher_number}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
