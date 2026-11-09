import { useState, useEffect } from 'react';
import { axiosClient } from '../../api/axiosClient';
import { User, Calendar, Tag, CreditCard } from 'lucide-react';
import { useBillingStore } from '../../store/billingStore';
import { useCompanyStore } from '../../store/companyStore';

export default function TopBar() {
  const [customers, setCustomers] = useState<any[]>([]);
  const { selectedCustomerId, setSelectedCustomerId } = useBillingStore();
  const { currentCompany, currentCompanyId } = useCompanyStore();
  
  useEffect(() => {
    axiosClient.get('/customers/')
      .then(res => setCustomers(res.data.items || []))
      .catch(() => {});
  }, [currentCompanyId]);



  const isGst = Boolean(currentCompany?.gst_enabled);

  return (
    <div className="bg-surface border border-gray-800 rounded-xl px-3 sm:px-4 py-2 shadow-lg flex flex-wrap justify-between items-center z-10 shrink-0 gap-2 sm:gap-3">
      {/* Customer Select */}
      <div className="flex items-center gap-2 flex-1 min-w-[200px] sm:min-w-[280px]">
        <label className="text-xs font-bold text-gray-500 uppercase flex items-center gap-1.5 shrink-0">
          <User size={14} className={isGst ? 'text-cyan-400' : 'text-primary'} /> Customer
        </label>
        <select 
          value={selectedCustomerId || ''}
          onChange={(e) => setSelectedCustomerId(e.target.value ? Number(e.target.value) : null)}
          className={`bg-background border rounded px-2.5 sm:px-3 py-1.5 outline-none text-textMain text-xs sm:text-sm w-full max-w-[300px] cursor-pointer ${isGst ? 'border-cyan-800/60 focus:border-cyan-400' : 'border-gray-700 focus:border-primary'}`}
        >
          <option value="">Walk-in Customer</option>
          {customers.map(c => (
            <option key={c.id} value={c.id}>
              {c.first_name} {c.last_name || ''} {c.phone_number ? `(${c.phone_number})` : ''}
            </option>
          ))}
        </select>


      </div>

      {/* Metadata Badges & Module Indicator */}
      <div className="flex items-center gap-3 text-xs">
        <div className={`hidden sm:flex items-center gap-1.5 bg-background border rounded px-2.5 py-1 ${isGst ? 'border-cyan-800/50 text-cyan-300' : 'border-gray-700 text-textMuted'}`}>
          <Tag size={13} className={isGst ? 'text-cyan-400' : 'text-primary'} />
          <span className="font-mono font-bold">{isGst ? 'SJ/S/AUTO' : 'INV-AUTO'}</span>
        </div>

        <div className="hidden sm:flex items-center gap-1.5 bg-background border border-gray-700 rounded px-2.5 py-1 text-textMain">
          <Calendar size={13} className={isGst ? 'text-cyan-400' : 'text-primary'} />
          <span className="font-mono">{new Date().toLocaleDateString('en-GB')}</span>
        </div>

        <div className="hidden md:flex items-center gap-1.5 bg-background border border-gray-700 rounded px-2.5 py-1 text-textMuted">
          <CreditCard size={13} className="text-gray-400" />
          <span>{isGst ? 'Tax Bullion / Wholesale' : 'Counter Sale'}</span>
        </div>

        <div className={`font-bold text-xs tracking-widest uppercase flex items-center gap-2 pl-2 border-l border-gray-800 ${isGst ? 'text-cyan-400' : 'text-primary'}`}>
          <span className={`w-2 h-2 rounded-full animate-pulse ${isGst ? 'bg-cyan-400' : 'bg-primary'}`} />
          {isGst ? 'Saideep GST' : 'Billing Studio'}
        </div>
      </div>
    </div>
  );
}
