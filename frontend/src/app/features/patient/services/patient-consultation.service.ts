import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { environment } from '../../../../environments/environment';
import { ConsultationDto } from '../models/patient.models';
import { PaginatedResponse } from '../../../core/models/models';

@Injectable({
  providedIn: 'root'
})
export class PatientConsultationService {
  private http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiUrl}/consultations`;

  /**
   * Récupère la liste paginée des consultations du patient connecté.
   * Conforme à la consigne : pagination stricte à 3 éléments par page.
   */
  getMyConsultations(page: number = 1, pageSize: number = 3): Observable<PaginatedResponse<ConsultationDto>> {
    const params = new HttpParams()
      .set('page', page.toString())
      .set('page_size', pageSize.toString());

    return this.http.get<PaginatedResponse<ConsultationDto>>(`${this.baseUrl}/`, {
      params,
      withCredentials: true
    }).pipe(
      map(res => {
        const rawResults = (res && res.results && Array.isArray(res.results)) ? res.results : [];
        const count = res?.count ?? rawResults.length;
        const totalPages = res?.total_pages ?? Math.max(1, Math.ceil(count / pageSize));

        return {
          count,
          total_pages: totalPages,
          current_page: res?.current_page ?? page,
          page_size: pageSize,
          next: res?.next ?? null,
          previous: res?.previous ?? null,
          results: rawResults
        };
      })
    );
  }

  /**
   * Récupère le détail d'une consultation par son identifiant.
   */
  getConsultationById(id: number): Observable<ConsultationDto> {
    return this.http.get<ConsultationDto>(`${this.baseUrl}/${id}/`, {
      withCredentials: true
    });
  }
}
