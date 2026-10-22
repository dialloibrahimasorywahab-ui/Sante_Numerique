import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule, ActivatedRoute, Router } from '@angular/router';
import { Subject, debounceTime, distinctUntilChanged } from 'rxjs';
import { ParcoursService } from '../../core/services/parcours.service';
import { AuthService } from '../../core/services/auth.service';
import {
  Sejour,
  DossierSyntheseSejour,
  TransfertPatientDto,
  SortiePatientDto,
  DashboardStats,
  LocalisationPatient,
  MouvementPatient,
} from '../../core/models/parcours.model';

@Component({
  selector: 'app-parcours-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './parcours-dashboard.component.html',
  styleUrls: ['./parcours-dashboard.component.scss'],
})
export class ParcoursDashboardComponent implements OnInit {
  parcoursService = inject(ParcoursService);
  authService = inject(AuthService);
  private route = inject(ActivatedRoute);
  private router = inject(Router);

  // Onglet actif : 'dashboard' | 'localisation' | 'dossier'
  activeTab = signal<'dashboard' | 'localisation' | 'dossier'>('dashboard');

  // Filtres et recherche rapide
  searchQuery = signal<string>('');
  private searchSubject = new Subject<string>();
  selectedStatut = signal<string>('');
  selectedService = signal<string>('');
  filterEstActuelle = signal<boolean>(true);
  bedViewMode = signal<'cards' | 'table'>('cards');
  timelineFilter = signal<'all' | 'visits' | 'nursing' | 'meds' | 'labs'>('all');

  // Données de formulaire de transfert & listes liées
  showTransfertModal = signal<boolean>(false);
  showSortieModal = signal<boolean>(false);
  showEventModal = signal<boolean>(false);
  isSubmitting = signal<boolean>(false);
  feedbackMessage = signal<{ type: 'success' | 'error'; text: string } | null>(null);

  // Données d'infrastructure pour formulaires
  servicesList = signal<any[]>([]);
  batimentsList = signal<any[]>([]);
  chambresList = signal<any[]>([]);
  litsDisponiblesList = signal<any[]>([]);

  // DTOs
  transfertData: TransfertPatientDto = {
    sejour: 0,
    service: 1,
    motif: '',
    commentaire: '',
  };

  sortieData: SortiePatientDto = {
    motifSortie: '',
  };

  newEventData = {
    sejour: 0,
    typeEvenement: 'OBSERVATION',
    titre: '',
    description: '',
    importance: 'INFO',
    constantes: {
      temperature: null as number | null,
      pouls: null as number | null,
      tension: '',
      respiration: null as number | null,
      douleur: null as number | null,
      poids: null as number | null,
    },
  };

  // Rôle de l'utilisateur
  userRole = computed(() => this.authService.currentUser()?.role || '');

  ngOnInit(): void {
    // Configurer le debounce sur la recherche rapide
    this.searchSubject
      .pipe(debounceTime(350), distinctUntilChanged())
      .subscribe((query) => {
        this.searchQuery.set(query);
        this.chargerDonnees();
      });

    // Écouter les queryParams (ex: ?tab=localisation ou ?sejour=12)
    this.route.queryParams.subscribe((params) => {
      if (params['tab'] && ['dashboard', 'localisation', 'dossier'].includes(params['tab'])) {
        this.activeTab.set(params['tab']);
      }
      if (params['sejour']) {
        const id = parseInt(params['sejour'], 10);
        if (!isNaN(id)) {
          this.chargerDossierParId(id);
        }
      }
    });

    this.chargerDonnees();
    this.chargerInfrastructure();
  }

  onSearchInput(value: string): void {
    this.searchSubject.next(value.trim());
  }

  changerOnglet(tab: 'dashboard' | 'localisation' | 'dossier'): void {
    this.activeTab.set(tab);
    if (tab === 'localisation') {
      this.chargerLocalisations();
    } else if (tab === 'dashboard') {
      this.chargerStats();
      this.chargerSejours();
      this.chargerMouvementsRecents();
    }
  }

  chargerDonnees(): void {
    this.chargerStats();
    this.chargerSejours();
    this.chargerLocalisations();
    this.chargerMouvementsRecents();
  }

  chargerStats(): void {
    this.parcoursService.getDashboardStats().subscribe();
  }

  chargerSejours(): void {
    this.parcoursService
      .getSejours({
        search: this.searchQuery(),
        statut: this.selectedStatut() || undefined,
        serviceId: this.selectedService() ? parseInt(this.selectedService(), 10) : undefined,
      })
      .subscribe((res) => {
        if (
          res.results &&
          res.results.length > 0 &&
          !this.parcoursService.activeDossier() &&
          this.activeTab() === 'dossier'
        ) {
          this.selectionnerSejour(res.results[0]);
        }
      });
  }

  chargerLocalisations(): void {
    this.parcoursService
      .getLocalisations({
        serviceId: this.selectedService() ? parseInt(this.selectedService(), 10) : undefined,
        estActuelle: this.filterEstActuelle(),
      })
      .subscribe();
  }

  chargerMouvementsRecents(): void {
    this.parcoursService.getMouvementsRecents(8).subscribe();
  }

  chargerInfrastructure(): void {
    this.parcoursService.getServicesList().subscribe({
      next: (data: any) => {
        const list = Array.isArray(data) ? data : data.results || [];
        this.servicesList.set(list);
      },
    });

    this.parcoursService.getBatimentsList().subscribe({
      next: (data: any) => {
        const list = Array.isArray(data) ? data : data.results || [];
        this.batimentsList.set(list);
      },
    });
  }

  onBatimentChange(batimentId: number | null): void {
    if (!batimentId) {
      this.chambresList.set([]);
      this.litsDisponiblesList.set([]);
      return;
    }
    this.parcoursService.getChambresList(batimentId).subscribe({
      next: (data: any) => {
        const list = Array.isArray(data) ? data : data.results || [];
        this.chambresList.set(list);
      },
    });
  }

  onChambreChange(chambreId: number | null): void {
    if (!chambreId) {
      this.litsDisponiblesList.set([]);
      return;
    }
    this.parcoursService.getLitsDisponibles(chambreId).subscribe({
      next: (data: any) => {
        const list = Array.isArray(data) ? data : data.results || [];
        this.litsDisponiblesList.set(list);
      },
    });
  }

  selectionnerSejour(sejour: Sejour): void {
    this.chargerDossierParId(sejour.idSejour);
    this.activeTab.set('dossier');
  }

  chargerDossierParId(id: number): void {
    this.parcoursService.getDossierSynthese(id).subscribe({
      error: () => {
        this.afficherMessage('error', 'Impossible de charger le dossier sélectionné.');
      },
    });
  }

  // --- ACTIONS TRANSFERT ---
  ouvrirTransfertModal(): void {
    const active = this.parcoursService.activeDossier();
    if (!active) return;
    this.transfertData = {
      sejour: active.sejour.idSejour,
      service: active.sejour.serviceResponsable,
      batiment: null,
      chambre: null,
      lit: null,
      motif: '',
      commentaire: '',
    };
    this.showTransfertModal.set(true);
  }

  validerTransfert(): void {
    if (!this.transfertData.motif) {
      this.afficherMessage('error', 'Le motif du transfert est requis.');
      return;
    }
    this.isSubmitting.set(true);
    this.parcoursService.effectuerTransfert(this.transfertData).subscribe({
      next: () => {
        this.isSubmitting.set(false);
        this.showTransfertModal.set(false);
        this.afficherMessage('success', 'Transfert effectué avec succès.');
        this.chargerDonnees();
      },
      error: (err) => {
        this.isSubmitting.set(false);
        const detail = err.error?.detail || err.error?.lit || 'Erreur lors du transfert.';
        this.afficherMessage('error', detail);
      },
    });
  }

  // --- ACTIONS SORTIE ---
  ouvrirSortieModal(): void {
    this.sortieData = { motifSortie: '' };
    this.showSortieModal.set(true);
  }

  validerSortie(): void {
    const active = this.parcoursService.activeDossier();
    if (!active || !this.sortieData.motifSortie) {
      this.afficherMessage('error', 'Le motif de sortie est obligatoire.');
      return;
    }

    this.isSubmitting.set(true);
    this.parcoursService.cloturerSejour(active.sejour.idSejour, this.sortieData).subscribe({
      next: () => {
        this.isSubmitting.set(false);
        this.showSortieModal.set(false);
        this.afficherMessage('success', 'Sortie définitive enregistrée et lit libéré.');
        this.chargerDonnees();
      },
      error: (err) => {
        this.isSubmitting.set(false);
        const detail = err.error?.detail || 'Erreur lors de la clôture de sortie.';
        this.afficherMessage('error', detail);
      },
    });
  }

  // --- ACTIONS EVENEMENTS ---
  ouvrirEventModal(): void {
    const active = this.parcoursService.activeDossier();
    if (!active) return;
    this.newEventData = {
      sejour: active.sejour.idSejour,
      typeEvenement: 'OBSERVATION',
      titre: '',
      description: '',
      importance: 'INFO',
      constantes: {
        temperature: null,
        pouls: null,
        tension: '',
        respiration: null,
        douleur: null,
        poids: null,
      },
    };
    this.showEventModal.set(true);
  }

  validerEvenement(): void {
    if (!this.newEventData.titre) {
      this.afficherMessage('error', 'Le titre de l’événement est requis.');
      return;
    }
    this.isSubmitting.set(true);
    this.parcoursService.consignerEvenement(this.newEventData).subscribe({
      next: () => {
        this.isSubmitting.set(false);
        this.showEventModal.set(false);
        this.afficherMessage('success', 'Événement consigné dans la timeline.');
      },
      error: (err) => {
        this.isSubmitting.set(false);
        this.afficherMessage('error', err.error?.detail || 'Erreur lors de l’enregistrement.');
      },
    });
  }

  afficherMessage(type: 'success' | 'error', text: string): void {
    this.feedbackMessage.set({ type, text });
    setTimeout(() => {
      this.feedbackMessage.set(null);
    }, 4500);
  }

  getPatientNomComplet(p: any): string {
    if (!p) return 'Patient';
    const prenom = p.prenom || p.id_utilisateur?.prenom || p.idUtilisateur?.prenom || '';
    const nom = p.nom || p.id_utilisateur?.nom || p.idUtilisateur?.nom || '';
    const full = `${prenom} ${nom}`.trim();
    return full || 'Patient';
  }

  getPatientInitials(p: any): string {
    if (!p) return 'PT';
    const prenom = p.prenom || p.id_utilisateur?.prenom || p.idUtilisateur?.prenom || '';
    const nom = p.nom || p.id_utilisateur?.nom || p.idUtilisateur?.nom || '';
    const pI = prenom ? prenom.charAt(0).toUpperCase() : '';
    const nI = nom ? nom.charAt(0).toUpperCase() : '';
    return `${pI}${nI}` || 'PT';
  }

  getPatientAge(dateNaissance?: string | null): string {
    if (!dateNaissance) return '';
    const birth = new Date(dateNaissance);
    if (isNaN(birth.getTime())) return '';
    const today = new Date();
    let age = today.getFullYear() - birth.getFullYear();
    const m = today.getMonth() - birth.getMonth();
    if (m < 0 || (m === 0 && today.getDate() < birth.getDate())) {
      age--;
    }
    return `${age} ans`;
  }

  getSexeBadge(sexe?: string | null): string {
    if (!sexe) return 'Non renseigné';
    if (sexe === 'M' || sexe.toLowerCase() === 'masculin') return 'Homme';
    if (sexe === 'F' || sexe.toLowerCase() === 'feminin') return 'Femme';
    return sexe;
  }
}
