import os

path = r'C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\pages\reports\ReportViewer.tsx'
with open(path, 'r', encoding='utf-8') as f:
    code = f.read()

# Add WastageProfitView component right before export default function ReportViewer
wastage_view_component = """
interface WastageData {
  company_id?: number;
  summary?: {
    gold_net_wastage_profit_g: number;
    silver_net_wastage_profit_g: number;
    diamond_carats_sold: number;
    total_making_profit_rs: number;
    total_value_profit_rs: number;
  };
  gold?: {
    sold_fine_g: number;
    sold_wastage_g: number;
    sold_making_rs: number;
    sold_total_val_rs: number;
    purchased_fine_g: number;
    purchased_wastage_g: number;
    purchased_labour_rs: number;
    purchased_total_val_rs: number;
    net_wastage_profit_g: number;
    net_labour_profit_rs: number;
    net_val_profit_rs: number;
  };
  silver?: {
    sold_pure_g: number;
    sold_wastage_g: number;
    sold_making_rs: number;
    sold_total_val_rs: number;
    purchased_pure_g: number;
    purchased_wastage_g: number;
    purchased_labour_rs: number;
    purchased_total_val_rs: number;
    net_wastage_profit_g: number;
    net_labour_profit_rs: number;
    net_val_profit_rs: number;
  };
  diamond?: {
    sold_carats: number;
    sold_weight_g: number;
    sold_making_rs: number;
    sold_total_val_rs: number;
    purchased_labour_rs: number;
    purchased_total_val_rs: number;
    net_making_profit_rs: number;
    net_val_profit_rs: number;
  };
  transactions?: Array<{
    date: string;
    type: string;
    bill_no: string;
    item_name: string;
    metal: string;
    weight_g: number;
    touch_pct: number;
    wastage_pct: number;
    wastage_g: number;
    fine_weight_g: number;
    making_charges: number;
    total_amount: number;
  }>;
}

function WastageProfitView({ data }: { data: WastageData }) {
  const sum = data.summary || {
    gold_net_wastage_profit_g: 0,
    silver_net_wastage_profit_g: 0,
    diamond_carats_sold: 0,
    total_making_profit_rs: 0,
    total_value_profit_rs: 0,
  };
  const g = data.gold || {} as any;
  const s = data.silver || {} as any;
  const d = data.diamond || {} as any;
  const txs = data.transactions || [];

  return (
    <div className="space-y-6">
      {/* 1. TOP HIGHLIGHT SUMMARY BANNER */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 p-4 bg-gradient-to-r from-amber-950/40 via-gray-900/60 to-purple-950/40 border border-gray-800 rounded-2xl shadow-xl">
        <div className="p-2 border-r border-gray-800/80">
          <div className="text-[11px] font-bold text-amber-400 uppercase tracking-widest flex items-center gap-1">
            <span>🪙 Gold Wastage Profit</span>
          </div>
          <div className={`text-xl sm:text-2xl font-black font-mono mt-1 ${sum.gold_net_wastage_profit_g >= 0 ? 'text-amber-400' : 'text-red-400'}`}>
            {sum.gold_net_wastage_profit_g >= 0 ? '+' : ''}{sum.gold_net_wastage_profit_g.toFixed(3)} g
          </div>
          <div className="text-[10px] text-gray-400 mt-0.5">Sold Wst − Pur Wst</div>
        </div>

        <div className="p-2 border-r border-gray-800/80">
          <div className="text-[11px] font-bold text-cyan-300 uppercase tracking-widest flex items-center gap-1">
            <span>🥈 Silver Wastage Profit</span>
          </div>
          <div className={`text-xl sm:text-2xl font-black font-mono mt-1 ${sum.silver_net_wastage_profit_g >= 0 ? 'text-cyan-300' : 'text-red-400'}`}>
            {sum.silver_net_wastage_profit_g >= 0 ? '+' : ''}{sum.silver_net_wastage_profit_g.toFixed(3)} g
          </div>
          <div className="text-[10px] text-gray-400 mt-0.5">Sold Wst − Pur Wst</div>
        </div>

        <div className="p-2 border-r border-gray-800/80">
          <div className="text-[11px] font-bold text-purple-300 uppercase tracking-widest flex items-center gap-1">
            <span>💎 Diamond Sold</span>
          </div>
          <div className="text-xl sm:text-2xl font-black font-mono mt-1 text-purple-300">
            {sum.diamond_carats_sold.toFixed(4)} cts
          </div>
          <div className="text-[10px] text-gray-400 mt-0.5">Total Carats Traded</div>
        </div>

        <div className="p-2 border-r border-gray-800/80">
          <div className="text-[11px] font-bold text-emerald-400 uppercase tracking-widest flex items-center gap-1">
            <span>🔨 Making/Labour Profit</span>
          </div>
          <div className={`text-xl sm:text-2xl font-black font-mono mt-1 ${sum.total_making_profit_rs >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
            ₹ {sum.total_making_profit_rs.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </div>
          <div className="text-[10px] text-gray-400 mt-0.5">Making Earned − Paid</div>
        </div>

        <div className="p-2 col-span-2 sm:col-span-1">
          <div className="text-[11px] font-bold text-yellow-400 uppercase tracking-widest flex items-center gap-1">
            <span>💰 Net Trading Profit</span>
          </div>
          <div className={`text-xl sm:text-2xl font-black font-mono mt-1 ${sum.total_value_profit_rs >= 0 ? 'text-yellow-400' : 'text-red-400'}`}>
            ₹ {sum.total_value_profit_rs.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </div>
          <div className="text-[10px] text-gray-400 mt-0.5">Sales Val − Pur Cost</div>
        </div>
      </div>

      {/* 2. THREE DEDICATED METAL ANALYSIS CARDS */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* GOLD CARD */}
        <div className="bg-surface border border-amber-500/30 rounded-2xl p-4 sm:p-5 shadow-lg flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-gray-800">
              <h3 className="text-sm font-bold text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
                <span>🪙 Gold (स्वर्ण) Wastage & Profit</span>
              </h3>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 font-mono font-bold">Gold Analysis</span>
            </div>

            <div className="mt-3 space-y-2 text-xs">
              <div className="flex justify-between py-1 border-b border-gray-800/60">
                <span className="text-gray-400">Customer Wastage Charged (Sell):</span>
                <span className="font-mono font-bold text-white">{(g.sold_wastage_g || 0).toFixed(3)} g</span>
              </div>
              <div className="flex justify-between py-1 border-b border-gray-800/60">
                <span className="text-gray-400">Supplier Wastage Paid (Purchase):</span>
                <span className="font-mono font-bold text-red-300">− {(g.purchased_wastage_g || 0).toFixed(3)} g</span>
              </div>
              <div className="flex justify-between py-1.5 bg-amber-500/10 px-2 rounded-lg border border-amber-500/20">
                <span className="font-bold text-amber-400">Net Gold Wastage Profit:</span>
                <span className="font-mono font-black text-amber-400 text-sm">
                  {(g.net_wastage_profit_g || 0) >= 0 ? '+' : ''}{(g.net_wastage_profit_g || 0).toFixed(3)} g
                </span>
              </div>
              <div className="flex justify-between py-1 border-b border-gray-800/60 pt-2">
                <span className="text-gray-400">Fine Gold Sold:</span>
                <span className="font-mono text-gray-200">{(g.sold_fine_g || 0).toFixed(3)} g</span>
              </div>
              <div className="flex justify-between py-1 border-b border-gray-800/60">
                <span className="text-gray-400">Fine Gold Purchased:</span>
                <span className="font-mono text-gray-200">{(g.purchased_fine_g || 0).toFixed(3)} g</span>
              </div>
              <div className="flex justify-between py-1 border-b border-gray-800/60">
                <span className="text-gray-400">Customer Making Earned:</span>
                <span className="font-mono text-emerald-400">₹ {(g.sold_making_rs || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-gray-800/60">
                <span className="text-gray-400">Supplier Labour Paid:</span>
                <span className="font-mono text-red-300">₹ {(g.purchased_labour_rs || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
              </div>
              <div className="flex justify-between py-1.5 bg-gray-900 px-2 rounded-lg font-bold">
                <span className="text-gray-300">Gold Labour Profit:</span>
                <span className="font-mono text-emerald-400">₹ {(g.net_labour_profit_rs || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
              </div>
            </div>
          </div>
        </div>

        {/* SILVER CARD */}
        <div className="bg-surface border border-cyan-500/30 rounded-2xl p-4 sm:p-5 shadow-lg flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-gray-800">
              <h3 className="text-sm font-bold text-cyan-300 uppercase tracking-wider flex items-center gap-1.5">
                <span>🥈 Silver (रजत) Wastage & Profit</span>
              </h3>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 font-mono font-bold">Silver Analysis</span>
            </div>

            <div className="mt-3 space-y-2 text-xs">
              <div className="flex justify-between py-1 border-b border-gray-800/60">
                <span className="text-gray-400">Customer Wastage Charged (Sell):</span>
                <span className="font-mono font-bold text-white">{(s.sold_wastage_g || 0).toFixed(3)} g</span>
              </div>
              <div className="flex justify-between py-1 border-b border-gray-800/60">
                <span className="text-gray-400">Supplier Wastage Paid (Purchase):</span>
                <span className="font-mono font-bold text-red-300">− {(s.purchased_wastage_g || 0).toFixed(3)} g</span>
              </div>
              <div className="flex justify-between py-1.5 bg-cyan-500/10 px-2 rounded-lg border border-cyan-500/20">
                <span className="font-bold text-cyan-300">Net Silver Wastage Profit:</span>
                <span className="font-mono font-black text-cyan-300 text-sm">
                  {(s.net_wastage_profit_g || 0) >= 0 ? '+' : ''}{(s.net_wastage_profit_g || 0).toFixed(3)} g
                </span>
              </div>
              <div className="flex justify-between py-1 border-b border-gray-800/60 pt-2">
                <span className="text-gray-400">Pure Silver Sold:</span>
                <span className="font-mono text-gray-200">{(s.sold_pure_g || 0).toFixed(3)} g</span>
              </div>
              <div className="flex justify-between py-1 border-b border-gray-800/60">
                <span className="text-gray-400">Pure Silver Purchased:</span>
                <span className="font-mono text-gray-200">{(s.purchased_pure_g || 0).toFixed(3)} g</span>
              </div>
              <div className="flex justify-between py-1 border-b border-gray-800/60">
                <span className="text-gray-400">Customer Making Earned:</span>
                <span className="font-mono text-emerald-400">₹ {(s.sold_making_rs || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-gray-800/60">
                <span className="text-gray-400">Supplier Labour Paid:</span>
                <span className="font-mono text-red-300">₹ {(s.purchased_labour_rs || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
              </div>
              <div className="flex justify-between py-1.5 bg-gray-900 px-2 rounded-lg font-bold">
                <span className="text-gray-300">Silver Labour Profit:</span>
                <span className="font-mono text-emerald-400">₹ {(s.net_labour_profit_rs || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
              </div>
            </div>
          </div>
        </div>

        {/* DIAMOND CARD */}
        <div className="bg-surface border border-purple-500/30 rounded-2xl p-4 sm:p-5 shadow-lg flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-gray-800">
              <h3 className="text-sm font-bold text-purple-300 uppercase tracking-wider flex items-center gap-1.5">
                <span>💎 Diamond (हीरा) Margin & Profit</span>
              </h3>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300 font-mono font-bold">Diamond Analysis</span>
            </div>

            <div className="mt-3 space-y-2 text-xs">
              <div className="flex justify-between py-1 border-b border-gray-800/60">
                <span className="text-gray-400">Total Carats Sold:</span>
                <span className="font-mono font-bold text-purple-300">{(d.sold_carats || 0).toFixed(4)} cts</span>
              </div>
              <div className="flex justify-between py-1 border-b border-gray-800/60">
                <span className="text-gray-400">Gold/Mounting Weight:</span>
                <span className="font-mono font-bold text-white">{(d.sold_weight_g || 0).toFixed(3)} g</span>
              </div>
              <div className="flex justify-between py-1 border-b border-gray-800/60">
                <span className="text-gray-400">Setting/Making Charges Earned:</span>
                <span className="font-mono text-emerald-400">₹ {(d.sold_making_rs || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-gray-800/60">
                <span className="text-gray-400">Setting/Labour Charges Paid:</span>
                <span className="font-mono text-red-300">₹ {(d.purchased_labour_rs || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
              </div>
              <div className="flex justify-between py-1.5 bg-purple-500/10 px-2 rounded-lg border border-purple-500/20">
                <span className="font-bold text-purple-300">Net Setting Profit:</span>
                <span className="font-mono font-black text-purple-300 text-sm">
                  ₹ {(d.net_making_profit_rs || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </span>
              </div>
              <div className="flex justify-between py-1 border-b border-gray-800/60 pt-2">
                <span className="text-gray-400">Diamond Sales Value:</span>
                <span className="font-mono text-gray-200">₹ {(d.sold_total_val_rs || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-gray-800/60">
                <span className="text-gray-400">Diamond Purchase Cost:</span>
                <span className="font-mono text-gray-200">₹ {(d.purchased_total_val_rs || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
              </div>
              <div className="flex justify-between py-1.5 bg-gray-900 px-2 rounded-lg font-bold">
                <span className="text-gray-300">Diamond Net Margin:</span>
                <span className="font-mono text-yellow-400">₹ {(d.net_val_profit_rs || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 3. TRANSACTION AUDIT TABLE */}
      <div className="bg-surface border border-gray-800 rounded-2xl p-4 sm:p-5 shadow-lg">
        <h4 className="text-xs sm:text-sm font-bold text-primary uppercase tracking-wider mb-3 flex items-center justify-between">
          <span>Detailed Itemized Wastage & Weight Breakdown ({txs.length} Transactions)</span>
          <span className="text-[10px] text-gray-400 font-normal">Audit Trail (Sales & Purchases)</span>
        </h4>

        {txs.length === 0 ? (
          <div className="py-8 text-center text-xs text-gray-500">No transactions recorded in this date range.</div>
        ) : (
          <div className="overflow-x-auto whitespace-nowrap custom-scrollbar">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-gray-800 text-gray-400 uppercase text-[10px] font-bold">
                  <th className="py-2 px-3">Date</th>
                  <th className="py-2 px-3">Type</th>
                  <th className="py-2 px-3">Bill No.</th>
                  <th className="py-2 px-3">Item Name</th>
                  <th className="py-2 px-3">Metal</th>
                  <th className="py-2 px-3 text-right">Gross Wt</th>
                  <th className="py-2 px-3 text-right">Touch %</th>
                  <th className="py-2 px-3 text-right">Wastage %</th>
                  <th className="py-2 px-3 text-right text-amber-400">Wastage (g)</th>
                  <th className="py-2 px-3 text-right">Fine Wt (g)</th>
                  <th className="py-2 px-3 text-right">Making (₹)</th>
                  <th className="py-2 px-3 text-right">Total (₹)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800/60 font-mono">
                {txs.map((tx, idx) => (
                  <tr key={idx} className="hover:bg-gray-800/30 transition-colors">
                    <td className="py-2 px-3 text-gray-400 font-sans">{tx.date}</td>
                    <td className="py-2 px-3 font-sans">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${tx.type === 'Sale' ? 'bg-emerald-500/20 text-emerald-300' : 'bg-amber-500/20 text-amber-300'}`}>
                        {tx.type}
                      </span>
                    </td>
                    <td className="py-2 px-3 font-bold text-white">{tx.bill_no}</td>
                    <td className="py-2 px-3 font-sans text-gray-300">{tx.item_name}</td>
                    <td className="py-2 px-3 font-sans">
                      <span className={tx.metal === 'Gold' ? 'text-amber-400 font-bold' : tx.metal === 'Silver' ? 'text-cyan-300 font-bold' : 'text-purple-300 font-bold'}>
                        {tx.metal}
                      </span>
                    </td>
                    <td className="py-2 px-3 text-right">{tx.weight_g.toFixed(3)}</td>
                    <td className="py-2 px-3 text-right">{tx.touch_pct.toFixed(2)}%</td>
                    <td className="py-2 px-3 text-right">{tx.wastage_pct.toFixed(2)}%</td>
                    <td className="py-2 px-3 text-right text-amber-400 font-bold">{tx.wastage_g.toFixed(3)} g</td>
                    <td className="py-2 px-3 text-right text-gray-200">{tx.fine_weight_g.toFixed(3)}</td>
                    <td className="py-2 px-3 text-right text-emerald-400">₹ {tx.making_charges.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</td>
                    <td className="py-2 px-3 text-right font-bold text-white">₹ {tx.total_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
"""

# Insert WastageProfitView component into file
insert_point = "export default function ReportViewer"
code = code.replace(insert_point, wastage_view_component + "\n" + insert_point)

# In the render method, if reportType === 'Wastage Profit', render <WastageProfitView data={data} />
old_render_start = "{/* KPI Cards */}\n      <div className=\"grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4\">"
new_render_start = """{reportType === 'Wastage Profit' ? (
        <WastageProfitView data={data} />
      ) : (
        <>
      {/* KPI Cards */}
      <div className=\"grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4\">"""

code = code.replace(old_render_start, new_render_start)

# Close the condition right before closing tag
old_chart_end = """        <div className=\"hidden print:block mt-8\">
          <table className=\"w-full text-left text-sm border-collapse border border-gray-800\">
            <thead>
              <tr className=\"bg-gray-100 text-black\">
                {Object.keys(data.chart[0]).map(k => (
                  <th key={k} className=\"p-2 border border-gray-300 uppercase\">{k}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.chart.map((row: any, i: number) => (
                <tr key={i}>
                  {Object.values(row).map((v: any, j: number) => (
                    <td key={j} className=\"p-2 border border-gray-300 text-black\">{v}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

    </div>"""

new_chart_end = """        <div className=\"hidden print:block mt-8\">
          <table className=\"w-full text-left text-sm border-collapse border border-gray-800\">
            <thead>
              <tr className=\"bg-gray-100 text-black\">
                {Object.keys(data.chart[0]).map(k => (
                  <th key={k} className=\"p-2 border border-gray-300 uppercase\">{k}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.chart.map((row: any, i: number) => (
                <tr key={i}>
                  {Object.values(row).map((v: any, j: number) => (
                    <td key={j} className=\"p-2 border border-gray-300 text-black\">{v}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      </>
      )}

    </div>"""

code = code.replace(old_chart_end, new_chart_end)

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)

print("ReportViewer.tsx updated with dedicated WastageProfitView!")
