import { Component, inject, signal, computed, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, RouterLink, ActivatedRoute } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { DoctorService } from '../../services/doctor.service';
import { DoctorAppointmentDto } from '../../models/doctor.models';

type TimeFilter = 'TOUS' | 'AUJOURDHUI' | 'DEMAIN' | 'SEMAINE' | 'A_VENIR' | 'PASSES';

@Component({
  selector: 'app-doctor-appointments',
  standalone: true,
  imports: [CommonModule, RouterModule, RouterLink, FormsModule],
  templateUrl: './doctor-appointments.component.html',
  styleUrl: './doctor-appointments.component.scss'
})
export class DoctorAppointmentsComponent implements OnInit {
  private doctorService = inject(DoctorService);
  private route = inject(ActivatedRoute);

  isLoading = signal<boolean>(true);
  errorMessage = signal<string | null>(null);

  appointments = signal<DoctorAppointmentDto[]>([]);
  searchQuery = signal<string>('');
  selectedStatus = signal<string>('TOUS');
  selectedTimeFilter = signal<TimeFilter>('TOUS');

  // Cancel Modal State
  selectedRdvToCancel = signal<DoctorAppointmentDto | null>(null);
  isCancelling = signal<boolean>(false);

  // Pagination
  currentPage = signal<number>(1);
  pageSize = 8;

  ngOnInit(): void {
    this.route.queryParams.subscribe(params => {
      if (params['filter'] === 'today') {
        this.selectedTimeFilter.set('AUJOURDHUI');
      }
      this.loadAppointments();
    });
  }

  loadAppointments(): void {
    this.isLoading.set(true);
    this.errorMessage.set(null);

    this.doctorService.getAppointments(1, '', '').subscribe({
      next: (res) => {
        this.appointments.set(res.results || []);
        this.isLoading.set(false);
      },
      error: () => {
        this.errorMessage.set('Erreur lors du chargement des rendez-vous.');
        this.isLoading.set(false);
      }
    });
  }

  // Filtered Appointments
  filteredAppointments = computed(() => {
    let list = this.appointments();
    const query = this.searchQuery().trim().toLowerCase();
    const status = this.selectedStatus();
    const timeFilter = this.selectedTimeFilter();

    const todayStr = new Date().toISOString().split('T')[0];
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const tomorrowStr = tomorrow.toISOString().split('T')[0];

    const weekLater = new Date();
    weekLater.setDate(weekLater.getDate() + 7);
    const weekLaterStr = weekLater.toISOString().split('T')[0];

    // 1. Text search
    if (query) {
      list = list.filter(r => {
        const nom = (r.patient_details?.nom || '').toLowerCase();
        const prenom = (r.patient_details?.prenom || '').toLowerCase();
        const motif = (r.motif || '').toLowerCase();
        const tel = (r.patient_details?.telephone || '').toLowerCase();
        return nom.includes(query) || prenom.includes(query) || motif.includes(query) || tel.includes(query);
      });
    }

    // 2. Status filter
    if (status !== 'TOUS') {
      list = list.filter(r => r.statut === status);
    }

    // 3. Time filter
    if (timeFilter !== 'TOUS') {
      list = list.filter(r => {
        const rDate = r.date_rdv || r.dateRdv;
        if (!rDate) return true;
        switch (timeFilter) {
          case 'AUJOURDHUI':
            return rDate === todayStr;
          case 'DEMAIN':
            return rDate === tomorrowStr;
          case 'SEMAINE':
            return rDate >= todayStr && rDate <= weekLaterStr;
          case 'A_VENIR':
            return rDate >= todayStr;
          case 'PASSES':
            return rDate < todayStr;
          default:
            return true;
        }
      });
    }

    return list;
  });

  paginatedAppointments = computed(() => {
    const list = this.filteredAppointments();
    const start = (this.currentPage() - 1) * this.pageSize;
    return list.slice(start, start + this.pageSize);
  });

  totalPages = computed(() => {
    return Math.ceil(this.filteredAppointments().length / this.pageSize) || 1;
  });

  setPage(p: number): void {
    if (p >= 1 && p <= this.totalPages()) {
      this.currentPage.set(p);
    }
  }

  setTimeFilter(tf: TimeFilter): void {
    this.selectedTimeFilter.set(tf);
    this.currentPage.set(1);
  }

  setStatusFilter(st: string): void {
    this.selectedStatus.set(st);
    this.currentPage.set(1);
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

  openCancelModal(rdv: DoctorAppointmentDto): void {
    this.selectedRdvToCancel.set(rdv);
  }

  closeCancelModal(): void {
    this.selectedRdvToCancel.set(null);
  }

  confirmCancelRdv(): void {
    const rdv = this.selectedRdvToCancel();
    if (!rdv) return;

    this.isCancelling.set(true);
    this.doctorService.cancelAppointment(rdv.id).subscribe({
      next: () => {
        rdv.statut = 'ANNULE';
        this.isCancelling.set(false);
        this.closeCancelModal();
      },
      error: () => {
        this.isCancelling.set(false);
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
}
