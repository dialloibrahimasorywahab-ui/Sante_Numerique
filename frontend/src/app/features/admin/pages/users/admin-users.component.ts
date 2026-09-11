import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { AdminService } from '../../services/admin.service';
import { formatDate as formatSharedDate } from '../../../../shared/utils';

export type UserTypeTab = 'patients' | 'medecins' | 'personnel';

@Component({
  selector: 'app-admin-users',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './admin-users.component.html',
  styleUrls: ['./admin-users.component.scss']
})
export class AdminUsersComponent implements OnInit {
  private adminService = inject(AdminService);
  private route = inject(ActivatedRoute);

  activeTab = signal<UserTypeTab>('patients');
  searchQuery = signal<string>('');
  currentPage = signal<number>(1);
  pageSize = 10;

  isLoading = signal<boolean>(false);
  isActionLoading = signal<number | null>(null);
  errorMessage = signal<string | null>(null);
  toastMessage = signal<{ type: 'success' | 'error'; text: string } | null>(null);

  // Modals state
  showPatientModal = signal<boolean>(false);
  showMedecinModal = signal<boolean>(false);
  showPersonnelModal = signal<boolean>(false);
  isSubmitting = signal<boolean>(false);
  formError = signal<string | null>(null);

  // Forms data
  patientForm = {
    nom: '',
    prenom: '',
    email: '',
    telephone: '',
    login: '',
    motDePasse: '',
    dateNaissance: '',
    sexe: 'M',
    groupeSanguin: 'O+',
    numeroSecuriteSociale: '',
    adresse: '',
    personneAContacter: ''
  };

  medecinForm = {
    nom: '',
    prenom: '',
    email: '',
    telephone: '',
    login: '',
    motDePasse: '',
    specialite: 'MEDECINE_GENERALE',
    matricule: '',
    numeroOrdre: '',
    bureau: 'Bureau 101',
    telephonePro: '',
    emailPro: ''
  };

  personnelForm = {
    nom: '',
    prenom: '',
    email: '',
    telephone: '',
    login: '',
    motDePasse: '',
    matricule: '',
    typePersonnel: 'INFIRMIER',
    poste: 'Infirmier Diplômé d\'État',
    serviceHopital: 'Pôle Général',
    telephonePro: '',
    emailPro: ''
  };

  items = signal<any[]>([]);
  totalCount = signal<number>(0);

  totalPages = computed(() => Math.ceil(this.totalCount() / this.pageSize) || 1);

  ngOnInit(): void {
    this.route.data.subscribe(data => {
      if (data['userType']) {
        this.activeTab.set(data['userType']);
      }
      this.loadData();
    });
  }

  setTab(tab: UserTypeTab): void {
    this.activeTab.set(tab);
    this.currentPage.set(1);
    this.searchQuery.set('');
    this.loadData();
  }

  onSearchChange(val: string): void {
    this.searchQuery.set(val);
    this.currentPage.set(1);
    this.loadData();
  }

  setPage(p: number): void {
    if (p < 1 || p > this.totalPages()) return;
    this.currentPage.set(p);
    this.loadData();
  }

  loadData(): void {
    this.isLoading.set(true);
    this.errorMessage.set(null);

    const tab = this.activeTab();
    let resource = 'patients';
    if (tab === 'medecins') resource = 'medecins';
    if (tab === 'personnel') resource = 'personnel';

    this.adminService.getEntityList(resource, this.currentPage(), this.searchQuery(), {
      page_size: this.pageSize,
      all: 'true'
    }).subscribe({
      next: (res) => {
        this.items.set(res.results || []);
        this.totalCount.set(res.count || (res.results ? res.results.length : 0));
        this.isLoading.set(false);
      },
      error: () => {
        this.errorMessage.set('Impossible de charger les données pour cette section.');
        this.isLoading.set(false);
      }
    });
  }

  // --- MODALS CONTROLLERS ---
  openModal(type: UserTypeTab): void {
    this.formError.set(null);
    if (type === 'patients') {
      this.resetPatientForm();
      this.showPatientModal.set(true);
    } else if (type === 'medecins') {
      this.resetMedecinForm();
      this.showMedecinModal.set(true);
    } else if (type === 'personnel') {
      this.resetPersonnelForm();
      this.showPersonnelModal.set(true);
    }
  }

  closeModals(): void {
    this.showPatientModal.set(false);
    this.showMedecinModal.set(false);
    this.showPersonnelModal.set(false);
    this.formError.set(null);
    this.isSubmitting.set(false);
  }

  submitPatient(): void {
    if (!this.patientForm.nom || !this.patientForm.prenom || !this.patientForm.email || !this.patientForm.telephone) {
      this.formError.set('Veuillez renseigner tous les champs obligatoires (*).');
      return;
    }

    this.isSubmitting.set(true);
    this.formError.set(null);

    const payload = {
      nom: this.patientForm.nom.trim(),
      prenom: this.patientForm.prenom.trim(),
      email: this.patientForm.email.trim(),
      telephone: this.patientForm.telephone.trim(),
      login: this.patientForm.login?.trim() || this.patientForm.email.split('@')[0],
      motDePasse: this.patientForm.motDePasse || 'PatientPass123!',
      date_naissance: this.patientForm.dateNaissance || null,
      sexe: this.patientForm.sexe,
      groupe_sanguin: this.patientForm.groupeSanguin,
      numero_securite_sociale: this.patientForm.numeroSecuriteSociale?.trim() || null,
      adresse: this.patientForm.adresse?.trim() || '',
      personne_a_contacter: this.patientForm.personneAContacter?.trim() || ''
    };

    this.adminService.createEntity('patients', payload).subscribe({
      next: () => {
        this.isSubmitting.set(false);
        this.closeModals();
        this.showToast('success', `Dossier patient créé avec succès pour ${payload.prenom} ${payload.nom}.`);
        this.loadData();
      },
      error: (err) => {
        this.isSubmitting.set(false);
        const detail = err.error?.error || err.error?.message || (typeof err.error === 'string' ? err.error : 'Erreur lors de la création du patient.');
        this.formError.set(detail);
      }
    });
  }

  submitMedecin(): void {
    if (!this.medecinForm.nom || !this.medecinForm.prenom || !this.medecinForm.email || !this.medecinForm.telephone || !this.medecinForm.matricule) {
      this.formError.set('Veuillez renseigner tous les champs obligatoires (*).');
      return;
    }

    this.isSubmitting.set(true);
    this.formError.set(null);

    const payload = {
      nom: this.medecinForm.nom.trim(),
      prenom: this.medecinForm.prenom.trim(),
      email: this.medecinForm.email.trim(),
      telephone: this.medecinForm.telephone.trim(),
      login: this.medecinForm.login?.trim() || this.medecinForm.email.split('@')[0],
      motDePasse: this.medecinForm.motDePasse || 'DocPass123!',
      specialite: this.medecinForm.specialite,
      matricule: this.medecinForm.matricule.trim(),
      numeroOrdre: this.medecinForm.numeroOrdre?.trim() || `CNOM-${Math.floor(10000 + Math.random() * 90000)}`,
      bureau: this.medecinForm.bureau?.trim() || 'Bureau Médical',
      telephonePro: this.medecinForm.telephonePro?.trim() || this.medecinForm.telephone.trim(),
      emailPro: this.medecinForm.emailPro?.trim() || this.medecinForm.email.trim()
    };

    this.adminService.createEntity('medecins', payload).subscribe({
      next: () => {
        this.isSubmitting.set(false);
        this.closeModals();
        this.showToast('success', `Médecin Dr. ${payload.prenom} ${payload.nom} enregistré avec succès.`);
        this.loadData();
      },
      error: (err) => {
        this.isSubmitting.set(false);
        const detail = err.error?.error || err.error?.message || (typeof err.error === 'string' ? err.error : 'Erreur lors de l\'enregistrement du médecin.');
        this.formError.set(detail);
      }
    });
  }

  submitPersonnel(): void {
    if (!this.personnelForm.nom || !this.personnelForm.prenom || !this.personnelForm.email || !this.personnelForm.telephone || !this.personnelForm.matricule) {
      this.formError.set('Veuillez renseigner tous les champs obligatoires (*).');
      return;
    }

    this.isSubmitting.set(true);
    this.formError.set(null);

    const payload = {
      nom: this.personnelForm.nom.trim(),
      prenom: this.personnelForm.prenom.trim(),
      email: this.personnelForm.email.trim(),
      telephone: this.personnelForm.telephone.trim(),
      login: this.personnelForm.login?.trim() || this.personnelForm.email.split('@')[0],
      motDePasse: this.personnelForm.motDePasse || 'StaffPass123!',
      matricule: this.personnelForm.matricule.trim(),
      typePersonnel: this.personnelForm.typePersonnel,
      poste: this.personnelForm.poste?.trim() || 'Personnel Soignant',
      serviceHopital: this.personnelForm.serviceHopital?.trim() || 'Pôle Général',
      telephonePro: this.personnelForm.telephonePro?.trim() || this.personnelForm.telephone.trim(),
      emailPro: this.personnelForm.emailPro?.trim() || this.personnelForm.email.trim()
    };

    this.adminService.createEntity('personnel', payload).subscribe({
      next: () => {
        this.isSubmitting.set(false);
        this.closeModals();
        this.showToast('success', `Membre du personnel ${payload.prenom} ${payload.nom} enregistré avec succès.`);
        this.loadData();
      },
      error: (err) => {
        this.isSubmitting.set(false);
        const detail = err.error?.error || err.error?.message || (typeof err.error === 'string' ? err.error : 'Erreur lors de l\'enregistrement du membre du personnel.');
        this.formError.set(detail);
      }
    });
  }

  // --- SUSPENSION / ACTIVATION ---
  isUserActive(item: any): boolean {
    if (typeof item.actif === 'boolean') return item.actif;
    if (typeof item.id_utilisateur?.actif === 'boolean') return item.id_utilisateur.actif;
    if (typeof item.idUtilisateur?.actif === 'boolean') return item.idUtilisateur.actif;
    return true;
  }

  getUserId(item: any): number | null {
    return item.id_utilisateur?.id_user ||
      item.id_utilisateur?.id ||
      item.idUtilisateur?.id_user ||
      item.idUtilisateur?.id ||
      (typeof item.id_utilisateur === 'number' ? item.id_utilisateur : null) ||
      (typeof item.idUtilisateur === 'number' ? item.idUtilisateur : null) ||
      item.id;
  }

  toggleSuspendUser(item: any): void {
    const userId = this.getUserId(item);
    if (!userId) return;

    const currentlyActive = this.isUserActive(item);
    const targetState = !currentlyActive;
    const itemId = item.id || item.idMedecin || item.id_medecin || item.idPersonnel || item.id_personnel || item.idPatient || item.id_patient;

    this.isActionLoading.set(itemId);

    this.adminService.toggleUserStatus(userId, targetState).subscribe({
      next: () => {
        this.isActionLoading.set(null);
        const actionLabel = targetState ? 'réactivé' : 'suspendu';
        this.showToast('success', `Le compte utilisateur (#${userId}) a été ${actionLabel} avec succès.`);
        this.loadData();
      },
      error: () => {
        this.isActionLoading.set(null);
        this.showToast('error', `Impossible de modifier le statut de l'utilisateur #${userId}.`);
      }
    });
  }

  showToast(type: 'success' | 'error', text: string): void {
    this.toastMessage.set({ type, text });
    setTimeout(() => {
      this.toastMessage.set(null);
    }, 4500);
  }

  formatDate(dateStr: string): string {
    return formatSharedDate(dateStr);
  }

  private resetPatientForm(): void {
    this.patientForm = {
      nom: '',
      prenom: '',
      email: '',
      telephone: '',
      login: '',
      motDePasse: '',
      dateNaissance: '',
      sexe: 'M',
      groupeSanguin: 'O+',
      numeroSecuriteSociale: '',
      adresse: '',
      personneAContacter: ''
    };
  }

  private resetMedecinForm(): void {
    this.medecinForm = {
      nom: '',
      prenom: '',
      email: '',
      telephone: '',
      login: '',
      motDePasse: '',
      specialite: 'MEDECINE_GENERALE',
      matricule: `MED-${Math.floor(1000 + Math.random() * 9000)}`,
      numeroOrdre: `CNOM-${Math.floor(10000 + Math.random() * 90000)}`,
      bureau: 'Bureau 101',
      telephonePro: '',
      emailPro: ''
    };
  }

  private resetPersonnelForm(): void {
    this.personnelForm = {
      nom: '',
      prenom: '',
      email: '',
      telephone: '',
      login: '',
      motDePasse: '',
      matricule: `STF-${Math.floor(1000 + Math.random() * 9000)}`,
      typePersonnel: 'INFIRMIER',
      poste: 'Infirmier(ère) Diplômé(e) d\'État',
      serviceHopital: 'Pôle Soins Généraux',
      telephonePro: '',
      emailPro: ''
    };
  }
}
