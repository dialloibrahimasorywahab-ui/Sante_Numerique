import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { environment } from '../../../../environments/environment';
import { HospitalisationDto } from '../models/patient.models';
import { PaginatedResponse } from '../../../core/models/models';

@Injectable({
  providedIn: 'root'
})
export class PatientHospitalizationService {
  private http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiUrl}/hospitalisations`;

  /**
   * Récupère la liste paginée des hospitalisations du patient connecté.
   */
  getMyHospitalizations(page: number = 1, pageSize: number = 3): Observable<PaginatedResponse<HospitalisationDto>> {
    const params = new HttpParams()
      .set('page', page.toString())
      .set('page_size', pageSize.toString());

    return this.http.get<PaginatedResponse<HospitalisationDto>>(`${this.baseUrl}/`, {
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
   * Récupère le détail d'une hospitalisation par son identifiant.
   */
  getHospitalizationById(id: number): Observable<HospitalisationDto> {
    return this.http.get<HospitalisationDto>(`${this.baseUrl}/${id}/`, {
      withCredentials: true
    });
  }
}
