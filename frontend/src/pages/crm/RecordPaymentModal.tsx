import { useState } from 'react';
import { X } from 'lucide-react';
import { axiosClient } from '../../api/axiosClient';
import toast from 'react-hot-toast';

export default function RecordPaymentModal({
  isOpen,
  onClose,
  onSuccess,
  entityId,
  isSupplier
}: {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  entityId: number;
  isSupplier: boolean;
}) {
  const [formData, setFormData] = useState({
    voucher_type: 'Payment',
    voucher_number: '',
    description: '',
    debit: 0,
    credit: 0,
    gold_debit: 0,
    gold_credit: 0,
    silver_debit: 0,
    silver_credit: 0,
  });

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (isSupplier) {
        await axiosClient.post(`/sellers/${entityId}/ledger`, formData);
      } else {
        await axiosClient.post(`/customers/${entityId}/ledger`, formData);
      }
      toast.success('Ledger updated successfully!');
      onSuccess();
      onClose();
    } catch (error) {
      toast.error('Failed to update ledger');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-2 sm:p-4 overflow-y-auto">
      <div className="bg-surface border border-gray-800 rounded-xl shadow-2xl w-full max-w-2xl max-h-[92vh] flex flex-col overflow-hidden my-auto">
        <div className="p-3.5 sm:p-4 border-b border-gray-800 flex justify-between items-center bg-black/20 shrink-0">
          <h2 className="text-base sm:text-lg font-bold text-primary uppercase tracking-widest truncate">
            Record {isSupplier ? 'Supplier' : 'Customer'} Settlement
          </h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white transition-colors p-1">
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-4 sm:p-6 space-y-4 sm:space-y-6 overflow-y-auto custom-scrollbar flex-1">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
            <div>
              <label className="block text-xs font-bold text-textMuted uppercase mb-1">Voucher Type</label>
              <select
                className="w-full bg-background border border-gray-700 rounded p-2 text-sm text-white"
                value={formData.voucher_type}
                onChange={e => setFormData({ ...formData, voucher_type: e.target.value })}
              >
                <option value="Payment">Payment</option>
                <option value="Receipt">Receipt</option>
                <option value="Metal Settlement">Metal Settlement</option>
                <option value="Manual">Manual</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-bold text-textMuted uppercase mb-1">Ref / Voucher No.</label>
              <input
                type="text"
                className="w-full bg-background border border-gray-700 rounded p-2 text-sm text-white"
                value={formData.voucher_number}
                onChange={e => setFormData({ ...formData, voucher_number: e.target.value })}
                placeholder="e.g. PAY-123"
              />
            </div>
            <div className="col-span-1 sm:col-span-2">
              <label className="block text-xs font-bold text-textMuted uppercase mb-1">Remarks / Description</label>
              <input
                type="text"
                className="w-full bg-background border border-gray-700 rounded p-2 text-sm text-white"
                value={formData.description}
                onChange={e => setFormData({ ...formData, description: e.target.value })}
                placeholder="e.g. Received Cash for Due Bill"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6 bg-black/20 p-3 sm:p-4 rounded border border-gray-800">
            <div>
              <h3 className="text-sm font-bold text-red-400 mb-4 border-b border-gray-800 pb-2">
                {isSupplier ? 'Debit (We Pay Them)' : 'Debit (They Owe Us)'}
              </h3>
              <div className="space-y-3">
                <div>
                  <label className="block text-xs text-gray-400 mb-1">Amount (₹)</label>
                  <input type="number" step="0.01" className="w-full bg-background border border-gray-700 rounded p-2 text-white" value={formData.debit} onChange={e => setFormData({ ...formData, debit: parseFloat(e.target.value) || 0 })} />
                </div>
                <div>
                  <label className="block text-xs text-yellow-500 mb-1">Gold (g)</label>
                  <input type="number" step="0.001" className="w-full bg-background border border-gray-700 rounded p-2 text-white" value={formData.gold_debit} onChange={e => setFormData({ ...formData, gold_debit: parseFloat(e.target.value) || 0 })} />
                </div>
                <div>
                  <label className="block text-xs text-gray-300 mb-1">Silver (g)</label>
                  <input type="number" step="0.001" className="w-full bg-background border border-gray-700 rounded p-2 text-white" value={formData.silver_debit} onChange={e => setFormData({ ...formData, silver_debit: parseFloat(e.target.value) || 0 })} />
                </div>
              </div>
            </div>

            <div>
              <h3 className="text-sm font-bold text-green-400 mb-4 border-b border-gray-800 pb-2">
                {isSupplier ? 'Credit (They Billed Us)' : 'Credit (They Paid Us)'}
              </h3>
              <div className="space-y-3">
                <div>
                  <label className="block text-xs text-gray-400 mb-1">Amount (₹)</label>
                  <input type="number" step="0.01" className="w-full bg-background border border-gray-700 rounded p-2 text-white" value={formData.credit} onChange={e => setFormData({ ...formData, credit: parseFloat(e.target.value) || 0 })} />
                </div>
                <div>
                  <label className="block text-xs text-yellow-500 mb-1">Gold (g)</label>
                  <input type="number" step="0.001" className="w-full bg-background border border-gray-700 rounded p-2 text-white" value={formData.gold_credit} onChange={e => setFormData({ ...formData, gold_credit: parseFloat(e.target.value) || 0 })} />
                </div>
                <div>
                  <label className="block text-xs text-gray-300 mb-1">Silver (g)</label>
                  <input type="number" step="0.001" className="w-full bg-background border border-gray-700 rounded p-2 text-white" value={formData.silver_credit} onChange={e => setFormData({ ...formData, silver_credit: parseFloat(e.target.value) || 0 })} />
                </div>
              </div>
            </div>
          </div>

          <div className="flex justify-end gap-3 mt-6">
            <button type="button" onClick={onClose} className="px-4 py-2 text-sm font-bold text-gray-400 hover:text-white transition-colors">Cancel</button>
            <button type="submit" className="bg-primary text-black px-6 py-2 rounded font-bold text-sm hover:bg-primary/90 transition-colors shadow-[0_0_15px_rgba(212,175,55,0.3)]">Save Record</button>
          </div>
        </form>
      </div>
    </div>
  );
}
