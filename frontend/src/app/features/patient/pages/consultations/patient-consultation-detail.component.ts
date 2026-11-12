import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, ActivatedRoute } from '@angular/router';
import { PatientConsultationService } from '../../services/patient-consultation.service';
import { PdfDownloadService } from '../../../../core/services/pdf-download.service';
import { ConsultationDto } from '../../models/patient.models';
import { formatDate as formatSharedDate } from '../../../../shared/utils';

@Component({
  selector: 'app-patient-consultation-detail',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './patient-consultation-detail.component.html',
  styleUrl: './patient-consultation-detail.component.scss'
})
export class PatientConsultationDetailComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private consultationService = inject(PatientConsultationService);
  private pdfDownloadService = inject(PdfDownloadService);

  consultationId = signal<number | null>(null);
  consultation = signal<ConsultationDto | null>(null);
  isLoading = signal<boolean>(true);
  isDownloadingPdf = signal<boolean>(false);
  errorMessage = signal<string | null>(null);

  ngOnInit(): void {
    const idParam = this.route.snapshot.paramMap.get('id');
    if (idParam) {
      const id = parseInt(idParam, 10);
      if (!isNaN(id)) {
        this.consultationId.set(id);
        this.loadConsultation(id);
        return;
      }
    }
    this.errorMessage.set('Identifiant de consultation invalide.');
    this.isLoading.set(false);
  }

  loadConsultation(id: number): void {
    this.isLoading.set(true);
    this.errorMessage.set(null);

    this.consultationService.getConsultationById(id).subscribe({
      next: (data) => {
        this.consultation.set(data);
        this.isLoading.set(false);
      },
      error: () => {
        this.errorMessage.set('Impossible de charger les détails de cette consultation.');
        this.isLoading.set(false);
      }
    });
  }

  printReport(): void {
    window.print();
  }

  downloadOfficialPdf(): void {
    const cons = this.consultation();
    if (!cons) return;

    this.isDownloadingPdf.set(true);
    this.pdfDownloadService.downloadConsultationPdf(cons.id).subscribe({
      next: () => {
        this.isDownloadingPdf.set(false);
      },
      error: () => {
        this.isDownloadingPdf.set(false);
        this.errorMessage.set('Erreur lors du téléchargement du certificat médical PDF.');
      }
    });
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
}
