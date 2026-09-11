import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { AppointmentService } from '../../../rendez-vous/services/appointment.service';
import { RendezVousDto } from '../../../rendez-vous/models/models';
import { formatLongDate } from '../../../../shared/utils';

@Component({
  selector: 'app-patient-appointments',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './patient-appointments.component.html',
  styleUrl: './patient-appointments.component.scss'
})
export class PatientAppointmentsComponent implements OnInit {
  private appointmentService = inject(AppointmentService);

  isLoading = signal<boolean>(true);
  errorMessage = signal<string | null>(null);
  successMessage = signal<string | null>(null);

  protected readonly Math = Math;

  appointments = signal<RendezVousDto[]>([]);
  activeTab = signal<'UPCOMING' | 'PAST' | 'ALL'>('UPCOMING');
  searchQuery = signal<string>('');
  statusFilter = signal<string>('ALL');

  // Pagination optimisée à 6 par page
  pageSize = signal<number>(6);
  currentPage = signal<number>(1);

  // Annulation state
  appointmentToCancel = signal<RendezVousDto | null>(null);
  isCancelling = signal<boolean>(false);

  // Filtered upcoming appointments
  upcomingAppointments = computed(() => {
    const now = Date.now();
    return this.appointments().filter(rdv => {
      const dt = new Date(`${rdv.date_rdv}T${rdv.heure.substring(0, 5)}`);
      const isPast = !isNaN(dt.getTime()) && dt.getTime() <= now;
      return !isPast && rdv.statut !== 'TERMINE' && rdv.statut !== 'ANNULE';
    }).sort((a, b) => (a.date_rdv + a.heure).localeCompare(b.date_rdv + b.heure));
  });

  // Filtered past appointments
  pastAppointments = computed(() => {
    const now = Date.now();
    return this.appointments().filter(rdv => {
      const dt = new Date(`${rdv.date_rdv}T${rdv.heure.substring(0, 5)}`);
      const isPast = !isNaN(dt.getTime()) && dt.getTime() <= now;
      return isPast || rdv.statut === 'TERMINE' || rdv.statut === 'ANNULE';
    }).sort((a, b) => (b.date_rdv + b.heure).localeCompare(a.date_rdv + a.heure));
  });

  // Prochain rendez-vous immédiat
  nextAppointment = computed(() => {
    const upcoming = this.upcomingAppointments();
    return upcoming.length > 0 ? upcoming[0] : null;
  });

  // Base list depending on activeTab
  tabAppointments = computed(() => {
    if (this.activeTab() === 'UPCOMING') return this.upcomingAppointments();
    if (this.activeTab() === 'PAST') return this.pastAppointments();
    return this.appointments();
  });

  // Filtered list with search & status filters
  filteredAppointments = computed(() => {
    let list = this.tabAppointments();
    const query = this.searchQuery().trim().toLowerCase();
    const status = this.statusFilter();

    if (status !== 'ALL') {
      list = list.filter(rdv => rdv.statut === status);
    }

    if (query) {
      list = list.filter(rdv => {
        const docName = this.getDoctorFullName(rdv).toLowerCase();
        const spec = this.getDoctorSpecialty(rdv).toLowerCase();
        const motif = (rdv.motif || '').toLowerCase();
        const date = (rdv.date_rdv || '').toLowerCase();
        const bureau = (rdv.bureau || '').toLowerCase();
        const id = String(rdv.id);
        return docName.includes(query) || spec.includes(query) || motif.includes(query) || date.includes(query) || bureau.includes(query) || id.includes(query);
      });
    }

    return list;
  });

  // Total pages based on filtered list
  totalPages = computed(() => {
    const total = this.filteredAppointments().length;
    return Math.max(1, Math.ceil(total / this.pageSize()));
  });

  // Paginated items for current view
  paginatedAppointments = computed(() => {
    const list = this.filteredAppointments();
    const startIndex = (this.currentPage() - 1) * this.pageSize();
    return list.slice(startIndex, startIndex + this.pageSize());
  });

  ngOnInit(): void {
    this.loadAppointments();
  }

  loadAppointments(): void {
    this.isLoading.set(true);
    this.errorMessage.set(null);

    this.appointmentService.getMyAppointments().subscribe({
      next: (list) => {
        this.appointments.set(list || []);
        this.isLoading.set(false);
      },
      error: () => {
        this.errorMessage.set('Impossible de charger vos rendez-vous. Veuillez réessayer.');
        this.isLoading.set(false);
      }
    });
  }

  setTab(tab: 'UPCOMING' | 'PAST' | 'ALL'): void {
    this.activeTab.set(tab);
    this.currentPage.set(1);
  }

  setStatusFilter(status: string): void {
    this.statusFilter.set(status);
    this.currentPage.set(1);
  }

  onSearchChange(): void {
    this.currentPage.set(1);
  }

  resetFilters(): void {
    this.searchQuery.set('');
    this.statusFilter.set('ALL');
    this.activeTab.set('UPCOMING');
    this.currentPage.set(1);
  }

  changePage(page: number): void {
    if (page >= 1 && page <= this.totalPages()) {
      this.currentPage.set(page);
    }
  }

  openCancelModal(rdv: RendezVousDto, event?: Event): void {
    if (event) event.stopPropagation();
    this.appointmentToCancel.set(rdv);
  }

  closeCancelModal(): void {
    this.appointmentToCancel.set(null);
  }

  confirmCancel(): void {
    const rdv = this.appointmentToCancel();
    if (!rdv) return;

    this.isCancelling.set(true);
    this.appointmentService.cancelAppointment(rdv.id).subscribe({
      next: () => {
        this.isCancelling.set(false);
        this.closeCancelModal();
        this.successMessage.set(`Le rendez-vous #${rdv.id} a été annulé avec succès.`);
        this.loadAppointments();
        setTimeout(() => this.successMessage.set(null), 5000);
      },
      error: (err) => {
        this.isCancelling.set(false);
        this.closeCancelModal();
        this.errorMessage.set(err?.friendlyMessage || 'Une erreur est survenue lors de l’annulation du rendez-vous.');
        setTimeout(() => this.errorMessage.set(null), 6000);
      }
    });
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
      case 'EN_ATTENTE': return 'En attente';
      case 'TERMINE': return 'Terminé';
      case 'ANNULE': return 'Annulé';
      default: return statut || 'Prévu';
    }
  }

  getDoctorFullName(rdv: RendezVousDto): string {
    if (rdv.medecin_nom || rdv.medecin_prenom) {
      return `Dr. ${rdv.medecin_prenom || ''} ${rdv.medecin_nom || ''}`.trim();
    }
    if (rdv.medecin_detail) {
      return `Dr. ${rdv.medecin_detail.prenom || ''} ${rdv.medecin_detail.nom || ''}`.trim();
    }
    return `Médecin #${rdv.id_medecin || ''}`.trim();
  }

  getDoctorSpecialty(rdv: RendezVousDto): string {
    return rdv.medecin_specialite || rdv.medecin_detail?.specialite || 'Médecine Générale';
  }

  getServiceNom(rdv: RendezVousDto): string | null {
    return rdv.service_nom || (rdv.medecin_detail as any)?.service_nom || (rdv.medecin_detail as any)?.service?.nom || null;
  }
}
