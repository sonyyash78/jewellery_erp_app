import { PlusCircle, Users, Package, FileText, Receipt, FileSpreadsheet } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function QuickShortcuts() {
  const shortcuts = [
    { name: 'New Bill', icon: <Receipt size={24} />, path: '/billing', color: 'bg-green-500/10 text-green-500' },
    { name: 'Add Customer', icon: <Users size={24} />, path: '/customers', color: 'bg-blue-500/10 text-blue-500' },
    { name: 'Add Inventory', icon: <Package size={24} />, path: '/inventory', color: 'bg-purple-500/10 text-purple-500' },
    { name: 'New Purchase', icon: <FileText size={24} />, path: '/purchases', color: 'bg-orange-500/10 text-orange-500' },
    { name: 'Exchange', icon: <PlusCircle size={24} />, path: '/exchange', color: 'bg-primary/10 text-primary' },
    { name: 'Reports', icon: <FileSpreadsheet size={24} />, path: '/reports', color: 'bg-teal-500/10 text-teal-500' },
  ];

  return (
    <div className="bg-surface rounded-xl border border-gray-800 p-4 sm:p-6">
      <h3 className="font-bold text-base sm:text-lg text-textMain mb-3 sm:mb-4">Quick Shortcuts</h3>
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5 sm:gap-4">
        {shortcuts.map(s => (
          <Link 
            key={s.name} 
            to={s.path}
            className="flex flex-col items-center justify-center p-3 sm:p-4 rounded-lg bg-background border border-gray-800 hover:border-gray-600 transition-colors group text-center"
          >
            <div className={`p-2.5 sm:p-3 rounded-full mb-2 sm:mb-3 ${s.color} group-hover:scale-110 transition-transform`}>
              {s.icon}
            </div>
            <span className="text-xs sm:text-sm font-medium text-textMuted group-hover:text-textMain">{s.name}</span>
          </Link>
        ))}
      </div>
    </div>
  );
}
