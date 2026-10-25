export const getErrorMessage = (error: any, defaultMessage: string = "An error occurred"): string => {
  if (!error) return defaultMessage;
  if (error.response?.data?.detail) {
    const detail = error.response.data.detail;
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail)) {
      // FastAPI Validation Error format
      return detail.map((d: any) => `${d.loc?.join('.') || 'Field'}: ${d.msg}`).join(', ');
    }
  }
  return error.message || defaultMessage;
};
