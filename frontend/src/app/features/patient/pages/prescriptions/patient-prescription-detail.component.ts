import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, ActivatedRoute } from '@angular/router';
import { PatientPrescriptionService } from '../../services/patient-prescription.service';
import { PdfDownloadService } from '../../../../core/services/pdf-download.service';
import { OrdonnanceDto } from '../../models/patient.models';
import { formatDate as formatSharedDate } from '../../../../shared/utils';

@Component({
  selector: 'app-patient-prescription-detail',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './patient-prescription-detail.component.html',
  styleUrl: './patient-prescription-detail.component.scss'
})
export class PatientPrescriptionDetailComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private prescriptionService = inject(PatientPrescriptionService);
  private pdfDownloadService = inject(PdfDownloadService);

  prescriptionId = signal<number | null>(null);
  prescription = signal<OrdonnanceDto | null>(null);
  isLoading = signal<boolean>(true);
  isDownloadingPdf = signal<boolean>(false);
  errorMessage = signal<string | null>(null);

  ngOnInit(): void {
    const idParam = this.route.snapshot.paramMap.get('id');
    if (idParam) {
      const id = parseInt(idParam, 10);
      if (!isNaN(id)) {
        this.prescriptionId.set(id);
        this.loadPrescription(id);
        return;
      }
    }
    this.errorMessage.set('Identifiant d’ordonnance invalide.');
    this.isLoading.set(false);
  }

  loadPrescription(id: number): void {
    this.isLoading.set(true);
    this.errorMessage.set(null);

    this.prescriptionService.getPrescriptionById(id).subscribe({
      next: (data) => {
        this.prescription.set(data);
        this.isLoading.set(false);
      },
      error: () => {
        this.errorMessage.set('Impossible de charger les détails de cette ordonnance.');
        this.isLoading.set(false);
      }
    });
  }

  printPrescription(): void {
    window.print();
  }

  downloadOfficialPdf(): void {
    const ord = this.prescription();
    if (!ord) return;

    this.isDownloadingPdf.set(true);
    this.pdfDownloadService.downloadOrdonnancePdf(ord.id, ord.reference).subscribe({
      next: () => {
        this.isDownloadingPdf.set(false);
      },
      error: () => {
        this.isDownloadingPdf.set(false);
        this.errorMessage.set('Erreur lors du téléchargement du PDF officiel.');
      }
    });
  }

  formatDate(dateStr?: string): string {
    return formatSharedDate(dateStr);
  }

  getDoctorName(p: OrdonnanceDto): string {
    const details = p.consultationDetails || p.consultation_details;
    const doc = details?.medecinDetails || details?.medecin_details;
    if (doc?.nom || doc?.prenom) {
      return `Dr. ${doc.prenom || ''} ${doc.nom || ''}`.trim();
    }
    const direct = p.medecinNom || p.medecin_nom;
    if (direct) {
      return direct;
    }
    return 'Médecin traitant';
  }

  getDoctorSpecialty(p: OrdonnanceDto): string {
    const details = p.consultationDetails || p.consultation_details;
    const doc = details?.medecinDetails || details?.medecin_details;
    return doc?.specialiteDisplay || doc?.specialite || 'Médecine générale';
  }

  getDoctorPhone(p: OrdonnanceDto): string {
    const details = p.consultationDetails || p.consultation_details;
    const doc = details?.medecinDetails || details?.medecin_details;
    return doc?.telephonePro || doc?.telephone || '';
  }

  getPatientName(p: OrdonnanceDto): string {
    const details = p.consultationDetails || p.consultation_details;
    const pat = details?.patientDetails || details?.patient_details;
    if (pat?.nom || pat?.prenom) {
      return `${pat.prenom || ''} ${pat.nom || ''}`.trim();
    }
    const direct = p.patientNom || p.patient_nom;
    if (direct) {
      return direct;
    }
    return 'Patient';
  }

  getPatientBirthDate(p: OrdonnanceDto): string {
    const details = p.consultationDetails || p.consultation_details;
    const pat = details?.patientDetails || details?.patient_details;
    return pat?.dateNaissance || pat?.date_naissance || '';
  }
}
