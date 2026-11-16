import { useState, useEffect } from 'react';
import { axiosClient } from '../../api/axiosClient';
import { User, Calendar, Tag, CreditCard, UserPlus, X, Check } from 'lucide-react';
import { useBillingStore } from '../../store/billingStore';
import { useCompanyStore } from '../../store/companyStore';
import toast from 'react-hot-toast';
import { getErrorMessage } from '../../utils/errorUtils';

export default function TopBar() {
  const [customers, setCustomers] = useState<any[]>([]);
  const { selectedCustomerId, setSelectedCustomerId } = useBillingStore();
  const { currentCompany, currentCompanyId } = useCompanyStore();

  const [showAddModal, setShowAddModal] = useState(false);
  const [saving, setSaving] = useState(false);
  const [newCust, setNewCust] = useState({
    first_name: '',
    last_name: '',
    phone: '',
    city: '',
    address: '',
    gst_number: '',
    aadhaar_pan: ''
  });

  const loadCustomers = () => {
    axiosClient.get('/customers/')
      .then(res => setCustomers(res.data.items || []))
      .catch(() => {});
  };

  useEffect(() => {
    loadCustomers();
  }, [currentCompanyId]);

  const handleSaveCustomer = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCust.first_name.trim() || !newCust.phone.trim()) {
      toast.error('First name and phone number are required');
      return;
    }
    setSaving(true);
    try {
      const res = await axiosClient.post('/customers/', {
        first_name: newCust.first_name.trim(),
        last_name: newCust.last_name.trim(),
        phone_number: newCust.phone.trim(),
        city: newCust.city.trim(),
        state: 'Rajasthan',
        address: newCust.address.trim(),
        gst_number: newCust.gst_number.trim() || null,
        aadhaar_pan: newCust.aadhaar_pan.trim() || null,
        company_id: currentCompanyId || 1
      });

      const saved = res.data;
      setCustomers(prev => {
        const idx = prev.findIndex(c => c.id === saved.id);
        if (idx >= 0) {
          const updated = [...prev];
          updated[idx] = saved;
          return updated;
        }
        return [...prev, saved];
      });

      setSelectedCustomerId(saved.id);
      setShowAddModal(false);
      setNewCust({
        first_name: '',
        last_name: '',
        phone: '',
        city: '',
        address: '',
        gst_number: '',
        aadhaar_pan: ''
      });
      toast.success(`Customer "${saved.first_name}" saved & selected!`);
    } catch (err: any) {
      toast.error(getErrorMessage(err, 'Failed to save customer'));
    } finally {
      setSaving(false);
    }
  };

  const isGst = Boolean(currentCompany?.gst_enabled);

  return (
    <div className="bg-surface border border-gray-800 rounded-xl px-3 sm:px-4 py-2 shadow-lg flex flex-wrap justify-between items-center z-10 shrink-0 gap-2 sm:gap-3">
      {/* Customer Select & Quick Add */}
      <div className="flex items-center gap-2 flex-1 min-w-[220px] sm:min-w-[320px]">
        <label className="text-xs font-bold text-gray-500 uppercase flex items-center gap-1.5 shrink-0">
          <User size={14} className={isGst ? 'text-cyan-400' : 'text-primary'} /> Customer
        </label>
        
        <select 
          value={selectedCustomerId || ''}
          onChange={(e) => setSelectedCustomerId(e.target.value ? Number(e.target.value) : null)}
          className={`bg-background border rounded px-2.5 sm:px-3 py-1.5 outline-none text-textMain text-xs sm:text-sm w-full max-w-[280px] cursor-pointer ${isGst ? 'border-cyan-800/60 focus:border-cyan-400' : 'border-gray-700 focus:border-primary'}`}
        >
          <option value="">-- Walk-in / Cash Customer --</option>
          {customers.map(c => (
            <option key={c.id} value={c.id}>
              {c.first_name} {c.last_name || ''} {c.phone_number ? `(${c.phone_number})` : ''}
            </option>
          ))}
        </select>

        <button
          type="button"
          onClick={() => setShowAddModal(true)}
          className={`text-xs px-2.5 py-1.5 rounded font-bold shrink-0 flex items-center gap-1 border transition-colors cursor-pointer ${
            isGst 
              ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40 hover:bg-cyan-500/30' 
              : 'bg-primary/20 text-primary border-primary/40 hover:bg-primary/30'
          }`}
          title="Add New Customer"
        >
          <UserPlus size={13} />
          <span className="hidden sm:inline">+ New</span>
        </button>
      </div>

      {/* Metadata Badges & Module Indicator */}
      <div className="flex items-center gap-3 text-xs">
        <div className={`hidden sm:flex items-center gap-1.5 bg-background border rounded px-2.5 py-1 ${isGst ? 'border-cyan-800/50 text-cyan-300' : 'border-gray-700 text-textMuted'}`}>
          <Tag size={13} className={isGst ? 'text-cyan-400' : 'text-primary'} />
          <span className="font-mono font-bold">{isGst ? `${currentCompany?.invoice_prefix || 'GST'}/${currentCompany?.invoice_series || 'S'}/AUTO` : `${currentCompany?.invoice_prefix || 'INV'}-AUTO`}</span>
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
          {currentCompany?.name || (isGst ? 'GST Billing' : 'Billing Studio')}
        </div>
      </div>

      {/* Quick Add Customer Modal */}
      {showAddModal && (
        <div 
          className="fixed inset-0 z-50 flex items-center justify-center p-3 bg-black/75 backdrop-blur-sm animate-fadeIn"
          onClick={() => setShowAddModal(false)}
        >
          <div 
            className="w-full max-w-md bg-surface border border-gray-700 rounded-xl p-4 shadow-2xl space-y-3 cursor-default"
            onClick={e => e.stopPropagation()}
          >
            <div className="flex justify-between items-center border-b border-gray-800 pb-2">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <UserPlus size={16} className={isGst ? 'text-cyan-400' : 'text-primary'} />
                Register New Customer
              </h3>
              <button 
                type="button" 
                onClick={() => setShowAddModal(false)}
                className="text-gray-400 hover:text-white p-1 rounded-lg"
              >
                <X size={16} />
              </button>
            </div>

            <form onSubmit={handleSaveCustomer} className="space-y-3">
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-[10px] font-bold text-gray-400 uppercase mb-1">First Name *</label>
                  <input
                    type="text"
                    required
                    placeholder="First Name"
                    value={newCust.first_name}
                    onChange={e => setNewCust({ ...newCust, first_name: e.target.value })}
                    className="w-full bg-background border border-gray-700 rounded px-2.5 py-1.5 text-xs text-white outline-none focus:border-primary"
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-bold text-gray-400 uppercase mb-1">Last Name</label>
                  <input
                    type="text"
                    placeholder="Last Name"
                    value={newCust.last_name}
                    onChange={e => setNewCust({ ...newCust, last_name: e.target.value })}
                    className="w-full bg-background border border-gray-700 rounded px-2.5 py-1.5 text-xs text-white outline-none focus:border-primary"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-[10px] font-bold text-gray-400 uppercase mb-1">Phone Number *</label>
                  <input
                    type="tel"
                    required
                    placeholder="10-digit Phone"
                    value={newCust.phone}
                    onChange={e => setNewCust({ ...newCust, phone: e.target.value })}
                    className="w-full bg-background border border-gray-700 rounded px-2.5 py-1.5 text-xs text-white outline-none focus:border-primary"
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-bold text-gray-400 uppercase mb-1">City</label>
                  <input
                    type="text"
                    placeholder="City"
                    value={newCust.city}
                    onChange={e => setNewCust({ ...newCust, city: e.target.value })}
                    className="w-full bg-background border border-gray-700 rounded px-2.5 py-1.5 text-xs text-white outline-none focus:border-primary"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[10px] font-bold text-gray-400 uppercase mb-1">Full Address (क्रेता का पता)</label>
                <input
                  type="text"
                  placeholder="Street / Area / Landmark"
                  value={newCust.address}
                  onChange={e => setNewCust({ ...newCust, address: e.target.value })}
                  className="w-full bg-background border border-gray-700 rounded px-2.5 py-1.5 text-xs text-white outline-none focus:border-primary"
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-[10px] font-bold text-gray-400 uppercase mb-1">GSTIN (Optional)</label>
                  <input
                    type="text"
                    placeholder="08XXXXX..."
                    value={newCust.gst_number}
                    onChange={e => setNewCust({ ...newCust, gst_number: e.target.value.toUpperCase() })}
                    className="w-full bg-background border border-gray-700 rounded px-2.5 py-1.5 text-xs text-white outline-none focus:border-primary font-mono uppercase"
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-bold text-gray-400 uppercase mb-1">PAN (Optional)</label>
                  <input
                    type="text"
                    placeholder="ABCDE1234F"
                    value={newCust.aadhaar_pan}
                    onChange={e => setNewCust({ ...newCust, aadhaar_pan: e.target.value.toUpperCase() })}
                    className="w-full bg-background border border-gray-700 rounded px-2.5 py-1.5 text-xs text-white outline-none focus:border-primary font-mono uppercase"
                  />
                </div>
              </div>

              <div className="flex gap-2 pt-2 border-t border-gray-800">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="flex-1 py-2 border border-gray-700 rounded text-gray-400 hover:bg-gray-800 text-xs font-bold cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className={`flex-1 py-2 font-bold rounded text-xs flex items-center justify-center gap-1.5 cursor-pointer disabled:opacity-50 ${
                    isGst 
                      ? 'bg-cyan-500 hover:bg-cyan-400 text-black' 
                      : 'bg-primary hover:bg-primary-dark text-black'
                  }`}
                >
                  <Check size={14} />
                  <span>{saving ? 'Saving...' : 'Save & Select'}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
