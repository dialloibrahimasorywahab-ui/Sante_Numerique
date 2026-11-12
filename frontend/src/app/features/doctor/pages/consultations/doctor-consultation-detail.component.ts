import { Component, inject, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterModule, RouterLink } from '@angular/router';
import { AuthService } from '../../../../core/services/auth.service';
import { DoctorService } from '../../services/doctor.service';
import { PdfDownloadService } from '../../../../core/services/pdf-download.service';
import { DoctorConsultationDto, DoctorPrescriptionDto } from '../../models/doctor.models';

@Component({
  selector: 'app-doctor-consultation-detail',
  standalone: true,
  imports: [CommonModule, RouterModule, RouterLink],
  templateUrl: './doctor-consultation-detail.component.html',
  styleUrl: './doctor-consultation-detail.component.scss'
})
export class DoctorConsultationDetailComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private doctorService = inject(DoctorService);
  private pdfDownloadService = inject(PdfDownloadService);
  authService = inject(AuthService);

  isLoading = signal<boolean>(true);
  isDownloadingPdf = signal<boolean>(false);
  errorMessage = signal<string | null>(null);

  consultationId = signal<number>(0);
  consultation = signal<DoctorConsultationDto | null>(null);
  prescriptions = signal<DoctorPrescriptionDto[]>([]);

  ngOnInit(): void {
    const idParam = this.route.snapshot.paramMap.get('id');
    if (idParam) {
      this.consultationId.set(+idParam);
      this.loadConsultation(+idParam);
    }
  }

  loadConsultation(id: number): void {
    this.isLoading.set(true);
    this.errorMessage.set(null);

    this.doctorService.getConsultationDetail(id).subscribe({
      next: (cons) => {
        this.consultation.set(cons);

        // Load prescriptions for this consultation
        this.doctorService.getPrescriptions(1, '', id).subscribe({
          next: (pRes) => {
            this.prescriptions.set(pRes.results || []);
            this.isLoading.set(false);
          },
          error: () => {
            this.isLoading.set(false);
          }
        });
      },
      error: () => {
        this.errorMessage.set('Impossible de charger le compte-rendu de consultation.');
        this.isLoading.set(false);
      }
    });
  }

  downloadCertificatePdf(): void {
    const cons = this.consultation();
    if (!cons) return;
    const id = cons.id || cons.idConsultation;
    if (!id) return;

    this.isDownloadingPdf.set(true);
    this.pdfDownloadService.downloadConsultationPdf(id).subscribe({
      next: () => {
        this.isDownloadingPdf.set(false);
      },
      error: () => {
        this.isDownloadingPdf.set(false);
        this.errorMessage.set('Erreur lors du téléchargement du certificat médical.');
      }
    });
  }
}

