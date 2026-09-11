import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { PatientConsultationService } from '../../services/patient-consultation.service';
import { ConsultationDto } from '../../models/patient.models';
import { formatDate as formatSharedDate } from '../../../../shared/utils';

@Component({
  selector: 'app-patient-consultations',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './patient-consultations.component.html',
  styleUrl: './patient-consultations.component.scss'
})
export class PatientConsultationsComponent implements OnInit {
  private consultationService = inject(PatientConsultationService);

  isLoading = signal<boolean>(true);
  errorMessage = signal<string | null>(null);

  consultations = signal<ConsultationDto[]>([]);
  totalCount = signal<number>(0);
  totalPages = signal<number>(1);

  // Pagination stricte à 3 par page selon consigne
  readonly pageSize = 3;
  currentPage = signal<number>(1);

  ngOnInit(): void {
    this.loadConsultations(1);
  }

  loadConsultations(page: number): void {
    this.isLoading.set(true);
    this.errorMessage.set(null);

    this.consultationService.getMyConsultations(page, this.pageSize).subscribe({
      next: (resp) => {
        this.consultations.set(resp.results || []);
        this.totalCount.set(resp.count);
        this.totalPages.set(resp.total_pages || Math.max(1, Math.ceil(resp.count / this.pageSize)));
        this.currentPage.set(page);
        this.isLoading.set(false);
      },
      error: () => {
        this.errorMessage.set('Impossible de charger votre historique de consultations.');
        this.isLoading.set(false);
      }
    });
  }

  changePage(page: number): void {
    if (page >= 1 && page <= this.totalPages() && page !== this.currentPage()) {
      this.loadConsultations(page);
    }
  }

  formatDate(dateStr?: string): string {
    return formatSharedDate(dateStr);
  }

  getDoctorName(c: ConsultationDto): string {
    if (c.medecin_details) {
      return `Dr. ${c.medecin_details.prenom || ''} ${c.medecin_details.nom || ''}`.trim();
    }
    return `Médecin #${c.medecin}`;
  }

  getDoctorSpecialty(c: ConsultationDto): string {
    return c.medecin_details?.specialite || 'Médecine générale';
  }
}
