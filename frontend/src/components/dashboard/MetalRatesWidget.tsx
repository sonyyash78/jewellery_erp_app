import { useEffect, useState } from 'react';
import { Activity, Plus, RefreshCw, WifiOff } from 'lucide-react';
import { useBillingStore } from '../../store/billingStore';
import LiveRatesModal from '../../pages/billing/LiveRatesModal';

const formatSyncTime = (iso?: string | null): string => {
  if (!iso) return 'Syncing...';
  const dt = new Date(iso);
  if (Number.isNaN(dt.getTime())) return 'Live';
  return dt.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

export default function MetalRatesWidget() {
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
  } = useBillingStore();

  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    if (!liveRatesLastUpdated) {
      fetchLiveRates(false);
    }
  }, [liveRatesLastUpdated, fetchLiveRates]);

  const standardRows = [
    { label: '24K Gold (999)', metal: 'Gold', rate: liveRates.gold24k, unit: '/ 10g' },
    { label: '22K Gold (916)', metal: 'Gold', rate: liveRates.gold22k, unit: '/ 10g' },
    { label: '20K Gold (833)', metal: 'Gold', rate: liveRates.gold20k, unit: '/ 10g' },
    { label: '18K Gold (750)', metal: 'Gold', rate: liveRates.gold18k, unit: '/ 10g' },
    { label: '14K Gold (583)', metal: 'Gold', rate: liveRates.gold14k, unit: '/ 10g' },
    { label: 'Silver Fine', metal: 'Silver', rate: liveRates.silver, unit: '/ kg' },
  ];

  return (
    <div className="bg-surface rounded-xl border border-gray-800 p-6 flex flex-col h-full">
      <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
        <div className="flex items-center space-x-2">
          <Activity size={20} className="text-primary" />
          <h3 className="font-bold text-lg text-textMain">Live Metal Rates</h3>
          {isOfflineFallback ? (
            <span className="inline-flex items-center space-x-1 text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-500/15 text-amber-400 border border-amber-500/30">
              <WifiOff size={10} />
              <span>CACHED</span>
            </span>
          ) : (
            <span className="inline-flex items-center space-x-1 text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              <span>LIVE</span>
            </span>
          )}
        </div>

        <div className="flex items-center space-x-2">
          <button
            type="button"
            onClick={() => fetchLiveRates(true)}
            disabled={liveRatesSyncing}
            className="p-1.5 rounded-lg bg-background border border-gray-700 text-textMuted hover:text-primary hover:border-primary/40 transition-colors disabled:opacity-50"
            title="Sync live market rates now"
          >
            <RefreshCw size={14} className={liveRatesSyncing ? 'animate-spin' : ''} />
          </button>
          <button
            type="button"
            onClick={() => setShowModal(true)}
            className="inline-flex items-center space-x-1 text-xs font-semibold px-2.5 py-1.5 rounded-lg bg-primary/15 text-primary border border-primary/30 hover:bg-primary/25 transition-colors"
          >
            <Plus size={13} />
            <span>Custom / Edit</span>
          </button>
        </div>
      </div>

      {/* Always-Live Market Banner */}
      <div className="bg-background/80 border border-gray-800 rounded-lg px-3 py-2 mb-3 flex flex-wrap items-center justify-between gap-2 text-xs">
        <div className="flex items-center space-x-3">
          <span className="text-textMuted font-medium">API Spot:</span>
          <span className="font-mono font-bold text-amber-400">
            24K ₹{Number(marketRates.gold24k || 0).toLocaleString('en-IN')}/10g
          </span>
          <span className="font-mono font-bold text-slate-300">
            Silver ₹{Number(marketRates.silver || 0).toLocaleString('en-IN')}/kg
          </span>
        </div>
        <div className="text-[11px] text-textMuted">
          {autoSyncLive ? 'Auto-Live' : 'Custom Active'} • {formatSyncTime(marketMeta?.fetched_at || liveRatesLastUpdated)}
        </div>
      </div>

      {/* Active Standard + User Custom Rates List */}
      <div className="flex-1 space-y-2 overflow-auto pr-1">
        {standardRows.map((row) => (
          <div
            key={row.label}
            className="flex justify-between items-center px-3 py-2.5 bg-background rounded border border-gray-800"
          >
            <div>
              <span className="font-semibold text-sm text-textMain">{row.label}</span>
              <span className="text-xs text-textMuted ml-2">{row.metal}</span>
            </div>
            <div className="font-bold font-mono text-sm text-primary">
              ₹ {Number(row.rate || 0).toLocaleString('en-IN')} <span className="text-xs font-sans text-textMuted">{row.unit}</span>
            </div>
          </div>
        ))}

        {customRates.map((custom) => (
          <div
            key={custom.id}
            className="flex justify-between items-center px-3 py-2.5 bg-background rounded border border-primary/30"
          >
            <div className="flex items-center space-x-2 min-w-0">
              <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-primary/20 text-primary uppercase">
                Custom
              </span>
              <span className="font-semibold text-sm text-textMain truncate">{custom.name}</span>
              <span className="text-xs text-textMuted shrink-0">
                {custom.metal_type} ({custom.purity_percent}%)
              </span>
            </div>
            <div className="font-bold font-mono text-sm text-primary shrink-0">
              ₹ {Number(custom.rate || 0).toLocaleString('en-IN')} <span className="text-xs font-sans text-textMuted">{custom.unit}</span>
            </div>
          </div>
        ))}
      </div>

      {showModal && <LiveRatesModal onClose={() => setShowModal(false)} />}
    </div>
  );
}
