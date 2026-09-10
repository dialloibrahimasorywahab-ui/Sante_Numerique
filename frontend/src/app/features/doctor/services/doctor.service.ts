import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, map, of, forkJoin, catchError } from 'rxjs';
import { environment } from '../../../../environments/environment';
import { AuthService } from '../../../core/services/auth.service';
import {
  DoctorProfileDto,
  DoctorAppointmentDto,
  DoctorPatientDto,
  CreatePatientDto,
  DoctorConsultationDto,
  CreateConsultationDto,
  DoctorPrescriptionDto,
  CreatePrescriptionDto,
  DisponibiliteMedecinDto,
  IndisponibiliteMedecinDto,
  CreneauxResponseDto,
  DoctorDashboardStats,
  PaginatedResult
} from '../models/doctor.models';

@Injectable({
  providedIn: 'root'
})
export class DoctorService {
  private http = inject(HttpClient);
  private authService = inject(AuthService);

  private get apiUrl(): string {
    return environment.apiUrl;
  }

  // ==========================================
  // PROFIL MÉDECIN
  // ==========================================

  getMyDoctorProfile(): Observable<DoctorProfileDto | null> {
    const user = this.authService.currentUser();
    if (!user) return of(null);

    return this.http.get<any>(`${this.apiUrl}/medecins/`, {
      params: new HttpParams().set('search', user.email || user.login || ''),
      withCredentials: true
    }).pipe(
      map(res => {
        const list: DoctorProfileDto[] = res.results || res;
        if (Array.isArray(list) && list.length > 0) {
          const match = list.find(m => m.idUtilisateur === user.id_user || m.email === user.email);
          return match || list[0];
        }
        return null;
      }),
      catchError(() => of(null))
    );
  }

  updateDoctorProfile(id: number, data: Partial<DoctorProfileDto>): Observable<DoctorProfileDto> {
    return this.http.patch<DoctorProfileDto>(`${this.apiUrl}/medecins/${id}/update/`, data, {
      withCredentials: true
    });
  }

  // ==========================================
  // RENDEZ-VOUS
  // ==========================================

  getAppointments(page = 1, search = '', statut = ''): Observable<PaginatedResult<DoctorAppointmentDto>> {
    let params = new HttpParams().set('page', page.toString());
    if (search.trim()) params = params.set('search', search.trim());
    if (statut.trim()) params = params.set('statut', statut.trim());

    return this.http.get<any>(`${this.apiUrl}/rendezvous/mes-rendezvous/`, {
      params,
      withCredentials: true
    }).pipe(
      map(res => {
        if (Array.isArray(res)) {
          return { count: res.length, results: res };
        }
        return {
          count: res.count ?? res.results?.length ?? 0,
          next: res.next,
          previous: res.previous,
          results: res.results || []
        };
      })
    );
  }

  confirmAppointment(id: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/rendezvous/${id}/confirmer/`, {}, { withCredentials: true });
  }

  completeAppointment(id: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/rendezvous/${id}/terminer/`, {}, { withCredentials: true });
  }

  cancelAppointment(id: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/rendezvous/${id}/annuler/`, {}, { withCredentials: true });
  }

  // ==========================================
  // PATIENTS
  // ==========================================

  getPatients(page = 1, search = ''): Observable<PaginatedResult<DoctorPatientDto>> {
    let params = new HttpParams().set('page', page.toString());
    if (search.trim()) params = params.set('search', search.trim());

    return this.http.get<any>(`${this.apiUrl}/patients/`, {
      params,
      withCredentials: true
    }).pipe(
      map(res => {
        if (Array.isArray(res)) {
          return { count: res.length, results: res };
        }
        return {
          count: res.count ?? res.results?.length ?? 0,
          next: res.next,
          previous: res.previous,
          results: res.results || []
        };
      })
    );
  }

  getPatientDetail(id: number): Observable<DoctorPatientDto> {
    return this.http.get<DoctorPatientDto>(`${this.apiUrl}/patients/${id}/`, {
      withCredentials: true
    });
  }

  createPatient(dto: CreatePatientDto): Observable<DoctorPatientDto> {
    return this.http.post<DoctorPatientDto>(`${this.apiUrl}/patients/`, dto, {
      withCredentials: true
    });
  }


  // ==========================================
  // CONSULTATIONS
  // ==========================================

  getConsultations(page = 1, search = '', patientId?: number): Observable<PaginatedResult<DoctorConsultationDto>> {
    let params = new HttpParams().set('page', page.toString());
    if (search.trim()) params = params.set('search', search.trim());
    if (patientId) params = params.set('patient_id', patientId.toString());

    return this.http.get<any>(`${this.apiUrl}/consultations/`, {
      params,
      withCredentials: true
    }).pipe(
      map(res => {
        if (Array.isArray(res)) {
          return { count: res.length, results: res };
        }
        return {
          count: res.count ?? res.results?.length ?? 0,
          next: res.next,
          previous: res.previous,
          results: res.results || []
        };
      })
    );
  }

  getConsultationDetail(id: number): Observable<DoctorConsultationDto> {
    return this.http.get<DoctorConsultationDto>(`${this.apiUrl}/consultations/${id}/`, {
      withCredentials: true
    });
  }

  createConsultation(dto: CreateConsultationDto): Observable<DoctorConsultationDto> {
    return this.http.post<DoctorConsultationDto>(`${this.apiUrl}/consultations/`, dto, {
      withCredentials: true
    });
  }

  updateConsultation(id: number, dto: Partial<CreateConsultationDto>): Observable<DoctorConsultationDto> {
    return this.http.patch<DoctorConsultationDto>(`${this.apiUrl}/consultations/${id}/`, dto, {
      withCredentials: true
    });
  }

  // ==========================================
  // ORDONNANCES
  // ==========================================

  getPrescriptions(page = 1, search = '', consultationId?: number): Observable<PaginatedResult<DoctorPrescriptionDto>> {
    let params = new HttpParams().set('page', page.toString());
    if (search.trim()) params = params.set('search', search.trim());
    if (consultationId) params = params.set('consultation_id', consultationId.toString());

    return this.http.get<any>(`${this.apiUrl}/ordonnances/`, {
      params,
      withCredentials: true
    }).pipe(
      map(res => {
        if (Array.isArray(res)) {
          return { count: res.length, results: res };
        }
        return {
          count: res.count ?? res.results?.length ?? 0,
          next: res.next,
          previous: res.previous,
          results: res.results || []
        };
      })
    );
  }

  getPrescriptionDetail(id: number): Observable<DoctorPrescriptionDto> {
    return this.http.get<DoctorPrescriptionDto>(`${this.apiUrl}/ordonnances/${id}/`, {
      withCredentials: true
    });
  }

  createPrescription(dto: CreatePrescriptionDto): Observable<DoctorPrescriptionDto> {
    return this.http.post<DoctorPrescriptionDto>(`${this.apiUrl}/ordonnances/`, dto, {
      withCredentials: true
    });
  }

  // ==========================================
  // DISPONIBILITÉS & CRÉNEAUX RÉGULIERS
  // ==========================================

  getAvailabilities(medecinId?: number): Observable<DisponibiliteMedecinDto[]> {
    let params = new HttpParams();
    if (medecinId) params = params.set('medecin_id', medecinId.toString());

    return this.http.get<DisponibiliteMedecinDto[]>(`${this.apiUrl}/medecins/disponibilites/`, {
      params,
      withCredentials: true
    });
  }

  saveAvailability(dto: Partial<DisponibiliteMedecinDto>): Observable<DisponibiliteMedecinDto> {
    return this.http.post<DisponibiliteMedecinDto>(`${this.apiUrl}/medecins/disponibilites/`, dto, {
      withCredentials: true
    });
  }

  saveBulkAvailabilities(days: Partial<DisponibiliteMedecinDto>[]): Observable<DisponibiliteMedecinDto[]> {
    return this.http.post<DisponibiliteMedecinDto[]>(`${this.apiUrl}/medecins/disponibilites/bulk/`, days, {
      withCredentials: true
    });
  }

  deleteAvailability(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/medecins/disponibilites/${id}/`, {
      withCredentials: true
    });
  }

  // ==========================================
  // INDISPONIBILITÉS & CONGÉS
  // ==========================================

  getUnavailabilities(): Observable<IndisponibiliteMedecinDto[]> {
    return this.http.get<IndisponibiliteMedecinDto[]>(`${this.apiUrl}/medecins/indisponibilites/`, {
      withCredentials: true
    });
  }

  createUnavailability(dto: Partial<IndisponibiliteMedecinDto>): Observable<IndisponibiliteMedecinDto> {
    return this.http.post<IndisponibiliteMedecinDto>(`${this.apiUrl}/medecins/indisponibilites/`, dto, {
      withCredentials: true
    });
  }

  deleteUnavailability(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/medecins/indisponibilites/${id}/`, {
      withCredentials: true
    });
  }

  // ==========================================
  // CRÉNEAUX CALCULÉS PAR DATE
  // ==========================================

  getDoctorSlots(dateStr: string, medecinId: number): Observable<CreneauxResponseDto> {
    return this.http.get<CreneauxResponseDto>(`${this.apiUrl}/rendezvous/creneaux/`, {
      params: new HttpParams().set('medecin_id', medecinId.toString()).set('date', dateStr),
      withCredentials: true
    });
  }

  // ==========================================
  // STATISTIQUES DASHBOARD
  // ==========================================

  getDashboardStats(): Observable<DoctorDashboardStats> {
    const today = new Date().toISOString().split('T')[0];

    return forkJoin({
      rdvs: this.getAppointments(1, '', ''),
      consultations: this.getConsultations(1, '', undefined),
      patients: this.getPatients(1, '')
    }).pipe(
      map(({ rdvs, consultations, patients }) => {
        const allRdvs = rdvs.results || [];
        const todayRdvs = allRdvs.filter(r => (r.date_rdv || r.dateRdv) === today);
        const upcomingRdvs = allRdvs.filter(r => {
          const rDate = r.date_rdv || r.dateRdv;
          return !!rDate && rDate >= today && r.statut !== 'ANNULE' && r.statut !== 'TERMINE';
        });

        return {
          appointmentsTodayCount: todayRdvs.length,
          appointmentsUpcomingCount: upcomingRdvs.length,
          consultationsTotalCount: consultations.count || consultations.results.length,
          patientsFollowedCount: patients.count || patients.results.length
        };
      }),
      catchError(() => of({
        appointmentsTodayCount: 0,
        appointmentsUpcomingCount: 0,
        consultationsTotalCount: 0,
        patientsFollowedCount: 0
      }))
    );
  }
}
