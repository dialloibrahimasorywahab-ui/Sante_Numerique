import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { forkJoin, of } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { AuthService } from '../../../../core/services/auth.service';
import { AppointmentService } from '../../../rendez-vous/services/appointment.service';
import { PatientConsultationService } from '../../services/patient-consultation.service';
import { PatientPrescriptionService } from '../../services/patient-prescription.service';
import { PatientHospitalizationService } from '../../services/patient-hospitalization.service';
import { PatientProfileService } from '../../services/patient-profile.service';
import { RendezVousDto } from '../../../rendez-vous/models/models';
import { ConsultationDto, HospitalisationDto, OrdonnanceDto, PatientDashboardStats, PatientRecord } from '../../models/patient.models';
import { calculateAge as calculateSharedAge, formatDate as formatSharedDate, isDateTimePast } from '../../../../shared/utils';

@Component({
  selector: 'app-patient-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './patient-dashboard.component.html',
  styleUrl: './patient-dashboard.component.scss'
})
export class PatientDashboardComponent implements OnInit {
  authService = inject(AuthService);
  private appointmentService = inject(AppointmentService);
  private consultationService = inject(PatientConsultationService);
  private prescriptionService = inject(PatientPrescriptionService);
  private hospitalizationService = inject(PatientHospitalizationService);
  private profileService = inject(PatientProfileService);

  isLoading = signal<boolean>(true);
  errorMessage = signal<string | null>(null);

  patientRecord = signal<PatientRecord | null>(null);

  // Raw data from APIs
  appointments = signal<RendezVousDto[]>([]);
  consultations = signal<ConsultationDto[]>([]);
  prescriptions = signal<OrdonnanceDto[]>([]);
  hospitalizations = signal<HospitalisationDto[]>([]);

  // Âge calculé du patient à partir de sa date de naissance
  userAge = computed<number | null>(() => {
    const user = this.authService.currentUser();
    const bday = user?.date_naissance || (user as any)?.dateNaissance || this.patientRecord()?.date_naissance || (this.patientRecord() as any)?.dateNaissance;
    if (!bday) return null;
    const age = calculateSharedAge(bday, '');
    return typeof age === 'number' && age >= 0 ? age : null;
  });

  isProfileIncomplete = computed<boolean>(() => {
    const user = this.authService.currentUser();
    const bday = user?.date_naissance || (user as any)?.dateNaissance || this.patientRecord()?.date_naissance;
    const rec = this.patientRecord();
    return !bday || !rec?.groupe_sanguin || !rec?.telephone;
  });

  // Computed next appointment
  nextAppointment = computed<RendezVousDto | null>(() => {
    const list = this.appointments();
    const now = Date.now();
    const upcoming = list.filter(rdv => {
      return !isDateTimePast(rdv.date_rdv, rdv.heure, new Date(now)) && rdv.statut !== 'ANNULE' && rdv.statut !== 'TERMINE';
    });
    if (upcoming.length === 0) return null;
    return upcoming.sort((a, b) => (a.date_rdv + a.heure).localeCompare(b.date_rdv + b.heure))[0];
  });

  // Recent 3 consultations
  recentConsultations = computed<ConsultationDto[]>(() => {
    return this.consultations().slice(0, 3);
  });

  // Active hospitalization if any
  activeHospitalization = computed<HospitalisationDto | null>(() => {
    return this.hospitalizations().find(h => h.statut === 'EN_COURS' || h.statut === 'PROGRAMMEE') || null;
  });

  // Stats cards computed strictly from real API lists
  stats = computed<PatientDashboardStats>(() => {
    const now = Date.now();
    const upcomingCount = this.appointments().filter(rdv => {
      return !isDateTimePast(rdv.date_rdv, rdv.heure, new Date(now)) && rdv.statut !== 'ANNULE' && rdv.statut !== 'TERMINE';
    }).length;

    const activeHospCount = this.hospitalizations().filter(h => h.statut === 'EN_COURS' || h.statut === 'PROGRAMMEE').length;

    return {
      upcomingAppointmentsCount: upcomingCount,
      totalConsultationsCount: this.consultations().length,
      totalPrescriptionsCount: this.prescriptions().length,
      activeHospitalizationsCount: activeHospCount
    };
  });

  ngOnInit(): void {
    this.loadDashboardData();
  }

  loadDashboardData(): void {
    this.isLoading.set(true);
    this.errorMessage.set(null);

    const user = this.authService.currentUser();
    const patientId = (user as any)?.patient_id || user?.id_user || user?.idUser;
    if (patientId) {
      this.profileService.getPatientRecord(patientId).subscribe({
        next: (rec) => this.patientRecord.set(rec)
      });
    }

    forkJoin({
      appointments: this.appointmentService.getMyAppointments().pipe(catchError(() => of([]))),
      consultations: this.consultationService.getMyConsultations(1, 20).pipe(catchError(() => of({ results: [], count: 0 }))),
      prescriptions: this.prescriptionService.getMyPrescriptions(1, 20).pipe(catchError(() => of({ results: [], count: 0 }))),
      hospitalizations: this.hospitalizationService.getMyHospitalizations(1, 20).pipe(catchError(() => of({ results: [], count: 0 })))
    }).subscribe({
      next: ({ appointments, consultations, prescriptions, hospitalizations }) => {
        this.appointments.set(appointments || []);
        this.consultations.set(consultations?.results || []);
        this.prescriptions.set(prescriptions?.results || []);
        this.hospitalizations.set(hospitalizations?.results || []);
        this.isLoading.set(false);
      },
      error: () => {
        this.errorMessage.set('Impossible de charger les informations de votre tableau de bord. Veuillez vérifier votre connexion.');
        this.isLoading.set(false);
      }
    });
  }

  formatDate(dateStr?: string | null): string {
    return formatSharedDate(dateStr);
  }

  formatTime(timeStr?: string): string {
    if (!timeStr) return '';
    return timeStr.substring(0, 5).replace(':', 'h');
  }

  getStatusBadgeClass(statut?: string): string {
    switch (statut) {
      case 'CONFIRME': return 'badge-status-confirmed';
      case 'PLANIFIE':
      case 'EN_ATTENTE': return 'badge-status-planned';
      case 'TERMINE': return 'badge-status-completed';
      case 'ANNULE': return 'badge-status-cancelled';
      default: return 'badge-status-default';
    }
  }

  getStatusLabel(statut?: string): string {
    switch (statut) {
      case 'CONFIRME': return 'Confirmé';
      case 'PLANIFIE': return 'Planifié';
      case 'EN_ATTENTE': return 'En attente';
      case 'TERMINE': return 'Effectué';
      case 'ANNULE': return 'Annulé';
      default: return statut || 'Prévu';
    }
  }

  getDoctorFullName(rdv: any): string {
    const m = rdv.medecinDetails || rdv.medecin_details || rdv.medecinDetail || rdv.medecin_detail;
    if (m && (m.prenom || m.nom)) {
      return `Dr. ${m.prenom || ''} ${m.nom || ''}`.trim();
    }
    const prenom = rdv.medecin_prenom || rdv.medecinPrenom || '';
    const nom = rdv.medecin_nom || rdv.medecinNom || '';
    if (prenom || nom) {
      return `Dr. ${prenom} ${nom}`.trim();
    }
    return 'Dr. Praticien Hospitalier';
  }

  getDoctorSpecialty(rdv: RendezVousDto): string {
    return rdv.medecin_specialite || rdv.medecin_detail?.specialite || 'Praticien Hospitalier';
  }

  getHospRoomBed(hosp: any): string {
    if (!hosp) return '—';
    const ch = hosp.chambreNumero || hosp.chambre_numero || hosp.lit_details?.chambre_detail?.numero_chambre || hosp.litDetails?.chambre_detail?.numero_chambre || '—';
    const lit = hosp.litNumero || hosp.lit_numero || hosp.lit_details?.numero_lit || hosp.litDetails?.numero_lit || '—';
    return `Chambre ${ch} — Lit ${lit}`;
  }

  getHospDoctor(hosp: any): string {
    if (!hosp) return 'Dr. Médecin Référent';
    const m = hosp.medecinDetails || hosp.medecin_details || hosp.medecinDetail || hosp.medecin_detail;
    if (m && (m.prenom || m.nom)) {
      return `Dr. ${m.prenom || ''} ${m.nom || ''}`.trim();
    }
    const prenom = hosp.medecin_prenom || hosp.medecinPrenom || '';
    const nom = hosp.medecin_nom || hosp.medecinNom || '';
    if (prenom || nom) {
      return `Dr. ${prenom} ${nom}`.trim();
    }
    return 'Dr. Médecin Référent';
  }

  getConsultationDoctor(cons: any): string {
    if (!cons) return 'Dr. Praticien';
    const m = cons.medecinDetails || cons.medecin_details || cons.medecinDetail || cons.medecin_detail;
    if (m && (m.prenom || m.nom)) {
      return `Dr. ${m.prenom || ''} ${m.nom || ''}`.trim();
    }
    const prenom = cons.medecin_prenom || cons.medecinPrenom || '';
    const nom = cons.medecin_nom || cons.medecinNom || '';
    if (prenom || nom) {
      return `Dr. ${prenom} ${nom}`.trim();
    }
    return 'Dr. Praticien Hospitalier';
  }

}
