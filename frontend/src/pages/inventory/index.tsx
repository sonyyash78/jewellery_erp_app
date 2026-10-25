import { useState, useEffect, useRef } from 'react';
import { useInventoryStore } from '../../store/inventoryStore';
import type { StockItem } from '../../store/inventoryStore';
import { axiosClient } from '../../api/axiosClient';
import { Package, PlusCircle, Search, Printer, Trash2, Download, Edit2 } from 'lucide-react';
import InventoryForm from './InventoryForm';
import { PrintLabel } from '../../components/PrintLabel';
import { ItemQRCode } from '../../components/ItemQRCode';
import QRCode from 'qrcode';
import { useReactToPrint } from 'react-to-print';
import toast from 'react-hot-toast';

const InventoryTableRow = ({ item, onDelete, onDownload, onEdit }: { item: StockItem, onDelete: (id: number) => void, onDownload: (path: string, code: string) => void, onEdit: (item: StockItem) => void }) => {
  const contentRef = useRef<HTMLDivElement>(null);
  
  const handlePrint = useReactToPrint({
    contentRef: contentRef,
  });

  return (
    <tr className="hover:bg-gray-800/30 transition-colors">
      <td className="py-2 px-4">
        {item.item_code ? (
          <ItemQRCode itemCode={item.item_code} serverPath={item.qr_code_path} className="w-12 h-12 bg-white p-0.5 rounded object-contain shadow-sm border border-gray-700/60" />
        ) : <span className="text-xs text-gray-600">N/A</span>}
      </td>
      <td className="py-3 px-4 font-mono font-bold text-gray-300">{item.item_code}</td>
      <td className="py-3 px-4 text-textMain">{item.item_name}</td>
      <td className="py-3 px-4">
        <div className="flex flex-col">
          <span className="text-gray-300">{item.category}</span>
          <span className="text-xs text-primary">{item.metal} {item.purity && `• ${item.purity}`}</span>
        </div>
      </td>
      <td className="py-3 px-4 font-mono">
        <div className="flex flex-col">
          <span className="text-primary font-bold">{item.net_weight}g</span>
          {item.tanch ? (
            <span className="text-xs text-green-400 font-medium tracking-tight mt-0.5">
              Fine: {((item.net_weight * (item.tanch + (item.wastage || 0))) / 100).toFixed(3)}g 
              ({item.tanch}%{item.wastage ? ` + ${item.wastage}%` : ''})
            </span>
          ) : null}
        </div>
      </td>
      <td className="py-3 px-4">
        <span className={`px-2 py-0.5 rounded text-xs font-bold ${item.status === 'Available' ? 'bg-green-900/30 text-green-400 border border-green-900/50' : 'bg-red-900/30 text-red-400 border border-red-900/50'}`}>
          {item.status}
        </span>
      </td>
      <td className="py-3 px-4 text-right">
        <div className="flex items-center justify-end gap-3">
          {item.qr_code_path && (
            <>
              <button onClick={() => handlePrint()} className="text-gray-400 hover:text-primary transition-colors" title="Print Label"><Printer size={18} /></button>
              <button onClick={() => onDownload(item.qr_code_path!, item.item_code)} className="text-gray-400 hover:text-blue-400 transition-colors" title="Download QR">
                <Download size={18} />
              </button>
            </>
          )}
          <button onClick={() => onEdit(item)} className="text-gray-400 hover:text-green-400 transition-colors" title="Edit">
            <Edit2 size={18} />
          </button>
          <button onClick={() => onDelete(item.id)} className="text-gray-400 hover:text-red-400 transition-colors" title="Delete">
            <Trash2 size={18} />
          </button>
        </div>

        {/* Hidden printable component */}
        <div className="hidden">
          <PrintLabel ref={contentRef} item={item} />
        </div>
      </td>
    </tr>
  );
};

export default function Inventory() {
  const { items, totalItems, totalWeight, setItems, searchQuery, setSearchQuery } = useInventoryStore();
  const [showForm, setShowForm] = useState(false);
  const [editingItem, setEditingItem] = useState<StockItem | null>(null);
  const [loading, setLoading] = useState(false);
  const [metalFilter, setMetalFilter] = useState('');
  
  const fetchItems = async () => {
    setLoading(true);
    try {
      const res = await axiosClient.get('/stock/', {
        params: { search: searchQuery, metal: metalFilter }
      });
      setItems(res.data.items, res.data.total, res.data.total_weight);
    } catch (e) {
      toast.error('Failed to fetch inventory');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchItems();
    
    // Auto-refresh when window regains focus (real-time across tabs)
    const onFocus = () => fetchItems();
    window.addEventListener('focus', onFocus);
    return () => window.removeEventListener('focus', onFocus);
  }, [searchQuery, metalFilter]);

  const handleDelete = async (id: number) => {
    if (!window.confirm("Delete this item?")) return;
    try {
      await axiosClient.delete(`/stock/${id}`);
      toast.success("Item deleted");
      fetchItems();
    } catch (e) {
      toast.error("Failed to delete");
    }
  };

  const handleDownloadQR = async (_path: string, itemCode: string) => {
    if (!itemCode) return;
    try {
      const dataUrl = await QRCode.toDataURL(itemCode, {
        width: 400,
        margin: 2,
        color: { dark: '#000000', light: '#ffffff' }
      });
      const link = document.createElement('a');
      link.href = dataUrl;
      link.download = `QR_${itemCode}.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      toast.success(`QR code downloaded for ${itemCode}`);
    } catch (e) {
      toast.error("Download failed");
    }
  };

  return (
    <div className="h-auto lg:h-[calc(100vh-6rem)] flex flex-col space-y-4 overflow-y-auto lg:overflow-hidden pb-8 lg:pb-0">
      {/* Dashboard Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4">
        <div className="bg-surface border border-gray-800 rounded-xl p-3.5 sm:p-4 shadow-lg flex items-center gap-3.5 sm:gap-4">
          <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-full bg-primary/10 flex items-center justify-center text-primary shrink-0"><Package size={22} /></div>
          <div><div className="text-textMuted text-xs sm:text-sm font-bold tracking-wider uppercase">Total Items</div><div className="text-xl sm:text-2xl font-bold font-mono">{totalItems}</div></div>
        </div>
        <div className="bg-surface border border-gray-800 rounded-xl p-3.5 sm:p-4 shadow-lg flex items-center gap-3.5 sm:gap-4">
          <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-full bg-primary/10 flex items-center justify-center text-primary shrink-0"><Package size={22} /></div>
          <div><div className="text-textMuted text-xs sm:text-sm font-bold tracking-wider uppercase">Total Weight (Net)</div><div className="text-xl sm:text-2xl font-bold font-mono text-primary">{totalWeight.toFixed(3)}g</div></div>
        </div>
        <div className="bg-surface border border-primary/20 rounded-xl p-3.5 sm:p-4 shadow-lg flex items-center justify-center cursor-pointer hover:bg-primary/5 transition-colors" onClick={() => setShowForm(true)}>
          <div className="flex flex-col items-center text-primary"><PlusCircle size={28} className="mb-1" /><span className="font-bold tracking-wider uppercase text-xs sm:text-sm">Add New Item</span></div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 bg-surface border border-gray-800 rounded-xl shadow-lg flex flex-col overflow-hidden min-h-[450px]">
        
        {/* Metal Tabs */}
        <div className="flex border-b border-gray-800 bg-background/50 overflow-x-auto whitespace-nowrap">
          <button 
            onClick={() => setMetalFilter('')}
            className={`px-4 sm:px-6 py-2.5 sm:py-3 font-bold uppercase tracking-wider text-xs sm:text-sm transition-colors ${metalFilter === '' ? 'text-primary border-b-2 border-primary bg-primary/5' : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/50'}`}
          >
            All Inventory
          </button>
          <button 
            onClick={() => setMetalFilter('Gold')}
            className={`px-4 sm:px-6 py-2.5 sm:py-3 font-bold uppercase tracking-wider text-xs sm:text-sm transition-colors ${metalFilter === 'Gold' ? 'text-primary border-b-2 border-primary bg-primary/5' : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/50'}`}
          >
            Gold Items
          </button>
          <button 
            onClick={() => setMetalFilter('Silver')}
            className={`px-4 sm:px-6 py-2.5 sm:py-3 font-bold uppercase tracking-wider text-xs sm:text-sm transition-colors ${metalFilter === 'Silver' ? 'text-primary border-b-2 border-primary bg-primary/5' : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/50'}`}
          >
            Silver Items
          </button>
        </div>

        {/* Toolbar */}
        <div className="p-3 sm:p-4 border-b border-gray-800 flex gap-3 sm:gap-4 bg-surface">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-2.5 text-gray-500" size={18} />
            <input 
              value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-background border border-gray-700 rounded-lg pl-10 pr-4 py-2 text-sm text-textMain focus:border-primary outline-none transition-colors" 
              placeholder="Search by Item Code or Name..." 
            />
          </div>
        </div>

        {/* Table */}
        <div className="flex-1 overflow-x-auto overflow-y-auto custom-scrollbar relative">
          {loading && <div className="absolute inset-0 bg-surface/50 z-10 flex items-center justify-center">Loading...</div>}
          <table className="w-full text-left text-sm text-textMuted min-w-[700px]">
            <thead className="bg-background sticky top-0 border-b border-gray-800 z-0">
              <tr>
                <th className="py-3 px-4 font-bold uppercase tracking-wider text-xs">QR Preview</th>
                <th className="py-3 px-4 font-bold uppercase tracking-wider text-xs">Item Code</th>
                <th className="py-3 px-4 font-bold uppercase tracking-wider text-xs">Name</th>
                <th className="py-3 px-4 font-bold uppercase tracking-wider text-xs">Category / Purity</th>
                <th className="py-3 px-4 font-bold uppercase tracking-wider text-xs">Net Wt</th>
                <th className="py-3 px-4 font-bold uppercase tracking-wider text-xs">Status</th>
                <th className="py-3 px-4 font-bold uppercase tracking-wider text-xs text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/50">
              {items.map((item) => (
                <InventoryTableRow key={item.id} item={item} onDelete={handleDelete} onDownload={handleDownloadQR} onEdit={(itm) => {setEditingItem(itm); setShowForm(true);}} />
              ))}
              {items.length === 0 && !loading && (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-gray-500 italic">No inventory items found. Add one above.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {showForm && <InventoryForm editItem={editingItem} onClose={() => {setShowForm(false); setEditingItem(null);}} onSaveSuccess={fetchItems} />}
    </div>
  );
}
