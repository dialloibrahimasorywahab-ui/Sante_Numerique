import { Component, OnInit, OnDestroy, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { AppointmentService } from '../../services/appointment.service';
import { AuthService } from '../../../../core/services/auth.service';
import { RendezVousDto } from '../../models/models';

@Component({
  selector: 'app-my-appointments',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './my-appointments.component.html',
  styleUrl: './my-appointments.component.scss'
})
export class MyAppointmentsComponent implements OnInit, OnDestroy {
  private appointmentService = inject(AppointmentService);
  authService = inject(AuthService);

  appointments = signal<RendezVousDto[]>([]);
  isLoading = signal<boolean>(true);
  errorMessage = signal<string | null>(null);
  activeTab = signal<'UPCOMING' | 'PAST'>('UPCOMING');

  cancellingId = signal<number | null>(null);
  appointmentToCancel = signal<RendezVousDto | null>(null);
  private refreshTimer?: ReturnType<typeof setInterval>;
  private currentTime = signal(Date.now());

  // Filtered upcoming vs past appointments
  upcomingAppointments = computed(() => {
    this.currentTime();
    return this.appointments().filter(rdv => {
      const isPast = this.isAppointmentPast(rdv) || rdv.statut === 'TERMINE' || rdv.statut === 'ANNULE';
      return !isPast;
    });
  });

  pastAppointments = computed(() => {
    this.currentTime();
    return this.appointments().filter(rdv => {
      const isPast = this.isAppointmentPast(rdv) || rdv.statut === 'TERMINE' || rdv.statut === 'ANNULE';
      return isPast;
    });
  });

  ngOnInit(): void {
    this.loadAppointments();
    this.refreshTimer = setInterval(() => this.currentTime.set(Date.now()), 30000);
  }

  ngOnDestroy(): void {
    if (this.refreshTimer) {
      clearInterval(this.refreshTimer);
    }
  }

  private isAppointmentPast(rdv: RendezVousDto): boolean {
    const dateTime = new Date(`${rdv.date_rdv}T${rdv.heure.substring(0, 5)}`);
    return !Number.isNaN(dateTime.getTime()) && dateTime.getTime() <= this.currentTime();
  }

  loadAppointments(): void {
    this.isLoading.set(true);
    this.errorMessage.set(null);

    const user = this.authService.currentUser();
    const filter = user ? {
      email: user.email,
      telephone: user.telephone,
      patient_id: user.id_user
    } : undefined;

    this.appointmentService.getMyAppointments(filter).subscribe({
      next: (data) => {
        const patientOnly = this.filterOnlyPatient(data, user);
        this.appointments.set(patientOnly);
        this.isLoading.set(false);
      },
      error: (err) => {
        console.error('Erreur lors du chargement des rendez-vous:', err);
        this.errorMessage.set('Impossible de récupérer la liste de vos rendez-vous.');
        this.isLoading.set(false);
      }
    });
  }

  private filterOnlyPatient(list: RendezVousDto[], user: any): RendezVousDto[] {
    if (!user) return [];
    const userEmail = (user.email || '').toLowerCase();
    const userTel = user.telephone || '';
    const userId = user.id_user;
    const userName = (user.nom || '').toLowerCase();

    return list.filter(rdv => {
      if (rdv.id_patient && rdv.id_patient === userId) return true;
      if (rdv.patient_email && rdv.patient_email.toLowerCase() === userEmail) return true;
      if (rdv.patient_telephone && rdv.patient_telephone === userTel) return true;
      if (rdv.patient_detail) {
        const patientDetail = rdv.patient_detail as any;
        const patientUserId = patientDetail.idUtilisateur || patientDetail.id_utilisateur;
        if (patientUserId === userId) return true;
        if (typeof patientUserId === 'object' && patientUserId) {
          if (patientUserId.id_user === userId) return true;
          if (patientUserId.email && patientUserId.email.toLowerCase() === userEmail) return true;
          if (patientUserId.telephone && patientUserId.telephone === userTel) return true;
          if (patientUserId.nom && patientUserId.nom.toLowerCase() === userName) return true;
        }
      }
      if (rdv.patient_nom && rdv.patient_nom.toLowerCase() === userName) return true;
      return false;
    });
  }

  cancelAppointment(rdv: RendezVousDto): void {
    if (this.cancellingId()) {
      return;
    }

    this.appointmentToCancel.set(rdv);
  }

  confirmCancellation(): void {
    const rdv = this.appointmentToCancel();
    if (!rdv) return;

    this.appointmentToCancel.set(null);

    this.cancellingId.set(rdv.id);
    this.appointmentService.cancelAppointment(rdv.id).subscribe({
      next: () => {
        this.cancellingId.set(null);
        // Refresh list
        this.loadAppointments();
      },
      error: (err) => {
        this.cancellingId.set(null);
        this.errorMessage.set('Une erreur est survenue lors de l\'annulation du rendez-vous.');
        console.error(err);
      }
    });
  }

  closeCancellationDialog(): void {
    if (!this.cancellingId()) {
      this.appointmentToCancel.set(null);
    }
  }

  getStatusBadgeClass(statut: string): string {
    switch (statut) {
      case 'CONFIRME':
      case 'PROGRAMME':
        return 'badge-confirmed';
      case 'EN_ATTENTE':
        return 'badge-pending';
      case 'TERMINE':
        return 'badge-completed';
      case 'ANNULE':
        return 'badge-cancelled';
      default:
        return 'badge-default';
    }
  }

  getStatusLabel(statut: string): string {
    switch (statut) {
      case 'CONFIRME':
        return '✓ Confirmé';
      case 'PROGRAMME':
        return '🗓️ Programmé';
      case 'EN_ATTENTE':
        return '⏳ En attente de validation';
      case 'EN_COURS':
        return '🩺 En cours';
      case 'TERMINE':
        return '✅ Terminé';
      case 'ANNULE':
        return '❌ Annulé';
      default:
        return statut;
    }
  }
}
