import { useState } from 'react';
import { useBillingStore } from '../../store/billingStore';
import { Trash2, Edit, ChevronDown, ChevronRight, Info } from 'lucide-react';
import toast from 'react-hot-toast';

export default function BillTable() {
  const { cart, removeFromCart, editingItemId, setEditingItemId } = useBillingStore();
  const [expandedRowId, setExpandedRowId] = useState<string | null>(null);

  const toggleExpand = (id: string) => {
    setExpandedRowId(prev => prev === id ? null : id);
  };

  const handleEdit = (item: any) => {
    if (item.itemType === 'Gold') {
      const fallbackRate = item.rateDisplay > 10000 ? item.rateDisplay : (item.rateDisplay * 10 || 72500);
      useBillingStore.setState({ 
        goldForm: item.rawGold || {
          itemName: item.itemName || '',
          category: '',
          hsn: '',
          purity: item.purityDisplay || '22K Gold',
          touch: item.touchDisplay || 91.6,
          wastage: item.wastageDisplay || 0,
          grossWeight: item.grossWeight || 0,
          stoneWeight: item.stoneWeight || 0,
          ratePerGm: fallbackRate,
          makingChargeType: item.rawGold?.makingChargeType || 'flat',
          makingChargeValue: item.makingAmount || 0,
          hallmark: item.hallmark || 0,
          otherCharges: item.otherCharges || 0,
          discount: item.discount || 0
        }
      });
    } else if (item.itemType === 'Silver') {
      useBillingStore.setState({ 
        silverForm: item.rawSilver || {
          itemName: item.itemName || '',
          category: '',
          hsn: '',
          tanch: item.touchDisplay || 65,
          wastage: item.wastageDisplay || 0,
          silverPurity: item.purityDisplay || 'Fine',
          grossWeight: item.grossWeight || 0,
          stoneWeight: item.stoneWeight || 0,
          ratePerKg: item.rateDisplay || 90000,
          makingChargeType: item.rawSilver?.makingChargeType || 'flat',
          makingChargeValue: item.makingAmount || 0,
          otherCharges: item.otherCharges || 0,
          discount: item.discount || 0
        }
      });
    }

    setEditingItemId(item.id);
    toast.success(`Loaded "${item.itemName}" into calculator for editing`);

    // Smooth scroll to top of calculator
    const scrollContainer = document.querySelector('.custom-scrollbar.overflow-y-auto');
    if (scrollContainer) {
      scrollContainer.scrollTo({ top: 0, behavior: 'smooth' });
    } else {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  return (
    <div className="bg-surface border border-gray-800 rounded-xl overflow-hidden mt-4 flex-shrink-0 flex flex-col min-h-[350px]">
      <div className="bg-[#312e81] border-b border-[#3730a3] px-3 sm:px-4 py-2.5 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <h3 className="font-bold text-white text-xs sm:text-sm uppercase tracking-wider">Bill Item List</h3>
          <span className="text-[11px] sm:text-xs bg-indigo-900/80 text-indigo-200 px-2 py-0.5 rounded-full font-mono border border-indigo-700">
            {cart.length} {cart.length === 1 ? 'Item' : 'Items'}
          </span>
        </div>
        <div className="hidden sm:block text-[11px] text-indigo-200">
          Click any item to view complete calculation breakdown
        </div>
      </div>

      <div className="overflow-x-auto flex-1 custom-scrollbar">
        <table className="w-full text-xs sm:text-sm text-left min-w-[700px]">
          <thead className="text-[11px] text-textMuted uppercase bg-background/60 border-b border-gray-800 sticky top-0 z-10">
            <tr>
              <th className="px-3 py-3 w-10 text-center">#</th>
              <th className="px-3 py-3">Metal</th>
              <th className="px-4 py-3">Item Details</th>
              <th className="px-3 py-3 text-right">Gross Wt</th>
              <th className="px-3 py-3 text-right">Net Wt</th>
              <th className="px-3 py-3 text-right">Fine Wt</th>
              <th className="px-3 py-3 text-right">Rate</th>
              <th className="px-3 py-3 text-right">Making</th>
              <th className="px-4 py-3 text-right">Total Price</th>
              <th className="px-3 py-3 text-center w-28">Actions</th>
            </tr>
          </thead>
          <tbody>
            {cart.length === 0 ? (
              <tr>
                <td colSpan={10} className="px-4 py-16 text-center text-textMuted italic">
                  <div className="flex flex-col items-center justify-center gap-2">
                    <Info size={28} className="text-gray-600" />
                    <span>No items in bill yet.</span>
                    <span className="text-xs text-gray-500">Add items using the calculator or scan a barcode/tag above.</span>
                  </div>
                </td>
              </tr>
            ) : (
              cart.map((item, index) => {
                const isEditing = editingItemId === item.id;
                const isExpanded = expandedRowId === item.id;
                const isGold = item.itemType === 'Gold';

                return (
                  <tr key={item.id} className="group contents">
                    {/* Main Row */}
                    <tr 
                      className={`border-b border-gray-800/60 transition-colors cursor-pointer ${
                        isEditing 
                          ? 'bg-amber-500/10 border-l-4 border-amber-400 font-medium' 
                          : isExpanded
                          ? 'bg-gray-900/60'
                          : 'hover:bg-gray-900/30'
                      }`}
                      onClick={() => toggleExpand(item.id)}
                    >
                      {/* Index */}
                      <td className="px-3 py-3 text-center text-gray-400 font-mono text-xs">
                        {index + 1}
                      </td>

                      {/* Metal */}
                      <td className="px-3 py-3">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                          isGold 
                            ? 'bg-yellow-500/15 text-yellow-400 border border-yellow-500/30' 
                            : 'bg-gray-400/15 text-gray-300 border border-gray-500/30'
                        }`}>
                          {item.itemType}
                        </span>
                      </td>

                      {/* Item Details (Name + Purity Badge) */}
                      <td className="px-4 py-3">
                        <div className="flex flex-col">
                          <span className="font-semibold text-white text-xs sm:text-sm">
                            {item.itemName || `${item.itemType} Item`}
                          </span>
                          <div className="flex items-center gap-1.5 mt-0.5">
                            <span className="text-[10px] text-primary font-medium">
                              {item.purityDisplay || (isGold ? '22K Gold' : 'Fine')}
                            </span>
                            <span className="text-[10px] text-gray-500">•</span>
                            <span className="text-[10px] text-gray-400 font-mono">
                              Touch: {item.touchDisplay}%{item.wastageDisplay ? ` + ${item.wastageDisplay}% Wst` : ''}
                            </span>
                          </div>
                        </div>
                      </td>

                      {/* Gross Weight */}
                      <td className="px-3 py-3 text-right font-mono text-gray-300">
                        {(item.grossWeight || 0).toFixed(3)}g
                        {item.stoneWeight > 0 && (
                          <div className="text-[10px] text-gray-500 font-mono">
                            St: {(item.stoneWeight || 0).toFixed(3)}g
                          </div>
                        )}
                      </td>

                      {/* Net Weight */}
                      <td className="px-3 py-3 text-right font-mono font-medium text-white">
                        {(item.netWeight || 0).toFixed(3)}g
                      </td>

                      {/* Fine Weight */}
                      <td className="px-3 py-3 text-right font-mono font-bold text-primary">
                        {(item.fineWeight || 0).toFixed(3)}g
                      </td>

                      {/* Rate */}
                      <td className="px-3 py-3 text-right font-mono text-gray-300">
                        ₹{(item.rateDisplay || 0).toLocaleString()}
                        <div className="text-[9.5px] text-gray-500 font-mono">
                          {isGold ? 'per 10g' : 'per kg'}
                        </div>
                      </td>

                      {/* Making */}
                      <td className="px-3 py-3 text-right font-mono text-gray-300">
                        ₹{(item.makingAmount || 0).toFixed(2)}
                      </td>

                      {/* Total Amount */}
                      <td className="px-4 py-3 text-right font-mono font-bold text-white text-sm">
                        ₹{(item.taxableAmount || 0).toFixed(2)}
                      </td>

                      {/* Actions */}
                      <td className="px-3 py-3 text-center" onClick={e => e.stopPropagation()}>
                        <div className="flex items-center justify-center gap-1.5">
                          <button 
                            type="button"
                            onClick={() => toggleExpand(item.id)}
                            className="p-1 rounded text-gray-400 hover:text-white hover:bg-gray-800 transition-colors"
                            title={isExpanded ? "Collapse Details" : "View Full Details"}
                          >
                            {isExpanded ? <ChevronDown size={15} /> : <ChevronRight size={15} />}
                          </button>
                          <button 
                            type="button"
                            onClick={() => handleEdit(item)} 
                            className={`p-1 rounded transition-colors ${isEditing ? 'text-amber-400 bg-amber-400/20' : 'text-gray-400 hover:text-blue-400 hover:bg-gray-800'}`} 
                            title="Edit Item"
                          >
                            <Edit size={14} />
                          </button>
                          <button 
                            type="button"
                            onClick={() => removeFromCart(item.id)} 
                            className="p-1 rounded text-gray-400 hover:text-red-400 hover:bg-gray-800 transition-colors" 
                            title="Delete Item"
                          >
                            <Trash2 size={14} />
                          </button>
                        </div>
                      </td>
                    </tr>

                    {/* Expandable Breakdown Drawer */}
                    {isExpanded && (
                      <tr className="bg-[#121218] border-b border-gray-800">
                        <td colSpan={10} className="px-4 py-3">
                          <div className="bg-[#181822] border border-gray-700/60 rounded-xl p-3 sm:p-4 text-xs">
                            <div className="flex justify-between items-center pb-2 mb-3 border-b border-gray-700/50">
                              <span className="font-bold text-primary flex items-center gap-1.5 uppercase tracking-wider text-[11px]">
                                <Info size={14} /> Complete Item Calculation Breakdown
                              </span>
                              {item.stockItemId && (
                                <span className="bg-gray-800 text-gray-300 px-2 py-0.5 rounded text-[10px] font-mono">
                                  Inventory Item ID: {item.stockItemId} (Code: {item.id})
                                </span>
                              )}
                            </div>

                            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4">
                              {/* 1. Metal & Purity */}
                              <div className="bg-background/80 p-2.5 rounded-lg border border-gray-800 space-y-1">
                                <span className="text-[10px] text-gray-400 uppercase font-bold tracking-wider block">Metal & Purity</span>
                                <div className="text-white font-semibold">{item.itemName}</div>
                                <div className="text-primary font-medium">{item.purityDisplay || 'Standard'} ({item.itemType})</div>
                                <div className="text-gray-400">Touch: <strong className="text-white font-mono">{item.touchDisplay}%</strong></div>
                                {item.wastageDisplay > 0 && (
                                  <div className="text-gray-400">Wastage: <strong className="text-yellow-400 font-mono">+{item.wastageDisplay}%</strong></div>
                                )}
                              </div>

                              {/* 2. Weights */}
                              <div className="bg-background/80 p-2.5 rounded-lg border border-gray-800 space-y-1">
                                <span className="text-[10px] text-gray-400 uppercase font-bold tracking-wider block">Weight Breakdown</span>
                                <div className="flex justify-between text-gray-400">
                                  <span>Gross Wt:</span>
                                  <strong className="text-white font-mono">{(item.grossWeight || 0).toFixed(3)}g</strong>
                                </div>
                                <div className="flex justify-between text-gray-400">
                                  <span>Stone Wt:</span>
                                  <strong className="text-gray-300 font-mono">{(item.stoneWeight || 0).toFixed(3)}g</strong>
                                </div>
                                <div className="flex justify-between text-gray-400">
                                  <span>Net Weight:</span>
                                  <strong className="text-white font-mono">{(item.netWeight || 0).toFixed(3)}g</strong>
                                </div>
                                <div className="flex justify-between text-primary font-bold border-t border-gray-800 pt-1">
                                  <span>Fine Metal:</span>
                                  <span className="font-mono">{(item.fineWeight || 0).toFixed(3)}g</span>
                                </div>
                              </div>

                              {/* 3. Valuation */}
                              <div className="bg-background/80 p-2.5 rounded-lg border border-gray-800 space-y-1">
                                <span className="text-[10px] text-gray-400 uppercase font-bold tracking-wider block">Rate & Metal Value</span>
                                <div className="flex justify-between text-gray-400">
                                  <span>Applied Rate:</span>
                                  <strong className="text-white font-mono">₹{(item.rateDisplay || 0).toLocaleString()}</strong>
                                </div>
                                <div className="flex justify-between text-gray-400">
                                  <span>Rate / Gram:</span>
                                  <strong className="text-gray-300 font-mono">
                                    ₹{isGold ? ((item.rateDisplay || 0) / 10).toFixed(1) : ((item.rateDisplay || 0) / 1000).toFixed(1)}/g
                                  </strong>
                                </div>
                                <div className="flex justify-between text-yellow-400 font-bold border-t border-gray-800 pt-1">
                                  <span>Pure Metal Value:</span>
                                  <span className="font-mono">₹{(item.metalValue || 0).toFixed(2)}</span>
                                </div>
                              </div>

                              {/* 4. Charges & Total */}
                              <div className="bg-background/80 p-2.5 rounded-lg border border-gray-800 space-y-1">
                                <span className="text-[10px] text-gray-400 uppercase font-bold tracking-wider block">Charges & Amount</span>
                                <div className="flex justify-between text-gray-400">
                                  <span>Making Charges:</span>
                                  <strong className="text-white font-mono">₹{(item.makingAmount || 0).toFixed(2)}</strong>
                                </div>
                                {item.hallmark > 0 && (
                                  <div className="flex justify-between text-gray-400">
                                    <span>Hallmark (+):</span>
                                    <strong className="text-gray-300 font-mono">₹{(item.hallmark || 0).toFixed(2)}</strong>
                                  </div>
                                )}
                                {item.otherCharges > 0 && (
                                  <div className="flex justify-between text-gray-400">
                                    <span>Other Charges (+):</span>
                                    <strong className="text-gray-300 font-mono">₹{(item.otherCharges || 0).toFixed(2)}</strong>
                                  </div>
                                )}
                                {item.discount > 0 && (
                                  <div className="flex justify-between text-red-400">
                                    <span>Discount (-):</span>
                                    <strong className="font-mono">− ₹{(item.discount || 0).toFixed(2)}</strong>
                                  </div>
                                )}
                                <div className="flex justify-between text-green-400 font-bold border-t border-gray-800 pt-1">
                                  <span>Total Item Amount:</span>
                                  <span className="font-mono text-sm">₹{(item.taxableAmount || 0).toFixed(2)}</span>
                                </div>
                              </div>
                            </div>
                          </div>
                        </td>
                      </tr>
                    )}
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
