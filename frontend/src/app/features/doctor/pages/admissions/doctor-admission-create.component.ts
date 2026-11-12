import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule, RouterLink, ActivatedRoute } from '@angular/router';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule, FormsModule } from '@angular/forms';
import { DoctorService } from '../../services/doctor.service';
import { AuthService } from '../../../../core/services/auth.service';
import {
  DoctorPatientDto,
  AvailableBedDto,
  CreateHospitalisationDto,
  AdmissionConfirmationDto,
  PrioriteAdmission
} from '../../models/doctor.models';

@Component({
  selector: 'app-doctor-admission-create',
  standalone: true,
  imports: [CommonModule, RouterModule, RouterLink, ReactiveFormsModule, FormsModule],
  templateUrl: './doctor-admission-create.component.html',
  styleUrl: './doctor-admission-create.component.scss'
})
export class DoctorAdmissionCreateComponent implements OnInit {
  private fb = inject(FormBuilder);
  private doctorService = inject(DoctorService);
  private authService = inject(AuthService);
  private router = inject(Router);
  private route = inject(ActivatedRoute);

  // Signaux d'état
  patientMode = signal<'existant' | 'nouveau'>('existant');
  isLoading = signal<boolean>(false);
  isSubmitting = signal<boolean>(false);
  isSearching = signal<boolean>(false);
  errorMessage = signal<string | null>(null);

  // Données
  patientQuery = signal<string>('');
  patientSearchResults = signal<DoctorPatientDto[]>([]);
  selectedPatient = signal<DoctorPatientDto | null>(null);
  servicesList = signal<any[]>([]);
  availableBeds = signal<AvailableBedDto[]>([]);

  // Confirmation post-enregistrement
  confirmationData = signal<AdmissionConfirmationDto | null>(null);

  // Formulaire d'admission
  admissionForm!: FormGroup;

  // Options prédéfinies
  readonly prioriteOptions: { value: PrioriteAdmission; label: string; desc: string; badgeClass: string }[] = [
    { value: 'NORMAL', label: 'Normale', desc: 'Prise en charge standard', badgeClass: 'badge-priorite-normal' },
    { value: 'URGENT', label: 'Urgente', desc: 'Prise en charge prioritaire requise', badgeClass: 'badge-priorite-urgent' },
    { value: 'TRES_URGENT', label: 'Très urgente', desc: 'Urgence vitale / Soins intensifs', badgeClass: 'badge-priorite-tres-urgent' }
  ];

  readonly sangOptions = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'];

  get currentUser() {
    return this.authService.currentUser();
  }

  ngOnInit(): void {
    this.initForm();
    this.loadPrerequisites();
    this.checkQueryParams();
  }

  private initForm(): void {
    const now = new Date();
    const defaultDateTime = new Date(now.getTime() - now.getTimezoneOffset() * 60000)
      .toISOString()
      .slice(0, 16);

    this.admissionForm = this.fb.group({
      // SECTION A - PATIENT
      // Cas existant
      patient_id: [null],
      // Cas nouveau patient
      nom: [''],
      prenom: [''],
      telephone: [''],
      email: [''],
      date_naissance: [''],
      sexe: ['M'],
      adresse: [''],
      groupe_sanguin: ['O+'],
      numero_securite_sociale: [''],
      personne_a_contacter: [''],

      // SECTION B - ADMISSION
      date_entree: [defaultDateTime, [Validators.required]],
      priorite: ['NORMAL', [Validators.required]],
      motif: ['', [Validators.required, Validators.minLength(3)]],
      symptomes: [''],
      diagnostic_provisoire: [''],
      service_nom: [''],
      lit: [null],
      observations_initiales: [''],

      // SECTION C - ANTÉCÉDENTS ET TRAITEMENTS
      antecedents: [''],
      allergies: [''],
      traitements_en_cours: [''],
      notes_soins: ['']
    });

    this.updatePatientValidators();
  }

  private updatePatientValidators(): void {
    const isExistant = this.patientMode() === 'existant';
    const nomCtrl = this.admissionForm.get('nom');
    const prenomCtrl = this.admissionForm.get('prenom');
    const telCtrl = this.admissionForm.get('telephone');
    const patIdCtrl = this.admissionForm.get('patient_id');

    if (isExistant) {
      patIdCtrl?.setValidators([Validators.required]);
      nomCtrl?.clearValidators();
      prenomCtrl?.clearValidators();
      telCtrl?.clearValidators();
    } else {
      patIdCtrl?.clearValidators();
      nomCtrl?.setValidators([Validators.required]);
      prenomCtrl?.setValidators([Validators.required]);
      telCtrl?.setValidators([Validators.required, Validators.pattern(/^[0-9+() -]{6,20}$/)]);
    }

    nomCtrl?.updateValueAndValidity();
    prenomCtrl?.updateValueAndValidity();
    telCtrl?.updateValueAndValidity();
    patIdCtrl?.updateValueAndValidity();
  }

  setPatientMode(mode: 'existant' | 'nouveau'): void {
    this.patientMode.set(mode);
    this.updatePatientValidators();
    this.errorMessage.set(null);
  }

  private loadPrerequisites(): void {
    this.isLoading.set(true);

    // Charger les lits disponibles
    this.doctorService.getAvailableBeds().subscribe({
      next: (beds) => this.availableBeds.set(beds),
      error: () => this.availableBeds.set([])
    });

    // Charger la liste des services hospitaliers
    this.doctorService.getServicesList().subscribe({
      next: (services) => {
        this.servicesList.set(services);
        this.isLoading.set(false);
      },
      error: () => {
        this.servicesList.set([]);
        this.isLoading.set(false);
      }
    });
  }

  private checkQueryParams(): void {
    this.route.queryParams.subscribe(params => {
      const patientId = params['patient_id'];
      if (patientId) {
        this.setPatientMode('existant');
        this.loadPatientById(+patientId);
      }
    });
  }

  // Recherche temps réel / multi-critères
  onSearchInput(event: Event): void {
    const input = (event.target as HTMLInputElement).value;
    this.patientQuery.set(input);
    if (!input.trim() || input.trim().length < 2) {
      this.patientSearchResults.set([]);
      return;
    }
    this.triggerSearch(input.trim());
  }

  triggerSearch(query: string): void {
    this.isSearching.set(true);
    this.doctorService.searchPatients(query).subscribe({
      next: (results) => {
        this.patientSearchResults.set(results);
        this.isSearching.set(false);
      },
      error: () => {
        this.patientSearchResults.set([]);
        this.isSearching.set(false);
      }
    });
  }

  selectPatient(p: DoctorPatientDto): void {
    this.selectedPatient.set(p);
    this.admissionForm.patchValue({
      patient_id: p.id_patient || p.idPatient
    });
    this.patientSearchResults.set([]);
    this.patientQuery.set('');
    this.errorMessage.set(null);
  }

  clearSelectedPatient(): void {
    this.selectedPatient.set(null);
    this.admissionForm.patchValue({
      patient_id: null
    });
  }

  private loadPatientById(id: number): void {
    this.isSearching.set(true);
    this.doctorService.searchPatients(id.toString()).subscribe({
      next: (list) => {
        const found = list.find(p => (p.id_patient || p.idPatient) === id) || list[0];
        if (found) {
          this.selectPatient(found);
        }
        this.isSearching.set(false);
      },
      error: () => {
        this.isSearching.set(false);
      }
    });
  }

  selectPriorite(p: PrioriteAdmission): void {
    this.admissionForm.patchValue({ priorite: p });
  }

  onSubmit(): void {
    this.errorMessage.set(null);

    if (this.patientMode() === 'existant' && !this.selectedPatient()) {
      this.errorMessage.set('Veuillez rechercher et sélectionner un patient existant, ou basculer en mode « Nouveau patient ».');
      return;
    }

    if (this.admissionForm.invalid) {
      this.admissionForm.markAllAsTouched();
      this.errorMessage.set('Veuillez renseigner tous les champs obligatoires du formulaire (marqués d’un astérisque rouge).');
      return;
    }

    const formVal = this.admissionForm.value;
    const isNouveau = this.patientMode() === 'nouveau';

    // Construction du payload selon les conventions du backend DRF
    const payload: CreateHospitalisationDto = {
      motif: formVal.motif.trim(),
      date_entree: formVal.date_entree,
      statut: 'EN_COURS',
      lit: formVal.lit ? +formVal.lit : null,
      priorite: formVal.priorite || 'NORMAL',
      symptomes: formVal.symptomes?.trim() || '',
      diagnostic_provisoire: formVal.diagnostic_provisoire?.trim() || '',
      service_nom: formVal.service_nom || '',
      antecedents: formVal.antecedents?.trim() || '',
      allergies: formVal.allergies?.trim() || '',
      traitements_en_cours: formVal.traitements_en_cours?.trim() || '',
      observation: [
        formVal.observations_initiales?.trim(),
        formVal.notes_soins?.trim() ? `[Notes de prise en charge]: ${formVal.notes_soins.trim()}` : ''
      ].filter(Boolean).join('\n\n')
    };

    if (isNouveau) {
      payload.nouveau_patient = true;
      payload.nom = formVal.nom.trim();
      payload.prenom = formVal.prenom.trim();
      payload.telephone = formVal.telephone.trim();
      payload.email = formVal.email?.trim() || undefined;
      payload.date_naissance = formVal.date_naissance || null;
      payload.sexe = formVal.sexe || 'M';
      payload.adresse = formVal.adresse?.trim() || '';
      payload.groupe_sanguin = formVal.groupe_sanguin || 'O+';
      payload.numero_securite_sociale = formVal.numero_securite_sociale?.trim() || '';
      payload.personne_a_contacter = formVal.personne_a_contacter?.trim() || '';
    } else {
      payload.nouveau_patient = false;
      payload.patient = this.selectedPatient()?.id_patient || this.selectedPatient()?.idPatient;
    }

    this.isSubmitting.set(true);

    this.doctorService.admitPatient(payload).subscribe({
      next: (response) => {
        this.isSubmitting.set(false);
        this.confirmationData.set(response);
        window.scrollTo({ top: 0, behavior: 'smooth' });
      },
      error: (err) => {
        this.isSubmitting.set(false);
        const errDetail = err.error?.detail || err.error?.error || (typeof err.error === 'string' ? err.error : null);
        const fieldErrors = err.error && typeof err.error === 'object' && !err.error.error
          ? Object.entries(err.error).map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`).join(' | ')
          : null;

        this.errorMessage.set(
          errDetail || fieldErrors || "Une erreur est survenue lors de l'enregistrement de l'admission. Veuillez vérifier les informations saisies."
        );
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    });
  }

  resetForm(): void {
    this.confirmationData.set(null);
    this.selectedPatient.set(null);
    this.patientQuery.set('');
    this.patientSearchResults.set([]);
    this.errorMessage.set(null);
    this.initForm();
    this.setPatientMode('existant');
    this.loadPrerequisites();
  }

  navigateToPatientFolder(patientId?: number): void {
    if (patientId) {
      this.router.navigate(['/medecin/patients', patientId]);
    }
  }

  navigateToAdmissionDetail(admissionId?: number): void {
    if (admissionId) {
      this.router.navigate(['/medecin/admissions', admissionId]);
    } else {
      this.router.navigate(['/medecin/hospitalisations']);
    }
  }
}

