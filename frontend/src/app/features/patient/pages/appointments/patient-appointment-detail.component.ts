import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, ActivatedRoute, Router } from '@angular/router';
import { AppointmentService } from '../../../rendez-vous/services/appointment.service';
import { formatLongDate } from '../../../../shared/utils';
import { RendezVousDto } from '../../../rendez-vous/models/models';

@Component({
  selector: 'app-patient-appointment-detail',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './patient-appointment-detail.component.html',
  styleUrl: './patient-appointment-detail.component.scss'
})
export class PatientAppointmentDetailComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private appointmentService = inject(AppointmentService);

  appointmentId = signal<number | null>(null);
  appointment = signal<RendezVousDto | null>(null);
  isLoading = signal<boolean>(true);
  errorMessage = signal<string | null>(null);
  successMessage = signal<string | null>(null);

  // Cancellation state
  showCancelModal = signal<boolean>(false);
  isCancelling = signal<boolean>(false);

  ngOnInit(): void {
    const idParam = this.route.snapshot.paramMap.get('id');
    if (idParam) {
      const id = parseInt(idParam, 10);
      if (!isNaN(id)) {
        this.appointmentId.set(id);
        this.loadAppointment(id);
        return;
      }
    }
    this.errorMessage.set('Identifiant de rendez-vous invalide.');
    this.isLoading.set(false);
  }

  loadAppointment(id: number): void {
    this.isLoading.set(true);
    this.errorMessage.set(null);

    this.appointmentService.getAppointmentById(id).subscribe({
      next: (rdv) => {
        this.appointment.set(rdv);
        this.isLoading.set(false);
      },
      error: () => {
        this.errorMessage.set('Impossible de charger les détails de ce rendez-vous.');
        this.isLoading.set(false);
      }
    });
  }

  openCancelModal(): void {
    this.showCancelModal.set(true);
  }

  closeCancelModal(): void {
    this.showCancelModal.set(false);
  }

  confirmCancel(): void {
    const rdv = this.appointment();
    if (!rdv) return;

    this.isCancelling.set(true);
    this.appointmentService.cancelAppointment(rdv.id).subscribe({
      next: () => {
        this.isCancelling.set(false);
        this.closeCancelModal();
        this.successMessage.set('Votre rendez-vous a bien été annulé.');
        this.appointment.set({ ...rdv, statut: 'ANNULE' });
        setTimeout(() => this.successMessage.set(null), 5000);
      },
      error: (err) => {
        this.isCancelling.set(false);
        this.closeCancelModal();
        this.errorMessage.set(err?.friendlyMessage || 'Une erreur est survenue lors de l’annulation.');
        setTimeout(() => this.errorMessage.set(null), 5000);
      }
    });
  }

  canCancel(statut?: string): boolean {
    return statut !== 'TERMINE' && statut !== 'ANNULE';
  }

  formatDate(dateStr?: string): string {
    return formatLongDate(dateStr);
  }

  formatTime(timeStr?: string): string {
    if (!timeStr) return '';
    return timeStr.substring(0, 5).replace(':', 'h');
  }

  getStatusBadgeClass(statut?: string): string {
    switch (statut) {
      case 'CONFIRME': return 'status-confirmed';
      case 'PLANIFIE':
      case 'EN_ATTENTE': return 'status-planned';
      case 'TERMINE': return 'status-completed';
      case 'ANNULE': return 'status-cancelled';
      default: return 'status-default';
    }
  }

  getStatusLabel(statut?: string): string {
    switch (statut) {
      case 'CONFIRME': return 'Confirmé';
      case 'PLANIFIE': return 'Planifié';
      case 'EN_ATTENTE': return 'En attente de validation';
      case 'TERMINE': return 'Terminé';
      case 'ANNULE': return 'Annulé';
      default: return statut || 'Prévu';
    }
  }
}
