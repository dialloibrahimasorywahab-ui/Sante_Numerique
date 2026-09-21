import { Component, inject, signal, computed, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { DoctorService } from '../../services/doctor.service';
import { calculateAge as calculateSharedAge } from '../../../../shared/utils';
import { DoctorPatientDto, CreatePatientDto } from '../../models/doctor.models';

@Component({
  selector: 'app-doctor-patients',
  standalone: true,
  imports: [CommonModule, RouterModule, RouterLink, FormsModule],
  templateUrl: './doctor-patients.component.html',
  styleUrl: './doctor-patients.component.scss'
})
export class DoctorPatientsComponent implements OnInit {
  private doctorService = inject(DoctorService);

  isLoading = signal<boolean>(true);
  errorMessage = signal<string | null>(null);

  patients = signal<DoctorPatientDto[]>([]);
  searchQuery = signal<string>('');

  currentPage = signal<number>(1);
  pageSize = 10;

  // Modale de création de patient
  isCreateModalOpen = signal<boolean>(false);
  isSubmitting = signal<boolean>(false);
  formError = signal<string | null>(null);
  successNotification = signal<string | null>(null);
  showPassword = signal<boolean>(false);

  newPatient: {
    nom: string;
    prenom: string;
    email: string;
    telephone: string;
    dateNaissance: string;
    sexe: 'M' | 'F' | '';
    groupeSanguin: string;
    numeroSecuriteSociale: string;
    adresse: string;
    personneAContacter: string;
    login: string;
    motDePasse: string;
  } = {
    nom: '',
    prenom: '',
    email: '',
    telephone: '',
    dateNaissance: '',
    sexe: 'M',
    groupeSanguin: 'O+',
    numeroSecuriteSociale: '',
    adresse: '',
    personneAContacter: '',
    login: '',
    motDePasse: '',
    autoLogin: true
  };

  ngOnInit(): void {
    this.loadPatients();
  }

  loadPatients(): void {
    this.isLoading.set(true);
    this.errorMessage.set(null);

    this.doctorService.getPatients(1, '').subscribe({
      next: (res) => {
        this.patients.set(res.results || []);
        this.isLoading.set(false);
      },
      error: () => {
        this.errorMessage.set('Impossible de charger les dossiers patients.');
        this.isLoading.set(false);
      }
    });
  }

  openCreateModal(): void {
    this.formError.set(null);
    this.newPatient = {
      nom: '',
      prenom: '',
      email: '',
      telephone: '',
      dateNaissance: '',
      sexe: 'M',
      groupeSanguin: 'O+',
      numeroSecuriteSociale: '',
      adresse: '',
      personneAContacter: '',
      login: '',
      motDePasse: '',
      autoLogin: true
    };
    this.showPassword.set(false);
    this.isCreateModalOpen.set(true);
  }

  closeCreateModal(): void {
    if (this.isSubmitting()) return;
    this.isCreateModalOpen.set(false);
    this.formError.set(null);
  }

  onNameOrEmailChange(): void {
    if (this.newPatient.autoLogin) {
      const p = (this.newPatient.prenom || '').trim().toLowerCase().replace(/[^a-z0-9]/g, '');
      const n = (this.newPatient.nom || '').trim().toLowerCase().replace(/[^a-z0-9]/g, '');
      if (p && n) {
        // Première lettre prénom + nom, plafonné à 6 caractères max
        this.newPatient.login = (p[0] + n).slice(0, 6);
      } else if (n) {
        this.newPatient.login = n.slice(0, 6);
      } else if (p) {
        this.newPatient.login = p.slice(0, 6);
      } else if (this.newPatient.email && this.newPatient.email.includes('@')) {
        const prefix = this.newPatient.email.split('@')[0].toLowerCase().replace(/[^a-z0-9]/g, '');
        this.newPatient.login = prefix.slice(0, 6);
      }
    }
  }

  submitCreatePatient(): void {
    this.formError.set(null);

    // Validation des champs obligatoires
    const nom = (this.newPatient.nom || '').trim();
    const prenom = (this.newPatient.prenom || '').trim();
    const email = (this.newPatient.email || '').trim();
    const telephone = (this.newPatient.telephone || '').trim();
    const login = (this.newPatient.login || '').trim().toLowerCase();
    const motDePasse = this.newPatient.motDePasse || '';

    if (!nom || !prenom) {
      this.formError.set('Veuillez saisir le nom et le prénom du patient.');
      return;
    }

    if (!this.newPatient.sexe) {
      this.formError.set('Veuillez sélectionner le sexe du patient.');
      return;
    }

    if (!email) {
      this.formError.set("L'adresse email est requise.");
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      this.formError.set("Format d'adresse email invalide.");
      return;
    }

    if (!telephone) {
      this.formError.set('Le numéro de téléphone est requis.');
      return;
    }

    if (!login) {
      this.formError.set("L'identifiant de connexion (login) est obligatoire.");
      return;
    }

    if (login.length > 6) {
      this.formError.set("L'identifiant de connexion (login) ne doit pas dépasser 6 caractères.");
      return;
    }

    if (!motDePasse) {
      this.formError.set('Veuillez saisir le mot de passe de connexion.');
      return;
    }

    if (motDePasse.length < 6) {
      this.formError.set('Le mot de passe doit comporter au moins 6 caractères.');
      return;
    }

    this.isSubmitting.set(true);

    const payload: CreatePatientDto = {
      nom,
      prenom,
      email,
      telephone,
      sexe: this.newPatient.sexe || 'M',
      dateNaissance: this.newPatient.dateNaissance || null,
      date_naissance: this.newPatient.dateNaissance || null,
      groupeSanguin: this.newPatient.groupeSanguin || 'O+',
      groupe_sanguin: this.newPatient.groupeSanguin || 'O+',
      numeroSecuriteSociale: (this.newPatient.numeroSecuriteSociale || '').trim() || null,
      numero_securite_sociale: (this.newPatient.numeroSecuriteSociale || '').trim() || null,
      adresse: (this.newPatient.adresse || '').trim() || undefined,
      personneAContacter: (this.newPatient.personneAContacter || '').trim() || null,
      personne_a_contacter: (this.newPatient.personneAContacter || '').trim() || null,
      login: login.slice(0, 6),
      motDePasse: motDePasse,
      mot_de_passe: motDePasse
    };

    this.doctorService.createPatient(payload).subscribe({
      next: (created) => {
        this.isSubmitting.set(false);
        this.isCreateModalOpen.set(false);

        // Ajout du nouveau patient en tête de liste
        this.patients.update(list => [created, ...list]);
        this.currentPage.set(1);

        const patientName = `${created.prenom || prenom} ${created.nom || nom}`;
        this.successNotification.set(`Le patient ${patientName} a été enregistré avec succès dans votre base hospitalière.`);

        // Auto-dissiper le toast après 6 secondes
        setTimeout(() => {
          this.successNotification.set(null);
        }, 6000);
      },
      error: (err) => {
        this.isSubmitting.set(false);
        if (err.error) {
          if (typeof err.error === 'string') {
            this.formError.set(err.error);
          } else if (err.error.error) {
            this.formError.set(err.error.error);
          } else if (err.error.detail) {
            this.formError.set(err.error.detail);
          } else {
            const firstKey = Object.keys(err.error)[0];
            const msg = Array.isArray(err.error[firstKey]) ? err.error[firstKey][0] : err.error[firstKey];
            this.formError.set(`${firstKey} : ${msg}`);
          }
        } else {
          this.formError.set("Une erreur est survenue lors de l'enregistrement du patient.");
        }
      }
    });
  }

  filteredPatients = computed(() => {
    let list = this.patients();
    const query = this.searchQuery().trim().toLowerCase();
    if (!query) return list;

    return list.filter(p => {
      const nom = (p.nom || '').toLowerCase();
      const prenom = (p.prenom || '').toLowerCase();
      const tel = (p.telephone || '').toLowerCase();
      const email = (p.email || '').toLowerCase();
      const secu = (p.numero_securite_sociale || p.numeroSecuriteSociale || '').toLowerCase();
      const id = String(p.id_patient || p.idPatient || '');
      return nom.includes(query) || prenom.includes(query) || tel.includes(query) || email.includes(query) || secu.includes(query) || id.includes(query);
    });
  });

  paginatedPatients = computed(() => {
    const list = this.filteredPatients();
    const start = (this.currentPage() - 1) * this.pageSize;
    return list.slice(start, start + this.pageSize);
  });

  totalPages = computed(() => {
    return Math.ceil(this.filteredPatients().length / this.pageSize) || 1;
  });

  setPage(p: number): void {
    if (p >= 1 && p <= this.totalPages()) {
      this.currentPage.set(p);
    }
  }

  calculateAge(dateStr?: string | null): string {
    const age = calculateSharedAge(dateStr, 'Non renseigné');
    return typeof age === 'number' ? `${age} ans` : age;
  }
}

