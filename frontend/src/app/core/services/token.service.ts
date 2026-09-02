import { Injectable } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class TokenService {
  private readonly storageKey = 'sante_numerique_access_token';

  getToken(): string | null {
    return typeof localStorage === 'undefined' ? null : localStorage.getItem(this.storageKey);
  }

  setToken(token: string): void {
    localStorage.setItem(this.storageKey, token);
  }

  clearToken(): void {
    localStorage.removeItem(this.storageKey);
  }
}
