import { useEffect, lazy, Suspense } from 'react';
import { Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { BACKEND_BASE_URL } from './config/api';
import Login from './pages/Login';
import AdminLayout from './components/layout/AdminLayout';
import ProtectedRoute from './routes/ProtectedRoute';

// Lazy-loaded routes for lightning-fast initial load & snappy navigation
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Billing = lazy(() => import('./pages/billing'));
const Purchase = lazy(() => import('./pages/purchase'));
const Inventory = lazy(() => import('./pages/inventory'));
const InvoiceHistory = lazy(() => import('./pages/invoices/InvoiceHistory'));
const CRM = lazy(() => import('./pages/crm'));
const ExchangeModule = lazy(() => import('./pages/exchange'));
const ReportsModule = lazy(() => import('./pages/reports'));
const SettingsModule = lazy(() => import('./pages/settings'));
const VerifyInvoice = lazy(() => import('./pages/VerifyInvoice'));
const ResetPassword = lazy(() => import('./pages/ResetPassword'));

const ModuleFallback = () => (
  <div className="flex h-full w-full min-h-[400px] items-center justify-center p-8">
    <div className="flex flex-col items-center gap-3">
      <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
      <span className="text-xs text-textMuted font-medium tracking-wide">Loading module...</span>
    </div>
  </div>
);

function App() {
  // Keep Render backend awake with proactive 2-minute keepalive heartbeat
  useEffect(() => {
    const keepAlive = () => {
      fetch(`${BACKEND_BASE_URL}/ping`, { method: 'GET', mode: 'cors' }).catch(() => {});
    };
    keepAlive();
    const interval = setInterval(keepAlive, 2 * 60 * 1000); // Heartbeat every 2 minutes while active
    return () => clearInterval(interval);
  }, []);

  return (
    <>
      <Toaster position="top-right" toastOptions={{ 
        style: { background: '#171717', color: '#f3f4f6', border: '1px solid #374151' } 
      }} />
      <Suspense fallback={<ModuleFallback />}>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/reset-password" element={<ResetPassword />} />
          <Route path="/verify" element={<VerifyInvoice />} />
          <Route path="/verify/:invoiceNumber" element={<VerifyInvoice />} />
          
          {/* Protected Routes */}
          <Route element={<ProtectedRoute />}>
            <Route element={<AdminLayout />}>
              <Route path="/" element={<Dashboard />} />
              <Route path="/customers" element={<CRM />} />
              <Route path="/exchange" element={<ExchangeModule />} />
              <Route path="/reports" element={<ReportsModule />} />
              <Route path="/settings" element={<SettingsModule />} />
              <Route path="/products" element={<div className="p-4">Products Module Coming Soon</div>} />
              <Route path="/inventory" element={<Inventory />} />
              <Route path="/billing" element={<Billing />} />
              <Route path="/invoices" element={<InvoiceHistory />} />
              <Route path="/purchases" element={<Purchase />} />
            </Route>
          </Route>
        </Routes>
      </Suspense>
    </>
  );
}

export default App;
