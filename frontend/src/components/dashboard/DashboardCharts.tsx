import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line, CartesianGrid, Cell } from 'recharts';

interface SalesTrendProps {
  data: { name: string; sales: number }[];
}

export function SalesTrendChart({ data }: SalesTrendProps) {
  return (
    <div className="bg-surface rounded-xl border border-gray-800 p-6 h-96 flex flex-col shadow-[0_0_20px_rgba(0,0,0,0.5)]">
      <h3 className="font-bold text-lg text-textMain mb-4 flex items-center gap-2">
        Sales Trend <span className="text-xs font-normal px-2 py-1 bg-primary/10 text-primary rounded-full">Last 7 Days</span>
      </h3>
      <div className="flex-1">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2a2a2a" vertical={false} />
            <XAxis dataKey="name" stroke="#6b7280" axisLine={false} tickLine={false} tick={{ fontSize: 12 }} />
            <YAxis stroke="#6b7280" axisLine={false} tickLine={false} tickFormatter={(value) => `₹${value > 1000 ? (value/1000).toFixed(1) + 'k' : value}`} tick={{ fontSize: 12 }} />
            <Tooltip 
              contentStyle={{ backgroundColor: '#1f1f1f', borderColor: '#374151', borderRadius: '12px', boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.5)' }}
              itemStyle={{ color: '#d4af37', fontWeight: 'bold' }}
              labelStyle={{ color: '#9ca3af' }}
            />
            <Line type="monotone" dataKey="sales" stroke="url(#colorSales)" strokeWidth={3} dot={{ fill: '#d4af37', r: 4, strokeWidth: 2, stroke: '#111' }} activeDot={{ r: 6, stroke: '#d4af37', strokeWidth: 2 }} />
            <defs>
              <linearGradient id="colorSales" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stopColor="#d4af37" />
                <stop offset="100%" stopColor="#fef08a" />
              </linearGradient>
            </defs>
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

interface TopSellingProps {
  data: { name: string; qty: number }[];
}

export function TopSellingChart({ data }: TopSellingProps) {
  return (
    <div className="bg-surface rounded-xl border border-gray-800 p-6 h-96 flex flex-col shadow-[0_0_20px_rgba(0,0,0,0.5)]">
      <h3 className="font-bold text-lg text-textMain mb-4 flex items-center gap-2">
        Top Selling Categories <span className="text-xs font-normal px-2 py-1 bg-primary/10 text-primary rounded-full">Last 30 Days</span>
      </h3>
      <div className="flex-1">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="vertical" margin={{ top: 0, right: 0, left: 10, bottom: 0 }}>
            <XAxis type="number" hide />
            <YAxis dataKey="name" type="category" stroke="#9ca3af" axisLine={false} tickLine={false} width={100} tick={{ fontSize: 13 }} />
            <Tooltip 
              cursor={{ fill: '#1f1f1f' }}
              contentStyle={{ backgroundColor: '#1f1f1f', borderColor: '#374151', borderRadius: '12px', boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.5)' }}
              itemStyle={{ color: '#d4af37', fontWeight: 'bold' }}
              labelStyle={{ color: '#9ca3af' }}
            />
            <Bar dataKey="qty" radius={[0, 6, 6, 0]} barSize={20}>
              {data.map((_, index) => (
                <Cell key={`cell-${index}`} fill={`hsl(43, 65%, ${50 + (index * 5)}%)`} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
