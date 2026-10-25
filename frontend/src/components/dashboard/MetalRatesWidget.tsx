import { useState, useEffect } from 'react';
import { getMetalRates } from '../../api/dashboardApi';
import { Activity } from 'lucide-react';

export default function MetalRatesWidget() {
  const [rates, setRates] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMetalRates().then(data => {
      setRates(data);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  if (loading) return <div className="h-48 bg-surface animate-pulse rounded-xl border border-gray-800"></div>;

  return (
    <div className="bg-surface rounded-xl border border-gray-800 p-6 flex flex-col h-full">
      <div className="flex items-center space-x-2 mb-4">
        <Activity size={20} className="text-primary" />
        <h3 className="font-bold text-lg text-textMain">Live Metal Rates</h3>
      </div>
      
      <div className="flex-1 space-y-3 overflow-auto pr-2">
        {rates.length === 0 ? (
          <p className="text-sm text-textMuted italic">No rates available.</p>
        ) : (
          rates.map((rate, i) => (
            <div key={i} className="flex justify-between items-center p-3 bg-background rounded border border-gray-800">
              <div>
                <span className="font-semibold text-textMain">{rate.purity_name}</span>
                <span className="text-xs text-textMuted ml-2">{rate.metal_type}</span>
              </div>
              <div className="font-bold text-primary">₹ {Number(rate.rate_per_gram).toLocaleString()} {rate.metal_type === 'Gold' ? '/ 10g' : '/ kg'}</div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
