import { useState } from 'react';
import ReportViewer from './ReportViewer';
import { LineChart, LayoutDashboard, Package, Users, Landmark, Receipt, Banknote } from 'lucide-react';

export default function ReportsModule() {
  const [activeReport, setActiveReport] = useState('Sales');

  const navs = [
    { name: 'Sales', icon: <LineChart size={18} /> },
    { name: 'Purchases', icon: <Package size={18} /> },
    { name: 'Profit', icon: <Landmark size={18} /> },
    { name: 'Metal Flow', icon: <Package size={18} /> },
    { name: 'Inventory', icon: <LayoutDashboard size={18} /> },
    { name: 'GST', icon: <Receipt size={18} /> },
    { name: 'Customers', icon: <Users size={18} /> },
    { name: 'Suppliers', icon: <Users size={18} /> },
    { name: 'Expenses', icon: <Banknote size={18} /> },
  ];

  return (
    <div className="flex flex-col lg:flex-row h-auto lg:h-[calc(100vh-6rem)] gap-4 overflow-y-auto lg:overflow-hidden">
      
      {/* Left Navigation */}
      <div className="w-full lg:w-64 bg-surface border border-gray-800 rounded-xl shadow-lg flex flex-row lg:flex-col overflow-x-auto lg:overflow-y-auto shrink-0 print:hidden custom-scrollbar">
        <div className="hidden lg:block p-4 border-b border-gray-800 shrink-0">
          <h2 className="text-primary font-bold uppercase tracking-widest text-sm">Analytics Engine</h2>
        </div>
        <div className="flex lg:flex-col overflow-x-auto lg:overflow-y-auto p-2 gap-1.5 whitespace-nowrap custom-scrollbar w-full">
          {navs.map(nav => (
            <button
              key={nav.name}
              onClick={() => setActiveReport(nav.name)}
              className={`shrink-0 lg:w-full flex items-center gap-2 lg:gap-3 px-3 lg:px-4 py-2 lg:py-3 rounded-lg text-left transition-colors font-bold text-xs sm:text-sm ${
                activeReport === nav.name 
                  ? 'bg-primary/20 text-primary border border-primary/30' 
                  : 'text-textMuted hover:bg-gray-800 hover:text-textMain'
              }`}
            >
              <span className={activeReport === nav.name ? 'text-primary' : 'text-gray-500'}>{nav.icon}</span>
              <span>{nav.name} Report</span>
            </button>
          ))}
        </div>
      </div>

      {/* Right Viewer */}
      <div className="flex-1 min-w-0 overflow-y-auto custom-scrollbar">
        <ReportViewer reportType={activeReport} />
      </div>

    </div>
  );
}
