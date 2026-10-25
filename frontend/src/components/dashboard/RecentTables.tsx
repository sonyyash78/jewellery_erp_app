export default function RecentTables({ data }: { data: { recent_bills: any[], recent_purchases: any[] } }) {
  if (!data) return <div className="h-64 bg-surface animate-pulse rounded-xl border border-gray-800"></div>;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="bg-surface rounded-xl border border-gray-800 p-6">
        <h3 className="font-bold text-lg text-textMain mb-4">Recent Bills</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="text-textMuted border-b border-gray-800">
                <th className="pb-3 font-medium">Invoice #</th>
                <th className="pb-3 font-medium">Date</th>
                <th className="pb-3 font-medium text-right">Amount</th>
              </tr>
            </thead>
            <tbody>
              {data.recent_bills.length === 0 ? (
                <tr><td colSpan={3} className="py-4 text-center text-textMuted italic">No recent bills</td></tr>
              ) : (
                data.recent_bills.map((bill, i) => (
                  <tr key={i} className="border-b border-gray-800/50 hover:bg-gray-800/20">
                    <td className="py-3 font-medium text-primary">{bill.invoice_number}</td>
                    <td className="py-3 text-textMuted">{new Date(bill.date).toLocaleDateString()}</td>
                    <td className="py-3 text-right font-semibold text-textMain">₹ {bill.amount.toLocaleString()}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      <div className="bg-surface rounded-xl border border-gray-800 p-6">
        <h3 className="font-bold text-lg text-textMain mb-4">Recent Expenses/Purchases</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="text-textMuted border-b border-gray-800">
                <th className="pb-3 font-medium">Description</th>
                <th className="pb-3 font-medium">Date</th>
                <th className="pb-3 font-medium text-right">Amount</th>
              </tr>
            </thead>
            <tbody>
              {data.recent_purchases.length === 0 ? (
                <tr><td colSpan={3} className="py-4 text-center text-textMuted italic">No recent purchases</td></tr>
              ) : (
                data.recent_purchases.map((purchase, i) => (
                  <tr key={i} className="border-b border-gray-800/50 hover:bg-gray-800/20">
                    <td className="py-3 text-textMain">{purchase.description}</td>
                    <td className="py-3 text-textMuted">{new Date(purchase.date).toLocaleDateString()}</td>
                    <td className="py-3 text-right font-semibold text-red-400">₹ {purchase.amount.toLocaleString()}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
