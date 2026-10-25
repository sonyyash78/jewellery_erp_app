import { useState, useEffect } from 'react';
import { axiosClient } from '../../api/axiosClient';
import toast from 'react-hot-toast';
import { UserPlus, User, Check, X } from 'lucide-react';
import { getErrorMessage } from '../../utils/errorUtils';

interface PostBillModalProps {
  invoiceId: number;
  onClose: () => void;
}

export default function PostBillModal({ invoiceId, onClose }: PostBillModalProps) {
  const [mode, setMode] = useState<'menu' | 'new' | 'existing'>('menu');
  const [customers, setCustomers] = useState<any[]>([]);
  const [selectedCustomer, setSelectedCustomer] = useState<number | ''>('');
  
  const [newCustomer, setNewCustomer] = useState({
    first_name: '',
    last_name: '',
    phone: ''
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (mode === 'existing') {
      axiosClient.get('/customers/').then(res => setCustomers(res.data.items || []));
    }
  }, [mode]);

  const handleLinkCustomer = async (customerId: number) => {
    setLoading(true);
    try {
      await axiosClient.patch(`/invoices/${invoiceId}/customer`, { customer_id: customerId });
      toast.success('Customer linked to invoice successfully!');
      onClose();
    } catch (e: any) {
      toast.error(getErrorMessage(e, 'Failed to link customer'));
    } finally {
      setLoading(false);
    }
  };

  const handleSaveNew = async () => {
    if (!newCustomer.first_name || !newCustomer.phone) {
      toast.error('First name and phone are required');
      return;
    }
    setLoading(true);
    try {
      const res = await axiosClient.post('/customers/', {
        first_name: newCustomer.first_name,
        last_name: newCustomer.last_name,
        phone_number: newCustomer.phone,
        email: null,
        address: ''
      });
      await handleLinkCustomer(res.data.id);
    } catch (e: any) {
      toast.error(getErrorMessage(e, 'Failed to create customer'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-surface border border-gray-700 rounded-xl shadow-2xl w-full max-w-md overflow-hidden flex flex-col">
        <div className="flex justify-between items-center p-4 border-b border-gray-700 bg-gray-900/50">
          <h2 className="text-lg font-bold text-primary">Bill Generated!</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white"><X size={20} /></button>
        </div>

        <div className="p-6">
          {mode === 'menu' && (
            <div className="space-y-4">
              <p className="text-sm text-textMuted text-center mb-6">
                Your invoice has been generated successfully. Would you like to link a customer?
              </p>
              
              <button 
                onClick={() => setMode('new')}
                className="w-full flex items-center justify-center space-x-2 bg-primary/20 hover:bg-primary/30 text-primary border border-primary/50 py-3 rounded-lg transition-colors"
              >
                <UserPlus size={18} /> <span>Save as New Customer</span>
              </button>
              
              <button 
                onClick={() => setMode('existing')}
                className="w-full flex items-center justify-center space-x-2 bg-gray-800 hover:bg-gray-700 text-white border border-gray-600 py-3 rounded-lg transition-colors"
              >
                <User size={18} /> <span>Select Existing Customer</span>
              </button>
              
              <button 
                onClick={onClose}
                className="w-full flex items-center justify-center space-x-2 bg-transparent hover:bg-gray-800 text-gray-400 py-3 rounded-lg transition-colors mt-2"
              >
                <span>Continue as Walk-in</span>
              </button>
            </div>
          )}

          {mode === 'new' && (
            <div className="space-y-4">
              <h3 className="font-semibold text-white mb-2">New Customer Details</h3>
              <input 
                placeholder="First Name" 
                className="w-full bg-background border border-gray-700 rounded p-2 text-white"
                value={newCustomer.first_name}
                onChange={e => setNewCustomer({...newCustomer, first_name: e.target.value})}
              />
              <input 
                placeholder="Last Name (Optional)" 
                className="w-full bg-background border border-gray-700 rounded p-2 text-white"
                value={newCustomer.last_name}
                onChange={e => setNewCustomer({...newCustomer, last_name: e.target.value})}
              />
              <input 
                placeholder="Phone Number" 
                className="w-full bg-background border border-gray-700 rounded p-2 text-white"
                value={newCustomer.phone}
                onChange={e => setNewCustomer({...newCustomer, phone: e.target.value})}
              />
              
              <div className="flex space-x-3 mt-6">
                <button onClick={() => setMode('menu')} className="flex-1 py-2 border border-gray-700 rounded text-gray-400 hover:bg-gray-800">Back</button>
                <button onClick={handleSaveNew} disabled={loading} className="flex-1 py-2 bg-primary text-black font-bold rounded hover:bg-primary/90 disabled:opacity-50 flex justify-center items-center">
                  {loading ? 'Saving...' : <><Check size={16} className="mr-1"/> Save & Link</>}
                </button>
              </div>
            </div>
          )}

          {mode === 'existing' && (
            <div className="space-y-4">
              <h3 className="font-semibold text-white mb-2">Select Customer</h3>
              <select 
                className="w-full bg-background border border-gray-700 rounded p-2 text-white outline-none"
                value={selectedCustomer}
                onChange={e => setSelectedCustomer(Number(e.target.value))}
              >
                <option value="">-- Choose Customer --</option>
                {customers.map(c => <option key={c.id} value={c.id}>{c.first_name} {c.last_name} - {c.phone}</option>)}
              </select>
              
              <div className="flex space-x-3 mt-6">
                <button onClick={() => setMode('menu')} className="flex-1 py-2 border border-gray-700 rounded text-gray-400 hover:bg-gray-800">Back</button>
                <button 
                  onClick={() => selectedCustomer && handleLinkCustomer(Number(selectedCustomer))} 
                  disabled={!selectedCustomer || loading} 
                  className="flex-1 py-2 bg-primary text-black font-bold rounded hover:bg-primary/90 disabled:opacity-50 flex justify-center items-center"
                >
                  {loading ? 'Linking...' : <><Check size={16} className="mr-1"/> Link to Invoice</>}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
