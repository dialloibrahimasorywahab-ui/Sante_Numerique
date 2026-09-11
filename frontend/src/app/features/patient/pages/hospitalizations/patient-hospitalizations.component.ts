import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { PatientHospitalizationService } from '../../services/patient-hospitalization.service';
import { HospitalisationDto } from '../../models/patient.models';
import { formatDate as formatSharedDate } from '../../../../shared/utils';

@Component({
  selector: 'app-patient-hospitalizations',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './patient-hospitalizations.component.html',
  styleUrl: './patient-hospitalizations.component.scss'
})
export class PatientHospitalizationsComponent implements OnInit {
  private hospitalizationService = inject(PatientHospitalizationService);

  isLoading = signal<boolean>(true);
  errorMessage = signal<string | null>(null);

  hospitalizations = signal<HospitalisationDto[]>([]);
  totalCount = signal<number>(0);
  totalPages = signal<number>(1);

  // Pagination stricte à 3 par page
  readonly pageSize = 3;
  currentPage = signal<number>(1);

  // Séjour actif en cours s'il y en a un
  activeHospitalization = computed(() => {
    return this.hospitalizations().find(h => h.statut === 'EN_COURS') || null;
  });

  ngOnInit(): void {
    this.loadHospitalizations(1);
  }

  loadHospitalizations(page: number): void {
    this.isLoading.set(true);
    this.errorMessage.set(null);

    this.hospitalizationService.getMyHospitalizations(page, this.pageSize).subscribe({
      next: (resp) => {
        this.hospitalizations.set(resp.results || []);
        this.totalCount.set(resp.count);
        this.totalPages.set(resp.total_pages || Math.max(1, Math.ceil(resp.count / this.pageSize)));
        this.currentPage.set(page);
        this.isLoading.set(false);
      },
      error: () => {
        this.errorMessage.set('Impossible de charger votre historique d’hospitalisations.');
        this.isLoading.set(false);
      }
    });
  }

  changePage(page: number): void {
    if (page >= 1 && page <= this.totalPages() && page !== this.currentPage()) {
      this.loadHospitalizations(page);
    }
  }

  formatDate(dateStr?: string | null): string {
    return formatSharedDate(dateStr, 'En cours');
  }

  getStatusBadgeClass(statut?: string): string {
    switch (statut) {
      case 'EN_COURS': return 'status-active';
      case 'PROGRAMMEE': return 'status-planned';
      case 'TERMINEE': return 'status-ended';
      case 'ANNULEE': return 'status-cancelled';
      default: return 'status-default';
    }
  }

  getStatusLabel(statut?: string): string {
    switch (statut) {
      case 'EN_COURS': return 'En cours de séjour';
      case 'PROGRAMMEE': return 'Séjour programmé';
      case 'TERMINEE': return 'Séjour terminé';
      case 'ANNULEE': return 'Annulé';
      default: return statut || 'Hospitalisation';
    }
  }

  getDoctorName(h: HospitalisationDto): string {
    if (h.medecin_details) {
      return `Dr. ${h.medecin_details.prenom || ''} ${h.medecin_details.nom || ''}`.trim();
    }
    return `Médecin #${h.medecin}`;
  }
}
