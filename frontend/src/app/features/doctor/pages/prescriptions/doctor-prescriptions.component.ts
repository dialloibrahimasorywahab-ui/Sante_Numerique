import { Component, inject, signal, computed, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { DoctorService } from '../../services/doctor.service';
import { PdfDownloadService } from '../../../../core/services/pdf-download.service';
import { formatDate as formatSharedDate } from '../../../../shared/utils';
import { DoctorPrescriptionDto } from '../../models/doctor.models';

@Component({
  selector: 'app-doctor-prescriptions',
  standalone: true,
  imports: [CommonModule, RouterModule, RouterLink, FormsModule],
  templateUrl: './doctor-prescriptions.component.html',
  styleUrl: './doctor-prescriptions.component.scss'
})
export class DoctorPrescriptionsComponent implements OnInit {
  private doctorService = inject(DoctorService);
  private pdfService = inject(PdfDownloadService);

  isLoading = signal<boolean>(true);
  errorMessage = signal<string | null>(null);
  downloadingId = signal<number | null>(null);

  prescriptions = signal<DoctorPrescriptionDto[]>([]);
  searchQuery = signal<string>('');

  currentPage = signal<number>(1);
  pageSize = 10;

  ngOnInit(): void {
    this.loadPrescriptions();
  }

  loadPrescriptions(): void {
    this.isLoading.set(true);
    this.errorMessage.set(null);

    this.doctorService.getPrescriptions(1, '', undefined).subscribe({
      next: (res) => {
        this.prescriptions.set(res.results || []);
        this.isLoading.set(false);
      },
      error: () => {
        this.errorMessage.set('Erreur lors du chargement des ordonnances.');
        this.isLoading.set(false);
      }
    });
  }

  filteredPrescriptions = computed(() => {
    let list = this.prescriptions();
    const query = this.searchQuery().trim().toLowerCase();
    if (!query) return list;

    return list.filter(p => {
      const ref = (p.reference || '').toLowerCase();
      const obs = (p.observation || '').toLowerCase();
      const date = (p.date_ordonnance || (p as any).dateOrdonnance || '').toLowerCase();
      const details = (p as any).consultationDetails || p.consultation_details;
      const pat = details?.patientDetails || details?.patient_details || details?.patient_detail;
      const patNom = (pat?.nom || (p as any).patientNom || (p as any).patient_nom || '').toLowerCase();
      const patPrenom = (pat?.prenom || '').toLowerCase();
      return ref.includes(query) || obs.includes(query) || date.includes(query) || patNom.includes(query) || patPrenom.includes(query);
    });
  });

  paginatedPrescriptions = computed(() => {
    const list = this.filteredPrescriptions();
    const start = (this.currentPage() - 1) * this.pageSize;
    return list.slice(start, start + this.pageSize);
  });

  totalPages = computed(() => {
    return Math.ceil(this.filteredPrescriptions().length / this.pageSize) || 1;
  });

  setPage(p: number): void {
    if (p >= 1 && p <= this.totalPages()) {
      this.currentPage.set(p);
    }
  }

  getPatientId(p: DoctorPrescriptionDto): number {
    const details = (p as any).consultationDetails || p.consultation_details;
    const pat = details?.patientDetails || details?.patient_details || details?.patient_detail;
    return Number(
      details?.patient ||
      pat?.id_patient ||
      pat?.idPatient ||
      0
    );
  }

  getPatientName(p: DoctorPrescriptionDto): string {
    const details = (p as any).consultationDetails || p.consultation_details;
    const pat = details?.patientDetails || details?.patient_details || details?.patient_detail;
    if (pat?.nom || pat?.prenom) {
      return `${pat.prenom || ''} ${pat.nom || ''}`.trim();
    }
    const direct = (p as any).patientNom || (p as any).patient_nom;
    if (direct) {
      return direct;
    }
    return 'Patient';
  }

  formatDate(dateStr?: string): string {
    return formatSharedDate(dateStr);
  }

  downloadPdf(p: DoctorPrescriptionDto): void {
    const id = p.id || p.idOrdonnance;
    if (!id) return;
    this.downloadingId.set(id);
    this.pdfService.downloadOrdonnancePdf(id, p.reference).subscribe({
      next: () => this.downloadingId.set(null),
      error: (err) => {
        console.error('Erreur téléchargement ordonnance PDF', err);
        this.downloadingId.set(null);
      }
    });
  }
}
