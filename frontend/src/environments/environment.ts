export function getApiBaseUrl(): string {
  if (typeof window !== 'undefined' && window.location) {
    const host = window.location.hostname;
    if (host === 'localhost') {
      return 'http://localhost:8000';
    }
    if (host === '127.0.0.1') {
      return 'http://127.0.0.1:8000';
    }
    return `${window.location.protocol}//${host}:8000`;
  }
  return 'http://localhost:8000';
}

export const environment = {
  production: true,
  get apiUrl(): string {
    return getApiBaseUrl();
  }
};
