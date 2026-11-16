from pathlib import Path
import re

index_file = Path(r"c:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\pages\exchange\index.tsx")
code = index_file.read_text(encoding="utf-8")

# 1. Update metal calculations
old_calcs = """  const silverOldFine = oldItems.filter(i => i.metal === 'Silver').reduce((acc, i) => acc + (i.fineWeight || 0), 0);
  const silverNewFine = newItems.filter(i => i.metal === 'Silver').reduce((acc, i) => acc + (i.fineWeight || 0), 0);
  const silverNetFine = silverNewFine - silverOldFine; // Positive = Customer owes silver (New > Old), Negative = Customer has surplus silver

  const hasMetalActivity = goldOldFine > 0 || goldNewFine > 0 || silverOldFine > 0 || silverNewFine > 0;"""

new_calcs = """  const silverOldFine = oldItems.filter(i => i.metal === 'Silver').reduce((acc, i) => acc + (i.fineWeight || 0), 0);
  const silverNewFine = newItems.filter(i => i.metal === 'Silver').reduce((acc, i) => acc + (i.fineWeight || 0), 0);
  const silverNetFine = silverNewFine - silverOldFine; // Positive = Customer owes silver (New > Old), Negative = Customer has surplus silver

  const diamondOldGms = oldItems.filter(i => i.metal === 'Diamond').reduce((acc, i) => acc + (i.netWeight || 0), 0);
  const diamondNewGms = newItems.filter(i => (i.metal || '').toLowerCase() === 'diamond').reduce((acc, i) => acc + (i.netWeight || 0), 0);
  const diamondNetGms = diamondNewGms - diamondOldGms;
  const hasDiamondActivity = diamondOldGms > 0 || diamondNewGms > 0;

  const hasMetalActivity = goldOldFine > 0 || goldNewFine > 0 || silverOldFine > 0 || silverNewFine > 0 || hasDiamondActivity;"""

code = code.replace(old_calcs, new_calcs)

# 2. Update Old Items and New Items rendering
old_items_block = """                {oldItems.map(item => (
                  <div key={`old-${item.id}`} className="bg-background border border-gray-800 rounded p-2.5 relative group">
                    <div className="absolute top-1.5 right-1.5 flex space-x-1.5 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button onClick={() => setEditingOldItem(item)} className="text-gray-600 hover:text-blue-400 transition-colors"><Edit2 size={14} /></button>
                      <button onClick={() => removeOldItem(item.id)} className="text-gray-600 hover:text-red-400 transition-colors"><Trash2 size={14} /></button>
                    </div>
                    <div className="flex justify-between items-start mb-1.5 pr-10">
                      <div>
                        <span className="text-[10px] font-bold px-1.5 py-0.5 rounded mr-1.5 bg-green-500/20 text-green-400">OLD (IN)</span>
                        <span className="text-xs text-textMain font-medium">{item.itemName}</span>
                      </div>
                      <span className="text-xs font-mono text-green-400 font-bold">- ₹{item.calculatedValue.toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2})}</span>
                    </div>
                    <div className="grid grid-cols-2 gap-x-3 gap-y-0.5 text-[10.5px] text-textMuted">
                      <div className="flex justify-between"><span>Net Wt:</span><span className="font-mono">{item.netWeight}g</span></div>
                      <div className="flex justify-between"><span>Tanch:</span><span className="font-mono">{item.touch}%</span></div>
                      <div className="flex justify-between"><span>Fine:</span><span className="font-mono text-primary font-bold">{item.fineWeight.toFixed(3)}g</span></div>
                      <div className="flex justify-between"><span>Rate:</span><span className="font-mono">₹{item.rateApplied}</span></div>
                    </div>
                  </div>
                ))}
                
                {newItems.map(item => (
                  <div key={`new-${item.id}`} className="bg-background border border-gray-800 rounded p-2.5 relative group">
                    <div className="absolute top-1.5 right-1.5 flex space-x-1.5 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button onClick={() => setEditingNewItem(item)} className="text-gray-600 hover:text-blue-400 transition-colors" title="Edit Item"><Edit2 size={14} /></button>
                      <button onClick={() => removeNewItem(item.id)} className="text-gray-600 hover:text-red-400 transition-colors" title="Delete Item"><Trash2 size={14} /></button>
                    </div>
                    <div className="flex justify-between items-start mb-1.5 pr-10">
                      <div>
                        <span className="text-[10px] font-bold px-1.5 py-0.5 rounded mr-1.5 bg-primary/20 text-primary">NEW (OUT)</span>
                        <span className="text-xs text-textMain font-medium">{item.itemName}</span>
                      </div>
                      <span className="text-xs font-mono text-red-400 font-bold">+ ₹{item.finalPrice.toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2})}</span>
                    </div>
                    <div className="grid grid-cols-2 gap-x-3 gap-y-0.5 text-[10.5px] text-textMuted">
                      <div className="flex justify-between"><span>Net Wt:</span><span className="font-mono">{item.netWeight}g</span></div>
                      <div className="flex justify-between"><span>Making:</span><span className="font-mono">₹{item.makingCharges.toLocaleString()}</span></div>
                      <div className="flex justify-between"><span>Other:</span><span className="font-mono">₹{(item.hallmark + item.otherCharges).toLocaleString()}</span></div>
                      <div className="flex justify-between"><span>Rate:</span><span className="font-mono">₹{item.rateApplied}</span></div>
                    </div>
                  </div>
                ))}"""

new_items_block = """                {oldItems.map(item => {
                  const isDia = item.metal === 'Diamond';
                  return (
                    <div key={`old-${item.id}`} className="bg-background border border-gray-800 rounded p-2.5 relative group">
                      <div className="absolute top-1.5 right-1.5 flex space-x-1.5 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button onClick={() => setEditingOldItem(item)} className="text-gray-600 hover:text-blue-400 transition-colors"><Edit2 size={14} /></button>
                        <button onClick={() => removeOldItem(item.id)} className="text-gray-600 hover:text-red-400 transition-colors"><Trash2 size={14} /></button>
                      </div>
                      <div className="flex justify-between items-start mb-1.5 pr-10">
                        <div>
                          <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded mr-1.5 ${isDia ? 'bg-cyan-500/20 text-cyan-400' : 'bg-green-500/20 text-green-400'}`}>
                            {isDia ? '💎 OLD DIA' : 'OLD (IN)'}
                          </span>
                          <span className="text-xs text-textMain font-medium">{item.itemName}</span>
                        </div>
                        <span className="text-xs font-mono text-green-400 font-bold">- ₹{item.calculatedValue.toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2})}</span>
                      </div>
                      <div className="grid grid-cols-2 gap-x-3 gap-y-0.5 text-[10.5px] text-textMuted">
                        <div className="flex justify-between"><span>Net Wt:</span><span className="font-mono">{item.netWeight}g {isDia ? `(${(item.netWeight * 5).toFixed(2)}ct)` : ''}</span></div>
                        <div className="flex justify-between"><span>{isDia ? 'Pieces:' : 'Tanch:'}</span><span className="font-mono">{isDia ? (item.diamondDetails?.pieces || 1) : `${item.touch}%`}</span></div>
                        <div className="flex justify-between"><span>{isDia ? 'Base Val:' : 'Fine:'}</span><span className={`font-mono font-bold ${isDia ? 'text-cyan-400' : 'text-primary'}`}>{isDia ? `₹${(item.netWeight * item.rateApplied).toFixed(0)}` : `${item.fineWeight.toFixed(3)}g`}</span></div>
                        <div className="flex justify-between"><span>Rate:</span><span className="font-mono">₹{item.rateApplied}{isDia ? '/g' : ''}</span></div>
                      </div>
                    </div>
                  );
                })}
                
                {newItems.map(item => {
                  const isDia = (item.metal || '').toLowerCase() === 'diamond';
                  return (
                    <div key={`new-${item.id}`} className="bg-background border border-gray-800 rounded p-2.5 relative group">
                      <div className="absolute top-1.5 right-1.5 flex space-x-1.5 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button onClick={() => setEditingNewItem(item)} className="text-gray-600 hover:text-blue-400 transition-colors" title="Edit Item"><Edit2 size={14} /></button>
                        <button onClick={() => removeNewItem(item.id)} className="text-gray-600 hover:text-red-400 transition-colors" title="Delete Item"><Trash2 size={14} /></button>
                      </div>
                      <div className="flex justify-between items-start mb-1.5 pr-10">
                        <div>
                          <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded mr-1.5 ${isDia ? 'bg-cyan-500/20 text-cyan-400' : 'bg-primary/20 text-primary'}`}>
                            {isDia ? '💎 NEW DIA' : 'NEW (OUT)'}
                          </span>
                          <span className="text-xs text-textMain font-medium">{item.itemName}</span>
                        </div>
                        <span className="text-xs font-mono text-red-400 font-bold">+ ₹{item.finalPrice.toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2})}</span>
                      </div>
                      <div className="grid grid-cols-2 gap-x-3 gap-y-0.5 text-[10.5px] text-textMuted">
                        <div className="flex justify-between"><span>Net Wt:</span><span className="font-mono">{item.netWeight}g {isDia ? `(${(item.netWeight * 5).toFixed(2)}ct)` : ''}</span></div>
                        <div className="flex justify-between"><span>{isDia ? 'Setting:' : 'Making:'}</span><span className="font-mono">₹{item.makingCharges.toLocaleString()}</span></div>
                        <div className="flex justify-between"><span>Other:</span><span className="font-mono">₹{(item.hallmark + item.otherCharges).toLocaleString()}</span></div>
                        <div className="flex justify-between"><span>Rate:</span><span className="font-mono">₹{item.rateApplied}{isDia ? '/g' : ''}</span></div>
                      </div>
                    </div>
                  );
                })}"""

code = code.replace(old_items_block, new_items_block)

# 3. Add Diamond row to Metal Summary Card
old_metal_summary = """                {/* Silver Row */}
                {(silverOldFine > 0 || silverNewFine > 0) && (
                  <div className="bg-gray-800/30 border border-gray-700/40 rounded px-2 py-1 flex items-center justify-between text-xs">
                    <span className="font-bold text-gray-300">🥈 Silver</span>
                    <div className="flex items-center gap-3 text-[10.5px] font-mono">
                      <span className="text-gray-400">In: <strong className="text-green-400">{silverOldFine.toFixed(3)}g</strong></span>
                      <span className="text-gray-400">Out: <strong className="text-gray-200">{silverNewFine.toFixed(3)}g</strong></span>
                      <span className={`font-bold px-1.5 py-0.5 rounded text-[10px] ${silverNetFine > 0.001 ? 'bg-red-500/20 text-red-400' : silverNetFine < -0.001 ? 'bg-green-500/20 text-green-400' : 'bg-gray-800 text-gray-400'}`}>
                        {silverNetFine > 0.001 ? `+${silverNetFine.toFixed(3)}g Due` : silverNetFine < -0.001 ? `${silverNetFine.toFixed(3)}g Surplus` : '0.000g'}
                      </span>
                    </div>
                  </div>
                )}"""

new_metal_summary = """                {/* Silver Row */}
                {(silverOldFine > 0 || silverNewFine > 0) && (
                  <div className="bg-gray-800/30 border border-gray-700/40 rounded px-2 py-1 flex items-center justify-between text-xs">
                    <span className="font-bold text-gray-300">🥈 Silver</span>
                    <div className="flex items-center gap-3 text-[10.5px] font-mono">
                      <span className="text-gray-400">In: <strong className="text-green-400">{silverOldFine.toFixed(3)}g</strong></span>
                      <span className="text-gray-400">Out: <strong className="text-gray-200">{silverNewFine.toFixed(3)}g</strong></span>
                      <span className={`font-bold px-1.5 py-0.5 rounded text-[10px] ${silverNetFine > 0.001 ? 'bg-red-500/20 text-red-400' : silverNetFine < -0.001 ? 'bg-green-500/20 text-green-400' : 'bg-gray-800 text-gray-400'}`}>
                        {silverNetFine > 0.001 ? `+${silverNetFine.toFixed(3)}g Due` : silverNetFine < -0.001 ? `${silverNetFine.toFixed(3)}g Surplus` : '0.000g'}
                      </span>
                    </div>
                  </div>
                )}

                {/* Diamond Row */}
                {hasDiamondActivity && (
                  <div className="bg-cyan-950/20 border border-cyan-800/40 rounded px-2 py-1 flex items-center justify-between text-xs">
                    <span className="font-bold text-cyan-400">💎 Diamond</span>
                    <div className="flex items-center gap-3 text-[10.5px] font-mono">
                      <span className="text-gray-400">In: <strong className="text-green-400">{diamondOldGms.toFixed(3)}g ({(diamondOldGms * 5).toFixed(2)}ct)</strong></span>
                      <span className="text-gray-400">Out: <strong className="text-cyan-300">{diamondNewGms.toFixed(3)}g ({(diamondNewGms * 5).toFixed(2)}ct)</strong></span>
                      <span className={`font-bold px-1.5 py-0.5 rounded text-[10px] ${diamondNetGms > 0.001 ? 'bg-red-500/20 text-red-400' : diamondNetGms < -0.001 ? 'bg-green-500/20 text-green-400' : 'bg-gray-800 text-gray-400'}`}>
                        {diamondNetGms > 0.001 ? `+${diamondNetGms.toFixed(3)}g Due` : diamondNetGms < -0.001 ? `${diamondNetGms.toFixed(3)}g Surplus` : '0.000g'}
                      </span>
                    </div>
                  </div>
                )}"""

code = code.replace(old_metal_summary, new_metal_summary)

index_file.write_text(code, encoding="utf-8")
print("Updated frontend/src/pages/exchange/index.tsx successfully!")
