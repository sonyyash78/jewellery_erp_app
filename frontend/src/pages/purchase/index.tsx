import { useState } from 'react';
import PurchaseMetalForm from './PurchaseMetalForm';
import { usePurchaseStore } from '../../store/purchaseStore';
import { Save, Printer, Trash2, FileText } from 'lucide-react';
import toast from 'react-hot-toast';
import PurchaseCheckoutModal from './PurchaseCheckoutModal';

export default function Purchase() {
  const { items, gstState, setGstState, removeItem, clearCart } = usePurchaseStore();
  const [showCheckout, setShowCheckout] = useState(false);

  const totalTaxable = items.reduce((sum, item) => sum + item.taxableAmount, 0);
  
  let cgst = 0, sgst = 0, igst = 0;
  if (gstState === 'same_state') {
    cgst = totalTaxable * 0.015;
    sgst = totalTaxable * 0.015;
  } else if (gstState === 'different_state') {
    igst = totalTaxable * 0.03;
  }
  
  const grandTotal = totalTaxable + cgst + sgst + igst;

  const handleSavePurchase = () => {
    if (items.length === 0) return toast.error("No items in purchase receipt");
    setShowCheckout(true);
  };

  const getPayload = () => {
    return {
      total_taxable: totalTaxable,
      cgst,
      sgst,
      igst,
      grand_total: grandTotal,
      items: items.map(i => {
        const defaultTouch = i.metalType === 'Gold' ? 91.6 : 99.9;
        const touch = Number(i.touchPurity || defaultTouch);
        return {
          metal_type: i.metalType,
          item_name: i.itemName,
          category: i.category,
          gross_weight: Number(i.grossWeight),
          stone_weight: Number(i.stoneWeight || 0),
          net_weight: Number(i.netWeight),
          touch_purity: touch > 0 ? touch : defaultTouch,
          wastage: Number(i.wastage || 0),
          fine_weight: Number(i.fineWeight),
          metal_rate: Number(i.metalRate || 0),
          metal_value: Number(i.metalValue || 0),
          labour_charge: Number(i.labourCharge || 0),
          testing_melting_charge: Number(i.testingMeltingCharge || 0),
          hallmark_charge: Number(i.hallmarkCharge || 0),
          other_charges: Number(i.otherCharges || 0),
          discount: Number(i.discount || 0),
          taxable_amount: Number(i.taxableAmount || 0)
        };
      })
    };
  };

  return (
    <div className="h-auto lg:h-[calc(100vh-6rem)] flex flex-col overflow-y-auto lg:overflow-hidden pb-8 lg:pb-0">

      <div className="flex-1 flex flex-col lg:flex-row gap-4 overflow-visible lg:overflow-hidden">
        {/* Left Column: Calculators */}
        <div className="w-full lg:flex-[3] min-h-0 flex flex-col">
          <PurchaseMetalForm />
        </div>

        {/* Right Column: Receipt Summary */}
        <div className="w-full lg:flex-[2] bg-surface border border-primary/30 rounded-xl shadow-lg flex flex-col min-h-[420px] lg:min-h-0 overflow-hidden">
          <div className="bg-background border-b border-gray-800 p-4 flex justify-between items-center">
            <h2 className="text-lg font-bold text-primary flex items-center gap-2 uppercase tracking-widest"><FileText size={20}/> Purchase Receipt</h2>
            <span className="text-xs font-mono bg-primary/10 text-primary px-2 py-1 rounded">ITEMS: {items.length}</span>
          </div>

          <div className="flex-1 overflow-y-auto p-4 custom-scrollbar space-y-3">
            {items.length === 0 ? (
              <div className="h-full flex items-center justify-center text-textMuted text-sm italic">No items added yet</div>
            ) : (
              items.map((item) => (
                <div key={item.id} className="bg-background border border-gray-800 rounded p-3 relative group">
                  <div className="absolute top-2 right-2 flex space-x-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button 
                      onClick={() => {
                        if (item.metalType === 'Gold') {
                          usePurchaseStore.setState({
                            goldForm: {
                              itemName: item.itemName,
                              category: item.category,
                              grossWeight: item.grossWeight,
                              stoneWeight: item.stoneWeight,
                              touchPurity: item.touchPurity,
                              wastage: item.wastage,
                              metalRate: item.metalRate,
                              makingChargeType: 'flat',
                              makingChargeValue: 0,
                              labourCharge: item.labourCharge,
                              hallmarkCharge: item.hallmarkCharge,
                              otherCharges: item.otherCharges,
                              discount: item.discount
                            }
                          });
                        } else {
                          usePurchaseStore.setState({
                            silverForm: {
                              itemName: item.itemName,
                              grossWeight: item.grossWeight,
                              stoneWeight: item.stoneWeight || 0,
                              tanch: item.touchPurity,
                              wastage: item.wastage,
                              metalRate: item.metalRate,
                              makingChargeType: item.makingChargeType || 'flat',
                              makingChargeValue: item.makingChargeValue ?? item.labourCharge ?? 0,
                              testingMeltingCharge: item.testingMeltingCharge,
                              otherCharges: item.otherCharges,
                              discount: item.discount
                            }
                          });
                        }
                        usePurchaseStore.getState().setEditingItemId(item.id);
                        import('react-hot-toast').then(mod => mod.default.success("Item loaded into calculator for editing"));
                      }} 
                      className="text-gray-600 hover:text-blue-400 transition-colors"
                      title="Edit Item"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 20h9"></path><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"></path></svg>
                    </button>
                    <button onClick={() => removeItem(item.id)} className="text-gray-600 hover:text-red-400 transition-colors" title="Delete Item">
                      <Trash2 size={16} />
                    </button>
                  </div>
                  <div className="flex justify-between items-start mb-2 pr-12">
                    <div>
                      <span className={`text-xs font-bold px-1.5 py-0.5 rounded mr-2 ${item.metalType === 'Gold' ? 'bg-primary/20 text-primary' : 'bg-gray-700 text-gray-300'}`}>{item.metalType}</span>
                      <span className="text-sm text-textMain font-medium">{item.itemName}</span>
                    </div>
                    <span className="text-sm font-mono text-textMain">₹{item.taxableAmount.toFixed(2)}</span>
                  </div>
                  <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs text-textMuted">
                    <div className="flex justify-between"><span>Gross:</span><span className="font-mono">{item.grossWeight}g</span></div>
                    <div className="flex justify-between"><span>Purity/Tanch:</span><span className="font-mono">{item.touchPurity}%</span></div>
                    <div className="flex justify-between"><span>Rec. Fine:</span><span className="font-mono text-primary">{item.fineWeight.toFixed(3)}g</span></div>
                    <div className="flex justify-between"><span>Rate:</span><span className="font-mono">₹{item.metalRate}</span></div>
                  </div>
                </div>
              ))
            )}
          </div>

          <div className="bg-background border-t border-gray-800 p-4">
            <div className="flex justify-between items-center mb-3">
              <span className="text-sm text-textMuted">GST Type</span>
              <div className="flex gap-2">
                <button onClick={() => setGstState('same_state')} className={`px-2 py-1 rounded text-xs font-bold transition-colors ${gstState === 'same_state' ? 'bg-primary text-black' : 'bg-gray-800 text-gray-400'}`}>Same State (3%)</button>
                <button onClick={() => setGstState('different_state')} className={`px-2 py-1 rounded text-xs font-bold transition-colors ${gstState === 'different_state' ? 'bg-primary text-black' : 'bg-gray-800 text-gray-400'}`}>Diff State (IGST)</button>
                <button onClick={() => setGstState('none')} className={`px-2 py-1 rounded text-xs font-bold transition-colors ${gstState === 'none' ? 'bg-primary text-black' : 'bg-gray-800 text-gray-400'}`}>Without GST</button>
              </div>
            </div>

            <div className="space-y-1 mb-4">
              <div className="flex justify-between text-sm text-textMuted"><span>Total Taxable</span><span className="font-mono">₹{totalTaxable.toFixed(2)}</span></div>
              {gstState === 'same_state' ? (
                <>
                  <div className="flex justify-between text-sm text-textMuted"><span>CGST (1.5%)</span><span className="font-mono">₹{cgst.toFixed(2)}</span></div>
                  <div className="flex justify-between text-sm text-textMuted"><span>SGST (1.5%)</span><span className="font-mono">₹{sgst.toFixed(2)}</span></div>
                </>
              ) : gstState === 'different_state' ? (
                <div className="flex justify-between text-sm text-textMuted"><span>IGST (3.0%)</span><span className="font-mono">₹{igst.toFixed(2)}</span></div>
              ) : (
                <div className="flex justify-between text-sm text-textMuted"><span>GST (0%)</span><span className="font-mono">₹0.00</span></div>
              )}
              <div className="flex justify-between text-xl font-bold text-primary pt-2 border-t border-gray-800 mt-2">
                <span>GRAND TOTAL</span><span className="font-mono">₹{grandTotal.toFixed(2)}</span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <button 
                disabled={items.length === 0}
                onClick={handleSavePurchase}
                className="bg-primary hover:bg-primary-dark text-black font-bold py-3 rounded flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
              >
                <Save size={18} /> Save Purchase
              </button>
              <button disabled className="bg-gray-800 text-gray-500 font-bold py-3 rounded flex items-center justify-center gap-2 cursor-not-allowed">
                <Printer size={18} /> Print Receipt
              </button>
            </div>
          </div>
        </div>
      </div>
      
      {showCheckout && (
        <PurchaseCheckoutModal 
          payload={getPayload()}
          grandTotal={grandTotal}
          onClose={() => setShowCheckout(false)}
          onSuccess={() => {
            setShowCheckout(false);
            clearCart();
          }}
        />
      )}
    </div>
  );
}
