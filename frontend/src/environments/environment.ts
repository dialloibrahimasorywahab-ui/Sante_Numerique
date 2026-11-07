export function getApiBaseUrl(): string {
  if (typeof window !== 'undefined' && window.location) {
    const host = window.location.hostname;
    // Support des VS Code Dev Tunnels si build testé via tunnel
    if (host.includes('.devtunnels.ms')) {
      const backendHost = host.replace(/-4200\./, '-8000.');
      return `${window.location.protocol}//${backendHost}`;
    }
    // Si accédé directement sur le serveur de dev Angular port 4200
    if (window.location.port === '4200') {
      return `${window.location.protocol}//${host}:8000`;
    }
  }
  // En production sous Nginx (domaine unique) : requêtes relatives vers /api
  return '/api';
}

export const environment = {
  production: true,
  get apiUrl(): string {
    return getApiBaseUrl();
  }
};
