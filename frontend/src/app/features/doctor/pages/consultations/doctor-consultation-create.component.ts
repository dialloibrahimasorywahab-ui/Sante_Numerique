import { Component, inject, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, ActivatedRoute, RouterModule, RouterLink } from '@angular/router';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { DoctorService } from '../../services/doctor.service';
import { DoctorPatientDto, DoctorProfileDto } from '../../models/doctor.models';
import { toIsoDate } from '../../../../shared/utils';

@Component({
  selector: 'app-doctor-consultation-create',
  standalone: true,
  imports: [CommonModule, RouterModule, RouterLink, ReactiveFormsModule],
  templateUrl: './doctor-consultation-create.component.html',
  styleUrl: './doctor-consultation-create.component.scss'
})
export class DoctorConsultationCreateComponent implements OnInit {
  private fb = inject(FormBuilder);
  private doctorService = inject(DoctorService);
  private router = inject(Router);
  private route = inject(ActivatedRoute);

  consultationForm!: FormGroup;

  isLoading = signal<boolean>(true);
  isSubmitting = signal<boolean>(false);
  errorMessage = signal<string | null>(null);
  successMessage = signal<string | null>(null);

  doctorProfile = signal<DoctorProfileDto | null>(null);
  patients = signal<DoctorPatientDto[]>([]);
  selectedPatient = signal<DoctorPatientDto | null>(null);
  linkedRdvId = signal<number | null>(null);

  ngOnInit(): void {
    this.initForm();
    this.loadInitialData();
  }

  private initForm(): void {
    const todayStr = toIsoDate();

    this.consultationForm = this.fb.group({
      patient: ['', [Validators.required]],
      date_cons: [todayStr, [Validators.required]],
      symptomes: ['', [Validators.required, Validators.minLength(3)]],
      diagnostic: ['', [Validators.required, Validators.minLength(3)]],
      observations: [''],
      montant_frais: [100000, [Validators.required, Validators.min(0)]],
      description_frais: ['Consultation médicale standard'],
      createPrescriptionNow: [false]
    });
  }

  private loadInitialData(): void {
    const queryPatientId = this.route.snapshot.queryParamMap.get('patient_id');
    const queryRdvId = this.route.snapshot.queryParamMap.get('rdv_id');

    if (queryRdvId) {
      this.linkedRdvId.set(+queryRdvId);
    }

    this.doctorService.getMyDoctorProfile().subscribe({
      next: (profile) => {
        this.doctorProfile.set(profile);

        // Load patients list
        this.doctorService.getPatients(1, '').subscribe({
          next: (pRes) => {
            const list = pRes.results || [];
            this.patients.set(list);

            if (queryPatientId) {
              const matched = list.find(p => (p.id_patient || p.idPatient) === +queryPatientId);
              if (matched) {
                this.selectedPatient.set(matched);
                this.consultationForm.patchValue({ patient: matched.id_patient || matched.idPatient });
              } else {
                // Fetch individually if not in first page
                this.doctorService.getPatientDetail(+queryPatientId).subscribe({
                  next: (p) => {
                    this.selectedPatient.set(p);
                    this.consultationForm.patchValue({ patient: p.id_patient || p.idPatient });
                  }
                });
              }
            }

            this.isLoading.set(false);
          },
          error: () => {
            this.errorMessage.set('Impossible de charger la liste des patients.');
            this.isLoading.set(false);
          }
        });
      },
      error: () => {
        this.errorMessage.set('Impossible de vérifier votre profil praticien.');
        this.isLoading.set(false);
      }
    });
  }

  onPatientChange(event: Event): void {
    const select = event.target as HTMLSelectElement;
    const pid = +select.value;
    const p = this.patients().find(pat => (pat.id_patient || pat.idPatient) === pid);
    this.selectedPatient.set(p || null);
  }

  onSubmit(): void {
    if (this.consultationForm.invalid) {
      this.consultationForm.markAllAsTouched();
      return;
    }

    const doc = this.doctorProfile();
    if (!doc) {
      this.errorMessage.set('Profil médecin non trouvé. Impossible d’enregistrer.');
      return;
    }

    this.isSubmitting.set(true);
    this.errorMessage.set(null);

    const fVal = this.consultationForm.value;

    const payload = {
      patient: +fVal.patient,
      medecin: doc.idMedecin,
      rdv: this.linkedRdvId(),
      date_cons: fVal.date_cons,
      symptomes: fVal.symptomes,
      diagnostic: fVal.diagnostic,
      observations: fVal.observations,
      montant_frais: fVal.montant_frais != null && fVal.montant_frais !== '' ? +fVal.montant_frais : 0,
      description_frais: fVal.description_frais || 'Consultation médicale standard'
    };

    this.doctorService.createConsultation(payload).subscribe({
      next: (created) => {
        this.isSubmitting.set(false);
        this.successMessage.set('Consultation enregistrée avec succès.');

        const consId = created.id || created.idConsultation;

        setTimeout(() => {
          if (fVal.createPrescriptionNow) {
            this.router.navigate(['/medecin/ordonnances/nouveau'], {
              queryParams: { consultation_id: consId }
            });
          } else {
            this.router.navigate(['/medecin/consultations', consId]);
          }
        }, 1200);
      },
      error: (err) => {
        this.isSubmitting.set(false);
        if (err?.error?.error) {
          this.errorMessage.set(err.error.error);
        } else {
          this.errorMessage.set('Une erreur est survenue lors de l’enregistrement de la consultation.');
        }
      }
    });
  }
}
