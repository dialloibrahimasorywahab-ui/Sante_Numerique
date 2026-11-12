import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class PdfDownloadService {
  private http = inject(HttpClient);
  private readonly API_BASE_URL = environment.apiUrl;

  /**
   * Télécharge l'ordonnance médicale officielle en PDF
   */
  downloadOrdonnancePdf(ordonnanceId: number, reference?: string): Observable<Blob> {
    const url = `${this.API_BASE_URL}/ordonnances/${ordonnanceId}/pdf/`;
    return this.http.get(url, { responseType: 'blob' }).pipe(
      tap((blob) => {
        const safeRef = reference ? reference.replace(/[/\\?%*:|"<>]/g, '_') : `ORD_${ordonnanceId}`;
        this.saveBlob(blob, `ordonnance_${safeRef}.pdf`);
      })
    );
  }

  /**
   * Télécharge le compte-rendu médical / certificat de consultation en PDF
   */
  downloadConsultationPdf(consultationId: number): Observable<Blob> {
    const url = `${this.API_BASE_URL}/consultations/${consultationId}/pdf/`;
    return this.http.get(url, { responseType: 'blob' }).pipe(
      tap((blob) => {
        this.saveBlob(blob, `certificat_consultation_${consultationId}.pdf`);
      })
    );
  }

  /**
   * Déclenche le téléchargement du fichier Blob dans le navigateur
   */
  saveBlob(blob: Blob, filename: string): void {
    const objectUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = objectUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(objectUrl);
  }
}
