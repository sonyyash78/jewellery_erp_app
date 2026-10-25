import { useBillingStore } from '../../store/billingStore';
import { X } from 'lucide-react';
import { useState } from 'react';
import toast from 'react-hot-toast';

interface LiveRatesModalProps {
  onClose: () => void;
}

export default function LiveRatesModal({ onClose }: LiveRatesModalProps) {
  const { liveRates, updateLiveRates } = useBillingStore();
  const [rates, setRates] = useState({ ...liveRates });

  const handleSave = () => {
    updateLiveRates(rates);
    useBillingStore.getState().updateGoldForm('ratePerGm', rates.gold22k || rates.gold24k);
    useBillingStore.getState().updateSilverForm('ratePerKg', rates.silver);
    toast.success('Live metal rates updated for billing');
    onClose();
  };

  const updateRate = (key: keyof typeof rates, value: string) => {
    setRates((prev) => ({ ...prev, [key]: Number(value) }));
  };

  return (
    <div className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4 backdrop-blur-sm">
      <div className="bg-surface border border-gray-800 rounded-2xl p-6 shadow-2xl w-full max-w-sm relative">
        <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 rounded-full blur-3xl -mr-10 -mt-10 pointer-events-none"></div>
        
        <div className="flex justify-between items-center mb-6 relative z-10">
          <h2 className="text-primary font-bold text-lg">Live Metal Rates Config</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white transition-colors">
            <X size={20} />
          </button>
        </div>

        <div className="space-y-4 relative z-10">
          <div className="bg-background border border-gray-700 rounded-lg p-3 relative">
            <label className="absolute -top-2 left-3 bg-background px-1 text-[10px] font-bold text-gray-400 uppercase">24K Benchmark Gold Rate (₹/10g)</label>
            <div className="flex items-center text-primary mt-1">
              <span className="mr-2">₹</span>
              <input 
                type="number" 
                value={rates.gold24k || ''} 
                onChange={(e) => updateRate('gold24k', e.target.value)}
                className="w-full bg-transparent outline-none font-mono text-lg text-white" 
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="bg-background border border-gray-700 rounded-lg p-3 relative">
              <label className="absolute -top-2 left-3 bg-background px-1 text-[10px] font-bold text-gray-400 uppercase">22K Rate</label>
              <div className="flex items-center text-primary mt-1">
                <span className="mr-2">₹</span>
                <input type="number" value={rates.gold22k || ''} onChange={(e) => updateRate('gold22k', e.target.value)} className="w-full bg-transparent outline-none font-mono text-white" />
              </div>
            </div>
            
            <div className="bg-background border border-gray-700 rounded-lg p-3 relative">
              <label className="absolute -top-2 left-3 bg-background px-1 text-[10px] font-bold text-gray-400 uppercase">20K Rate</label>
              <div className="flex items-center text-primary mt-1">
                <span className="mr-2">₹</span>
                <input type="number" value={rates.gold20k || ''} onChange={(e) => updateRate('gold20k', e.target.value)} className="w-full bg-transparent outline-none font-mono text-white" />
              </div>
            </div>

            <div className="bg-background border border-gray-700 rounded-lg p-3 relative">
              <label className="absolute -top-2 left-3 bg-background px-1 text-[10px] font-bold text-gray-400 uppercase">18K Rate</label>
              <div className="flex items-center text-primary mt-1">
                <span className="mr-2">₹</span>
                <input type="number" value={rates.gold18k || ''} onChange={(e) => updateRate('gold18k', e.target.value)} className="w-full bg-transparent outline-none font-mono text-white" />
              </div>
            </div>

            <div className="bg-background border border-gray-700 rounded-lg p-3 relative">
              <label className="absolute -top-2 left-3 bg-background px-1 text-[10px] font-bold text-gray-400 uppercase">14K Rate</label>
              <div className="flex items-center text-primary mt-1">
                <span className="mr-2">₹</span>
                <input type="number" value={rates.gold14k || ''} onChange={(e) => updateRate('gold14k', e.target.value)} className="w-full bg-transparent outline-none font-mono text-white" />
              </div>
            </div>
          </div>

          <div className="bg-background border border-gray-700 rounded-lg p-3 relative mt-6">
            <label className="absolute -top-2 left-3 bg-background px-1 text-[10px] font-bold text-gray-400 uppercase">Silver Rate (₹ / 1kg)</label>
            <div className="flex items-center text-primary mt-1">
              <span className="mr-2">₹</span>
              <input type="number" value={rates.silver || ''} onChange={(e) => updateRate('silver', e.target.value)} className="w-full bg-transparent outline-none font-mono text-lg text-white" />
            </div>
          </div>
        </div>

        <div className="mt-6 flex justify-end relative z-10">
          <button onClick={handleSave} className="flex items-center space-x-2 text-primary hover:text-primary-dark font-bold px-6 py-2 transition-colors">
            <span>Done</span>
          </button>
        </div>
      </div>
    </div>
  );
}
