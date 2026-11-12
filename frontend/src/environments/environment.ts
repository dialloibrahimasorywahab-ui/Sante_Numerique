/**
 * Configuration d'environnement Angular pour la production.
 * L'URL du backend est configurable et ne présuppose aucun port 8000.
 */
declare global {
  interface Window {
    __env?: {
      apiUrl?: string;
    };
  }
}

export function getProductionApiUrl(): string {
  // 1. Surcharge runtime prioritaire (ex: injectée via window.__env.apiUrl dans index.html ou config.js)
  if (typeof window !== 'undefined' && window.__env?.apiUrl) {
    return window.__env.apiUrl.replace(/\/$/, '');
  }

  // 2. Si accédé via un VS Code Dev Tunnel ou en direct sur port 4200
  if (typeof window !== 'undefined' && window.location) {
    const host = window.location.hostname;
    if (host.includes('.devtunnels.ms')) {
      const backendHost = host.replace(/-4200\./, '-8000.');
      return `${window.location.protocol}//${backendHost}`;
    }
    if (window.location.port === '4200') {
      return `${window.location.protocol}//${host}:8000`;
    }
  }

  // 3. En production standard derrière un reverse proxy Nginx (domaine unique) : requêtes relatives vers /api
  return '/api';
}

export const environment = {
  production: true,
  get apiUrl(): string {
    return getProductionApiUrl();
  }
};
