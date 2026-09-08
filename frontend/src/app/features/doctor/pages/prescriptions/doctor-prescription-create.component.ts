import { Component, inject, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, ActivatedRoute, RouterModule, RouterLink } from '@angular/router';
import { FormBuilder, FormGroup, FormArray, ReactiveFormsModule, Validators } from '@angular/forms';
import { DoctorService } from '../../services/doctor.service';
import { DoctorConsultationDto } from '../../models/doctor.models';

@Component({
  selector: 'app-doctor-prescription-create',
  standalone: true,
  imports: [CommonModule, RouterModule, RouterLink, ReactiveFormsModule],
  templateUrl: './doctor-prescription-create.component.html',
  styleUrl: './doctor-prescription-create.component.scss'
})
export class DoctorPrescriptionCreateComponent implements OnInit {
  private fb = inject(FormBuilder);
  private doctorService = inject(DoctorService);
  private router = inject(Router);
  private route = inject(ActivatedRoute);

  prescriptionForm!: FormGroup;

  isLoading = signal<boolean>(true);
  isSubmitting = signal<boolean>(false);
  errorMessage = signal<string | null>(null);
  successMessage = signal<string | null>(null);

  consultations = signal<DoctorConsultationDto[]>([]);
  selectedConsultation = signal<DoctorConsultationDto | null>(null);

  ngOnInit(): void {
    this.initForm();
    this.loadConsultations();
  }

  private initForm(): void {
    const todayStr = new Date().toISOString().split('T')[0];
    const autoRef = `ORD-${new Date().toISOString().slice(0, 10).replace(/-/g, '')}-${Math.floor(100 + Math.random() * 900)}`;

    this.prescriptionForm = this.fb.group({
      consultation: ['', [Validators.required]],
      date_ordonnance: [todayStr, [Validators.required]],
      reference: [autoRef, [Validators.required]],
      medicaments: this.fb.array([
        this.createMedicamentRow()
      ]),
      instructionsGenerales: ['']
    });
  }

  get medicamentsArray(): FormArray {
    return this.prescriptionForm.get('medicaments') as FormArray;
  }

  createMedicamentRow(): FormGroup {
    return this.fb.group({
      nom: ['', [Validators.required]],
      dosage: ['', [Validators.required]],
      frequence: ['', [Validators.required]],
      duree: ['', [Validators.required]],
      instructions: ['']
    });
  }

  addMedicament(): void {
    this.medicamentsArray.push(this.createMedicamentRow());
  }

  removeMedicament(index: number): void {
    if (this.medicamentsArray.length > 1) {
      this.medicamentsArray.removeAt(index);
    }
  }

  private loadConsultations(): void {
    const queryConsId = this.route.snapshot.queryParamMap.get('consultation_id');

    this.doctorService.getConsultations(1, '', undefined).subscribe({
      next: (res) => {
        const list = res.results || [];
        this.consultations.set(list);

        if (queryConsId) {
          const match = list.find(c => (c.id || c.idConsultation) === +queryConsId);
          if (match) {
            this.selectedConsultation.set(match);
            this.prescriptionForm.patchValue({ consultation: match.id || match.idConsultation });
          } else {
            this.doctorService.getConsultationDetail(+queryConsId).subscribe({
              next: (c) => {
                this.selectedConsultation.set(c);
                this.prescriptionForm.patchValue({ consultation: c.id || c.idConsultation });
              }
            });
          }
        }

        this.isLoading.set(false);
      },
      error: () => {
        this.errorMessage.set('Impossible de charger vos consultations.');
        this.isLoading.set(false);
      }
    });
  }

  onConsultationChange(event: Event): void {
    const select = event.target as HTMLSelectElement;
    const cid = +select.value;
    const cons = this.consultations().find(c => (c.id || c.idConsultation) === cid);
    this.selectedConsultation.set(cons || null);
  }

  onSubmit(): void {
    if (this.prescriptionForm.invalid) {
      this.prescriptionForm.markAllAsTouched();
      return;
    }

    this.isSubmitting.set(true);
    this.errorMessage.set(null);

    const fVal = this.prescriptionForm.value;

    // Formater la liste des médicaments en observation textuelle structurée
    const medLines = (fVal.medicaments || []).map((m: any, idx: number) => {
      let line = `${idx + 1}. ${m.nom} - ${m.dosage} | ${m.frequence} pendant ${m.duree}`;
      if (m.instructions) {
        line += ` (${m.instructions})`;
      }
      return line;
    }).join('\n');

    let fullObservation = medLines;
    if (fVal.instructionsGenerales?.trim()) {
      fullObservation += `\n\nConseils & Recommandations :\n${fVal.instructionsGenerales.trim()}`;
    }

    const payload = {
      consultation: +fVal.consultation,
      reference: fVal.reference,
      date_ordonnance: fVal.date_ordonnance,
      observation: fullObservation
    };

    this.doctorService.createPrescription(payload).subscribe({
      next: () => {
        this.isSubmitting.set(false);
        this.successMessage.set('Ordonnance enregistrée avec succès.');
        setTimeout(() => {
          this.router.navigate(['/medecin/ordonnances']);
        }, 1200);
      },
      error: (err) => {
        this.isSubmitting.set(false);
        if (err?.error?.error) {
          this.errorMessage.set(err.error.error);
        } else {
          this.errorMessage.set('Erreur lors de la création de l’ordonnance.');
        }
      }
    });
  }
}
