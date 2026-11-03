import { Injectable } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class TokenService {
  private readonly storageKey = 'sante_numerique_access_token';

  /**
   * Les jetons JWT sont désormais gérés exclusivement via des cookies HttpOnly sécurisés.
   * Aucun jeton n'est stocké ni exposé dans localStorage ou sessionStorage.
   */
  getToken(): string | null {
    return null;
  }

  setToken(token: string): void {
    // Les jetons ne sont plus stockés dans localStorage pour prévenir les attaques XSS.
    this.clearToken();
  }

  clearToken(): void {
    if (typeof window !== 'undefined' && window.localStorage) {
      try {
        localStorage.removeItem(this.storageKey);
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('token');
      } catch {}
    }
  }
}
