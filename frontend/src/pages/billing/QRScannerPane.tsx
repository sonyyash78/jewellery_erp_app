import { useState, useEffect, useRef } from 'react';
import { Html5QrcodeScanner } from 'html5-qrcode';
import { Camera, Keyboard, ScanLine } from 'lucide-react';
import { axiosClient } from '../../api/axiosClient';
import { useBillingStore } from '../../store/billingStore';
import type { BillItem } from '../../store/billingStore';
import toast from 'react-hot-toast';
import { getErrorMessage } from '../../utils/errorUtils';

export default function QRScannerPane() {
  const [mode, setMode] = useState<'camera' | 'manual'>('manual');
  const [manualCode, setManualCode] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { addToCart, recentScans, addRecentScan, cart } = useBillingStore();
  const scannerRef = useRef<Html5QrcodeScanner | null>(null);

  // Initialize Camera Scanner
  useEffect(() => {
    if (mode === 'camera') {
      scannerRef.current = new Html5QrcodeScanner(
        "reader",
        { fps: 10, qrbox: { width: 250, height: 250 } },
        false
      );
      
      scannerRef.current.render(onScanSuccess, onScanFailure);
    } else {
      if (scannerRef.current) {
        scannerRef.current.clear().catch(console.error);
        scannerRef.current = null;
      }
    }

    return () => {
      if (scannerRef.current) {
        scannerRef.current.clear().catch(console.error);
      }
    };
  }, [mode]);

  const onScanSuccess = (decodedText: string) => {
    handleCodeSubmit(decodedText);
    // Pause briefly to prevent rapid double scans
    if (scannerRef.current) {
      scannerRef.current.pause(true);
      setTimeout(() => scannerRef.current?.resume(), 2000);
    }
  };

  const onScanFailure = (_error: any) => {
    // Ignore frequent scan failures (when nothing is in view)
  };

  const handleManualSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!manualCode.trim()) return;
    handleCodeSubmit(manualCode.trim());
    setManualCode('');
  };

  const handleCodeSubmit = async (code: string) => {
    // Check if already in cart
    if (cart.some(item => item.id === code)) {
      toast.error(`Item ${code} is already in the cart`);
      return;
    }

    setLoading(true);
    try {
      // Fetch StockItem
      const res = await axiosClient.get(`/stock/scan/${code}`);
      const item = res.data;

      // Ensure it's not sold (handled by backend 400, but double checking)
      if (item.status.toLowerCase() === 'sold') {
        toast.error(`Item ${code} is already sold!`);
        return;
      }

      const { liveRates } = useBillingStore.getState();
      const isGold = item.metal.toLowerCase() === 'gold';
      
      let metalRate = 0;
      if (isGold) {
        const p = (item.purity || '').toUpperCase();
        if (p.includes('24')) metalRate = liveRates.gold24k || 79100;
        else if (p.includes('20')) metalRate = liveRates.gold20k || 65900;
        else if (p.includes('18')) metalRate = liveRates.gold18k || 59300;
        else if (p.includes('14')) metalRate = liveRates.gold14k || 46100;
        else metalRate = liveRates.gold22k || 72500;
      } else {
        metalRate = liveRates.silver || 90000;
      }

      const touchDisplay = item.tanch || (isGold ? (item.purity === '22K' ? 91.6 : item.purity === '18K' ? 75.0 : 91.6) : 65);
      const wastageDisplay = item.wastage || 0;
      const netWeight = item.net_weight || (item.gross_weight || 0) - (item.stone_weight || 0);
      const fineWeight = netWeight * ((touchDisplay + wastageDisplay) / 100);

      let metalValue = 0;
      if (isGold) {
        metalValue = fineWeight * (metalRate / 10);
      } else {
        metalValue = fineWeight * (metalRate / 1000);
      }

      const makingAmount = item.making_type === 'flat' 
        ? (item.making_charge || 0) 
        : ((item.making_charge || 0) * netWeight);
      
      const hallmark = item.hallmark || 0;
      const otherCharges = item.other_charges || 0;
      const discount = 0;

      const taxableAmount = metalValue + makingAmount + hallmark + otherCharges - discount;

      const billItem: BillItem = {
        id: item.item_code, // Use item_code as unique cart ID
        stockItemId: item.id,
        itemType: isGold ? 'Gold' : 'Silver',
        itemName: item.item_name,
        purityDisplay: item.purity || (isGold ? '22K Gold' : 'Fine'),
        touchDisplay,
        wastageDisplay,
        grossWeight: item.gross_weight || netWeight,
        stoneWeight: item.stone_weight || 0,
        netWeight,
        fineWeight,
        rateDisplay: metalRate,
        metalValue,
        makingAmount,
        hallmark,
        otherCharges,
        discount,
        taxableAmount,
        rawGold: isGold ? {
          itemName: item.item_name,
          category: item.category || '',
          hsn: item.hsn || '',
          purity: item.purity || '22K Gold',
          touch: touchDisplay,
          wastage: wastageDisplay,
          grossWeight: item.gross_weight || netWeight,
          stoneWeight: item.stone_weight || 0,
          ratePerGm: metalRate,
          makingChargeType: (item.making_type || 'per_gm') as any,
          makingChargeValue: item.making_charge || 0,
          hallmark,
          otherCharges,
          discount: 0
        } : undefined,
        rawSilver: !isGold ? {
          itemName: item.item_name,
          category: item.category || '',
          hsn: item.hsn || '',
          silverPurity: item.purity || 'Fine',
          tanch: touchDisplay,
          wastage: wastageDisplay,
          grossWeight: item.gross_weight || netWeight,
          stoneWeight: item.stone_weight || 0,
          ratePerKg: metalRate,
          makingChargeType: (item.making_type || 'per_gm') as any,
          makingChargeValue: item.making_charge || 0,
          otherCharges,
          discount: 0
        } : undefined
      };

      addToCart(billItem);
      addRecentScan(item.item_code);
      toast.success(`Scanned: ${item.item_name}`);

    } catch (e: any) {
      if (e.response?.status === 400 || e.response?.status === 422) {
        toast.error(getErrorMessage(e));
      } else if (e.response?.status === 404) {
        toast.error(`Item ${code} not found in inventory.`);
      } else {
        toast.error('Failed to fetch item details.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-surface border border-gray-800 rounded-xl flex flex-col overflow-hidden h-full">
      
      {/* Header Tabs */}
      <div className="flex border-b border-gray-800">
        <button 
          onClick={() => setMode('manual')}
          className={`flex-1 flex items-center justify-center gap-2 py-3 text-sm font-bold uppercase tracking-wider transition-colors ${mode === 'manual' ? 'bg-primary/10 text-primary border-b-2 border-primary' : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/50'}`}
        >
          <Keyboard size={18} /> USB / Manual
        </button>
        <button 
          onClick={() => setMode('camera')}
          className={`flex-1 flex items-center justify-center gap-2 py-3 text-sm font-bold uppercase tracking-wider transition-colors ${mode === 'camera' ? 'bg-primary/10 text-primary border-b-2 border-primary' : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/50'}`}
        >
          <Camera size={18} /> Camera
        </button>
      </div>

      {/* Main Scanner Area */}
      <div className="flex-1 p-4 flex flex-col items-center justify-center relative">
        
        {loading && (
          <div className="absolute inset-0 bg-surface/80 z-20 flex items-center justify-center">
            <span className="text-primary font-bold animate-pulse">Fetching Item...</span>
          </div>
        )}

        {mode === 'camera' ? (
          <div className="w-full max-w-[300px] bg-black border border-gray-700 rounded-lg overflow-hidden relative">
            {/* The ID must match what Html5QrcodeScanner targets */}
            <div id="reader" className="w-full"></div>
            <style>{`
              #reader { border: none !important; }
              #reader__scan_region { background: black; }
              #reader__dashboard_section_csr span { color: white !important; }
              #reader__dashboard_section_swaplink { display: none !important; }
              #html5-qrcode-button-camera-permission { background: #d4af37 !important; color: black !important; border: none; padding: 8px; border-radius: 4px; font-weight: bold; }
              #html5-qrcode-button-camera-stop { background: #ef4444 !important; color: white !important; border: none; padding: 8px; border-radius: 4px; }
            `}</style>
          </div>
        ) : (
          <form onSubmit={handleManualSubmit} className="w-full max-w-[300px] flex flex-col gap-4">
            <div className="text-center">
              <ScanLine size={48} className="mx-auto text-primary/50 mb-4" />
              <p className="text-sm text-textMuted mb-2">Scan barcode or enter manually</p>
            </div>
            <input
              type="text"
              autoFocus
              value={manualCode}
              onChange={(e) => setManualCode(e.target.value.toUpperCase())}
              placeholder="e.g. GLD-000001"
              className="w-full bg-background border border-gray-700 rounded-lg px-4 py-3 text-center text-lg font-mono text-primary font-bold uppercase focus:border-primary outline-none"
            />
            <button type="submit" disabled={loading} className="w-full bg-primary hover:bg-primary-dark text-black font-bold py-3 rounded-lg transition-colors">
              Lookup Item
            </button>
          </form>
        )}
      </div>

      {/* Recent Scans Footer */}
      <div className="h-16 border-t border-gray-800 bg-black/20 p-2 flex items-center gap-2 overflow-x-auto custom-scrollbar">
        {recentScans.length === 0 ? (
          <span className="text-xs text-gray-600 italic px-2">No items scanned yet</span>
        ) : (
          recentScans.map((scan, i) => (
            <span key={i} className="flex-shrink-0 bg-primary/10 border border-primary/30 text-primary text-xs font-mono px-3 py-1 rounded-full">
              {scan}
            </span>
          ))
        )}
      </div>
    </div>
  );
}
