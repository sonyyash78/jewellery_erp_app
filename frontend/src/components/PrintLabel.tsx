import { forwardRef } from 'react';
import type { StockItem } from '../store/inventoryStore';
import { ItemQRCode } from './ItemQRCode';

interface PrintLabelProps {
  item: StockItem;
}

export const PrintLabel = forwardRef<HTMLDivElement, PrintLabelProps>(({ item }, ref) => {
  return (
    <div ref={ref} className="bg-white text-black p-4 w-[400px] font-sans flex items-center justify-between border-2 border-dashed border-gray-300">
      
      {/* Left Side: Details */}
      <div className="flex flex-col flex-1 pr-4 border-r-2 border-dashed border-gray-300">
        <div className="text-xl font-bold tracking-wider mb-1 uppercase">{item.item_code}</div>
        <div className="text-sm font-bold mb-2 truncate max-w-[200px]">{item.item_name}</div>
        
        <div className="grid grid-cols-2 gap-x-2 gap-y-1 text-xs">
          <div><span className="text-gray-500">Gross:</span> <span className="font-bold">{item.gross_weight}g</span></div>
          <div><span className="text-gray-500">Net:</span> <span className="font-bold">{item.net_weight}g</span></div>
          <div><span className="text-gray-500">Purity:</span> <span className="font-bold">{item.purity || '-'}</span></div>
          <div><span className="text-gray-500">Metal:</span> <span className="font-bold">{item.metal}</span></div>
        </div>
      </div>

      {/* Right Side: QR Code */}
      <div className="pl-4 flex flex-col items-center justify-center">
        {item.item_code ? (
          <ItemQRCode itemCode={item.item_code} serverPath={item.qr_code_path} className="w-24 h-24 object-contain" />
        ) : (
          <div className="w-24 h-24 border border-gray-300 flex items-center justify-center text-xs text-gray-400 text-center">No QR</div>
        )}
      </div>

    </div>
  );
});

PrintLabel.displayName = 'PrintLabel';
