import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, ActivatedRoute } from '@angular/router';
import { PatientConsultationService } from '../../services/patient-consultation.service';
import { ConsultationDto } from '../../models/patient.models';

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

  consultationId = signal<number | null>(null);
  consultation = signal<ConsultationDto | null>(null);
  isLoading = signal<boolean>(true);
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

  formatDate(dateStr?: string): string {
    if (!dateStr) return '—';
    try {
      const d = new Date(dateStr);
      return isNaN(d.getTime()) ? dateStr : d.toLocaleDateString('fr-FR', {
        weekday: 'long',
        day: 'numeric',
        month: 'long',
        year: 'numeric'
      });
    } catch {
      return dateStr;
    }
  }

  getDoctorName(c: ConsultationDto): string {
    if (c.medecin_details) {
      return `Dr. ${c.medecin_details.prenom || ''} ${c.medecin_details.nom || ''}`.trim();
    }
    return `Médecin #${c.medecin}`;
  }
}
