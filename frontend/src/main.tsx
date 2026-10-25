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
import App from './App'
import './index.css'

function ErrorFallback({error, resetErrorBoundary}: any) {
  return (
    <div role="alert" className="p-10 bg-red-900 text-white min-h-screen">
      <h2 className="text-3xl font-bold mb-4">Something went wrong:</h2>
      <pre className="text-red-200 whitespace-pre-wrap">{error?.message || 'An unexpected error occurred.'}</pre>
      {import.meta.env.DEV && error?.stack && (
        <pre className="text-red-300 mt-4 text-xs whitespace-pre-wrap">{error.stack}</pre>
      )}
      <button onClick={resetErrorBoundary} className="mt-6 px-4 py-2 bg-white text-red-900 rounded font-bold">Try again</button>
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
