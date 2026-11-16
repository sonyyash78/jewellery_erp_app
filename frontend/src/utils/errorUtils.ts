/**
 * Robust error message extractor for FastAPI, Axios, Pydantic, and JavaScript errors.
 * GUARANTEED to ALWAYS return a clean, user-friendly string — NEVER an Object or Array,
 * completely preventing React Error #31 ("Objects are not valid as a React child").
 */
export const getErrorMessage = (error: any, defaultMessage: string = "An error occurred"): string => {
  if (!error) return defaultMessage;
  if (typeof error === 'string') return error;

  // 1. Array of error objects (e.g. FastAPI/Pydantic validation errors: [{ loc, msg, type, input, ctx }])
  if (Array.isArray(error)) {
    return error
      .map((d: any) => {
        if (typeof d === 'string') return d;
        if (!d) return '';
        const field = Array.isArray(d.loc)
          ? d.loc.filter((part: any) => part !== 'body').join('.')
          : (d.loc || '');
        const msg = d.msg || d.message || (typeof d === 'object' ? JSON.stringify(d) : String(d));
        return field ? `${field}: ${msg}` : msg;
      })
      .filter(Boolean)
      .join('; ') || defaultMessage;
  }

  // 2. Axios Response error with detail
  if (error.response?.data) {
    const data = error.response.data;

    // detail field
    if (data.detail !== undefined && data.detail !== null) {
      if (typeof data.detail === 'string') return data.detail;
      if (Array.isArray(data.detail)) {
        return getErrorMessage(data.detail, defaultMessage);
      }
      if (typeof data.detail === 'object') {
        if (data.detail.msg || data.detail.message) {
          return String(data.detail.msg || data.detail.message);
        }
        try {
          return JSON.stringify(data.detail);
        } catch {
          return defaultMessage;
        }
      }
    }

    // message field on response data
    if (typeof data.message === 'string') return data.message;
    if (typeof data.error === 'string') return data.error;
  }

  // 3. Single Pydantic validation error object directly ({ type, loc, msg, input, ctx })
  if (error.msg && typeof error.msg === 'string') {
    const field = Array.isArray(error.loc)
      ? error.loc.filter((part: any) => part !== 'body').join('.')
      : (error.loc || '');
    return field ? `${field}: ${error.msg}` : error.msg;
  }

  // 4. Standard JS Error
  if (error.message && typeof error.message === 'string') {
    return error.message;
  }

  // 5. Fallback safe stringification
  try {
    const str = JSON.stringify(error);
    return str && str !== '{}' ? str : defaultMessage;
  } catch {
    return defaultMessage;
  }
};
