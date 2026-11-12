import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, RouterLink } from '@angular/router';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { DoctorService } from '../../services/doctor.service';
import {
  DoctorHospitalisationDto,
  CreateHospitalisationDto,
  AvailableBedDto,
  DoctorPatientDto
} from '../../models/doctor.models';
import { AuthService } from '../../../../core/services/auth.service';

@Component({
  selector: 'app-doctor-hospitalisations',
  standalone: true,
  imports: [CommonModule, RouterModule, RouterLink, FormsModule, ReactiveFormsModule],
  templateUrl: './doctor-hospitalisations.component.html',
  styleUrl: './doctor-hospitalisations.component.scss'
})
export class DoctorHospitalisationsComponent implements OnInit {
  private doctorService = inject(DoctorService);
  private authService = inject(AuthService);
  private fb = inject(FormBuilder);

  // Signaux d'état
  isLoading = signal<boolean>(true);
  isSubmitting = signal<boolean>(false);
  hospitalisations = signal<DoctorHospitalisationDto[]>([]);
  availableBeds = signal<AvailableBedDto[]>([]);
  existingPatients = signal<DoctorPatientDto[]>([]);
  filteredPatients = signal<DoctorPatientDto[]>([]);

  // Filtres et recherche
  activeStatut = signal<string>('');
  searchTerm = signal<string>('');
  patientSearchTerm = signal<string>('');

  // Modales
  isAdmissionModalOpen = signal<boolean>(false);
  isDischargeModalOpen = signal<boolean>(false);
  selectedHospForDischarge = signal<DoctorHospitalisationDto | null>(null);

  // Message de succès / alerte nouveau compte
  createdAccountSuccess = signal<{
    login: string;
    email: string;
    nom: string;
    prenom: string;
    motDePasse: string;
  } | null>(null);
  feedbackMessage = signal<{ type: 'success' | 'error'; text: string } | null>(null);

  // Formulaire d'admission
  admissionMode = signal<'existant' | 'nouveau'>('existant');
  admissionForm!: FormGroup;
  dischargeForm!: FormGroup;

  // Options de statut
  readonly statusFilters = [
    { label: 'Toutes les admissions', value: '' },
    { label: 'Hospitalisations en cours', value: 'EN_COURS' },
    { label: 'Programmées', value: 'PROGRAMMEE' },
    { label: 'Terminées (Sorties)', value: 'TERMINEE' },
  ];

  // Statistiques calculées
  stats = computed(() => {
    const list = this.hospitalisations();
    const enCours = list.filter(h => h.statut === 'EN_COURS').length;
    const terminees = list.filter(h => h.statut === 'TERMINEE').length;
    const programmees = list.filter(h => h.statut === 'PROGRAMMEE').length;
    const litsDispos = this.availableBeds().length;

    return {
      total: list.length,
      enCours,
      terminees,
      programmees,
      litsDispos
    };
  });

  ngOnInit(): void {
    this.initForms();
    this.loadData();
  }

  private initForms(): void {
    const now = new Date();
    const defaultDateTime = new Date(now.getTime() - now.getTimezoneOffset() * 60000)
      .toISOString()
      .slice(0, 16);

    this.admissionForm = this.fb.group({
      // Patient existant
      patient: [null],
      // Nouveau patient
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
      // Hospitalisation
      lit: [null, [Validators.required]],
      date_entree: [defaultDateTime, [Validators.required]],
      motif: ['', [Validators.required]],
      statut: ['EN_COURS'],
      observation: ['']
    });

    this.dischargeForm = this.fb.group({
      date_sortie: [defaultDateTime, [Validators.required]],
      observation: ['', [Validators.required]]
    });
  }

  loadData(): void {
    this.isLoading.set(true);
    this.doctorService.getHospitalisations(1, this.activeStatut(), this.searchTerm()).subscribe({
      next: (res) => {
        this.hospitalisations.set(res.results || []);
        this.isLoading.set(false);
      },
      error: () => {
        this.hospitalisations.set([]);
        this.isLoading.set(false);
      }
    });

    // Charger les lits disponibles
    this.doctorService.getAvailableBeds().subscribe({
      next: (beds) => this.availableBeds.set(beds),
      error: () => this.availableBeds.set([])
    });

    // Charger les patients pour l'autocomplétion
    this.doctorService.getPatients(1, '').subscribe({
      next: (res) => {
        const list = res.results || [];
        this.existingPatients.set(list);
        this.filteredPatients.set(list.slice(0, 20));
      }
    });
  }

  filterPatientList(term: string): void {
    this.patientSearchTerm.set(term);
    if (!term.trim()) {
      this.filteredPatients.set(this.existingPatients().slice(0, 20));
      return;
    }
    const clean = term.toLowerCase().trim();
    const filtered = this.existingPatients().filter(p => {
      const nom = (p.nom || '').toLowerCase();
      const prenom = (p.prenom || '').toLowerCase();
      const tel = (p.telephone || '').toLowerCase();
      return nom.includes(clean) || prenom.includes(clean) || tel.includes(clean);
    });
    this.filteredPatients.set(filtered.slice(0, 20));
  }

  setAdmissionMode(mode: 'existant' | 'nouveau'): void {
    this.admissionMode.set(mode);
    if (mode === 'existant') {
      this.admissionForm.get('patient')?.setValidators([Validators.required]);
      this.admissionForm.get('nom')?.clearValidators();
      this.admissionForm.get('prenom')?.clearValidators();
      this.admissionForm.get('telephone')?.clearValidators();
    } else {
      this.admissionForm.get('patient')?.clearValidators();
      this.admissionForm.get('nom')?.setValidators([Validators.required]);
      this.admissionForm.get('prenom')?.setValidators([Validators.required]);
      this.admissionForm.get('telephone')?.setValidators([Validators.required]);
    }
    this.admissionForm.get('patient')?.updateValueAndValidity();
    this.admissionForm.get('nom')?.updateValueAndValidity();
    this.admissionForm.get('prenom')?.updateValueAndValidity();
    this.admissionForm.get('telephone')?.updateValueAndValidity();
  }

  openAdmissionModal(): void {
    this.createdAccountSuccess.set(null);
    this.feedbackMessage.set(null);
    this.initForms();
    this.setAdmissionMode('existant');
    this.isAdmissionModalOpen.set(true);
    // Rafraîchir les lits libres
    this.doctorService.getAvailableBeds().subscribe({
      next: (beds) => this.availableBeds.set(beds)
    });
  }

  closeAdmissionModal(): void {
    this.isAdmissionModalOpen.set(false);
    this.admissionForm.reset();
  }

  submitAdmission(): void {
    if (this.admissionForm.invalid) {
      this.admissionForm.markAllAsTouched();
      return;
    }

    this.isSubmitting.set(true);
    this.feedbackMessage.set(null);

    const val = this.admissionForm.value;
    const isNouveau = this.admissionMode() === 'nouveau';

    const payload: CreateHospitalisationDto = {
      lit: +val.lit,
      date_entree: val.date_entree,
      motif: val.motif,
      statut: val.statut || 'EN_COURS',
      observation: val.observation || '',
      nouveau_patient: isNouveau
    };

    if (isNouveau) {
      payload.nom = val.nom;
      payload.prenom = val.prenom;
      payload.telephone = val.telephone;
      payload.email = val.email || undefined;
      payload.date_naissance = val.date_naissance || null;
      payload.sexe = val.sexe || 'M';
      payload.adresse = val.adresse || '';
      payload.groupe_sanguin = val.groupe_sanguin || 'O+';
      payload.numero_securite_sociale = val.numero_securite_sociale || undefined;
      payload.personne_a_contacter = val.personne_a_contacter || undefined;
    } else {
      payload.patient = +val.patient;
    }

    this.doctorService.admitPatient(payload).subscribe({
      next: (res) => {
        this.isSubmitting.set(false);
        if (res.nouveau_patient_cree && res.patient_identifiants) {
          this.createdAccountSuccess.set({
            login: res.patient_identifiants.login,
            email: res.patient_identifiants.email,
            nom: res.patient_identifiants.nom || val.nom,
            prenom: res.patient_identifiants.prenom || val.prenom,
            motDePasse: res.patient_identifiants.mot_de_passe_initial || 'Securite2026!'
          });
        } else {
          this.feedbackMessage.set({
            type: 'success',
            text: 'Patient admis avec succès. Le lit a été immédiatement réservé et le suivi est ouvert.'
          });
          setTimeout(() => {
            this.closeAdmissionModal();
          }, 1400);
        }
        this.loadData();
      },
      error: (err) => {
        this.isSubmitting.set(false);
        const errMsg = err?.error?.detail || err?.error?.error || 'Erreur lors de l\'enregistrement de l\'admission.';
        this.feedbackMessage.set({ type: 'error', text: errMsg });
      }
    });
  }

  // Clôture d'hospitalisation / Sortie
  openDischargeModal(hosp: DoctorHospitalisationDto): void {
    this.selectedHospForDischarge.set(hosp);
    const now = new Date();
    const defaultDateTime = new Date(now.getTime() - now.getTimezoneOffset() * 60000)
      .toISOString()
      .slice(0, 16);

    this.dischargeForm.patchValue({
      date_sortie: defaultDateTime,
      observation: 'Traitement hospitalier terminé avec succès. Patient orienté vers soins de suite à domicile.'
    });
    this.isDischargeModalOpen.set(true);
  }

  closeDischargeModal(): void {
    this.isDischargeModalOpen.set(false);
    this.selectedHospForDischarge.set(null);
  }

  submitDischarge(): void {
    const hosp = this.selectedHospForDischarge();
    if (!hosp) return;

    if (this.dischargeForm.invalid) {
      this.dischargeForm.markAllAsTouched();
      return;
    }

    this.isSubmitting.set(true);
    const formVal = this.dischargeForm.value;

    this.doctorService.dischargePatient(hosp.id, {
      observation: formVal.observation
    }).subscribe({
      next: () => {
        this.isSubmitting.set(false);
        this.closeDischargeModal();
        this.loadData();
      },
      error: (err) => {
        this.isSubmitting.set(false);
        const msg = err?.error?.detail || err?.error?.error || 'Erreur lors de la clôture de l\'hospitalisation.';
        alert(msg);
      }
    });
  }

  // Filtrage par statut
  onStatusChange(statut: string): void {
    this.activeStatut.set(statut);
    this.loadData();
  }

  // Recherche textuelle
  onSearch(): void {
    this.loadData();
  }

  clearSearch(): void {
    this.searchTerm.set('');
    this.loadData();
  }

  // Helpers pour les templates typés et sécurisés
  getPatientName(hosp: DoctorHospitalisationDto): string {
    if (hosp.patient_nom) return hosp.patient_nom;
    if (hosp.patientNom) return hosp.patientNom;
    if (hosp.patient_details?.prenom || hosp.patient_details?.nom) {
      return `${hosp.patient_details.prenom || ''} ${hosp.patient_details.nom || ''}`.trim();
    }
    return `Patient #${hosp.patient}`;
  }

  getPatientPhone(hosp: DoctorHospitalisationDto): string {
    return hosp.patient_details?.telephone || 'Non renseigné';
  }

  getBedRoom(hosp: DoctorHospitalisationDto): string {
    const ch = hosp.chambre_numero || hosp.chambreNumero;
    const lit = hosp.lit_numero || hosp.litNumero;
    const bat = hosp.batiment_nom || hosp.batimentNom;

    let parts: string[] = [];
    if (bat) parts.push(bat);
    if (ch) parts.push(ch);
    if (lit) parts.push(lit);

    return parts.length > 0 ? parts.join(' — ') : 'Lit non assigné';
  }

  getDoctorName(hosp: DoctorHospitalisationDto): string {
    if (hosp.medecin_nom) return hosp.medecin_nom;
    if (hosp.medecinNom) return hosp.medecinNom;
    if (hosp.medecin_details?.prenom || hosp.medecin_details?.nom) {
      return `Dr. ${hosp.medecin_details.prenom || ''} ${hosp.medecin_details.nom || ''}`.trim();
    }
    return 'Médecin assigné';
  }

  getStatusBadgeClass(statut: string): string {
    switch (statut) {
      case 'EN_COURS':
        return 'badge-status-encours';
      case 'PROGRAMMEE':
        return 'badge-status-programme';
      case 'TERMINEE':
        return 'badge-status-terminee';
      case 'ANNULEE':
        return 'badge-status-annulee';
      default:
        return 'badge-status-default';
    }
  }

  getStatusLabel(statut: string): string {
    switch (statut) {
      case 'EN_COURS':
        return 'En cours (Hospitalisé)';
      case 'PROGRAMMEE':
        return 'Programmée';
      case 'TERMINEE':
        return 'Terminée (Sortie)';
      case 'ANNULEE':
        return 'Annulée';
      default:
        return statut;
    }
  }
}

