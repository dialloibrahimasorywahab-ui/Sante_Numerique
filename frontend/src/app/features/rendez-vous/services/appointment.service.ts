import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import {
  RendezVousDto,
  AvailableSlotsResponse,
  CreateAppointmentDto,
} from '../models/models';
import { environment } from '../../../../environments/environment';

export interface AppointmentFilterParams {
  telephone?: string;
  email?: string;
  patient_id?: number;
}

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

    return this.http.get<AvailableSlotsResponse>(`${this.baseUrl}/creneaux/`, { params });
  }

  /**
   * Crée un nouveau rendez-vous via l'API Django (avec cookie HttpOnly).
   */
  createAppointment(dto: CreateAppointmentDto): Observable<RendezVousDto> {
    const rawHeure = dto.time || dto.heure || '';
    const formattedHeure = rawHeure.length === 5 ? `${rawHeure}:00` : rawHeure;

    const payload: any = {
      patient: dto.patient || dto.id_patient,
      doctor: dto.doctor || dto.id_medecin,
      service: dto.service,
      id_patient: dto.id_patient || dto.patient,
      id_medecin: dto.id_medecin || dto.doctor,
      date: dto.date || dto.date_rdv,
      date_rdv: dto.date_rdv || dto.date,
      time: formattedHeure,
      heure: formattedHeure,
      appointment_type: dto.appointment_type || dto.type_consultation || 'consultation_presentiel',
      type_consultation: dto.type_consultation || dto.appointment_type || 'SUR_PLACE',
      reason: dto.reason || dto.motif || '',
      motif: dto.motif || dto.reason || '',
      notes: dto.notes || ''
    };

    return this.http.post<RendezVousDto>(`${this.baseUrl}/`, payload, {
      withCredentials: true
    }).pipe(
      map(res => {
        const idRdv = res.id || res.idRendezVous || 0;
        return {
          ...res,
          id: idRdv,
          id_patient: payload.id_patient,
          patient_nom: dto.patient_nom,
          patient_prenom: dto.patient_prenom,
          patient_email: dto.patient_email,
          patient_telephone: dto.patient_telephone,
          codeConfirmation: `RDV-${idRdv}-${new Date(payload.date_rdv || Date.now()).getFullYear()}`
        };
      })
    );
  }

  /**
   * Récupère la liste des rendez-vous du patient connecté avec filtrage strict.
   */
  getMyAppointments(filter?: AppointmentFilterParams): Observable<RendezVousDto[]> {
    let params = new HttpParams();
    if (filter?.telephone) {
      params = params.set('telephone', filter.telephone);
    }
    if (filter?.email) {
      params = params.set('email', filter.email);
    }
    if (filter?.patient_id) {
      params = params.set('patient_id', filter.patient_id.toString());
    }

    return this.http.get<any>(`${this.baseUrl}/mes-rendezvous/`, {
      params,
      withCredentials: true
    }).pipe(
      map(res => {
        if (res && res.results && Array.isArray(res.results)) {
          return res.results as RendezVousDto[];
        } else if (Array.isArray(res)) {
          return res as RendezVousDto[];
        }
        return [];
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
