import { useEffect, useState } from 'react';
import { Check, Plus, Radio, RefreshCw, Trash2, WifiOff, X } from 'lucide-react';
import toast from 'react-hot-toast';
import { type CustomRateItem, type LiveRates, useBillingStore } from '../../store/billingStore';

interface LiveRatesModalProps {
  onClose: () => void;
}

const formatTimestamp = (iso?: string | null): string => {
  if (!iso) return 'Just now';
  const dt = new Date(iso);
  if (Number.isNaN(dt.getTime())) return 'Live';
  return dt.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
};

const STANDARD_GOLD_FIELDS: Array<{ key: keyof Omit<LiveRates, 'silver'>; label: string }> = [
  { key: 'gold22k', label: '22K Rate (₹/10g)' },
  { key: 'gold20k', label: '20K Rate (₹/10g)' },
  { key: 'gold18k', label: '18K Rate (₹/10g)' },
  { key: 'gold14k', label: '14K Rate (₹/10g)' },
];

export default function LiveRatesModal({ onClose }: LiveRatesModalProps) {
  const {
    liveRates,
    marketRates,
    marketMeta,
    customRates,
    autoSyncLive,
    isOfflineFallback,
    liveRatesLastUpdated,
    liveRatesSyncing,
    fetchLiveRates,
    saveLiveRatesConfig,
    updateGoldForm,
    updateSilverForm,
  } = useBillingStore();

  const [rates, setRates] = useState<LiveRates>({ ...liveRates });
  const [autoSync, setAutoSync] = useState<boolean>(autoSyncLive);
  const [customDraft, setCustomDraft] = useState<CustomRateItem[]>(customRates);
  const [saving, setSaving] = useState(false);

  // Add Custom Rate inline form state
  const [newName, setNewName] = useState('');
  const [newMetal, setNewMetal] = useState<'Gold' | 'Silver'>('Gold');
  const [newPurity, setNewPurity] = useState('91.6');
  const [newRate, setNewRate] = useState('');

  useEffect(() => {
    fetchLiveRates(false);
  }, [fetchLiveRates]);

  useEffect(() => {
    if (autoSync) {
      setRates({ ...marketRates });
    }
  }, [marketRates, autoSync]);

  const handleSyncLiveNow = async () => {
    const res = await fetchLiveRates(true);
    if (!res) {
      toast.error('Could not reach live market API right now');
      return;
    }
    if (res.is_offline_fallback) {
      toast('Showing cached market rate (offline)', { icon: '📡' });
    } else {
      toast.success('Live Gold & Silver API synced');
    }
    if (autoSync) {
      setRates({ ...res.market_rates });
    }
  };

  const handleToggleAutoSync = () => {
    const next = !autoSync;
    setAutoSync(next);
    if (next) {
      setRates({ ...marketRates });
    }
  };

  const handleApplyMarketToDraft = () => {
    setRates({ ...marketRates });
    setAutoSync(true);
    toast.success('Live API rates applied to active rate boxes');
  };

  const updateStandardRate = (key: keyof LiveRates, value: string) => {
    setAutoSync(false);
    setRates((prev) => ({ ...prev, [key]: Number(value) || 0 }));
  };

  const handleAddCustomRate = () => {
    const trimmedName = newName.trim();
    const numericRate = Number(newRate);
    const numericPurity = Number(newPurity) || (newMetal === 'Gold' ? 91.6 : 99.9);
    if (!trimmedName) {
      toast.error('Please enter a custom rate name');
      return;
    }
    if (!Number.isFinite(numericRate) || numericRate <= 0) {
      toast.error('Please enter a valid custom rate amount');
      return;
    }

    const item: CustomRateItem = {
      id: `custom-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
      name: trimmedName,
      metal_type: newMetal,
      purity_percent: numericPurity,
      rate: numericRate,
      unit: newMetal === 'Gold' ? '/ 10g' : '/ kg',
    };

    setCustomDraft((prev) => [...prev, item]);
    setNewName('');
    setNewRate('');
    toast.success(`Added "${trimmedName}"`);
  };

  const handleDeleteCustomRate = (id: string) => {
    setCustomDraft((prev) => prev.filter((item) => item.id !== id));
  };

  const handleApplyCustomToBilling = async (item: CustomRateItem) => {
    try {
      await saveLiveRatesConfig({
        auto_sync_live: autoSync,
        active_rates: autoSync ? undefined : rates,
        custom_rates: customDraft,
      });
      if (item.metal_type === 'Gold') {
        updateGoldForm('ratePerGm', item.rate);
        updateGoldForm('touch', item.purity_percent);
      } else {
        updateSilverForm('ratePerKg', item.rate);
        updateSilverForm('tanch', item.purity_percent);
      }
      toast.success(`Applied "${item.name}" (₹${item.rate.toLocaleString('en-IN')}) to billing`);
      onClose();
    } catch {
      toast.error('Failed to save custom rate');
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await saveLiveRatesConfig({
        auto_sync_live: autoSync,
        active_rates: autoSync ? undefined : rates,
        custom_rates: customDraft,
      });
      toast.success(autoSync ? 'Auto-Live & custom rates saved' : 'Custom active rates saved');
      onClose();
    } catch {
      toast.error('Failed to save metal rates configuration');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4 backdrop-blur-sm">
      <div className="bg-surface border border-gray-800 rounded-2xl p-5 sm:p-6 shadow-2xl w-full max-w-2xl max-h-[92vh] overflow-y-auto relative">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h2 className="text-primary font-bold text-lg">Live Gold & Silver Rates + Custom Rates</h2>
            <p className="text-xs text-textMuted">
              Always-live market feed synced automatically + add or edit your custom showroom rates
            </p>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-white transition-colors p-1">
            <X size={20} />
          </button>
        </div>

        {/* Always-Live Market Ticker */}
        <div className="bg-background/90 border border-gray-800 rounded-xl p-4 mb-5">
          <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
            <div className="flex items-center space-x-2">
              {isOfflineFallback ? (
                <span className="inline-flex items-center space-x-1.5 text-xs font-semibold px-2.5 py-1 rounded-full bg-amber-500/15 text-amber-400 border border-amber-500/30">
                  <WifiOff size={12} />
                  <span>CACHED / OFFLINE</span>
                </span>
              ) : (
                <span className="inline-flex items-center space-x-1.5 text-xs font-semibold px-2.5 py-1 rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                  <Radio size={12} />
                  <span>LIVE MARKET API</span>
                </span>
              )}
              <span className="text-[11px] text-textMuted">
                Updated: {formatTimestamp(marketMeta?.fetched_at || liveRatesLastUpdated)}
              </span>
              {marketMeta?.source && (
                <span className="text-[11px] text-gray-500 hidden sm:inline">({marketMeta.source})</span>
              )}
            </div>

            <div className="flex items-center space-x-2">
              <button
                type="button"
                onClick={handleApplyMarketToDraft}
                className="text-xs px-2.5 py-1.5 rounded-lg border border-primary/40 text-primary hover:bg-primary/10 transition-colors font-semibold"
              >
                Use Live Rates
              </button>
              <button
                type="button"
                onClick={handleSyncLiveNow}
                disabled={liveRatesSyncing}
                className="inline-flex items-center space-x-1.5 text-xs px-3 py-1.5 rounded-lg bg-primary text-black font-bold hover:bg-primary-dark transition-colors disabled:opacity-60"
              >
                <RefreshCw size={13} className={liveRatesSyncing ? 'animate-spin' : ''} />
                <span>{liveRatesSyncing ? 'Syncing...' : 'Sync Live'}</span>
              </button>
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="bg-surface border border-gray-800 rounded-lg px-3 py-2">
              <div className="text-[10px] uppercase font-bold text-textMuted">Live 24K Gold</div>
              <div className="font-mono text-sm font-bold text-amber-400">
                ₹{Number(marketRates.gold24k || 0).toLocaleString('en-IN')} <span className="text-[10px] text-textMuted">/10g</span>
              </div>
            </div>
            <div className="bg-surface border border-gray-800 rounded-lg px-3 py-2">
              <div className="text-[10px] uppercase font-bold text-textMuted">Live 22K Gold</div>
              <div className="font-mono text-sm font-bold text-amber-300">
                ₹{Number(marketRates.gold22k || 0).toLocaleString('en-IN')} <span className="text-[10px] text-textMuted">/10g</span>
              </div>
            </div>
            <div className="bg-surface border border-gray-800 rounded-lg px-3 py-2">
              <div className="text-[10px] uppercase font-bold text-textMuted">Live Silver</div>
              <div className="font-mono text-sm font-bold text-slate-200">
                ₹{Number(marketRates.silver || 0).toLocaleString('en-IN')} <span className="text-[10px] text-textMuted">/kg</span>
              </div>
            </div>
            <div className="bg-surface border border-gray-800 rounded-lg px-3 py-2">
              <div className="text-[10px] uppercase font-bold text-textMuted">Spot / FX</div>
              <div className="font-mono text-xs text-textMain mt-0.5">
                {marketMeta?.xau_usd ? `$${marketMeta.xau_usd.toFixed(0)}/oz` : '--'} •{' '}
                {marketMeta?.usd_inr ? `₹${marketMeta.usd_inr.toFixed(2)}` : '--'}
              </div>
            </div>
          </div>
        </div>

        {/* Auto-Live Sync Control */}
        <div className="flex flex-wrap items-center justify-between gap-3 bg-background/60 border border-gray-800 rounded-xl px-4 py-3 mb-5">
          <div>
            <div className="text-sm font-semibold text-textMain">
              Auto-Sync Billing & Dashboard with Live API
            </div>
            <div className="text-xs text-textMuted">
              {autoSync
                ? 'ON: Active billing rates auto-update every 60s from live market API.'
                : 'CUSTOM ACTIVE MODE: Using your manually edited active rates until you re-enable Auto-Sync.'}
            </div>
          </div>
          <button
            type="button"
            onClick={handleToggleAutoSync}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-bold border transition-colors ${
              autoSync
                ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                : 'bg-amber-500/15 text-amber-300 border-amber-500/40'
            }`}
          >
            {autoSync ? 'Auto-Live: ON' : 'Auto-Live: OFF (Custom)'}
          </button>
        </div>

        {/* Standard Editable Active Rates */}
        <div className="space-y-4 mb-6">
          <div className="bg-background border border-gray-700 rounded-lg p-3 relative">
            <label className="absolute -top-2 left-3 bg-background px-1 text-[10px] font-bold text-gray-400 uppercase">
              Active 24K Benchmark Gold Rate (₹/10g)
            </label>
            <div className="flex items-center text-primary mt-1">
              <span className="mr-2">₹</span>
              <input
                type="number"
                value={rates.gold24k || ''}
                onChange={(e) => updateStandardRate('gold24k', e.target.value)}
                className="w-full bg-transparent outline-none font-mono text-lg text-white"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {STANDARD_GOLD_FIELDS.map(({ key, label }) => (
              <div key={key} className="bg-background border border-gray-700 rounded-lg p-3 relative">
                <label className="absolute -top-2 left-3 bg-background px-1 text-[10px] font-bold text-gray-400 uppercase">
                  {label}
                </label>
                <div className="flex items-center text-primary mt-1">
                  <span className="mr-1.5">₹</span>
                  <input
                    type="number"
                    value={rates[key] || ''}
                    onChange={(e) => updateStandardRate(key, e.target.value)}
                    className="w-full bg-transparent outline-none font-mono text-sm text-white"
                  />
                </div>
              </div>
            ))}
          </div>

          <div className="bg-background border border-gray-700 rounded-lg p-3 relative">
            <label className="absolute -top-2 left-3 bg-background px-1 text-[10px] font-bold text-gray-400 uppercase">
              Active Silver Rate (₹ / 1kg)
            </label>
            <div className="flex items-center text-primary mt-1">
              <span className="mr-2">₹</span>
              <input
                type="number"
                value={rates.silver || ''}
                onChange={(e) => updateStandardRate('silver', e.target.value)}
                className="w-full bg-transparent outline-none font-mono text-lg text-white"
              />
            </div>
          </div>
        </div>

        {/* Custom Rates Add & Manage Section */}
        <div className="border-t border-gray-800 pt-5 mb-5">
          <div className="flex items-center justify-between mb-3">
            <div>
              <h3 className="text-sm font-bold text-textMain">Your Custom Rates</h3>
              <p className="text-[11px] text-textMuted">
                Add custom showroom rates (e.g. Kundan Gold, Showroom 22K, Payal Silver) alongside always-live rates
              </p>
            </div>
            <span className="text-xs font-mono text-textMuted">{customDraft.length} saved</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-12 gap-2 bg-background/70 border border-gray-800 rounded-xl p-3 mb-3">
            <input
              type="text"
              placeholder="Custom Rate Name (e.g. 22K Showroom)"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              className="sm:col-span-5 bg-surface border border-gray-700 rounded-lg px-3 py-2 text-xs text-white outline-none focus:border-primary"
            />
            <select
              value={newMetal}
              onChange={(e) => {
                const m = e.target.value as 'Gold' | 'Silver';
                setNewMetal(m);
                setNewPurity(m === 'Gold' ? '91.6' : '99.9');
              }}
              className="sm:col-span-2 bg-surface border border-gray-700 rounded-lg px-2 py-2 text-xs text-white outline-none focus:border-primary"
            >
              <option value="Gold">Gold (/10g)</option>
              <option value="Silver">Silver (/kg)</option>
            </select>
            <input
              type="number"
              step="0.1"
              placeholder="Purity %"
              value={newPurity}
              onChange={(e) => setNewPurity(e.target.value)}
              className="sm:col-span-2 bg-surface border border-gray-700 rounded-lg px-2.5 py-2 text-xs text-white font-mono outline-none focus:border-primary"
            />
            <input
              type="number"
              placeholder="Rate ₹"
              value={newRate}
              onChange={(e) => setNewRate(e.target.value)}
              className="sm:col-span-2 bg-surface border border-gray-700 rounded-lg px-2.5 py-2 text-xs text-white font-mono outline-none focus:border-primary"
            />
            <button
              type="button"
              onClick={handleAddCustomRate}
              className="sm:col-span-1 inline-flex items-center justify-center rounded-lg bg-primary/20 border border-primary/40 text-primary hover:bg-primary hover:text-black transition-colors py-2"
              title="Add Custom Rate"
            >
              <Plus size={16} />
            </button>
          </div>

          {customDraft.length === 0 ? (
            <div className="text-xs text-textMuted italic py-2">
              No custom rates added yet. Add one above anytime.
            </div>
          ) : (
            <div className="space-y-2 max-h-44 overflow-y-auto pr-1">
              {customDraft.map((item) => (
                <div
                  key={item.id}
                  className="flex items-center justify-between gap-2 bg-background border border-gray-800 rounded-lg px-3 py-2"
                >
                  <div className="min-w-0">
                    <div className="flex items-center space-x-2">
                      <span className="text-xs font-semibold text-textMain truncate">{item.name}</span>
                      <span
                        className={`text-[10px] px-1.5 py-0.5 rounded font-bold ${
                          item.metal_type === 'Gold'
                            ? 'bg-amber-500/15 text-amber-300'
                            : 'bg-slate-500/20 text-slate-300'
                        }`}
                      >
                        {item.metal_type} • {item.purity_percent}%
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2 shrink-0">
                    <span className="font-mono text-xs font-bold text-primary">
                      ₹{Number(item.rate).toLocaleString('en-IN')} {item.unit}
                    </span>
                    <button
                      type="button"
                      onClick={() => handleApplyCustomToBilling(item)}
                      className="text-[11px] px-2 py-1 rounded bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 hover:bg-emerald-500/25 font-semibold"
                    >
                      Apply
                    </button>
                    <button
                      type="button"
                      onClick={() => handleDeleteCustomRate(item.id)}
                      className="p-1 text-gray-500 hover:text-red-400 transition-colors"
                      title="Delete custom rate"
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="flex justify-end items-center space-x-3 pt-2 border-t border-gray-800">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 rounded-lg text-sm text-textMuted hover:text-white transition-colors"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleSave}
            disabled={saving}
            className="inline-flex items-center space-x-1.5 bg-primary hover:bg-primary-dark text-black font-bold px-5 py-2 rounded-lg text-sm transition-colors disabled:opacity-60"
          >
            <Check size={16} />
            <span>{saving ? 'Saving...' : 'Save Rates'}</span>
          </button>
        </div>
      </div>
    </div>
  );
}
