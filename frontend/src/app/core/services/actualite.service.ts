import { Injectable, inject, signal } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, tap, catchError, throwError } from 'rxjs';
import { environment } from '../../../environments/environment';
import { PaginatedResponse } from '../models/models';
import {
  Actualite,
  CategorieActualite,
  ActualitePayload,
  ActualiteFilterParams
} from '../models/actualite.model';

@Injectable({
  providedIn: 'root'
})
export class ActualiteService {
  private http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiUrl}/actualites`;

  // Signals d'état pour les composants réactifs
  actualites = signal<Actualite[]>([]);
  featuredActualite = signal<Actualite | null>(null);
  categories = signal<CategorieActualite[]>([]);
  isLoading = signal<boolean>(false);
  errorMessage = signal<string | null>(null);
  totalCount = signal<number>(0);
  totalPages = signal<number>(1);
  currentPage = signal<number>(1);

  /**
   * Récupère la liste des catégories actives
   */
  getCategories(): Observable<CategorieActualite[]> {
    return this.http.get<CategorieActualite[]>(`${this.baseUrl}/categories/`).pipe(
      tap(cats => this.categories.set(cats)),
      catchError(err => {
        console.error('Erreur lors du chargement des catégories:', err);
        return throwError(() => err);
      })
    );
  }

  /**
   * Récupère les actualités avec filtres de recherche, catégorie, tri et pagination
   */
  getActualites(params?: ActualiteFilterParams): Observable<PaginatedResponse<Actualite>> {
    let httpParams = new HttpParams();

    if (params) {
      if (params.search) {
        httpParams = httpParams.set('search', params.search.trim());
      }
      if (params.categorie !== undefined && params.categorie !== null && params.categorie !== '') {
        httpParams = httpParams.set('categorie', params.categorie.toString());
      }
      if (params.statut) {
        httpParams = httpParams.set('statut', params.statut);
      }
      if (params.estALaUne !== undefined) {
        httpParams = httpParams.set('est_a_la_une', params.estALaUne ? 'true' : 'false');
      }
      if (params.ordering) {
        httpParams = httpParams.set('ordering', params.ordering);
      }
      if (params.page) {
        httpParams = httpParams.set('page', params.page.toString());
      }
      if (params.pageSize) {
        httpParams = httpParams.set('page_size', params.pageSize.toString());
      }
    }

    this.isLoading.set(true);
    this.errorMessage.set(null);

    return this.http.get<PaginatedResponse<Actualite>>(`${this.baseUrl}/`, { params: httpParams }).pipe(
      tap(response => {
        this.actualites.set(response.results);
        this.totalCount.set(response.count);
        const pages = response.total_pages || (response as any).totalPages || Math.ceil(response.count / (params?.pageSize || 20)) || 1;
        this.totalPages.set(pages);
        this.currentPage.set(params?.page || 1);

        // Détection automatique de l'article à la une pour la page publique
        const une = response.results.find(a => a.estALaUne && a.statut === 'PUBLIE');
        this.featuredActualite.set(une || (response.results.length > 0 ? response.results[0] : null));
        this.isLoading.set(false);
      }),
      catchError(err => {
        this.isLoading.set(false);
        this.errorMessage.set('Impossible de charger les actualités.');
        console.error('Erreur API actualités:', err);
        return throwError(() => err);
      })
    );
  }

  /**
   * Récupère le détail d'une actualité par son slug ou son identifiant numérique
   */
  getActualiteBySlugOrId(slugOrId: string | number): Observable<Actualite> {
    this.isLoading.set(true);
    this.errorMessage.set(null);

    return this.http.get<Actualite>(`${this.baseUrl}/${slugOrId}/`).pipe(
      tap(() => this.isLoading.set(false)),
      catchError(err => {
        this.isLoading.set(false);
        this.errorMessage.set('Article introuvable ou indisponible.');
        return throwError(() => err);
      })
    );
  }

  /**
   * Récupère des suggestions d'articles connexes
   */
  getSuggestions(slugOrId: string | number): Observable<Actualite[]> {
    return this.http.get<Actualite[]>(`${this.baseUrl}/${slugOrId}/suggestions/`).pipe(
      catchError(err => {
        console.error('Erreur chargement suggestions:', err);
        return throwError(() => err);
      })
    );
  }

  /**
   * Création d'une actualité (Admin uniquement)
   */
  createActualite(data: FormData | ActualitePayload): Observable<Actualite> {
    return this.http.post<Actualite>(`${this.baseUrl}/`, data);
  }

  /**
   * Mise à jour d'une actualité (Admin uniquement)
   */
  updateActualite(id: number, data: FormData | Partial<ActualitePayload>): Observable<Actualite> {
    return this.http.patch<Actualite>(`${this.baseUrl}/${id}/`, data);
  }

  /**
   * Suppression d'une actualité (Admin uniquement)
   */
  deleteActualite(id: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/${id}/`);
  }

  /**
   * Création d'une catégorie (Admin uniquement)
   */
  createCategory(category: Partial<CategorieActualite>): Observable<CategorieActualite> {
    return this.http.post<CategorieActualite>(`${this.baseUrl}/categories/`, category);
  }

  /**
   * Modification d'une catégorie (Admin uniquement)
   */
  updateCategory(id: number, category: Partial<CategorieActualite>): Observable<CategorieActualite> {
    return this.http.patch<CategorieActualite>(`${this.baseUrl}/categories/${id}/`, category);
  }

  /**
   * Suppression d'une catégorie (Admin uniquement)
   */
  deleteCategory(id: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/categories/${id}/`);
  }
}

