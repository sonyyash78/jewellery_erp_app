import React, { useEffect } from 'react';
import { useCompanyStore } from '../../store/companyStore';
import { Building2, ChevronDown, Check } from 'lucide-react';

export default function CompanySelector() {
  const { currentCompany, currentCompanyId, companies, fetchCompanies, selectCompany } = useCompanyStore();
  const [open, setOpen] = React.useState(false);

  useEffect(() => {
    fetchCompanies();
  }, []);

  const handleSelect = (id: number) => {
    selectCompany(id);
    setOpen(false);
  };

  return (
    <div className="relative inline-block text-left">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className="flex items-center gap-2 px-2.5 py-1.5 rounded-lg bg-surface border border-gray-700 hover:border-primary/50 text-xs text-textMain transition-all shadow-sm focus:outline-none"
        title="Switch Operating Company"
      >
        <Building2 size={14} className={currentCompany?.gst_enabled ? 'text-emerald-400' : 'text-primary'} />
        <div className="flex flex-col text-left">
          <span className="font-semibold leading-tight flex items-center gap-1.5">
            {currentCompany?.name || 'Saideep Jewellers'}
            {currentCompany?.gst_enabled ? (
              <span className="text-[10px] bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 px-1.5 py-0.5 rounded font-bold">
                GST Tax Invoice
              </span>
            ) : (
              <span className="text-[10px] bg-amber-500/20 text-amber-300 border border-amber-500/30 px-1.5 py-0.5 rounded font-bold">
                Normal (No-GST)
              </span>
            )}
          </span>
        </div>
        <ChevronDown size={12} className="text-gray-400 ml-1" />
      </button>

      {open && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />
          <div className="absolute right-0 mt-2 w-64 rounded-xl bg-surface border border-gray-700 shadow-2xl z-50 p-1.5 space-y-1">
            <div className="px-2.5 py-1.5 text-[11px] font-bold text-gray-400 uppercase tracking-wider border-b border-gray-800">
              Select Company
            </div>
            {companies.map((c) => {
              const isSelected = c.id === currentCompanyId;
              return (
                <button
                  key={c.id}
                  onClick={() => handleSelect(c.id)}
                  className={`w-full flex items-center justify-between px-2.5 py-2 rounded-lg text-xs text-left transition-colors ${
                    isSelected
                      ? 'bg-primary/15 text-primary font-bold border border-primary/20'
                      : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                  }`}
                >
                  <div className="flex flex-col">
                    <span className="font-medium text-white flex items-center gap-1.5">
                      {c.name}
                      {c.gst_enabled && (
                        <span className="text-[9px] bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 px-1 py-0.2 rounded">
                          GST Tax Invoice
                        </span>
                      )}
                    </span>
                    <span className="text-[10px] text-gray-400">
                      Prefix: {c.invoice_prefix} | {c.gst_enabled ? `GSTIN: ${c.gstin || 'None'}` : 'Non-GST Retail'}
                    </span>
                  </div>
                  {isSelected && <Check size={14} className="text-primary" />}
                </button>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}
