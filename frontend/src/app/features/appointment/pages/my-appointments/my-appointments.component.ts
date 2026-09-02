import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { AppointmentService } from '../../../../core/services/appointment.service';
import { AuthService } from '../../../../core/services/auth.service';
import { RendezVousDto } from '../../models/models';

@Component({
  selector: 'app-my-appointments',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './my-appointments.component.html',
  styleUrl: './my-appointments.component.scss'
})
export class MyAppointmentsComponent implements OnInit {
  private appointmentService = inject(AppointmentService);
  authService = inject(AuthService);

  appointments = signal<RendezVousDto[]>([]);
  isLoading = signal<boolean>(true);
  errorMessage = signal<string | null>(null);
  activeTab = signal<'UPCOMING' | 'PAST'>('UPCOMING');

  cancellingId = signal<number | null>(null);

  // Filtered upcoming vs past appointments
  upcomingAppointments = computed(() => {
    const today = new Date().toISOString().split('T')[0];
    return this.appointments().filter(rdv => {
      const isPast = rdv.date_rdv < today || rdv.statut === 'TERMINE' || rdv.statut === 'ANNULE';
      return !isPast;
    });
  });

  pastAppointments = computed(() => {
    const today = new Date().toISOString().split('T')[0];
    return this.appointments().filter(rdv => {
      const isPast = rdv.date_rdv < today || rdv.statut === 'TERMINE' || rdv.statut === 'ANNULE';
      return isPast;
    });
  });

  ngOnInit(): void {
    this.loadAppointments();
  }

  loadAppointments(): void {
    this.isLoading.set(true);
    this.errorMessage.set(null);

    this.appointmentService.getMyAppointments().subscribe({
      next: (data) => {
        this.appointments.set(data);
        this.isLoading.set(false);
      },
      error: (err) => {
        console.error('Erreur lors du chargement des rendez-vous:', err);
        this.errorMessage.set('Impossible de récupérer la liste de vos rendez-vous.');
        this.isLoading.set(false);
      }
    });
  }

  cancelAppointment(rdv: RendezVousDto): void {
    if (!confirm(`Êtes-vous sûr de vouloir annuler votre rendez-vous du ${rdv.date_rdv} à ${rdv.heure} ?`)) {
      return;
    }

    this.cancellingId.set(rdv.id);
    this.appointmentService.cancelAppointment(rdv.id).subscribe({
      next: () => {
        this.cancellingId.set(null);
        // Refresh list
        this.loadAppointments();
      },
      error: (err) => {
        this.cancellingId.set(null);
        alert('Une erreur est survenue lors de l\'annulation du rendez-vous.');
        console.error(err);
      }
    });
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
