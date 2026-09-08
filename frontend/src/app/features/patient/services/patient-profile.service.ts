import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, catchError, map, of, throwError } from 'rxjs';
import { environment } from '../../../../environments/environment';
import { User } from '../../../core/models/user.model';
import { ChangePasswordDto, PatientRecord, UpdateProfileDto } from '../models/patient.models';

@Injectable({
  providedIn: 'root'
})
export class PatientProfileService {
  private http = inject(HttpClient);
  private readonly baseUrl = environment.apiUrl;

  /**
   * Récupère le profil complet de l'utilisateur connecté depuis GET /users/me/
   */
  getProfile(): Observable<User> {
    return this.http.get<User>(`${this.baseUrl}/users/me/`, {
      withCredentials: true
    });
  }

  /**
   * Met à jour les informations personnelles (nom, prénom, email, téléphone, date_naissance)
   * via PATCH /users/<id>/update/
   */
  updateProfile(userId: number, payload: UpdateProfileDto): Observable<User> {
    return this.http.patch<User>(`${this.baseUrl}/users/${userId}/update/`, payload, {
      withCredentials: true
    });
  }

  /**
   * Modifie le mot de passe de l'utilisateur connecté via POST /users/change-password/
   */
  changePassword(payload: ChangePasswordDto): Observable<{ message: string }> {
    return this.http.post<{ message: string }>(`${this.baseUrl}/users/change-password/`, payload, {
      withCredentials: true
    });
  }

  /**
   * Récupère la fiche médicale patient si elle existe (groupe sanguin, adresse, etc.)
   */
  getPatientRecord(patientId: number): Observable<PatientRecord | null> {
    return this.http.get<PatientRecord>(`${this.baseUrl}/patients/${patientId}/`, {
      withCredentials: true
    }).pipe(
      catchError(() => of(null))
    );
  }

  /**
   * Met à jour les coordonnées médicales de la fiche patient via PATCH /patients/<id>/update/
   */
  updatePatientRecord(patientId: number, data: Partial<PatientRecord>): Observable<PatientRecord> {
    return this.http.patch<PatientRecord>(`${this.baseUrl}/patients/${patientId}/update/`, data, {
      withCredentials: true
    });
  }
}
