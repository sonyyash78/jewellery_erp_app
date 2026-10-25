import { useState, useEffect } from 'react';
import { Users, Building2, Wallet, PlusCircle, Search, X } from 'lucide-react';
import { getErrorMessage } from '../../utils/errorUtils';
import { axiosClient } from '../../api/axiosClient';
import toast from 'react-hot-toast';
import CustomerProfile from './CustomerProfile';
import SupplierProfile from './SupplierProfile';

export default function CRM() {
  const [tab, setTab] = useState<'customers'|'suppliers'>('customers');
  const [customers, setCustomers] = useState<any[]>([]);
  const [suppliers, setSuppliers] = useState<any[]>([]);
  const [metrics, setMetrics] = useState({ totalCustomers: 0, totalSuppliers: 0, outstanding: 0 });
  const [search, setSearch] = useState('');
  
  const [selectedCustomerId, setSelectedCustomerId] = useState<number | null>(null);
  const [selectedSupplierId, setSelectedSupplierId] = useState<number | null>(null);

  // Modals state
  const [showAddCustomer, setShowAddCustomer] = useState(false);
  const [showAddSupplier, setShowAddSupplier] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);

  // Customer Form State
  const [custName, setCustName] = useState('');
  const [custCountryCode, setCustCountryCode] = useState('+91');
  const [custMobile, setCustMobile] = useState('');
  const [custCity, setCustCity] = useState('');
  const [custPan, setCustPan] = useState('');
  const [custGst, setCustGst] = useState('');
  const [custBalance, setCustBalance] = useState('');

  // Supplier Form State
  const [suppName, setSuppName] = useState('');
  const [suppCountryCode, setSuppCountryCode] = useState('+91');
  const [suppMobile, setSuppMobile] = useState('');
  const [suppCity, setSuppCity] = useState('');
  const [suppGst, setSuppGst] = useState('');
  const [suppBalance, setSuppBalance] = useState('');

  const fetchData = async () => {
    try {
      const [custRes, suppRes] = await Promise.all([
        axiosClient.get('/customers/', { params: { search } }),
        axiosClient.get('/sellers/', { params: { search } })
      ]);
      setCustomers(custRes.data.items);
      setSuppliers(suppRes.data.items);
      setMetrics({
        totalCustomers: custRes.data.total,
        totalSuppliers: suppRes.data.total,
        outstanding: custRes.data.total_outstanding - suppRes.data.total_outstanding // Net outstanding (we receive - we pay)
      });
    } catch (e) {
      toast.error('Failed to load CRM data');
    }
  };

  useEffect(() => {
    fetchData();
  }, [search]);

  const handleAddCustomer = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!custName || (custMobile.length !== 10 && custMobile.length !== 12)) {
      toast.error('Please enter valid Name and 10 or 12-digit Mobile');
      return;
    }
    try {
      const payload = {
        first_name: custName,
        phone_number: custMobile,
        city: custCity,
        aadhaar_pan: custPan,
        gst_number: custGst,
        outstanding_balance: Number(custBalance) || 0
      };
      if (editingId) {
        await axiosClient.put(`/customers/${editingId}`, payload);
        toast.success('Customer updated successfully');
      } else {
        await axiosClient.post('/customers/', payload);
        toast.success('Customer created successfully');
      }
      setShowAddCustomer(false);
      setEditingId(null);
      fetchData();
    } catch (e: any) {
      toast.error(getErrorMessage(e, 'Failed to save customer'));
    } finally {};
  };

  const handleAddSupplier = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const payload = {
        name: suppName,
        mobile: suppMobile,
        city: suppCity,
        gst_number: suppGst,
        outstanding_balance: Number(suppBalance) || 0
      };
      if (editingId) {
        await axiosClient.put(`/sellers/${editingId}`, payload);
        toast.success('Supplier updated successfully');
      } else {
        await axiosClient.post('/sellers/', payload);
        toast.success('Supplier created successfully');
      }
      setShowAddSupplier(false);
      setEditingId(null);
      fetchData();
    } catch (e: any) {
      toast.error(getErrorMessage(e, 'Failed to save supplier'));
    } finally {};
  };

  const deleteCustomer = async (id: number) => {
    try {
      await axiosClient.delete(`/customers/${id}`);
      toast.success('Customer deleted successfully');
      fetchData();
    } catch (e) {
      toast.error('Failed to delete customer');
    }
  };

  const deleteSupplier = async (id: number) => {
    try {
      await axiosClient.delete(`/sellers/${id}`);
      toast.success('Supplier deleted successfully');
      fetchData();
    } catch (e) {
      toast.error('Failed to delete supplier');
    }
  };

  if (selectedCustomerId) {
    return <CustomerProfile id={selectedCustomerId} onBack={() => { setSelectedCustomerId(null); fetchData(); }} />;
  }

  if (selectedSupplierId) {
    return <SupplierProfile id={selectedSupplierId} onBack={() => { setSelectedSupplierId(null); fetchData(); }} />;
  }

  return (
    <div className="h-auto lg:h-[calc(100vh-6rem)] flex flex-col space-y-4 relative overflow-y-auto lg:overflow-hidden pb-8 lg:pb-0">
      {/* Dashboard Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        <div className="bg-surface border border-gray-800 rounded-xl p-3.5 sm:p-4 shadow-lg flex items-center gap-3.5 sm:gap-4">
          <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-full bg-primary/10 flex items-center justify-center text-primary shrink-0"><Users size={22} /></div>
          <div><div className="text-textMuted text-xs sm:text-sm font-bold tracking-wider uppercase">Total Customers</div><div className="text-xl sm:text-2xl font-bold font-mono">{metrics.totalCustomers}</div></div>
        </div>
        <div className="bg-surface border border-gray-800 rounded-xl p-3.5 sm:p-4 shadow-lg flex items-center gap-3.5 sm:gap-4">
          <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-full bg-primary/10 flex items-center justify-center text-primary shrink-0"><Building2 size={22} /></div>
          <div><div className="text-textMuted text-xs sm:text-sm font-bold tracking-wider uppercase">Total Suppliers</div><div className="text-xl sm:text-2xl font-bold font-mono">{metrics.totalSuppliers}</div></div>
        </div>
        <div className="bg-surface border border-gray-800 rounded-xl p-3.5 sm:p-4 shadow-lg flex items-center gap-3.5 sm:gap-4">
          <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-full bg-primary/10 flex items-center justify-center text-primary shrink-0"><Wallet size={22} /></div>
          <div><div className="text-textMuted text-xs sm:text-sm font-bold tracking-wider uppercase">Net Outstanding</div><div className="text-xl sm:text-2xl font-bold font-mono text-primary truncate">₹ {metrics.outstanding.toLocaleString()}</div></div>
        </div>
        <div 
          onClick={() => {
            setEditingId(null);
            if (tab === 'customers') {
              setCustName(''); setCustCountryCode('+91'); setCustMobile(''); setCustCity(''); setCustPan(''); setCustGst(''); setCustBalance('');
              setShowAddCustomer(true);
            } else {
              setSuppName(''); setSuppCountryCode('+91'); setSuppMobile(''); setSuppCity(''); setSuppGst(''); setSuppBalance('');
              setShowAddSupplier(true);
            }
          }}
          className="bg-surface border border-primary/20 rounded-xl p-3.5 sm:p-4 shadow-lg flex items-center justify-center cursor-pointer hover:bg-primary/5 transition-colors"
        >
          <div className="flex flex-col items-center text-primary">
            <PlusCircle size={28} className="mb-1" />
            <button className="font-bold tracking-wider uppercase text-xs sm:text-sm">
              {tab === 'customers' ? 'Add Customer' : 'Add Supplier'}
            </button>
          </div>
        </div>
      </div>

      <div className="flex-1 bg-surface border border-gray-800 rounded-xl shadow-lg flex flex-col overflow-hidden min-h-[450px]">
        
        {/* Toolbar */}
        <div className="flex flex-col sm:flex-row border-b border-gray-800">
          <div className="flex-1 flex overflow-x-auto whitespace-nowrap">
            <button 
              onClick={() => setTab('customers')}
              className={`px-4 sm:px-6 py-3 sm:py-4 font-bold uppercase tracking-wider text-xs sm:text-sm transition-colors ${tab === 'customers' ? 'bg-primary/10 text-primary border-b-2 border-primary' : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/50'}`}
            >
              Customers Directory
            </button>
            <button 
              onClick={() => setTab('suppliers')}
              className={`px-4 sm:px-6 py-3 sm:py-4 font-bold uppercase tracking-wider text-xs sm:text-sm transition-colors ${tab === 'suppliers' ? 'bg-primary/10 text-primary border-b-2 border-primary' : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/50'}`}
            >
              Suppliers Directory
            </button>
          </div>
          <div className="w-full sm:w-64 p-3 relative border-t sm:border-t-0 border-gray-800">
            <Search className="absolute left-6 top-5 text-gray-500" size={18} />
            <input 
              value={search} onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-background border border-gray-700 rounded-lg pl-10 pr-4 py-2 text-sm text-textMain focus:border-primary outline-none" 
              placeholder={tab === 'customers' ? "Search customers..." : "Search suppliers..."} 
            />
          </div>
        </div>

        {/* Table Area */}
        <div className="flex-1 overflow-x-auto overflow-y-auto custom-scrollbar">
          <table className="w-full text-left text-sm text-textMuted min-w-[700px]">
            <thead className="bg-background sticky top-0 border-b border-gray-800">
              <tr>
                <th className="py-3 px-4 font-bold uppercase tracking-wider text-xs">Name</th>
                <th className="py-3 px-4 font-bold uppercase tracking-wider text-xs">Contact</th>
                <th className="py-3 px-4 font-bold uppercase tracking-wider text-xs">City</th>
                <th className="py-3 px-4 font-bold uppercase tracking-wider text-xs">GST / ID</th>
                <th className="py-3 px-4 font-bold uppercase tracking-wider text-xs">{tab === 'customers' ? 'Credit Limit' : 'Status'}</th>
                <th className="py-3 px-4 font-bold uppercase tracking-wider text-xs">Outstanding</th>
                <th className="py-3 px-4 font-bold uppercase tracking-wider text-xs text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/50">
              {(tab === 'customers' ? customers : suppliers).map((person) => (
                <tr key={person.id} className="hover:bg-gray-800/30 transition-colors">
                  <td className="py-3 px-4 font-bold text-textMain">{tab === 'customers' ? `${person.first_name} ${person.last_name || ''}` : person.name}</td>
                  <td className="py-3 px-4">{person.phone_number || person.mobile}</td>
                  <td className="py-3 px-4">{person.city || '—'}</td>
                  <td className="py-3 px-4">
                    {person.gst_number && person.aadhaar_pan 
                      ? `GST: ${person.gst_number} / PAN: ${person.aadhaar_pan}`
                      : person.gst_number ? `GST: ${person.gst_number}` : person.aadhaar_pan ? `PAN: ${person.aadhaar_pan}` : 'N/A'
                    }
                  </td>
                  <td className="py-3 px-4 font-mono">
                    {tab === 'customers' ? (person.credit_limit ? `₹ ${person.credit_limit.toLocaleString()}` : 'None') : (person.is_active ? 'Active' : 'Inactive')}
                  </td>
                  <td className="py-3 px-4 font-mono font-bold text-primary">₹ {Number(person.outstanding_balance).toLocaleString()}</td>
                  <td className="py-3 px-4 text-right flex justify-end gap-2">
                    <button 
                      onClick={() => {
                        setEditingId(person.id);
                        if (tab === 'customers') {
                          setCustName(person.first_name);
                          setCustMobile(person.phone_number);
                          setCustCity(person.city || '');
                          setCustBalance(person.outstanding_balance?.toString() || '0');
                          setCustPan(person.aadhaar_pan || '');
                          setCustGst(person.gst_number || '');
                          setShowAddCustomer(true);
                        } else {
                          setSuppName(person.name);
                          setSuppMobile(person.mobile);
                          setSuppCity(person.city || '');
                          setSuppGst(person.gst_number || '');
                          setSuppBalance(person.outstanding_balance?.toString() || '0');
                          setShowAddSupplier(true);
                        }
                      }}
                      className="bg-primary/20 text-primary px-3 py-1 rounded text-xs font-bold uppercase hover:bg-primary/30 transition-colors"
                      aria-label={`Edit ${person.first_name || person.name}`}
                    >
                      Edit
                    </button>
                    <button 
                      onClick={() => tab === 'customers' ? setSelectedCustomerId(person.id) : setSelectedSupplierId(person.id)}
                      className="bg-primary/20 text-primary px-3 py-1 rounded text-xs font-bold uppercase hover:bg-primary/30 transition-colors"
                    >
                      Ledger
                    </button>
                    {tab === 'customers' ? (
                      <button 
                        onClick={() => deleteCustomer(person.id)}
                        className="bg-red-500/20 text-red-500 px-3 py-1 rounded text-xs font-bold uppercase hover:bg-red-500/30 transition-colors"
                        aria-label={`Delete ${person.first_name}`}
                      >
                        Delete
                      </button>
                    ) : (
                      <button 
                        onClick={() => deleteSupplier(person.id)}
                        className="bg-red-500/20 text-red-500 px-3 py-1 rounded text-xs font-bold uppercase hover:bg-red-500/30 transition-colors"
                        aria-label={`Delete ${person.name}`}
                      >
                        Delete
                      </button>
                    )}
                  </td>
                </tr>
              ))}
              {(tab === 'customers' ? customers : suppliers).length === 0 && (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-gray-500 italic">No records found.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add Customer Modal */}
      {showAddCustomer && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center">
          <div className="bg-surface border border-gray-800 rounded-xl p-6 w-96 max-w-full">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold text-primary">{editingId ? 'Edit' : 'Add'} Customer</h3>
              <button onClick={() => setShowAddCustomer(false)}><X className="text-textMuted hover:text-textMain" /></button>
            </div>
            <form onSubmit={handleAddCustomer} className="space-y-4">
              <div>
                <label htmlFor="cust-name" className="block text-sm text-textMuted">Name <span className="text-red-500">*</span></label>
                <input id="cust-name" required value={custName} onChange={e => setCustName(e.target.value)} className="w-full bg-background border border-gray-700 rounded px-3 py-2 text-textMain" />
              </div>
                <div>
                  <label htmlFor="cust-mobile" className="block text-sm text-textMuted">Mobile Number <span className="text-red-500">*</span></label>
                  <div className="flex gap-2">
                    <input type="text" value={custCountryCode} onChange={e => setCustCountryCode(e.target.value)} className="w-16 bg-background border border-gray-700 rounded px-2 text-center text-textMain focus:border-primary outline-none" />
                    <input id="cust-mobile" required minLength={10} maxLength={10} value={custMobile} onChange={e => setCustMobile(e.target.value.replace(/\D/g, ''))} className="flex-1 bg-background border border-gray-700 rounded px-3 py-2 text-textMain focus:border-primary outline-none" placeholder="10-digit number" />
                  </div>
                </div>
              <div>
                <label htmlFor="cust-city" className="block text-sm text-textMuted">City</label>
                <input id="cust-city" value={custCity} onChange={e => setCustCity(e.target.value)} className="w-full bg-background border border-gray-700 rounded px-3 py-2 text-textMain" />
              </div>
              <div>
                <label htmlFor="cust-gst" className="block text-sm text-textMuted">GST Number</label>
                <input id="cust-gst" value={custGst} onChange={e => setCustGst(e.target.value)} className="w-full bg-background border border-gray-700 rounded px-3 py-2 text-textMain" />
              </div>
              <div>
                <label htmlFor="cust-pan" className="block text-sm text-textMuted">PAN Number</label>
                <input id="cust-pan" value={custPan} onChange={e => setCustPan(e.target.value)} className="w-full bg-background border border-gray-700 rounded px-3 py-2 text-textMain" />
              </div>
              <div>
                <label htmlFor="cust-balance" className="block text-sm text-textMuted">Opening Balance</label>
                <input id="cust-balance" type="number" value={custBalance} onChange={e => setCustBalance(e.target.value)} className="w-full bg-background border border-gray-700 rounded px-3 py-2 text-textMain" />
              </div>
              {!custName && <p className="text-red-500 text-xs">Name is required</p>}
              {(custMobile.length !== 10 && custMobile.length !== 12) && <p className="text-red-500 text-xs">Mobile number must be 10 or 12 digits</p>}
              <button type="submit" className="w-full bg-primary text-black font-bold py-2 rounded">Save</button>
            </form>
          </div>
        </div>
      )}

      {/* Add Supplier Modal */}
      {showAddSupplier && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center">
          <div className="bg-surface border border-gray-800 rounded-xl p-6 w-96 max-w-full">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold text-primary">{editingId ? 'Edit' : 'Add'} Supplier</h3>
              <button onClick={() => setShowAddSupplier(false)}><X className="text-textMuted hover:text-textMain" /></button>
            </div>
            <form onSubmit={handleAddSupplier} className="space-y-4">
              <div>
                <label htmlFor="supp-name" className="block text-sm text-textMuted">Name <span className="text-red-500">*</span></label>
                <input id="supp-name" required value={suppName} onChange={e => setSuppName(e.target.value)} className="w-full bg-background border border-gray-700 rounded px-3 py-2 text-textMain" />
              </div>
                <div>
                  <label htmlFor="supp-mobile" className="block text-sm text-textMuted">Mobile Number <span className="text-red-500">*</span></label>
                  <div className="flex gap-2">
                    <input type="text" value={suppCountryCode} onChange={e => setSuppCountryCode(e.target.value)} className="w-16 bg-background border border-gray-700 rounded px-2 text-center text-textMain focus:border-primary outline-none" />
                    <input id="supp-mobile" required minLength={10} maxLength={10} value={suppMobile} onChange={e => setSuppMobile(e.target.value.replace(/\D/g, ''))} className="flex-1 bg-background border border-gray-700 rounded px-3 py-2 text-textMain focus:border-primary outline-none" placeholder="10-digit number" />
                  </div>
                </div>
              <div>
                <label htmlFor="supp-city" className="block text-sm text-textMuted">City</label>
                <input id="supp-city" value={suppCity} onChange={e => setSuppCity(e.target.value)} className="w-full bg-background border border-gray-700 rounded px-3 py-2 text-textMain" />
              </div>
              <div>
                <label htmlFor="supp-gst" className="block text-sm text-textMuted">GST Number</label>
                <input id="supp-gst" value={suppGst} onChange={e => setSuppGst(e.target.value)} className="w-full bg-background border border-gray-700 rounded px-3 py-2 text-textMain" />
              </div>
              <div>
                <label htmlFor="supp-balance" className="block text-sm text-textMuted">Opening Balance</label>
                <input id="supp-balance" type="number" value={suppBalance} onChange={e => setSuppBalance(e.target.value)} className="w-full bg-background border border-gray-700 rounded px-3 py-2 text-textMain" />
              </div>
              <button type="submit" className="w-full bg-primary text-black font-bold py-2 rounded">Save</button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
