import { useState, useEffect } from 'react';
import { Outlet, useLocation, Link, Navigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { axiosClient } from '../../api/axiosClient';
import { LayoutDashboard, Users, ArrowLeftRight, LogOut, Package, Settings, Receipt, FileText, ShoppingBag, BarChart2, Menu, X, Database, ShieldAlert } from 'lucide-react';
import AIAssistant from '../ai/AIAssistant';
import { BACKEND_BASE_URL } from '../../config/api';

export default function AdminLayout() {
  const logout = useAuthStore(state => state.logout);
  const user = useAuthStore(state => state.user);
  const setAuth = useAuthStore(state => state.setAuth);
  const token = useAuthStore(state => state.token);
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const syncStoreDetails = () => {
    if (token) {
      axiosClient.get('/auth/me')
        .then(res => {
          if (res.data) {
            setAuth(token, res.data);
          }
        })
        .catch(() => {});
    }
  };

  useEffect(() => {
    syncStoreDetails();
    window.addEventListener('settings-updated', syncStoreDetails);
    return () => window.removeEventListener('settings-updated', syncStoreDetails);
  }, [token]);

  useEffect(() => {
    setMobileMenuOpen(false);
  }, [location.pathname]);

  const backendBase = BACKEND_BASE_URL;
  const logoPath = user?.logo_url || `/static/logo_store_${user?.tenant_id || 1}.png`;
  const logoSrc = logoPath.startsWith('http') ? logoPath : `${backendBase}${logoPath.startsWith('/') ? '' : '/'}${logoPath}`;

  const allNavItems = [
    { key: 'dashboard', name: 'Dashboard', path: '/', icon: <LayoutDashboard size={20} /> },
    { key: 'customers', name: 'Customers', path: '/customers', icon: <Users size={20} /> },
    { key: 'inventory', name: 'Inventory', path: '/inventory', icon: <Package size={20} /> },
    { key: 'billing', name: 'Billing', path: '/billing', icon: <Receipt size={20} /> },
    { key: 'invoices', name: 'Invoices', path: '/invoices', icon: <FileText size={20} /> },
    { key: 'exchange', name: 'Exchange', path: '/exchange', icon: <ArrowLeftRight size={20} /> },
    { key: 'purchases', name: 'Purchases', path: '/purchases', icon: <ShoppingBag size={20} /> },
    { key: 'reports', name: 'Reports', path: '/reports', icon: <BarChart2 size={20} /> },
    { key: 'settings', name: 'Settings', path: '/settings', icon: <Settings size={20} /> },
  ];

  const isOwner = user?.is_owner !== false;
  const allowedModules: string[] = isOwner
    ? allNavItems.map(i => i.key)
    : (Array.isArray(user?.allowed_modules) && user.allowed_modules.length > 0
        ? user.allowed_modules
        : ['billing', 'invoices', 'exchange', 'customers', 'inventory']);

  const navItems = allNavItems.filter(item => allowedModules.includes(item.key));
  const currentMatchedItem = allNavItems.find(i => i.path === location.pathname);
  const isCurrentRouteRestricted = currentMatchedItem && !allowedModules.includes(currentMatchedItem.key);

  if (isCurrentRouteRestricted && location.pathname === '/' && navItems.length > 0) {
    return <Navigate to={navItems[0].path} replace />;
  }

  return (
    <div className="flex h-screen bg-background text-textMain overflow-hidden relative">
      <AIAssistant />

      {/* Mobile Slide-out Drawer */}
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-50 md:hidden flex">
          <div 
            className="fixed inset-0 bg-black/70 backdrop-blur-sm transition-opacity" 
            onClick={() => setMobileMenuOpen(false)} 
          />
          <aside className="relative w-72 max-w-[80vw] bg-surface border-r border-gray-800 flex flex-col z-10 h-full shadow-2xl">
            <div className="h-16 flex items-center justify-between border-b border-gray-800 px-4">
              <div className="flex items-center gap-2 min-w-0">
                <div className="w-8 h-8 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center overflow-hidden flex-shrink-0">
                  <img 
                    src={logoSrc}
                    alt="Logo"
                    className="w-full h-full object-contain"
                    onError={(e) => {
                      e.currentTarget.src = `${backendBase}/static/logo.png`;
                    }}
                  />
                </div>
                <span className="text-sm font-bold text-primary truncate">{user?.store_name || 'Jewellery ERP'}</span>
              </div>
              <button 
                onClick={() => setMobileMenuOpen(false)}
                className="p-1.5 text-gray-400 hover:text-white rounded-lg hover:bg-gray-800"
                aria-label="Close menu"
              >
                <X size={20} />
              </button>
            </div>
            <nav className="flex-1 p-4 space-y-1.5 overflow-y-auto">
              {navItems.map(item => (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                    location.pathname === item.path 
                      ? 'bg-primary/10 text-primary border border-primary/20 font-semibold' 
                      : 'text-textMuted hover:bg-gray-800 hover:text-textMain'
                  }`}
                >
                  {item.icon}
                  <span className="font-medium">{item.name}</span>
                </Link>
              ))}
            </nav>
            <div className="p-4 border-t border-gray-800">
              <button 
                onClick={() => { setMobileMenuOpen(false); logout(); }}
                className="w-full flex items-center justify-center space-x-2 text-red-400 hover:text-red-300 transition-colors bg-red-400/10 py-2.5 rounded-lg"
              >
                <LogOut size={16} />
                <span className="text-sm font-medium">Logout</span>
              </button>
            </div>
          </aside>
        </div>
      )}

      {/* Desktop Sidebar */}
      <aside className="w-64 bg-surface border-r border-gray-800 flex flex-col hidden md:flex print:hidden">
        <div className="h-16 flex items-center gap-3 border-b border-gray-800 px-4">
          <div className="w-9 h-9 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center overflow-hidden flex-shrink-0">
            <img 
              key={`${logoSrc}-${user?.store_name}`}
              src={logoSrc}
              alt="Logo"
              className="w-full h-full object-contain"
              onError={(e) => {
                e.currentTarget.src = `${backendBase}/static/logo.png`;
              }}
            />
          </div>
          <div className="flex flex-col min-w-0 flex-1">
            <h1 className="text-sm font-bold text-primary tracking-wide uppercase truncate" title={user?.store_name || 'Jewellery ERP'}>
              {user?.store_name || 'Jewellery ERP'}
            </h1>
            <span className="text-[10px] text-gray-500 uppercase tracking-widest truncate">
              {user?.role_name || 'Shop Owner'}
            </span>
          </div>
        </div>
        <nav className="flex-1 p-4 space-y-2">
          {navItems.map(item => (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                location.pathname === item.path 
                  ? 'bg-primary/10 text-primary border border-primary/20' 
                  : 'text-textMuted hover:bg-gray-800 hover:text-textMain'
              }`}
            >
              {item.icon}
              <span className="font-medium">{item.name}</span>
            </Link>
          ))}
        </nav>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Navbar */}
        <header className="h-16 bg-surface border-b border-gray-800 flex items-center justify-between px-3 sm:px-6">
          <div className="flex items-center gap-2 min-w-0">
            <button
              onClick={() => setMobileMenuOpen(true)}
              className="md:hidden p-1.5 text-gray-400 hover:text-white rounded-lg hover:bg-gray-800 transition-colors focus:outline-none"
              aria-label="Open menu"
            >
              <Menu size={22} />
            </button>
            <div className="text-base sm:text-lg font-semibold text-textMuted truncate">
              {allNavItems.find(i => i.path === location.pathname)?.name || 'Admin'}
            </div>
          </div>
          <div className="flex items-center space-x-1.5 sm:space-x-3 shrink-0">
            <div className="flex items-center space-x-1.5">
              <span className="text-xs sm:text-sm text-textMuted hidden sm:inline">Welcome,</span>
              <span className="text-xs sm:text-sm text-primary font-medium truncate max-w-[85px] sm:max-w-[140px] md:max-w-none">
                {user?.full_name || user?.username || 'User'}
              </span>
              {user?.role_name && !isOwner && (
                <span className="text-[10px] bg-blue-500/20 text-blue-300 border border-blue-500/30 px-1.5 py-0.5 rounded font-semibold uppercase tracking-wider">
                  {user.role_name}
                </span>
              )}
              {user?.store_name && (
                <span className="text-[11px] sm:text-xs bg-primary/20 text-primary border border-primary/30 px-1.5 sm:px-2 py-0.5 rounded font-semibold hidden md:inline-block truncate max-w-[120px]">
                  {user.store_name}
                </span>
              )}
            </div>
            {allowedModules.includes('settings') && (
              <Link
                to="/settings?tab=database"
                className="flex items-center gap-1 text-xs text-primary/90 hover:text-primary bg-primary/10 hover:bg-primary/20 border border-primary/20 hover:border-primary/40 px-2 sm:px-2.5 py-1.5 rounded transition font-medium"
                title="Store Data & Backup"
              >
                <Database size={13} />
                <span className="hidden lg:inline">Store Backup</span>
              </Link>
            )}
            <button 
              onClick={logout}
              className="flex items-center space-x-1 text-red-400 hover:text-red-300 transition-colors bg-red-400/10 px-2 sm:px-2.5 py-1.5 rounded"
              title="Logout"
            >
              <LogOut size={14} />
              <span className="text-xs hidden sm:inline">Logout</span>
            </button>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-auto p-2 sm:p-4 md:p-6">
          {isCurrentRouteRestricted ? (
            <div className="h-full flex flex-col items-center justify-center text-center p-6">
              <div className="bg-surface border border-gray-800 rounded-2xl p-8 max-w-md shadow-xl flex flex-col items-center gap-4">
                <div className="w-14 h-14 rounded-full bg-red-500/10 border border-red-500/30 flex items-center justify-center text-red-400">
                  <ShieldAlert size={28} />
                </div>
                <h2 className="text-xl font-bold text-white">Access Restricted</h2>
                <p className="text-sm text-gray-400">
                  Your staff account (<span className="text-primary font-semibold">{user?.role_name || 'Staff'}</span>) does not have permission to view the <span className="text-white font-semibold">{currentMatchedItem?.name}</span> module. Please contact the Shop Owner if you need access.
                </p>
                {navItems.length > 0 && (
                  <Link
                    to={navItems[0].path}
                    className="mt-2 bg-primary text-black font-bold text-sm px-5 py-2.5 rounded-lg hover:bg-primary/90 transition-colors"
                  >
                    Go to {navItems[0].name}
                  </Link>
                )}
              </div>
            </div>
          ) : (
            <Outlet />
          )}
        </main>
      </div>
    </div>
  );
}

