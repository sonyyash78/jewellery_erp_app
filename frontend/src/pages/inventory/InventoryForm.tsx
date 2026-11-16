import { useState, useEffect } from 'react';
import { X, Save, Building2 } from 'lucide-react';
import toast from 'react-hot-toast';
import { getErrorMessage } from '../../utils/errorUtils';
import { axiosClient } from '../../api/axiosClient';
import { useCompanyStore } from '../../store/companyStore';
import type { StockItem } from '../../store/inventoryStore';
import { validateWastage } from '../../utils/wastageValidation';

const InputLabel = ({ label }: { label: string }) => (
  <label className="block text-[10px] font-bold text-textMuted uppercase tracking-wider mb-1">{label}</label>
);

export default function InventoryForm({ 
  onClose, 
  onSaveSuccess, 
  editItem, 
  activeCompany 
}: { 
  onClose: () => void, 
  onSaveSuccess: () => void, 
  editItem?: StockItem | null, 
  activeCompany?: any 
}) {
  const [loading, setLoading] = useState(false);
  const { companies } = useCompanyStore();
  
  const [form, setForm] = useState({
    item_name: '', metal: 'Gold', category: '', hsn: '',
    purity: '22K916', tanch: '', wastage: '', gross_weight: '', stone_weight: '',
    making_type: 'flat', making_charge: '', hallmark: '', other_charges: '',
    location: '', shelf: '', description: '', status: 'Available',
    company_id: activeCompany?.id || 1
  });

  useEffect(() => {
    if (editItem) {
      setForm({
        item_name: editItem.item_name || '', 
        metal: editItem.metal || 'Gold', 
        category: editItem.category || '', 
        hsn: editItem.hsn || '',
        purity: editItem.purity || '22K916', 
        tanch: editItem.tanch?.toString() || '', 
        wastage: editItem.wastage?.toString() || '', 
        gross_weight: editItem.gross_weight?.toString() || '', 
        stone_weight: editItem.stone_weight?.toString() || '',
        making_type: editItem.making_type || 'flat', 
        making_charge: editItem.making_charge?.toString() || '', 
        hallmark: editItem.hallmark?.toString() || '', 
        other_charges: editItem.other_charges?.toString() || '', 
        location: editItem.location || '', 
        shelf: editItem.shelf || '', 
        description: editItem.description || '', 
        status: editItem.status || 'Available',
        company_id: editItem.company_id || activeCompany?.id || 1
      });
    } else {
      setForm(prev => ({
        ...prev,
        company_id: activeCompany?.id || 1
      }));
    }
  }, [editItem, activeCompany]);

  const netWeight = (Number(form.gross_weight) || 0) - (Number(form.stone_weight) || 0);

  const handleSave = async () => {
    if (!form.item_name || !form.gross_weight) {
      toast.error('Item Name and Gross Weight are required');
      return;
    }

    const wastageErr = validateWastage(Number(form.tanch) || 0, form.wastage);
    if (wastageErr) {
      toast.error(wastageErr);
      return;
    }

    setLoading(true);
    try {
      const payload = {
        ...form,
        company_id: Number(form.company_id) || activeCompany?.id || 1,
        tanch: form.tanch ? Number(form.tanch) : null,
        wastage: form.wastage === '' || form.wastage === null || form.wastage === undefined ? null : Number(form.wastage),
        gross_weight: Number(form.gross_weight),
        stone_weight: Number(form.stone_weight) || 0,
        net_weight: netWeight,
        making_charge: Number(form.making_charge) || 0,
        hallmark: Number(form.hallmark) || 0,
        other_charges: Number(form.other_charges) || 0,
      };

      if (editItem) {
        await axiosClient.put(`/stock/${editItem.id}`, payload);
        toast.success('Inventory Item updated successfully');
      } else {
        await axiosClient.post('/stock/', payload, {
          params: { company_id: payload.company_id }
        });
        toast.success('Inventory Item saved successfully');
      }
      onSaveSuccess();
      onClose();
    } catch (e: any) {
      toast.error(getErrorMessage(e, 'Failed to save item'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 z-50 flex justify-end">
      <div 
        className="bg-surface w-full max-w-2xl h-full border-l border-primary/20 shadow-2xl flex flex-col animate-slide-left"
        data-enter-container="true"
      >
        
        <div className="h-16 flex items-center justify-between px-6 border-b border-gray-800">
          <div className="flex items-center gap-3">
            <h2 className="text-lg font-bold text-primary uppercase tracking-widest">{editItem ? 'Edit Item' : 'Add New Item'}</h2>
            <span className={`text-xs px-2.5 py-0.5 rounded font-bold border ${form.company_id === 2 ? 'bg-blue-900/30 text-blue-400 border-blue-700/60' : 'bg-amber-900/30 text-amber-400 border-amber-700/60'}`}>
              {form.company_id === 2 ? 'GST Mode' : 'Normal / No-GST'}
            </span>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-white transition-colors"><X size={24} /></button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 sm:p-6 custom-scrollbar space-y-4 sm:space-y-6">
          {/* Company Assignment */}
          <div className="bg-background/80 p-3.5 rounded-lg border border-gray-800">
            <div className="flex items-center gap-2 mb-2">
              <Building2 size={16} className="text-primary" />
              <InputLabel label="Inventory Company / Store Type *" />
            </div>
            <div className="grid grid-cols-2 gap-3">
              {companies.map(c => (
                <button
                  type="button"
                  key={c.id}
                  onClick={() => setForm({ ...form, company_id: c.id })}
                  className={`py-2 px-3 rounded-lg text-xs font-bold border flex items-center justify-between transition-all ${
                    form.company_id === c.id
                      ? (c.gst_enabled 
                          ? 'bg-blue-950 border-blue-500 text-blue-300 ring-1 ring-blue-500' 
                          : 'bg-primary/10 border-primary text-primary ring-1 ring-primary')
                      : 'bg-surface border-gray-700 text-gray-400 hover:border-gray-600'
                  }`}
                >
                  <span>{c.name}</span>
                  <span className={`text-[10px] px-1.5 py-0.5 rounded ${c.gst_enabled ? 'bg-blue-900/50 text-blue-300' : 'bg-amber-900/50 text-amber-300'}`}>
                    {c.gst_enabled ? 'GST' : 'Without GST'}
                  </span>
                </button>
              ))}
            </div>
          </div>

          {/* Section 1: Basic Info */}
          <div>
            <h3 className="text-sm font-bold text-gray-300 border-b border-gray-800 pb-2 mb-3">Basic Information</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4 mb-3 sm:mb-4">
              <div><InputLabel label="Item Name *" /><input autoFocus value={form.item_name} onChange={e=>setForm({...form, item_name: e.target.value})} className="w-full bg-background border border-gray-700 rounded px-3 py-2 text-sm text-textMain focus:border-primary outline-none" placeholder="e.g. Gold Chain 22K" /></div>
              <div><InputLabel label="Category" /><input value={form.category} onChange={e=>setForm({...form, category: e.target.value})} className="w-full bg-background border border-gray-700 rounded px-3 py-2 text-sm text-textMain focus:border-primary outline-none" placeholder="e.g. Ring, Chain, Kundan" /></div>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4">
              <div><InputLabel label="Metal" />
                <select value={form.metal} onChange={e=>setForm({...form, metal: e.target.value})} className="w-full bg-background border border-gray-700 rounded px-3 py-2 text-sm text-textMain focus:border-primary outline-none appearance-none">
                  <option value="Gold">Gold</option>
                  <option value="Silver">Silver</option>
                </select>
              </div>
              <div><InputLabel label="Purity" /><input value={form.purity} onChange={e=>setForm({...form, purity: e.target.value})} className="w-full bg-background border border-gray-700 rounded px-3 py-2 text-sm text-textMain focus:border-primary outline-none" placeholder="e.g. 22K916" /></div>
              <div><InputLabel label="HSN Code" /><input value={form.hsn} onChange={e=>setForm({...form, hsn: e.target.value})} className="w-full bg-background border border-gray-700 rounded px-3 py-2 text-sm text-textMain focus:border-primary outline-none" placeholder={form.metal === 'Silver' ? '711311' : '711319'} /></div>
            </div>
          </div>

          {/* Section 2: Weight & Purity */}
          <div>
            <h3 className="text-sm font-bold text-gray-300 border-b border-gray-800 pb-2 mb-3">Weight & Purity Details</h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2 sm:gap-4">
              <div><InputLabel label="Gross Wt(g) *" /><input type="number" step="0.001" value={form.gross_weight} onChange={e=>setForm({...form, gross_weight: e.target.value})} className="w-full bg-background border border-gray-700 rounded px-3 py-2 text-sm text-textMain focus:border-primary outline-none font-mono" /></div>
              <div><InputLabel label="Stone Wt(g)" /><input type="number" step="0.001" value={form.stone_weight} onChange={e=>setForm({...form, stone_weight: e.target.value})} className="w-full bg-background border border-gray-700 rounded px-3 py-2 text-sm text-textMain focus:border-primary outline-none font-mono" /></div>
              <div><InputLabel label="Net Wt(g)" /><input disabled value={netWeight.toFixed(3)} className="w-full bg-gray-900 border border-gray-800 rounded px-3 py-2 text-sm text-primary font-bold outline-none font-mono cursor-not-allowed" /></div>
              <div><InputLabel label="Touch / Tanch" /><input type="number" step="0.1" value={form.tanch} onChange={e=>setForm({...form, tanch: e.target.value})} className="w-full bg-background border border-gray-700 rounded px-3 py-2 text-sm text-textMain focus:border-primary outline-none font-mono" placeholder="e.g. 91.6" /></div>
              <div><InputLabel label="Wastage (gm) *" /><input type="number" step="0.1" min="0" value={form.wastage} onChange={e=>setForm({...form, wastage: e.target.value})} className="w-full bg-background border border-gray-700 rounded px-3 py-2 text-sm text-textMain focus:border-primary outline-none font-mono" placeholder="Required (0+)" /></div>
              <div><InputLabel label="Fine Wt(g)" /><input disabled value={((netWeight * ((Number(form.tanch) || 0) + (Number(form.wastage) || 0))) / 100).toFixed(3)} className="w-full bg-gray-900 border border-gray-800 rounded px-3 py-2 text-sm text-green-400 font-bold outline-none font-mono cursor-not-allowed" /></div>
            </div>
          </div>

          {/* Section 3: Charges */}
          <div>
            <h3 className="text-sm font-bold text-gray-300 border-b border-gray-800 pb-2 mb-3">Charges</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2 sm:gap-4">
              <div><InputLabel label="Making Type" />
                <select value={form.making_type} onChange={e=>setForm({...form, making_type: e.target.value})} className="w-full bg-background border border-gray-700 rounded px-3 py-2 text-sm text-textMain focus:border-primary outline-none appearance-none">
                  <option value="flat">Flat (₹)</option>
                  <option value="per_gram">Per Gram</option>
                  <option value="percentage">% of Metal</option>
                </select>
              </div>
              <div><InputLabel label="Making Chg" /><input type="number" value={form.making_charge} onChange={e=>setForm({...form, making_charge: e.target.value})} className="w-full bg-background border border-gray-700 rounded px-3 py-2 text-sm text-textMain focus:border-primary outline-none font-mono" /></div>
              <div><InputLabel label="Hallmark" /><input type="number" value={form.hallmark} onChange={e=>setForm({...form, hallmark: e.target.value})} className="w-full bg-background border border-gray-700 rounded px-3 py-2 text-sm text-textMain focus:border-primary outline-none font-mono" /></div>
              <div><InputLabel label="Other Chg" /><input type="number" value={form.other_charges} onChange={e=>setForm({...form, other_charges: e.target.value})} className="w-full bg-background border border-gray-700 rounded px-3 py-2 text-sm text-textMain focus:border-primary outline-none font-mono" /></div>
            </div>
          </div>

          {/* Section 4: Location */}
          <div>
            <h3 className="text-sm font-bold text-gray-300 border-b border-gray-800 pb-2 mb-3">Storage & Status</h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4 mb-4">
              <div><InputLabel label="Location" /><input value={form.location} onChange={e=>setForm({...form, location: e.target.value})} className="w-full bg-background border border-gray-700 rounded px-3 py-2 text-sm text-textMain focus:border-primary outline-none" placeholder="e.g. Main Store" /></div>
              <div><InputLabel label="Shelf / Tray" /><input value={form.shelf} onChange={e=>setForm({...form, shelf: e.target.value})} className="w-full bg-background border border-gray-700 rounded px-3 py-2 text-sm text-textMain focus:border-primary outline-none" placeholder="e.g. Tray 5" /></div>
              <div><InputLabel label="Status" />
                <select value={form.status} onChange={e=>setForm({...form, status: e.target.value})} className="w-full bg-background border border-gray-700 rounded px-3 py-2 text-sm text-textMain focus:border-primary outline-none appearance-none">
                  <option value="Available">Available</option>
                  <option value="Reserved">Reserved</option>
                </select>
              </div>
            </div>
            <div>
              <InputLabel label="Description" />
              <textarea rows={3} value={form.description} onChange={e=>setForm({...form, description: e.target.value})} className="w-full bg-background border border-gray-700 rounded px-3 py-2 text-sm text-textMain focus:border-primary outline-none resize-none" placeholder="Optional notes..."></textarea>
            </div>
          </div>
        </div>

        <div className="p-4 sm:p-6 border-t border-gray-800 bg-background flex justify-end gap-2 sm:gap-3">
          <button type="button" onClick={onClose} className="px-6 py-2 rounded text-sm font-bold text-gray-400 hover:text-white transition-colors">Cancel (Esc)</button>
          <button 
            type="submit" 
            data-save-only="true"
            data-action="submit"
            onClick={handleSave} 
            disabled={loading} 
            className="bg-primary hover:bg-primary-dark text-black px-6 py-2 rounded text-sm font-bold flex items-center gap-2 transition-colors disabled:opacity-50"
          >
            <Save size={16} /> {editItem ? 'Update Item (Enter)' : 'Save Item & Generate QR (Enter)'}
          </button>
        </div>

      </div>
    </div>
  );
}
