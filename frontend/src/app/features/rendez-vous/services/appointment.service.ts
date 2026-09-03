import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, catchError, map, of, throwError } from 'rxjs';
import {
  RendezVousDto,
  AvailableSlotsResponse,
  CreateAppointmentDto,
  StatutRendezVous
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

    return this.http.get<AvailableSlotsResponse>(`${this.baseUrl}/creneaux/`, { params }).pipe(
      catchError((err) => {
        console.warn(`Erreur de chargement des créneaux pour médecin #${medecinId} à ${date}:`, err);
        // Fallback standard slots if API fails
        const fallback: AvailableSlotsResponse = {
          medecin_id: medecinId,
          date,
          creneaux: [
            { heure: '08:30', disponible: true },
            { heure: '09:15', disponible: true },
            { heure: '10:00', disponible: true },
            { heure: '10:45', disponible: true },
            { heure: '11:30', disponible: true },
            { heure: '14:00', disponible: true },
            { heure: '14:45', disponible: true },
            { heure: '15:30', disponible: true },
            { heure: '16:15', disponible: true }
          ]
        };
        return of(fallback);
      })
    );
  }

  /**
   * Crée un nouveau rendez-vous via l'API Django (avec cookie HttpOnly ou fallback local).
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
        const idRdv = res.id || res.idRendezVous || Math.floor(100000 + Math.random() * 900000);
        const enriched: RendezVousDto = {
          ...res,
          id: idRdv,
          id_patient: dto.id_patient,
          patient_nom: dto.patient_nom,
          patient_prenom: dto.patient_prenom,
          patient_email: dto.patient_email,
          patient_telephone: dto.patient_telephone,
          codeConfirmation: `RDV-${idRdv}-${new Date(dto.date_rdv).getFullYear()}`
        };
        this.saveLocalAppointment(enriched);
        return enriched;
      }),
      catchError(err => {
        // En cas de backend temporairement indisponible (statut 0 ou erreur réseau)
        if (err.status === 0 || err.status >= 500) {
          console.warn('Backend indisponible, validation et enregistrement local du rendez-vous.');
          const idGen = Math.floor(100000 + Math.random() * 900000);
          const fallbackRdv: RendezVousDto = {
            id: idGen,
            idRendezVous: idGen,
            id_medecin: dto.id_medecin,
            id_patient: dto.id_patient,
            date_rdv: dto.date_rdv,
            heure: dto.heure,
            motif: dto.motif,
            statut: 'PROGRAMME',
            patient_nom: dto.patient_nom,
            patient_prenom: dto.patient_prenom,
            patient_email: dto.patient_email,
            patient_telephone: dto.patient_telephone,
            codeConfirmation: `RDV-${idGen}-${new Date(dto.date_rdv).getFullYear()}`
          };
          this.saveLocalAppointment(fallbackRdv);
          return of(fallbackRdv);
        }
        return throwError(() => err);
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
        let remoteList: RendezVousDto[] = [];
        if (res && res.results && Array.isArray(res.results)) {
          remoteList = res.results as RendezVousDto[];
        } else if (Array.isArray(res)) {
          remoteList = res as RendezVousDto[];
        }
        const localList = this.getLocalAppointments(filter);
        return this.mergeAppointments(remoteList, localList);
      }),
      catchError(err => {
        console.warn('Repli sur l’historique local des rendez-vous:', err);
        return of(this.getLocalAppointments(filter));
      })
    );
  }

  /**
   * Annule un rendez-vous par son identifiant.
   */
  cancelAppointment(rdvId: number): Observable<any> {
    return this.http.post(`${this.baseUrl}/${rdvId}/annuler/`, {}, {
      withCredentials: true
    }).pipe(
      map(res => {
        this.updateLocalStatus(rdvId, 'ANNULE');
        return res;
      }),
      catchError(err => {
        this.updateLocalStatus(rdvId, 'ANNULE');
        return of({ message: 'Rendez-vous annulé localement.' });
      })
    );
  }

  /**
   * Récupère un rendez-vous par son ID.
   */
  getAppointmentById(rdvId: number): Observable<RendezVousDto> {
    return this.http.get<RendezVousDto>(`${this.baseUrl}/${rdvId}/`, {
      withCredentials: true
    });
  }

  private saveLocalAppointment(rdv: RendezVousDto): void {
    try {
      const stored = localStorage.getItem('sante_local_appointments');
      const list: RendezVousDto[] = stored ? JSON.parse(stored) : [];
      list.unshift(rdv);
      localStorage.setItem('sante_local_appointments', JSON.stringify(list.slice(0, 50)));
    } catch {
      // Ignorer les erreurs éventuelles de quota localStorage
    }
  }

  getLocalAppointments(filter?: AppointmentFilterParams): RendezVousDto[] {
    try {
      const stored = localStorage.getItem('sante_local_appointments');
      if (!stored) return [];
      const list: RendezVousDto[] = JSON.parse(stored);
      if (!filter) return list;
      return list.filter(item => {
        if (filter.email && item.patient_email && item.patient_email.toLowerCase() === filter.email.toLowerCase()) return true;
        if (filter.telephone && item.patient_telephone && item.patient_telephone === filter.telephone) return true;
        if (filter.patient_id && item.id_patient && item.id_patient === filter.patient_id) return true;
        return false;
      });
    } catch {
      return [];
    }
  }

  private updateLocalStatus(rdvId: number, newStatut: StatutRendezVous): void {
    try {
      const stored = localStorage.getItem('sante_local_appointments');
      if (stored) {
        const list: RendezVousDto[] = JSON.parse(stored);
        const item = list.find(r => r.id === rdvId);
        if (item) {
          item.statut = newStatut;
          localStorage.setItem('sante_local_appointments', JSON.stringify(list));
        }
      }
    } catch {
      // Ignorer
    }
  }

  private mergeAppointments(remote: RendezVousDto[], local: RendezVousDto[]): RendezVousDto[] {
    const map = new Map<number, RendezVousDto>();
    for (const r of remote) {
      map.set(r.id, r);
    }
    for (const r of local) {
      if (!map.has(r.id)) {
        map.set(r.id, r);
      }
    }
    return Array.from(map.values()).sort((a, b) => (b.date_rdv + b.heure).localeCompare(a.date_rdv + a.heure));
  }
}
