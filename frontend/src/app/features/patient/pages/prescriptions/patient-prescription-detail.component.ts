import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, ActivatedRoute } from '@angular/router';
import { PatientPrescriptionService } from '../../services/patient-prescription.service';
import { OrdonnanceDto } from '../../models/patient.models';

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

  prescriptionId = signal<number | null>(null);
  prescription = signal<OrdonnanceDto | null>(null);
  isLoading = signal<boolean>(true);
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

  formatDate(dateStr?: string): string {
    if (!dateStr) return '—';
    try {
      const d = new Date(dateStr);
      return isNaN(d.getTime()) ? dateStr : d.toLocaleDateString('fr-FR', {
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
