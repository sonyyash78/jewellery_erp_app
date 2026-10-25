/**
 * Global API & Backend URL configuration.
 * Dynamically resolves to:
 * - Local desktop backend in Electron / Offline mode
 * - Live Render backend when running in cloud production (e.g. Vercel)
 * - Localhost during local development
 */

export const getBackendBaseUrl = (): string => {
  // If running inside Electron desktop app or offline mode, always use local backend
  if (
    typeof window !== 'undefined' &&
    (window.navigator.userAgent.includes('Electron') ||
      (window as any).isElectron ||
      (window as any).electronAPI ||
      window.location.protocol === 'file:')
  ) {
    const customUrl = (window as any).electronAPI?.getBackendUrl?.();
    if (customUrl) return customUrl.replace(/\/+$/, '');
    return 'http://127.0.0.1:8000';
  }

  const envBackend = import.meta.env.VITE_BACKEND_URL;
  if (envBackend && !envBackend.includes('localhost') && !envBackend.includes('127.0.0.1')) {
    return envBackend.replace(/\/+$/, '');
  }

  const envApi = import.meta.env.VITE_API_URL;
  if (envApi && !envApi.includes('localhost') && !envApi.includes('127.0.0.1')) {
    return envApi.replace(/\/api\/v1\/?$/, '').replace(/\/+$/, '');
  }

  // Deployed production environment (e.g. Vercel preview or production)
  if (typeof window !== 'undefined' && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
    return 'https://saideep-backend-loet.onrender.com';
  }

  return 'http://localhost:8000';
};

export const BACKEND_BASE_URL = getBackendBaseUrl();
export const API_BASE_URL = `${BACKEND_BASE_URL}/api/v1`;
