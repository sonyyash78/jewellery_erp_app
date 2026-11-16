// Canonicalize preview domains to production domain so Google OAuth origin always matches
if (
  typeof window !== 'undefined' &&
  window.location.hostname.endsWith('.vercel.app') &&
  window.location.hostname !== 'jewellery-erp-beta.vercel.app'
) {
  const target = `https://jewellery-erp-beta.vercel.app${window.location.pathname}${window.location.search}${window.location.hash}`;
  window.location.replace(target);
}

import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, HashRouter } from 'react-router-dom'
import { ErrorBoundary } from 'react-error-boundary'
import toast from 'react-hot-toast'
import App from './App'
import './index.css'
import { initGlobalEnterNavigation } from './utils/keyboardNavigation'
import { getErrorMessage } from './utils/errorUtils'

// Initialize global ERP Enter-to-Next-Field navigation across the entire application
initGlobalEnterNavigation();

// GLOBAL DEFENSE: Monkey-patch toast.error and toast so that passing an Object, Axios error,
// or Pydantic validation array never throws React Error #31 ("Objects are not valid as a React child")
const originalToastError = toast.error;
toast.error = (message: any, options?: any) => {
  const safeMsg = typeof message === 'string' ? message : getErrorMessage(message);
  return originalToastError(safeMsg, options);
};

function ErrorFallback({error, resetErrorBoundary}: any) {
  const handleReload = () => {
    resetErrorBoundary();
    if (typeof window !== 'undefined') {
      window.location.href = window.location.pathname + '#/';
      window.location.reload();
    }
  };

  return (
    <div role="alert" className="p-8 sm:p-12 bg-[#0F0F12] text-white min-h-screen flex flex-col justify-center items-center">
      <div className="max-w-xl w-full bg-[#18181D] border border-red-500/30 rounded-xl p-8 shadow-2xl space-y-5 text-center">
        <div className="w-14 h-14 bg-red-500/20 rounded-full flex items-center justify-center mx-auto text-red-400 text-2xl font-bold">
          !
        </div>
        <h2 className="text-2xl font-bold text-white tracking-wide">Something went wrong</h2>
        <p className="text-gray-400 text-sm">
          An unexpected interface error occurred. You can easily reload the application to continue safely.
        </p>
        <pre className="text-red-400 bg-black/50 p-4 rounded-lg text-xs font-mono text-left overflow-x-auto border border-red-500/20 max-h-48 custom-scrollbar whitespace-pre-wrap">
          {error?.message || 'An unexpected error occurred.'}
        </pre>
        <div className="flex gap-4 justify-center pt-2">
          <button 
            onClick={handleReload}
            className="px-5 py-2.5 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 text-black rounded-lg font-bold shadow-lg transition-all"
          >
            Return to Dashboard
          </button>
          <button 
            onClick={resetErrorBoundary} 
            className="px-5 py-2.5 bg-gray-800 hover:bg-gray-700 text-white rounded-lg font-semibold transition-all border border-gray-700"
          >
            Try again
          </button>
        </div>
      </div>
    </div>
  )
}

import { GoogleOAuthProvider } from '@react-oauth/google';

const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || '600695546964-a2qcg0vtcn4o15e7pma3msimvol3n4fr.apps.googleusercontent.com';

// Select HashRouter for local file:// Electron environments and BrowserRouter for standard HTTP
const isFileProtocol = typeof window !== 'undefined' && window.location.protocol === 'file:';
const isElectron = typeof window !== 'undefined' && (
  window.navigator.userAgent.includes('Electron') ||
  Boolean((window as any).isElectron) ||
  Boolean((window as any).electronAPI)
);
const Router = (isFileProtocol || (isElectron && !window.location.hostname)) ? HashRouter : BrowserRouter;

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <ErrorBoundary FallbackComponent={ErrorFallback}>
      <Router>
        <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
          <App />
        </GoogleOAuthProvider>
      </Router>
    </ErrorBoundary>
  </React.StrictMode>,
)
