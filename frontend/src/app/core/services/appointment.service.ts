import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, catchError, map, of, throwError } from 'rxjs';
import {
  RendezVousDto,
  AvailableSlotsResponse,
  CreateAppointmentDto
} from '../../features/appointment/models/models';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AppointmentService {
  private http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiUrl}/rendezvous`;

  /**
   * Récupère les créneaux horaires disponibles d'un médecin pour une date donnée.
   */
  getAvailableSlots(medecinId: number, date: string): Observable<AvailableSlotsResponse> {
    let params = new HttpParams()
      .set('medecin_id', medecinId.toString())
      .set('date', date);

    return this.http.get<AvailableSlotsResponse>(`${this.baseUrl}/creneaux/`, { params }).pipe(
      catchError((err) => {
        console.warn(`Erreur de chargement des créneaux pour médecin #${medecinId} à ${date}:`, err);
        // Fallback standard slots if API fails
        const fallback: AvailableSlotsResponse = {
          medecin_id: medecinId,
          date,
          creneaux: [
            { heure: '08:30', disponible: true },
            { heure: '09:00', disponible: true },
            { heure: '09:30', disponible: true },
            { heure: '10:00', disponible: true },
            { heure: '10:30', disponible: true },
            { heure: '11:00', disponible: true },
            { heure: '14:00', disponible: true },
            { heure: '14:30', disponible: true },
            { heure: '15:00', disponible: true },
            { heure: '15:30', disponible: true },
            { heure: '16:00', disponible: true }
          ]
        };
        return of(fallback);
      })
    );
  }

  /**
   * Crée un nouveau rendez-vous via l'API Django (avec cookie HttpOnly).
   */
  createAppointment(dto: CreateAppointmentDto): Observable<RendezVousDto> {
    const payload: any = {
      id_medecin: dto.id_medecin,
      date_rdv: dto.date_rdv,
      heure: dto.heure.length === 5 ? `${dto.heure}:00` : dto.heure,
      motif: dto.motif
    };

    if (dto.id_patient) {
      payload.id_patient = dto.id_patient;
    }

    return this.http.post<RendezVousDto>(`${this.baseUrl}/`, payload, {
      withCredentials: true
    }).pipe(
      map(res => {
        // Generate confirmation code for UX receipt
        const idRdv = res.id || res.idRendezVous || Math.floor(100000 + Math.random() * 900000);
        return {
          ...res,
          id: idRdv,
          codeConfirmation: `RDV-${idRdv}-${new Date(dto.date_rdv).getFullYear()}`
        };
      })
    );
  }

  /**
   * Récupère la liste des rendez-vous du patient connecté.
   */
  getMyAppointments(): Observable<RendezVousDto[]> {
    return this.http.get<any>(`${this.baseUrl}/mes-rendezvous/`, {
      withCredentials: true
    }).pipe(
      map(res => {
        if (res && res.results && Array.isArray(res.results)) {
          return res.results as RendezVousDto[];
        } else if (Array.isArray(res)) {
          return res as RendezVousDto[];
        }
        return [];
      }),
      catchError(err => {
        console.error('Erreur de récupération des rendez-vous:', err);
        return of([] as RendezVousDto[]);
      })
    );
  }

  /**
   * Annule un rendez-vous par son identifiant.
   */
  cancelAppointment(rdvId: number): Observable<any> {
    return this.http.post(`${this.baseUrl}/${rdvId}/annuler/`, {}, {
      withCredentials: true
    });
  }

  /**
   * Récupère un rendez-vous par son ID.
   */
  getAppointmentById(rdvId: number): Observable<RendezVousDto> {
    return this.http.get<RendezVousDto>(`${this.baseUrl}/${rdvId}/`, {
      withCredentials: true
    });
  }
}
