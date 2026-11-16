import { useState, useEffect } from 'react';
import { useCompanyStore } from '../../store/companyStore';
import { useBillingStore } from '../../store/billingStore';
import { Building2, ShieldCheck, FileSpreadsheet, Sparkles, CheckCircle2, ArrowRight } from 'lucide-react';

interface StartupCompanyModalProps {
  forceOpen?: boolean;
  onClose?: () => void;
}

export default function StartupCompanyModal({ forceOpen, onClose }: StartupCompanyModalProps) {
  const { companies, currentCompanyId, selectCompany, fetchCompanies } = useCompanyStore();
  const { clearCart, resetGoldForm, resetSilverForm, resetDiamondForm } = useBillingStore();
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    fetchCompanies();
    const dismissed = sessionStorage.getItem('erp_company_modal_dismissed');
    if (!dismissed || forceOpen) {
      setIsOpen(true);
    }
  }, [forceOpen]);

  // Listen to custom event to open modal on demand
  useEffect(() => {
    const handleOpen = () => {
      fetchCompanies();
      setIsOpen(true);
    };
    window.addEventListener('open-company-picker', handleOpen);
    return () => window.removeEventListener('open-company-picker', handleOpen);
  }, [fetchCompanies]);

  const handleChoose = (companyId: number) => {
    selectCompany(companyId);
    // Clear billing inputs so calculations never bleed between companies
    clearCart();
    resetGoldForm();
    resetSilverForm();
    resetDiamondForm();
    sessionStorage.setItem('erp_company_modal_dismissed', 'true');
    setIsOpen(false);
    if (onClose) onClose();
  };

  if (!isOpen) return null;

  const co1 = companies.find((c) => c.id === 1) || {
    id: 1,
    name: 'Normal Company',
    address: '',
    gst_enabled: false,
    invoice_prefix: 'INV',
    invoice_series: 'S'
  };

  const co2 = companies.find((c) => c.id === 2) || {
    id: 2,
    name: 'GST Company',
    address: '',
    gst_enabled: true,
    invoice_prefix: 'GST',
    invoice_series: 'S'
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md animate-fade-in">
      <div className="bg-[#111116] border border-gray-800 rounded-3xl max-w-3xl w-full p-6 sm:p-8 shadow-[0_20px_60px_rgba(0,0,0,0.9)] relative overflow-hidden">
        {/* Glow Effects */}
        <div className="absolute -top-24 -left-24 w-72 h-72 bg-amber-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-24 -right-24 w-72 h-72 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />

        {/* Modal Header */}
        <div className="text-center mb-8 relative z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20 text-primary text-xs font-bold uppercase tracking-wider mb-3">
            <Sparkles size={14} /> Multi-Company Workspace
          </div>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Select Operating Company / बिलिंग मोड चुनें
          </h2>
          <p className="text-sm text-gray-400 mt-2 max-w-lg mx-auto">
            Choose the company mode. Both companies maintain completely separate invoices, calculations, sequences, and archives.
          </p>
        </div>

        {/* Two Company Options */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5 relative z-10">
          {/* Company 1: Normal / Without GST */}
          <div
            onClick={() => handleChoose(1)}
            className={`group cursor-pointer rounded-2xl p-6 border-2 transition-all flex flex-col justify-between ${
              currentCompanyId === 1
                ? 'bg-gradient-to-b from-amber-950/30 to-[#181820] border-amber-500 shadow-[0_0_25px_rgba(245,158,11,0.25)]'
                : 'bg-[#16161D] border-gray-800 hover:border-amber-500/50 hover:bg-[#1A1A22]'
            }`}
          >
            <div>
              <div className="flex justify-between items-start mb-4">
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-amber-500/20 text-amber-300 border border-amber-500/30">
                  Normal • Non-GST
                </span>
                {currentCompanyId === 1 && (
                  <CheckCircle2 size={20} className="text-amber-400 shrink-0" />
                )}
              </div>
              <h3 className="text-xl font-bold text-white group-hover:text-amber-300 transition-colors flex items-center gap-2">
                <Building2 size={22} className="text-amber-400" />
                {co1.name}
              </h3>
              <p className="text-xs text-amber-200/70 mt-1 font-mono">
                {co1.address || 'Non-GST Retail Workspace'}
              </p>
              
              <div className="mt-4 space-y-2 text-xs text-gray-400 border-t border-gray-800/80 pt-3">
                <div className="flex items-center gap-2">
                  <ShieldCheck size={14} className="text-amber-400" />
                  <span>Traditional Gold &amp; Silver Fine Settlement</span>
                </div>
                <div className="flex items-center gap-2">
                  <FileSpreadsheet size={14} className="text-amber-400" />
                  <span>Series: <span className="font-mono text-gray-300">{co1.invoice_prefix || 'INV'}-YYYYMMDD-XXXX</span></span>
                </div>
                <div className="flex items-center gap-2">
                  <Sparkles size={14} className="text-amber-400" />
                  <span>Untouched Standard Customer Receipts</span>
                </div>
              </div>
            </div>

            <button
              type="button"
              className="mt-6 w-full py-3 px-4 rounded-xl font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 transition-all bg-amber-500 hover:bg-amber-400 text-black shadow-lg shadow-amber-500/20 group-hover:shadow-amber-500/40"
            >
              Enter {co1.name || 'Company 1'} (Normal) <ArrowRight size={14} />
            </button>
          </div>

          {/* Company 2: GST Tax Invoice */}
          <div
            onClick={() => handleChoose(2)}
            className={`group cursor-pointer rounded-2xl p-6 border-2 transition-all flex flex-col justify-between ${
              currentCompanyId === 2
                ? 'bg-gradient-to-b from-cyan-950/30 to-[#181820] border-cyan-500 shadow-[0_0_25px_rgba(6,182,212,0.25)]'
                : 'bg-[#16161D] border-gray-800 hover:border-cyan-500/50 hover:bg-[#1A1A22]'
            }`}
          >
            <div>
              <div className="flex justify-between items-start mb-4">
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                  GST Tax Invoice
                </span>
                {currentCompanyId === 2 && (
                  <CheckCircle2 size={20} className="text-cyan-400 shrink-0" />
                )}
              </div>
              <h3 className="text-xl font-bold text-white group-hover:text-cyan-300 transition-colors flex items-center gap-2">
                <Building2 size={22} className="text-cyan-400" />
                {co2.name}
              </h3>
              <p className="text-xs text-cyan-200/70 mt-1 font-mono">
                {co2.address || 'GST Tax Invoice Workspace'}
              </p>

              <div className="mt-4 space-y-2 text-xs text-gray-400 border-t border-gray-800/80 pt-3">
                <div className="flex items-center gap-2">
                  <ShieldCheck size={14} className="text-cyan-400" />
                  <span>Full GST Engine (CGST 1.5% + SGST 1.5% / IGST 3%)</span>
                </div>
                <div className="flex items-center gap-2">
                  <FileSpreadsheet size={14} className="text-cyan-400" />
                  <span>Series: <span className="font-mono text-gray-300">{co2.invoice_prefix || 'GST'}/{co2.invoice_series || 'S'}/01/...</span></span>
                </div>
                <div className="flex items-center gap-2">
                  <Sparkles size={14} className="text-cyan-400" />
                  <span>Official e-Invoice IRN &amp; QR Code Layout</span>
                </div>
              </div>
            </div>

            <button
              type="button"
              className="mt-6 w-full py-3 px-4 rounded-xl font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 transition-all bg-cyan-500 hover:bg-cyan-400 text-black shadow-lg shadow-cyan-500/20 group-hover:shadow-cyan-500/40"
            >
              Enter {co2.name || 'Company 2'} (GST) <ArrowRight size={14} />
            </button>
          </div>
        </div>

        {/* Footer info note */}
        <div className="mt-6 text-center text-xs text-gray-500 relative z-10">
          You can switch companies at any time using the company selector at the top header.
        </div>
      </div>
    </div>
  );
}
