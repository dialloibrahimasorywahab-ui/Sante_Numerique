import { Injectable, computed, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, of } from 'rxjs';
import { catchError, finalize, switchMap, tap } from 'rxjs/operators';
import { environment } from '../../../environments/environment';
import { LoginDto, RegisterDto, User, UserRole } from '../models/user.model';

const STORAGE_USER_KEY = 'sante_user_profile';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private http = inject(HttpClient);
  private router = inject(Router);

  private get apiUrl(): string {
    return environment.apiUrl;
  }

  /**
   * Récupère le profil utilisateur mis en cache dans sessionStorage lors de la session active.
   * Ne lit ni ne manipule AUCUN JWT (les JWT restent 100% dans des cookies HttpOnly).
   */
  private loadStoredUser(): User | null {
    if (typeof window === 'undefined' || !window.sessionStorage) {
      return null;
    }
    try {
      const raw = sessionStorage.getItem(STORAGE_USER_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  }

  // State signals - Initialisé directement avec le profil pour éviter toute déconnexion au rafraîchissement
  readonly currentUser = signal<User | null>(this.loadStoredUser());
  readonly isAuthenticated = computed(() => !!this.currentUser());
  readonly isLoading = signal<boolean>(false);
  readonly isInitialized = signal<boolean>(false);

  /**
   * Connexion utilisateur avec transmission et stockage des cookies HttpOnly par Django.
   */
  login(credentials: LoginDto): Observable<User> {
    this.isLoading.set(true);
    return this.http.post<User>(`${this.apiUrl}/users/login/`, credentials, {
      withCredentials: true
    }).pipe(
      tap((user) => {
        try {
          sessionStorage.setItem(STORAGE_USER_KEY, JSON.stringify(user));
        } catch {}
        this.currentUser.set(user);
        this.isInitialized.set(true);
      }),
      finalize(() => {
        this.isLoading.set(false);
      })
    );
  }

  /**
   * Inscription d'un nouveau patient via l'API Django.
   */
  register(payload: RegisterDto): Observable<User> {
    this.isLoading.set(true);
    return this.http.post<User>(`${this.apiUrl}/users/`, payload, {
      withCredentials: true
    }).pipe(
      finalize(() => {
        this.isLoading.set(false);
      })
    );
  }

  /**
   * Déconnexion sécurisée : appelle l'endpoint Django pour invalider les tokens
   * et effacer les cookies HttpOnly, puis vide l'état frontend et redirige.
   */
  logout(): Observable<any> {
    this.isLoading.set(true);
    return this.http.post(`${this.apiUrl}/users/logout/`, {}, {
      withCredentials: true
    }).pipe(
      tap(() => {
        this.clearSession();
      }),
      catchError(() => {
        this.clearSession();
        return of(null);
      }),
      finalize(() => {
        this.isLoading.set(false);
        this.router.navigate(['/']);
      })
    );
  }

  private clearSession(): void {
    if (typeof window !== 'undefined' && window.sessionStorage) {
      try {
        sessionStorage.removeItem(STORAGE_USER_KEY);
      } catch {}
    }
    this.currentUser.set(null);
  }

  /**
   * Restauration et vérification transparente de la session utilisateur.
   * Interroge GET /users/me/ avec les cookies HttpOnly.
   * Si l'access_token a expiré, tente de le renouveler via POST /users/token/refresh/.
   */
  checkSession(): Observable<User | null> {
    return this.http.get<User>(`${this.apiUrl}/users/me/`, {
      withCredentials: true
    }).pipe(
      tap((user) => {
        try {
          sessionStorage.setItem(STORAGE_USER_KEY, JSON.stringify(user));
        } catch {}
        this.currentUser.set(user);
        this.isInitialized.set(true);
      }),
      catchError(() => {
        // Tenter le rafraîchissement via le cookie HttpOnly refresh_token
        return this.http.post<any>(`${this.apiUrl}/users/token/refresh/`, {}, {
          withCredentials: true
        }).pipe(
          switchMap(() => {
            // Le token a été renouvelé dans les cookies, recharger le profil
            return this.http.get<User>(`${this.apiUrl}/users/me/`, {
              withCredentials: true
            }).pipe(
              tap((user) => {
                try {
                  sessionStorage.setItem(STORAGE_USER_KEY, JSON.stringify(user));
                } catch {}
                this.currentUser.set(user);
                this.isInitialized.set(true);
              }),
              catchError(() => {
                this.clearSession();
                this.isInitialized.set(true);
                return of(null);
              })
            );
          }),
          catchError(() => {
            // Ni access_token ni refresh_token ne sont valides
            this.clearSession();
            this.isInitialized.set(true);
            return of(null);
          })
        );
      })
    );
  }

  /**
   * Rafraîchit les tokens JWT en arrière-plan via les cookies HttpOnly.
   */
  refreshSession(): Observable<any> {
    return this.http.post(`${this.apiUrl}/users/token/refresh/`, {}, {
      withCredentials: true
    }).pipe(
      catchError((err) => {
        this.clearSession();
        throw err;
      })
    );
  }

  /**
   * Retourne la route de redirection par défaut selon le rôle de l'utilisateur.
   */
  getDashboardRouteForRole(role?: UserRole): string {
    switch (role) {
      case 'PATIENT':
        return '/patient/dashboard';
      case 'MEDECIN':
        return '/medecin/dashboard';
      case 'INFIRMIER':
        return '/personnel/dashboard';
      case 'ADMINISTRATEUR':
        return '/admin/dashboard';
      default:
        return '/';
    }
  }
}
