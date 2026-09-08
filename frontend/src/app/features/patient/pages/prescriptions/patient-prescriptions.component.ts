import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { PatientPrescriptionService } from '../../services/patient-prescription.service';
import { OrdonnanceDto } from '../../models/patient.models';

@Component({
  selector: 'app-patient-prescriptions',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './patient-prescriptions.component.html',
  styleUrl: './patient-prescriptions.component.scss'
})
export class PatientPrescriptionsComponent implements OnInit {
  private prescriptionService = inject(PatientPrescriptionService);

  isLoading = signal<boolean>(true);
  errorMessage = signal<string | null>(null);

  prescriptions = signal<OrdonnanceDto[]>([]);
  totalCount = signal<number>(0);
  totalPages = signal<number>(1);

  // Pagination stricte à 3 éléments par page selon la consigne
  readonly pageSize = 3;
  currentPage = signal<number>(1);

  ngOnInit(): void {
    this.loadPrescriptions(1);
  }

  loadPrescriptions(page: number): void {
    this.isLoading.set(true);
    this.errorMessage.set(null);

    this.prescriptionService.getMyPrescriptions(page, this.pageSize).subscribe({
      next: (resp) => {
        this.prescriptions.set(resp.results || []);
        this.totalCount.set(resp.count);
        this.totalPages.set(resp.total_pages || Math.max(1, Math.ceil(resp.count / this.pageSize)));
        this.currentPage.set(page);
        this.isLoading.set(false);
      },
      error: () => {
        this.errorMessage.set('Impossible de charger la liste de vos ordonnances.');
        this.isLoading.set(false);
      }
    });
  }

  changePage(page: number): void {
    if (page >= 1 && page <= this.totalPages() && page !== this.currentPage()) {
      this.loadPrescriptions(page);
    }
  }

  formatDate(dateStr?: string): string {
    if (!dateStr) return '—';
    try {
      const d = new Date(dateStr);
      return isNaN(d.getTime()) ? dateStr : d.toLocaleDateString('fr-FR', {
        weekday: 'short',
        day: 'numeric',
        month: 'long',
        year: 'numeric'
      });
    } catch {
      return dateStr;
    }
  }

  getDoctorName(p: OrdonnanceDto): string {
    const doc = p.consultation_details?.medecin_details;
    if (doc) {
      return `Dr. ${doc.prenom || ''} ${doc.nom || ''}`.trim();
    }
    return 'Médecin traitant';
  }

  getDoctorSpecialty(p: OrdonnanceDto): string {
    return p.consultation_details?.medecin_details?.specialite || 'Médecine générale';
  }
}
