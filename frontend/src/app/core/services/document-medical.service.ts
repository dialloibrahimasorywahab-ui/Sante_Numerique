import { Injectable, inject, signal } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { environment } from '../../../environments/environment';
import { PaginatedResponse } from '../models/models';
import { DocumentMedicalDto, DocumentFilterParams, CategorieDocument } from '../models/document-medical.models';

export interface CategorieOption {
  code: string;
  nom: string;
  icon: string;
}

@Injectable({
  providedIn: 'root'
})
export class DocumentMedicalService {
  private http = inject(HttpClient);
  private readonly API_BASE_URL = environment.apiUrl;

  // Signaux réactifs pour l'état des documents
  documents = signal<DocumentMedicalDto[]>([]);
  totalCount = signal<number>(0);
  totalPages = signal<number>(1);
  currentPage = signal<number>(1);
  isLoading = signal<boolean>(false);
  errorMessage = signal<string | null>(null);

  readonly categoriesList: CategorieOption[] = [
    { code: '', nom: 'Toutes les catégories', icon: 'folder' },
    { code: 'RADIO', nom: 'Radiographie', icon: 'photograph' },
    { code: 'SCANNER', nom: 'Scanner / Tomodensitométrie', icon: 'cpu' },
    { code: 'IRM', nom: 'IRM', icon: 'cube' },
    { code: 'ECHOGRAPHIE', nom: 'Échographie', icon: 'sound' },
    { code: 'ANALYSE_SANG', nom: 'Analyse Sanguine / NFS', icon: 'beaker' },
    { code: 'ANALYSE_URINE', nom: 'Analyse Urinaire', icon: 'beaker' },
    { code: 'ANAPATH', nom: 'Anatomopathologie / Biopsie', icon: 'document-text' },
    { code: 'COMPTE_RENDU', nom: 'Compte-rendu clinique', icon: 'clipboard' },
    { code: 'CERTIFICAT', nom: 'Certificat médical', icon: 'badge-check' },
    { code: 'ORDONNANCE', nom: 'Ordonnance numérisée', icon: 'document' },
    { code: 'AUTRE', nom: 'Autre document', icon: 'paperclip' }
  ];

  /**
   * Récupère la liste paginée et filtrée des documents médicaux
   */
  getDocuments(params: DocumentFilterParams = {}): Observable<PaginatedResponse<DocumentMedicalDto>> {
    this.isLoading.set(true);
    this.errorMessage.set(null);

    let httpParams = new HttpParams();
    if (params.patient_id) {
      httpParams = httpParams.set('patient_id', params.patient_id.toString());
    }
    if (params.categorie) {
      httpParams = httpParams.set('categorie', params.categorie);
    }
    if (params.search) {
      httpParams = httpParams.set('search', params.search);
    }
    if (params.page) {
      httpParams = httpParams.set('page', params.page.toString());
    }
    if (params.page_size) {
      httpParams = httpParams.set('page_size', params.page_size.toString());
    }

    return this.http.get<PaginatedResponse<DocumentMedicalDto>>(`${this.API_BASE_URL}/documents_medicaux/`, { params: httpParams }).pipe(
      tap({
        next: (res) => {
          this.documents.set(res.results || []);
          this.totalCount.set(res.count || 0);
          this.totalPages.set(res.total_pages || Math.ceil((res.count || 0) / (res.page_size || 10)) || 1);
          this.currentPage.set(res.current_page || params.page || 1);
          this.isLoading.set(false);
        },
        error: (err) => {
          this.errorMessage.set(err?.error?.message || 'Erreur lors du chargement des documents médicaux.');
          this.isLoading.set(false);
        }
      })
    );
  }

  /**
   * Téléverse un nouveau document médical (avec chiffrement transparent côté backend)
   */
  uploadDocument(formData: FormData): Observable<DocumentMedicalDto> {
    this.isLoading.set(true);
    return this.http.post<DocumentMedicalDto>(`${this.API_BASE_URL}/documents_medicaux/`, formData).pipe(
      tap({
        next: (doc) => {
          this.documents.update(docs => [doc, ...docs]);
          this.totalCount.update(c => c + 1);
          this.isLoading.set(false);
        },
        error: () => {
          this.isLoading.set(false);
        }
      })
    );
  }

  /**
   * Télécharge et déchiffre un document médical à la volée, puis l'ouvre / le sauvegarde
   */
  downloadDecrypted(documentId: number, filename?: string): Observable<Blob> {
    const url = `${this.API_BASE_URL}/documents_medicaux/${documentId}/download/`;
    return this.http.get(url, { responseType: 'blob' }).pipe(
      tap((blob) => {
        // Détecter ou déduire le type MIME pour prévisualisation immédiate
        const isPdf = (filename && filename.toLowerCase().endsWith('.pdf')) || blob.type === 'application/pdf';
        const mimeType = isPdf ? 'application/pdf' : (blob.type || 'application/octet-stream');
        const typedBlob = new Blob([blob], { type: mimeType });
        const objectUrl = window.URL.createObjectURL(typedBlob);

        // Tenter d'ouvrir dans un nouvel onglet pour lecture directe du compte-rendu
        const newWindow = window.open(objectUrl, '_blank');

        // Déclencher le téléchargement du fichier physique
        const a = document.createElement('a');
        a.href = objectUrl;
        a.download = filename || `document_medical_${documentId}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);

        // Conserver l'URL 60 secondes pour laisser le temps au lecteur PDF d'afficher le document
        setTimeout(() => window.URL.revokeObjectURL(objectUrl), 60000);
      })
    );
  }

  /**
   * Supprime ou archive un document
   */
  deleteDocument(documentId: number, hard: boolean = false): Observable<{ message: string }> {
    const params = new HttpParams().set('hard', hard.toString());
    return this.http.delete<{ message: string }>(`${this.API_BASE_URL}/documents_medicaux/${documentId}/`, { params }).pipe(
      tap(() => {
        this.documents.update(docs => docs.filter(d => (d.idDocument ?? d.id_document ?? (d as any).id) !== documentId));
        this.totalCount.update(c => Math.max(0, c - 1));
      })
    );
  }

  formatFileSize(bytes?: number | null): string {
    if (!bytes || bytes === 0) return '0 Octets';
    const k = 1024;
    const sizes = ['Octets', 'Ko', 'Mo', 'Go'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  }
}
