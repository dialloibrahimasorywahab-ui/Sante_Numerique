import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { DoctorService } from '../../services/doctor.service';
import { DoctorHospitalisationDto } from '../../models/doctor.models';

@Component({
  selector: 'app-doctor-admission-detail',
  standalone: true,
  imports: [CommonModule, RouterModule, RouterLink, FormsModule],
  templateUrl: './doctor-admission-detail.component.html',
  styleUrl: './doctor-admission-detail.component.scss'
})
export class DoctorAdmissionDetailComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private doctorService = inject(DoctorService);

  admissionId = signal<number | null>(null);
  admission = signal<DoctorHospitalisationDto | null>(null);
  isLoading = signal<boolean>(true);
  errorMessage = signal<string | null>(null);

  // Modal de sortie / clôture
  isDischargeModalOpen = signal<boolean>(false);
  isSubmittingDischarge = signal<boolean>(false);
  dischargeObservation = signal<string>('');
  dischargeDate = signal<string>('');

  ngOnInit(): void {
    const idParam = this.route.snapshot.paramMap.get('id');
    if (idParam && !isNaN(+idParam)) {
      this.admissionId.set(+idParam);
      this.loadAdmission(+idParam);
    } else {
      this.errorMessage.set("Identifiant d'admission non valide.");
      this.isLoading.set(false);
    }
  }

  loadAdmission(id: number): void {
    this.isLoading.set(true);
    this.errorMessage.set(null);

    this.doctorService.getAdmissionDetail(id).subscribe({
      next: (data) => {
        this.admission.set(data);
        this.isLoading.set(false);
      },
      error: (err) => {
        this.isLoading.set(false);
        this.errorMessage.set(
          err.error?.detail || err.error?.error || "Impossible de charger les détails de cette admission."
        );
      }
    });
  }

  openDischargeModal(): void {
    const now = new Date();
    const defaultDateTime = new Date(now.getTime() - now.getTimezoneOffset() * 60000)
      .toISOString()
      .slice(0, 16);

    this.dischargeDate.set(defaultDateTime);
    this.dischargeObservation.set('');
    this.isDischargeModalOpen.set(true);
  }

  closeDischargeModal(): void {
    this.isDischargeModalOpen.set(false);
  }

  confirmDischarge(): void {
    const adm = this.admission();
    if (!adm) return;

    if (!this.dischargeObservation().trim()) {
      alert("Veuillez saisir une observation ou un compte-rendu de sortie.");
      return;
    }

    this.isSubmittingDischarge.set(true);

    this.doctorService.dischargePatient(adm.id, {
      observation: this.dischargeObservation().trim()
    }).subscribe({
      next: (updated) => {
        this.isSubmittingDischarge.set(false);
        this.isDischargeModalOpen.set(false);
        this.admission.set(updated);
      },
      error: (err) => {
        this.isSubmittingDischarge.set(false);
        alert(
          err.error?.detail || err.error?.error || "Erreur lors de la clôture du séjour hospitalier."
        );
      }
    });
  }

  getPatientId(): number | null {
    const adm = this.admission();
    if (!adm) return null;
    return (adm.patient_details?.id_patient || adm.patient_details?.idPatient || adm.patient) as number;
  }
}

