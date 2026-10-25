import axios from 'axios';
import type { AxiosResponse } from 'axios';
import { useAuthStore } from '../store/authStore';

import { API_BASE_URL } from '../config/api';

// In-flight request deduplication map to prevent double-click storming
const inFlightRequests = new Map<string, Promise<AxiosResponse<any>>>();

export const clearApiCache = (pattern?: string) => {
  if (!pattern) {
    inFlightRequests.clear();
  } else {
    for (const key of inFlightRequests.keys()) {
      if (key.includes(pattern)) {
        inFlightRequests.delete(key);
      }
    }
  }
};

export const axiosClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 90000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Intercept requests to attach JWT
axiosClient.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Intercept responses to handle auto-retry, 401 Unauthorized, and Cache Invalidation on Mutations
axiosClient.interceptors.response.use(
  (response) => {
    const method = response.config.method?.toLowerCase();
    // If a mutation was performed (POST, PUT, PATCH, DELETE), clear cached GET data so fresh data is fetched
    if (method && method !== 'get' && method !== 'head') {
      clearApiCache();
    }
    return response;
  },
  async (error: any) => {
    const config = error.config;

    // Handle 401 Unauthorized (except on login / register endpoints so users can see the error message)
    if (error.response && error.response.status === 401) {
      if (!config?.url?.includes('/auth/login') && !config?.url?.includes('/auth/register')) {
        useAuthStore.getState().logout();
        if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
          window.location.href = '/login';
        }
      }
      return Promise.reject(error);
    }

    // Auto-retry ONLY idempotent safe methods (GET, HEAD, OPTIONS) when backend is waking up (502/503/504 or timeout).
    // Non-idempotent mutations (POST, PUT, PATCH, DELETE) MUST NEVER be automatically retried
    // by the HTTP client to guarantee no duplicate records (invoices, sales, transactions) are created.
    const reqMethod = config?.method?.toLowerCase() || 'get';
    const isIdempotent = ['get', 'head', 'options'].includes(reqMethod);

    const isNetworkOrColdStart =
      !error.response ||
      error.code === 'ECONNABORTED' ||
      Boolean(error.message && error.message.toLowerCase().includes('timeout')) ||
      (error.response && [502, 503, 504].includes(error.response.status));

    if (config && isNetworkOrColdStart && isIdempotent) {
      config.__retryCount = config.__retryCount || 0;
      const MAX_RETRIES = 2;

      if (config.__retryCount < MAX_RETRIES) {
        config.__retryCount += 1;
        const delay = config.__retryCount * 1500;
        await new Promise((resolve) => setTimeout(resolve, delay));
        return axiosClient(config);
      }
    }

    return Promise.reject(error);
  }
);

// Wrap axiosClient.get with in-flight deduplication to prevent double-click storming,
// while guaranteeing fresh, real-time ERP data on every navigation without stale cache leaks.
const originalGet = axiosClient.get.bind(axiosClient);

(axiosClient as any).get = function (
  url: string,
  config?: any
): Promise<AxiosResponse<any>> {
  const currentUser = useAuthStore.getState().user;
  const userScope = currentUser ? `u${currentUser.id}_s${currentUser.tenant_id || 1}` : 'guest';
  const flightKey = `${userScope}:${url}_${JSON.stringify(config?.params || {})}`;

  // Deduplicate identical in-flight requests that are currently in progress
  const existingFlight = inFlightRequests.get(flightKey);
  if (existingFlight) {
    return existingFlight;
  }

  const requestPromise = originalGet(url, config)
    .finally(() => {
      inFlightRequests.delete(flightKey);
    });

  inFlightRequests.set(flightKey, requestPromise);
  return requestPromise;
};
