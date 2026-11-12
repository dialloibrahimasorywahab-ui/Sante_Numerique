/**
 * Configuration d'environnement Angular pour le développement local.
 */
declare global {
  interface Window {
    __env?: {
      apiUrl?: string;
    };
  }
}

export function getDevelopmentApiUrl(): string {
  // 1. Surcharge runtime prioritaire (ex: injectée via window.__env.apiUrl dans index.html ou config.js)
  if (typeof window !== 'undefined' && window.__env?.apiUrl) {
    return window.__env.apiUrl.replace(/\/$/, '');
  }

  // 2. Détection dynamique de l'hôte de développement
  if (typeof window !== 'undefined' && window.location) {
    const host = window.location.hostname;
    if (host === 'localhost') {
      return 'http://localhost:8000';
    }
    if (host === '127.0.0.1') {
      return 'http://127.0.0.1:8000';
    }
    // Support des VS Code Dev Tunnels (ex: *-4200.*.devtunnels.ms -> *-8000.*.devtunnels.ms)
    if (host.includes('.devtunnels.ms')) {
      const backendHost = host.replace(/-4200\./, '-8000.');
      return `${window.location.protocol}//${backendHost}`;
    }
    if (host) {
      return `http://${host}:8000`;
    }
  }

  return 'http://localhost:8000';
}

export const environment = {
  production: false,
  get apiUrl(): string {
    return getDevelopmentApiUrl();
  }
};
