import { Component, OnInit, OnDestroy, inject, signal, computed } from '@angular/core';
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
  LocalisationPatient,
  MouvementPatient,
  EvenementParcours,
} from '../../core/models/parcours.model';

export interface ParcoursStep {
  titre: string;
  heure: string;
  description: string;
  icone: string;
  couleurClass: string;
}

@Component({
  selector: 'app-parcours-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './parcours-dashboard.component.html',
  styleUrls: ['./parcours-dashboard.component.scss'],
})
export class ParcoursDashboardComponent implements OnInit, OnDestroy {
  parcoursService = inject(ParcoursService);
  authService = inject(AuthService);
  private route = inject(ActivatedRoute);
  private router = inject(Router);

  // Sidebar mobile
  sidebarOpen = signal<boolean>(false);

  // Recherche & filtres
  searchQuery = signal<string>('');
  private searchSubject = new Subject<string>();
  selectedStatut = signal<string>('');
  selectedService = signal<string>('');
  showFilters = signal<boolean>(false);

  // Horodatage dynamique
  currentDate = signal<Date>(new Date());
  private clockInterval: any;

  // Patient / séjour sélectionné pour le parcours détaillé
  selectedSejour = signal<Sejour | null>(null);

  // Modales d'actions & synthèse
  showDossierModal = signal<boolean>(false);
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

  // DTOs formulaires
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
  };

  // Date et heure formatées selon la locale française
  formattedDate = computed(() => {
    const d = this.currentDate();
    const formatted = d.toLocaleDateString('fr-FR', {
      weekday: 'long',
      day: 'numeric',
      month: 'long',
      year: 'numeric',
    });
    return formatted.charAt(0).toUpperCase() + formatted.slice(1);
  });

  formattedTime = computed(() => {
    const d = this.currentDate();
    return d.toLocaleTimeString('fr-FR', {
      hour: '2-digit',
      minute: '2-digit',
    });
  });

  // Utilisateur connecté
  currentUser = computed(() => this.authService.currentUser());
  userRole = computed(() => this.currentUser()?.role || '');

  userDisplayName = computed(() => {
    const u = this.currentUser();
    if (!u) return 'Dr. Connecté';
    const prenom = u.prenom || '';
    const nom = u.nom || '';
    if (u.role === 'MEDECIN') {
      return `Dr. ${nom || prenom || 'Praticien'}`;
    }
    return `${prenom} ${nom}`.trim() || u.login || 'Utilisateur';
  });

  userRoleDisplay = computed(() => {
    const r = this.userRole();
    switch (r) {
      case 'MEDECIN': return 'Médecin';
      case 'ADMINISTRATEUR': return 'Administrateur';
      case 'INFIRMIER': return 'Infirmier';
      case 'PATIENT': return 'Patient';
      default: return r || 'Personnel';
    }
  });

  userInitials = computed(() => {
    const u = this.currentUser();
    if (!u) return 'AD';
    const n = (u.nom || '').trim().charAt(0);
    const p = (u.prenom || '').trim().charAt(0);
    return (n + p).toUpperCase() || 'AD';
  });

  isStaffOrAdmin = computed(() => {
    const r = this.userRole();
    return r === 'ADMINISTRATEUR' || r === 'MEDECIN' || r === 'INFIRMIER';
  });

  // Statistiques agrégées
  stats = computed(() => this.parcoursService.dashboardStats());

  totalLits = computed(() => this.stats()?.totalLits ?? 0);
  litsOccupes = computed(() => this.stats()?.litsOccupes ?? 0);
  litsDisponibles = computed(() => this.stats()?.litsDisponibles ?? 0);
  litsIndisponibles = computed(() => {
    const s = this.stats();
    if (!s) return 0;
    if (s.litsIndisponibles !== undefined) return s.litsIndisponibles;
    return Math.max(0, s.totalLits - s.litsOccupes - s.litsDisponibles);
  });

  pourcentageOccupes = computed(() => {
    const total = this.totalLits();
    return total > 0 ? Math.round((this.litsOccupes() / total) * 100) : 0;
  });

  pourcentageDisponibles = computed(() => {
    const total = this.totalLits();
    return total > 0 ? Math.round((this.litsDisponibles() / total) * 100) : 0;
  });

  pourcentageIndisponibles = computed(() => {
    const total = this.totalLits();
    if (total <= 0) return 0;
    return Math.max(0, 100 - this.pourcentageOccupes() - this.pourcentageDisponibles());
  });

  // Segments du donut SVG (rayon = 42, circonférence = 263.89)
  readonly donutCircumference = 263.89;

  donutDashOccupes = computed(() => {
    const total = this.totalLits();
    if (total <= 0) return `0 ${this.donutCircumference}`;
    const len = (this.litsOccupes() / total) * this.donutCircumference;
    return `${len.toFixed(2)} ${(this.donutCircumference - len).toFixed(2)}`;
  });

  donutDashDisponibles = computed(() => {
    const total = this.totalLits();
    if (total <= 0) return `0 ${this.donutCircumference}`;
    const len = (this.litsDisponibles() / total) * this.donutCircumference;
    return `${len.toFixed(2)} ${(this.donutCircumference - len).toFixed(2)}`;
  });

  donutOffsetDisponibles = computed(() => {
    const total = this.totalLits();
    if (total <= 0) return 0;
    const len1 = (this.litsOccupes() / total) * this.donutCircumference;
    return -len1;
  });

  donutDashIndisponibles = computed(() => {
    const total = this.totalLits();
    if (total <= 0) return `0 ${this.donutCircumference}`;
    const len = (this.litsIndisponibles() / total) * this.donutCircumference;
    return `${len.toFixed(2)} ${(this.donutCircumference - len).toFixed(2)}`;
  });

  donutOffsetIndisponibles = computed(() => {
    const total = this.totalLits();
    if (total <= 0) return 0;
    const len1 = (this.litsOccupes() / total) * this.donutCircumference;
    const len2 = (this.litsDisponibles() / total) * this.donutCircumference;
    return -(len1 + len2);
  });

  // Séjours filtrés
  filteredSejours = computed(() => {
    let list = this.parcoursService.sejours();
    const query = this.searchQuery().toLowerCase().trim();
    const statut = this.selectedStatut();
    const srvId = this.selectedService() ? parseInt(this.selectedService(), 10) : null;

    if (srvId && !isNaN(srvId)) {
      list = list.filter(
        (s) =>
          Number(s.serviceResponsable) === srvId ||
          Number(s.serviceDetails?.id) === srvId ||
          Number(s.localisationActuelleInfo?.serviceId) === srvId
      );
    } else if (this.selectedService()) {
      const srvStr = this.selectedService().toLowerCase();
      list = list.filter(
        (s) =>
          s.serviceDetails?.nomService?.toLowerCase() === srvStr ||
          s.localisationActuelleInfo?.serviceNom?.toLowerCase() === srvStr
      );
    }

    if (statut) {
      if (statut === 'TRANSFERE') {
        list = list.filter(
          (s) =>
            s.statut === 'TRANSFERE' ||
            s.statutDisplay?.toLowerCase().includes('transf')
        );
      } else {
        list = list.filter(
          (s) =>
            s.statut === statut ||
            s.statutDisplay?.toLowerCase().includes(statut.toLowerCase())
        );
      }
    }

    if (query) {
      list = list.filter((s) => {
        const nom = s.patientDetails ? `${s.patientDetails.prenom} ${s.patientDetails.nom}`.toLowerCase() : '';
        const nss = s.patientDetails?.numeroSecuriteSociale?.toLowerCase() || '';
        const ref = s.reference?.toLowerCase() || '';
        const srv = s.serviceDetails?.nomService?.toLowerCase() || '';
        return nom.includes(query) || nss.includes(query) || ref.includes(query) || srv.includes(query);
      });
    }

    return list;
  });

  // Mouvements récents triés
  recentMouvements = computed(() => {
    const list = this.parcoursService.mouvements();
    return list.slice(0, 6);
  });

  // Parcours type construit à partir du séjour sélectionné ou données métier
  parcoursSteps = computed<ParcoursStep[]>(() => {
    const sejour = this.selectedSejour();
    const dossier = this.parcoursService.activeDossier();

    const defAdmissionHeure = sejour?.dateAdmission ? this.formatHeure(sejour.dateAdmission) : '08:15';
    const defAdmissionService = sejour?.serviceDetails?.nomService || 'Service des urgences';

    let consultationHeure = '10:30';
    let consultationService = 'Médecine interne';
    let labHeure = '14:20';
    let labDesc = 'Prélèvements';
    let hospHeure = '16:05';
    let hospDesc = this.getChambreLitLabel(sejour);
    let transfertHeure = '09:45';
    let transfertService = 'Chirurgie';

    if (dossier) {
      // Chercher consultation
      const evtConsult = dossier.evenements?.find(
        (e) => e.typeEvenement === 'CONSULTATION'
      );
      if (evtConsult) {
        consultationHeure = this.formatHeure(evtConsult.dateEvenement);
        consultationService = evtConsult.titre || consultationService;
      }

      // Chercher analyse / labo
      const evtLab = dossier.evenements?.find(
        (e) => e.typeEvenement === 'EXAMEN_EN_COURS' || e.typeEvenement === 'RESULTAT_EXAMEN'
      );
      if (evtLab) {
        labHeure = this.formatHeure(evtLab.dateEvenement);
        labDesc = evtLab.titre || labDesc;
      } else if (dossier.analyses && dossier.analyses.length > 0) {
        labHeure = this.formatHeure(dossier.analyses[0].datePrescription);
        labDesc = dossier.analyses[0].typeAnalyse || labDesc;
      }

      // Chercher attribution lit
      const evtLit = dossier.evenements?.find((e) => e.typeEvenement === 'ATTRIBUTION_LIT');
      if (evtLit) {
        hospHeure = this.formatHeure(evtLit.dateEvenement);
      }

      // Chercher dernier mouvement de transfert
      const mvtTransfert = dossier.mouvements?.find(
        (m) => m.typeMouvement === 'TRANSFERT_SERVICE' || m.typeMouvement === 'CHANGEMENT_CHAMBRE'
      );
      if (mvtTransfert) {
        transfertHeure = this.formatHeure(mvtTransfert.dateMouvement);
        const dstObj: any = mvtTransfert.destinationDetails || mvtTransfert.localisationDestinationDetails;
        transfertService =
          dstObj?.service_details?.nom_service ||
          dstObj?.serviceDetails?.nomService ||
          dstObj?.serviceNom ||
          dstObj?.nomService ||
          mvtTransfert.motif ||
          transfertService;
      }
    }

    return [
      {
        titre: 'Admission',
        heure: defAdmissionHeure,
        description: defAdmissionService,
        icone: 'ri-login-box-line',
        couleurClass: 'step-blue',
      },
      {
        titre: 'Consultation',
        heure: consultationHeure,
        description: consultationService,
        icone: 'ri-stethoscope-line',
        couleurClass: 'step-teal',
      },
      {
        titre: 'Laboratoire',
        heure: labHeure,
        description: labDesc,
        icone: 'ri-test-tube-line',
        couleurClass: 'step-purple',
      },
      {
        titre: 'Hospitalisation',
        heure: hospHeure,
        description: hospDesc,
        icone: 'ri-hotel-bed-line',
        couleurClass: 'step-green',
      },
      {
        titre: 'Transfert',
        heure: transfertHeure,
        description: transfertService,
        icone: 'ri-arrow-left-right-line',
        couleurClass: 'step-orange',
      },
    ];
  });

  ngOnInit(): void {
    // Horloge temps réel
    this.clockInterval = setInterval(() => {
      this.currentDate.set(new Date());
    }, 60000);

    // Débouncing de la recherche
    this.searchSubject
      .pipe(debounceTime(300), distinctUntilChanged())
      .subscribe((query) => {
        this.searchQuery.set(query);
      });

    // Écoute des queryParams
    this.route.queryParams.subscribe((params) => {
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

  ngOnDestroy(): void {
    if (this.clockInterval) {
      clearInterval(this.clockInterval);
    }
    this.searchSubject.complete();
  }

  onSearchInput(value: string): void {
    this.searchSubject.next(value);
  }

  toggleFilters(): void {
    this.showFilters.set(!this.showFilters());
  }

  toggleSidebar(): void {
    this.sidebarOpen.set(!this.sidebarOpen());
  }

  chargerDonnees(): void {
    this.chargerStats();
    this.chargerSejours();
    this.chargerMouvementsRecents();
  }

  chargerStats(): void {
    this.parcoursService.getDashboardStats().subscribe();
  }

  chargerSejours(): void {
    const srv = this.selectedService();
    const srvId = srv && !isNaN(parseInt(srv, 10)) ? parseInt(srv, 10) : undefined;
    this.parcoursService
      .getSejours({
        search: this.searchQuery() || undefined,
        statut: this.selectedStatut() || undefined,
        serviceId: srvId,
      })
      .subscribe((res) => {
        if (res.results && res.results.length > 0 && !this.selectedSejour()) {
          this.selectionnerSejour(res.results[0], false);
        }
      });
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

  selectionnerSejour(sejour: Sejour, openModal: boolean = true): void {
    this.selectedSejour.set(sejour);
    this.chargerDossierParId(sejour.idSejour);
    if (openModal) {
      this.showDossierModal.set(true);
    }
  }

  chargerDossierParId(id: number): void {
    this.parcoursService.getDossierSynthese(id).subscribe({
      next: (dossier) => {
        if (!this.selectedSejour()) {
          this.selectedSejour.set(dossier.sejour);
        }
      },
      error: () => {
        this.afficherMessage('error', 'Impossible de charger le parcours du dossier sélectionné.');
      },
    });
  }

  closeDossierModal(): void {
    this.showDossierModal.set(false);
  }

  // --- ACTIONS TRANSFERT ---
  private getBatimentRecommandePourService(serviceId: number): number | null {
    const srv = this.servicesList().find((s) => (s.id || s.id_service || s.idService) === Number(serviceId));
    const nomService = (srv?.nom || srv?.nom_service || srv?.nomService || '').toUpperCase();
    const bats = this.batimentsList();
    if (!bats || bats.length === 0) return null;

    if (nomService.includes('URGENCE') || nomService.includes('REANIMATION')) {
      const b = bats.find((x) => x.nom?.toUpperCase().includes('URGENCE'));
      if (b) return b.id || b.id_batiment || b.idBatiment;
    }
    if (nomService.includes('CHIRURGIE') || nomService.includes('OPERA')) {
      const b = bats.find((x) => x.nom?.toUpperCase().includes('CHIRURGIE') || x.nom?.toUpperCase().includes('BLOC'));
      if (b) return b.id || b.id_batiment || b.idBatiment;
    }
    if (nomService.includes('MATERN') || nomService.includes('GYNECO')) {
      const b = bats.find((x) => x.nom?.toUpperCase().includes('MATERN'));
      if (b) return b.id || b.id_batiment || b.idBatiment;
    }
    if (
      nomService.includes('CARDIO') ||
      nomService.includes('NEURO') ||
      nomService.includes('DERMATO') ||
      nomService.includes('OPHTALMO') ||
      nomService.includes('RADIO') ||
      nomService.includes('PEDIATRI')
    ) {
      const b = bats.find((x) => x.nom?.toUpperCase().includes('SPÉCIAL') || x.nom?.toUpperCase().includes('SPECIAL') || x.nom?.toUpperCase().includes('C'));
      if (b) return b.id || b.id_batiment || b.idBatiment;
    }
    if (nomService.includes('MEDECINE') || nomService.includes('PSYCHIATR')) {
      const b = bats.find((x) => x.nom?.toUpperCase().includes('PRINCIPAL') || x.nom?.toUpperCase().includes('A'));
      if (b) return b.id || b.id_batiment || b.idBatiment;
    }

    return bats[0].id || bats[0].id_batiment || bats[0].idBatiment || null;
  }

  ouvrirTransfertModal(): void {
    const sejour = this.selectedSejour() || this.parcoursService.activeDossier()?.sejour;
    if (!sejour) return;

    const sejourId = sejour.idSejour || (sejour as any).id_sejour || (sejour as any).id;
    const srvId =
      sejour.serviceResponsable ||
      (sejour as any).service_responsable ||
      sejour.serviceDetails?.id ||
      (sejour as any).service_details?.id_service ||
      (this.servicesList().length > 0 ? (this.servicesList()[0].id || this.servicesList()[0].id_service) : null);

    this.transfertData = {
      sejour: Number(sejourId),
      service: Number(srvId),
      batiment: null,
      chambre: null,
      lit: null,
      motif: '',
      commentaire: '',
    };
    this.showTransfertModal.set(true);

    if (srvId) {
      this.onServiceChange(Number(srvId));
    }
  }

  onServiceChange(serviceId: number | null): void {
    if (!serviceId) {
      this.transfertData.service = null as any;
      return;
    }
    this.transfertData.service = Number(serviceId);
    const batId = this.getBatimentRecommandePourService(Number(serviceId));
    if (batId) {
      this.transfertData.batiment = batId;
      this.onBatimentChange(batId);
    } else {
      this.transfertData.batiment = null;
      this.transfertData.chambre = null;
      this.transfertData.lit = null;
      this.chambresList.set([]);
      this.litsDisponiblesList.set([]);
    }
  }

  onBatimentChange(batimentId: number | null): void {
    this.transfertData.batiment = batimentId ? Number(batimentId) : null;
    this.transfertData.chambre = null;
    this.transfertData.lit = null;
    if (!batimentId) {
      this.chambresList.set([]);
      this.litsDisponiblesList.set([]);
      return;
    }
    this.parcoursService.getChambresList(Number(batimentId)).subscribe({
      next: (list: any[]) => {
        this.chambresList.set(list);
      },
    });
    this.parcoursService.getLitsDisponibles(undefined, Number(batimentId)).subscribe({
      next: (list: any[]) => {
        this.litsDisponiblesList.set(list);
      },
    });
  }

  onChambreChange(chambreId: number | null): void {
    this.transfertData.chambre = chambreId ? Number(chambreId) : null;
    this.transfertData.lit = null;
    if (!chambreId) {
      if (this.transfertData.batiment) {
        this.parcoursService.getLitsDisponibles(undefined, Number(this.transfertData.batiment)).subscribe({
          next: (list: any[]) => this.litsDisponiblesList.set(list),
        });
      } else {
        this.litsDisponiblesList.set([]);
      }
      return;
    }
    this.parcoursService.getLitsDisponibles(Number(chambreId)).subscribe({
      next: (list: any[]) => {
        this.litsDisponiblesList.set(list);
        if (list && list.length > 0) {
          this.transfertData.lit = list[0].id;
        }
      },
    });
  }

  validerTransfert(): void {
    if (!this.transfertData.motif || !this.transfertData.motif.trim()) {
      this.afficherMessage('error', 'Le motif du transfert est requis.');
      return;
    }
    if (!this.transfertData.service) {
      this.afficherMessage('error', 'Le service de destination est requis.');
      return;
    }

    this.isSubmitting.set(true);
    const payload: TransfertPatientDto = {
      sejour: Number(this.transfertData.sejour),
      service: Number(this.transfertData.service),
      batiment: this.transfertData.batiment ? Number(this.transfertData.batiment) : null,
      chambre: this.transfertData.chambre ? Number(this.transfertData.chambre) : null,
      lit: this.transfertData.lit ? Number(this.transfertData.lit) : null,
      motif: this.transfertData.motif.trim(),
      commentaire: this.transfertData.commentaire ? this.transfertData.commentaire.trim() : '',
    };

    this.parcoursService.effectuerTransfert(payload).subscribe({
      next: () => {
        this.isSubmitting.set(false);
        this.showTransfertModal.set(false);
        this.afficherMessage('success', 'Transfert effectué avec succès.');
        this.chargerDonnees();
        if (payload.sejour) {
          this.parcoursService.getDossierSynthese(payload.sejour).subscribe();
        }
      },
      error: (err) => {
        this.isSubmitting.set(false);
        let detail = 'Erreur lors du transfert.';
        if (err.error) {
          if (typeof err.error === 'string') {
            detail = err.error;
          } else if (err.error.detail) {
            detail = err.error.detail;
          } else if (err.error.lit) {
            detail = Array.isArray(err.error.lit) ? err.error.lit[0] : err.error.lit;
          } else if (err.error.service) {
            detail = Array.isArray(err.error.service) ? err.error.service[0] : err.error.service;
          } else if (err.error.chambre) {
            detail = Array.isArray(err.error.chambre) ? err.error.chambre[0] : err.error.chambre;
          } else if (err.error.non_field_errors) {
            detail = Array.isArray(err.error.non_field_errors) ? err.error.non_field_errors[0] : err.error.non_field_errors;
          }
        }
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
    const sejour = this.selectedSejour() || this.parcoursService.activeDossier()?.sejour;
    if (!sejour || !this.sortieData.motifSortie) {
      this.afficherMessage('error', 'Le motif de sortie est obligatoire.');
      return;
    }

    this.isSubmitting.set(true);
    this.parcoursService.cloturerSejour(sejour.idSejour, this.sortieData).subscribe({
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
    const sejour = this.selectedSejour() || this.parcoursService.activeDossier()?.sejour;
    if (!sejour) return;
    this.newEventData = {
      sejour: sejour.idSejour,
      typeEvenement: 'OBSERVATION',
      titre: '',
      description: '',
      importance: 'INFO',
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

  onLogout(): void {
    this.authService.logout().subscribe();
  }

  // --- HELPERS D'AFFICHAGE MÉTIER ---

  getPatientNom(s: Sejour | null | undefined): string {
    if (!s) return 'Patient';
    if (s.patientDetails) {
      const p = s.patientDetails;
      const full = `${p.prenom || ''} ${p.nom || ''}`.trim();
      if (full) return full;
    }
    return `Patient ${String(s.idSejour).padStart(2, '0')}`;
  }

  getPatientDossier(s: Sejour | null | undefined): string {
    if (!s) return 'Dossier non spécifié';
    if (s.patientDetails?.numeroSecuriteSociale) {
      return `Dossier #${s.patientDetails.numeroSecuriteSociale.slice(-5)}`;
    }
    if (s.reference) {
      const parts = s.reference.split('-');
      return `Dossier #${parts[parts.length - 1]}`;
    }
    return `Dossier #${s.idSejour}`;
  }

  getServiceNom(s: Sejour | null | undefined): string {
    if (!s) return 'Non assigné';
    let raw = s.serviceDetails?.nomService || s.localisationActuelleInfo?.serviceNom || 'Médecine interne';
    raw = raw.trim();
    if (raw === raw.toUpperCase() && raw.length > 3) {
      return raw.charAt(0) + raw.slice(1).toLowerCase();
    }
    return raw;
  }

  getChambreLitLabel(s: Sejour | null | undefined): string {
    if (!s) return 'Zone d’accueil';
    const loc = s.localisationActuelleInfo;
    if (loc?.chambreNumero) {
      let bat = '';
      if (loc.batimentNom) {
        const bn = loc.batimentNom;
        if (/Pavillon\s+A/i.test(bn)) bat = 'Bât. A';
        else if (/Pavillon\s+B/i.test(bn)) bat = 'Bât. B';
        else if (/Pavillon\s+C/i.test(bn)) bat = 'Bât. C';
        else if (/Bâtiment\s+([A-Z0-9]+)/i.test(bn)) {
          const m = bn.match(/Bâtiment\s+([A-Z0-9]+)/i);
          bat = `Bât. ${m ? m[1] : 'A'}`;
        } else if (/Bât\.?\s*([A-Z0-9]+)/i.test(bn)) {
          const m = bn.match(/Bât\.?\s*([A-Z0-9]+)/i);
          bat = `Bât. ${m ? m[1] : 'A'}`;
        } else {
          bat = 'Bât. A';
        }
      }

      let lit = '';
      if (loc.litNumero) {
        const cleanLit = String(loc.litNumero).replace(/^lit\s*/i, '').trim();
        lit = ` / Lit ${cleanLit}`;
      }

      const batPrefix = bat ? `${bat} - ` : '';
      return `${batPrefix}Ch. ${loc.chambreNumero}${lit}`;
    }

    if (
      s.typePriseEnCharge === 'URGENCE' ||
      s.serviceDetails?.nomService?.toLowerCase().includes('urgenc')
    ) {
      return 'Zone d’accueil';
    }
    return 'Zone d’accueil';
  }

  getStatutLabel(statut: string): string {
    const map: Record<string, string> = {
      EN_COURS: 'En cours',
      EN_ATTENTE: 'En attente',
      TRANSFERE: 'Transfert',
      SORTIE_AUTORISEE: 'Sortie autorisée',
      TERMINE: 'Terminé',
      ANNULE: 'Annulé',
    };
    return map[statut] || statut || 'En cours';
  }

  getStatutBadgeClass(statut: string): string {
    switch (statut) {
      case 'EN_COURS': return 'badge-en-cours';
      case 'EN_ATTENTE': return 'badge-en-attente';
      case 'TRANSFERE': return 'badge-transfert';
      case 'SORTIE_AUTORISEE': return 'badge-sortie';
      case 'TERMINE': return 'badge-termine';
      default: return 'badge-default';
    }
  }

  getMouvementTitre(m: MouvementPatient): string {
    switch (m.typeMouvement) {
      case 'ADMISSION': return 'Admission';
      case 'TRANSFERT_SERVICE': return 'Transfert';
      case 'CHANGEMENT_CHAMBRE': return 'Changement de chambre';
      case 'CHANGEMENT_LIT': return 'Changement de lit';
      case 'DEPART_EXAMEN': return 'Départ examen';
      case 'RETOUR_EXAMEN': return 'Retour examen';
      case 'SORTIE_TEMPORAIRE': return 'Sortie temporaire';
      case 'SORTIE_DEFINITIVE': return 'Sortie';
      default: return m.typeMouvementDisplay || 'Mouvement';
    }
  }

  getMouvementTrajet(m: MouvementPatient): string {
    const srcObj: any = m.sourceDetails || m.localisationOrigineDetails;
    const dstObj: any = m.destinationDetails || m.localisationDestinationDetails;
    const src = srcObj?.service_details?.nom_service ||
      srcObj?.serviceDetails?.nomService ||
      srcObj?.serviceNom ||
      srcObj?.nomService ||
      '';
    const dst = dstObj?.service_details?.nom_service ||
      dstObj?.serviceDetails?.nomService ||
      dstObj?.serviceNom ||
      dstObj?.nomService ||
      '';

    if (m.typeMouvement === 'ADMISSION') {
      return dst || src || 'Urgences';
    }
    if (m.typeMouvement === 'SORTIE_DEFINITIVE') {
      return src ? `${src}` : 'Hospitalisation';
    }
    if (m.typeMouvement === 'CHANGEMENT_LIT') {
      return 'Lit 1 → Lit 3';
    }
    if (src && dst) {
      return `${src} → ${dst}`;
    }
    return dst || src || m.motif || 'Service de soins';
  }

  getMouvementIcon(type: string): string {
    switch (type) {
      case 'ADMISSION': return 'ri-add-line';
      case 'TRANSFERT_SERVICE': return 'ri-arrow-left-right-line';
      case 'SORTIE_DEFINITIVE': return 'ri-logout-box-r-line';
      case 'CHANGEMENT_LIT':
      case 'CHANGEMENT_CHAMBRE': return 'ri-hotel-bed-line';
      case 'DEPART_EXAMEN':
      case 'RETOUR_EXAMEN': return 'ri-test-tube-line';
      default: return 'ri-arrow-right-line';
    }
  }

  getMouvementIconClass(type: string): string {
    switch (type) {
      case 'ADMISSION': return 'mvt-icon-green';
      case 'TRANSFERT_SERVICE': return 'mvt-icon-orange';
      case 'SORTIE_DEFINITIVE': return 'mvt-icon-salmon';
      case 'CHANGEMENT_LIT':
      case 'CHANGEMENT_CHAMBRE': return 'mvt-icon-teal';
      default: return 'mvt-icon-blue';
    }
  }

  getMouvementActeur(m: MouvementPatient): string {
    if (m.effectueParRole) {
      switch (m.effectueParRole) {
        case 'MEDECIN': return 'Médecin';
        case 'INFIRMIER': return 'Infirmier';
        case 'ADMINISTRATEUR': return 'Administrateur';
        default: return m.effectueParRole;
      }
    }
    if (m.typeMouvement === 'ADMISSION' || m.typeMouvement === 'SORTIE_DEFINITIVE') {
      return 'Médecin';
    }
    return 'Infirmier';
  }

  formatHeure(dateStr: string | null | undefined): string {
    if (!dateStr) return '--:--';
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return '--:--';
    return d.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
  }

  scrollToSection(sectionId: string): void {
    const el = document.getElementById(sectionId);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    }
  }

  formatTypeEvenement(type: string | undefined): string {
    if (!type) return '';
    const map: Record<string, string> = {
      TRANSFERT_INTERNE: 'Transfert interne',
      TRANSFERT_SERVICE: 'Transfert de service',
      ADMISSION: 'Admission du patient',
      SORTIE: 'Sortie',
      SORTIE_AUTORISEE: 'Sortie autorisée',
      SORTIE_DEFINITIVE: 'Sortie effective',
      ATTRIBUTION_LIT: 'Attribution de lit',
      LIBERATION_LIT: 'Libération de lit',
      SOIN_ADMINISTRE: 'Soin administré',
      OBSERVATION: 'Observation clinique',
      CONSULTATION: 'Consultation',
      PRESCRIPTION_EXAMEN: 'Prescription examen',
      EXAMEN_EN_COURS: 'Examen en cours',
      RESULTAT_EXAMEN: 'Résultats disponibles',
    };
    return map[type] || type;
  }

  formatEventDescription(desc: string | undefined): string {
    if (!desc) return '';
    let clean = desc;
    // Remplacer les syntaxes techniques [S-XXXX @ ... (ACTUELLE)]
    clean = clean.replace(/\[[A-Z0-9-]+\s*@\s*([^\]]+?)\s*\((?:ACTUELLE|PASSÉE)\)\s*\]/gi, '$1');
    clean = clean.replace(/\[([^\]]+?)\]/g, '$1');
    clean = clean.replace(/Lit\s+Lit\s+/gi, 'Lit ');
    clean = clean.replace(/\s+/g, ' ').trim();
    return clean;
  }
}
