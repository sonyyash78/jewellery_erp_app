import TopBar from './TopBar';
import MetalCalculator from './MetalCalculator';
import QRScannerPane from './QRScannerPane';
import LiveBillSummary from './LiveBillSummary';

export default function Billing() {
  return (
    <div className="h-auto lg:h-[calc(100vh-4.5rem)] flex flex-col gap-2.5 overflow-y-auto lg:overflow-hidden p-0.5 sm:p-1">
      {/* Dynamic Metadata Row */}
      <TopBar />
      
      {/* Main Layout: Responsive 1-col on mobile/tablet, 3-col studio layout on desktop (>= 1024px) */}
      <div className="flex-1 min-h-0 grid grid-cols-1 lg:grid-cols-12 gap-3 lg:overflow-hidden pb-8 lg:pb-0">
        
        {/* Left Column: QR Scanner / Item Lookup */}
        <div className="lg:col-span-4 min-h-[300px] lg:min-h-0 h-full flex flex-col overflow-hidden">
          <QRScannerPane />
        </div>

        {/* Center Column: Metal Calculator */}
        <div className="lg:col-span-4 min-h-[520px] lg:min-h-0 h-full flex flex-col overflow-hidden">
          <MetalCalculator />
        </div>

        {/* Right Column: Live Bill Summary & Items List */}
        <div className="lg:col-span-4 min-h-[460px] lg:min-h-0 h-full flex flex-col bg-surface border border-primary/30 rounded-2xl shadow-[0_4px_20px_rgba(0,0,0,0.5)] overflow-hidden">
          <LiveBillSummary />
        </div>

      </div>
    </div>
  );
}
