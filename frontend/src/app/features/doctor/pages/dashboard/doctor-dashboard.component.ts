import { Component, inject, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';
import { AuthService } from '../../../../core/services/auth.service';
import { DoctorService } from '../../services/doctor.service';
import {
  DoctorAppointmentDto,
  DoctorConsultationDto,
  DoctorDashboardStats,
  DoctorProfileDto
} from '../../models/doctor.models';

@Component({
  selector: 'app-doctor-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule, RouterLink],
  templateUrl: './doctor-dashboard.component.html',
  styleUrl: './doctor-dashboard.component.scss'
})
export class DoctorDashboardComponent implements OnInit {
  authService = inject(AuthService);
  doctorService = inject(DoctorService);

  isLoading = signal<boolean>(true);
  errorMessage = signal<string | null>(null);

  stats = signal<DoctorDashboardStats>({
    appointmentsTodayCount: 0,
    appointmentsUpcomingCount: 0,
    consultationsTotalCount: 0,
    patientsFollowedCount: 0
  });

  todayAppointments = signal<DoctorAppointmentDto[]>([]);
  recentConsultations = signal<DoctorConsultationDto[]>([]);
  doctorProfile = signal<DoctorProfileDto | null>(null);

  readonly todayDateFormatted = new Intl.DateTimeFormat('fr-FR', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  }).format(new Date());

  ngOnInit(): void {
    this.loadDashboardData();
  }

  loadDashboardData(): void {
    this.isLoading.set(true);
    this.errorMessage.set(null);

    const todayStr = new Date().toISOString().split('T')[0];

    forkJoin({
      profile: this.doctorService.getMyDoctorProfile(),
      stats: this.doctorService.getDashboardStats(),
      appointments: this.doctorService.getAppointments(1, '', ''),
      consultations: this.doctorService.getConsultations(1, '', undefined)
    }).subscribe({
      next: ({ profile, stats, appointments, consultations }) => {
        this.doctorProfile.set(profile);
        this.stats.set(stats);

        const allAppointments = appointments.results || [];
        // Filtrer les rendez-vous du jour
        const todayRdvs = allAppointments.filter(r => (r.date_rdv || r.dateRdv) === todayStr);
        this.todayAppointments.set(todayRdvs.slice(0, 5));

        // Consultations récentes
        this.recentConsultations.set((consultations.results || []).slice(0, 5));
        this.isLoading.set(false);
      },
      error: () => {
        this.errorMessage.set('Impossible de charger les données du tableau de bord. Veuillez réessayer.');
        this.isLoading.set(false);
      }
    });
  }

  confirmAppointment(rdv: DoctorAppointmentDto): void {
    this.doctorService.confirmAppointment(rdv.id).subscribe({
      next: () => {
        rdv.statut = 'CONFIRME';
      }
    });
  }

  completeAppointment(rdv: DoctorAppointmentDto): void {
    this.doctorService.completeAppointment(rdv.id).subscribe({
      next: () => {
        rdv.statut = 'TERMINE';
      }
    });
  }

  getStatusClass(statut: string): string {
    switch (statut) {
      case 'CONFIRME': return 'status-confirmed';
      case 'TERMINE': return 'status-completed';
      case 'ANNULE': return 'status-cancelled';
      case 'EN_COURS': return 'status-in-progress';
      default: return 'status-pending';
    }
  }

  getStatusLabel(statut: string): string {
    switch (statut) {
      case 'CONFIRME': return 'Confirmé';
      case 'TERMINE': return 'Terminé';
      case 'ANNULE': return 'Annulé';
      case 'EN_COURS': return 'En cours';
      case 'EN_ATTENTE': return 'En attente';
      default: return statut;
    }
  }

  getPatientId(item: DoctorAppointmentDto | DoctorConsultationDto): number {
    return Number(item.patient || item.patient_details?.id_patient || item.patient_details?.idPatient || 0);
  }

  formatDate(dateStr?: string): string {
    if (!dateStr) return '—';
    try {
      const d = new Date(dateStr);
      if (isNaN(d.getTime())) {
        return dateStr.split('T')[0] || dateStr;
      }
      return d.toLocaleDateString('fr-FR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      });
    } catch {
      return dateStr;
    }
  }
}
