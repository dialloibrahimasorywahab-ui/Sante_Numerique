import { Injectable, inject, signal } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, tap, catchError, throwError, map } from 'rxjs';
import { environment } from '../../../environments/environment';
import { PaginatedResponse } from '../models/models';
import {
  Sejour,
  DossierSyntheseSejour,
  AdmissionPatientDto,
  TransfertPatientDto,
  SortiePatientDto,
  LocalisationPatient,
  MouvementPatient,
  EvenementParcours,
  DashboardStats,
} from '../models/parcours.model';

@Injectable({
  providedIn: 'root',
})
export class ParcoursService {
  private http = inject(HttpClient);
  private readonly baseUrl = environment.apiUrl;

  // State Signals
  sejours = signal<Sejour[]>([]);
  activeDossier = signal<DossierSyntheseSejour | null>(null);
  dashboardStats = signal<DashboardStats | null>(null);
  localisations = signal<LocalisationPatient[]>([]);
  mouvements = signal<MouvementPatient[]>([]);
  isLoading = signal<boolean>(false);
  errorMessage = signal<string | null>(null);
  lastRefreshed = signal<Date | null>(null);

  /**
   * Récupère les métriques consolidées du tableau de bord
   */
  getDashboardStats(): Observable<DashboardStats> {
    return this.http.get<any>(`${this.baseUrl}/sejours/statistiques-dashboard/`).pipe(
      map((raw: any) => ({
        patientsPresents: raw.patients_presents ?? raw.patientsPresents ?? 0,
        sejoursEnCours: raw.sejours_en_cours ?? raw.sejoursEnCours ?? 0,
        patientsUrgences: raw.patients_urgences ?? raw.patientsUrgences ?? 0,
        patientsHospitalises: raw.patients_hospitalises ?? raw.patientsHospitalises ?? 0,
        litsOccupes: raw.lits_occupes ?? raw.litsOccupes ?? 0,
        litsDisponibles: raw.lits_disponibles ?? raw.litsDisponibles ?? 0,
        totalLits: raw.total_lits ?? raw.totalLits ?? 0,
        transfertsRecents: raw.transferts_recents ?? raw.transfertsRecents ?? 0,
        sortiesRecentes: raw.sorties_recentes ?? raw.sortiesRecentes ?? 0,
        timestamp: raw.timestamp || new Date().toISOString(),
      })),
      tap({
        next: (stats) => {
          this.dashboardStats.set(stats);
          this.lastRefreshed.set(new Date());
        },
        error: (err) => {
          this.errorMessage.set(err.message || 'Impossible de récupérer les statistiques du tableau de bord.');
        },
      })
    );
  }

  /**
   * Liste les séjours avec filtres et pagination
   */
  getSejours(filters?: {
    patientId?: number;
    serviceId?: number;
    medecinId?: number;
    statut?: string;
    typePriseEnCharge?: string;
    search?: string;
    page?: number;
  }): Observable<PaginatedResponse<Sejour>> {
    this.isLoading.set(true);
    let params = new HttpParams();
    if (filters?.patientId) params = params.set('patient_id', filters.patientId.toString());
    if (filters?.serviceId) params = params.set('service_id', filters.serviceId.toString());
    if (filters?.medecinId) params = params.set('medecin_id', filters.medecinId.toString());
    if (filters?.statut) params = params.set('statut', filters.statut);
    if (filters?.typePriseEnCharge) params = params.set('type_prise_en_charge', filters.typePriseEnCharge);
    if (filters?.search) params = params.set('search', filters.search);
    if (filters?.page) params = params.set('page', filters.page.toString());

    return this.http.get<any>(`${this.baseUrl}/sejours/`, { params }).pipe(
      map((res: any) => {
        const rawList = res.results || (Array.isArray(res) ? res : []);
        const mappedList: Sejour[] = rawList.map((s: any) => {
          const p = s.patient_details || s.patientDetails;
          const srv = s.service_details || s.serviceDetails;
          const med = s.medecin_details || s.medecinDetails;
          return {
            idSejour: s.id_sejour ?? s.idSejour ?? s.id,
            reference: s.reference,
            patient: s.patient,
            patientDetails: p ? {
              id: p.id_patient || p.idPatient || p.id || s.patient,
              nom: p.nom || p.id_utilisateur?.nom || p.idUtilisateur?.nom || '',
              prenom: p.prenom || p.id_utilisateur?.prenom || p.idUtilisateur?.prenom || '',
              dateNaissance: p.date_naissance || p.dateNaissance,
              sexe: p.sexe,
              numeroSecuriteSociale: p.numero_securite_sociale || p.numeroSecuriteSociale,
              groupeSanguin: p.groupe_sanguin || p.groupeSanguin,
              telephone: p.telephone || p.id_utilisateur?.telephone,
              email: p.email || p.id_utilisateur?.email,
              adresse: p.adresse,
            } : undefined,
            dateAdmission: s.date_admission || s.dateAdmission,
            dateSortie: s.date_sortie || s.dateSortie,
            statut: s.statut,
            statutDisplay: s.statut_display || s.statutDisplay || s.statut,
            typePriseEnCharge: s.type_prise_en_charge || s.typePriseEnCharge,
            typePriseEnChargeDisplay: s.type_prise_en_charge_display || s.typePriseEnChargeDisplay || s.type_prise_en_charge,
            serviceResponsable: s.service_responsable || s.serviceResponsable,
            serviceDetails: srv ? {
              id: srv.idService || srv.id_service || srv.id,
              nomService: srv.nomService || srv.nom_service,
              codeService: srv.codeService || srv.code_service,
            } : undefined,
            medecinResponsable: s.medecin_responsable || s.medecinResponsable,
            medecinDetails: med ? {
              id: med.idMedecin || med.id_medecin || med.id,
              nom: med.nom || med.idUtilisateur?.nom || med.id_utilisateur?.nom,
              prenom: med.prenom || med.idUtilisateur?.prenom || med.id_utilisateur?.prenom,
              specialite: med.specialite,
            } : undefined,
            motifAdmission: s.motif_admission || s.motifAdmission,
            commentaireSortie: s.commentaire_sortie || s.commentaireSortie,
            localisationActuelleInfo: s.localisation_actuelle_info ? {
              id: s.localisation_actuelle_info.id,
              serviceId: s.localisation_actuelle_info.service_id || s.localisation_actuelle_info.serviceId,
              serviceNom: s.localisation_actuelle_info.service_nom || s.localisation_actuelle_info.serviceNom,
              batimentNom: s.localisation_actuelle_info.batiment_nom || s.localisation_actuelle_info.batimentNom,
              chambreNumero: s.localisation_actuelle_info.chambre_numero || s.localisation_actuelle_info.chambreNumero,
              litNumero: s.localisation_actuelle_info.lit_numero || s.localisation_actuelle_info.litNumero,
              dateDebut: s.localisation_actuelle_info.date_debut || s.localisation_actuelle_info.dateDebut,
            } : (s.localisationActuelleInfo ? s.localisationActuelleInfo : undefined),
            actif: s.actif,
          };
        });
        return {
          count: res.count ?? mappedList.length,
          total_pages: res.total_pages ?? res.totalPages ?? 1,
          current_page: res.current_page ?? res.currentPage ?? 1,
          page_size: res.page_size ?? res.pageSize ?? mappedList.length,
          next: res.next ?? null,
          previous: res.previous ?? null,
          results: mappedList,
        };
      }),
      tap({
        next: (res) => {
          this.sejours.set(res.results || []);
          this.lastRefreshed.set(new Date());
          this.isLoading.set(false);
        },
        error: (err) => {
          this.errorMessage.set(err.message || 'Erreur lors du chargement des séjours.');
          this.isLoading.set(false);
        },
      })
    );
  }

  getSejourById(id: number): Observable<Sejour> {
    return this.http.get<Sejour>(`${this.baseUrl}/sejours/${id}/`);
  }

  getDossierSynthese(id: number): Observable<DossierSyntheseSejour> {
    this.isLoading.set(true);
    return this.http.get<any>(`${this.baseUrl}/sejours/${id}/dossier-synthese/`).pipe(
      map((raw: any) => {
        const s = raw.sejour || raw || {};
        const p = s.patient_details || s.patientDetails || raw.patient_details || raw.patientDetails;
        const srv = s.service_details || s.serviceDetails;
        const med = s.medecin_details || s.medecinDetails;
        return {
          sejour: {
            ...s,
            idSejour: s.id_sejour ?? s.idSejour ?? s.id,
            reference: s.reference,
            patientDetails: p ? {
              id: p.id_patient || p.idPatient || p.id || s.patient,
              nom: p.nom || p.id_utilisateur?.nom || p.idUtilisateur?.nom || '',
              prenom: p.prenom || p.id_utilisateur?.prenom || p.idUtilisateur?.prenom || '',
              dateNaissance: p.date_naissance || p.dateNaissance,
              sexe: p.sexe,
              numeroSecuriteSociale: p.numero_securite_sociale || p.numeroSecuriteSociale,
              groupeSanguin: p.groupe_sanguin || p.groupeSanguin,
              telephone: p.telephone || p.id_utilisateur?.telephone,
              email: p.email || p.id_utilisateur?.email,
              adresse: p.adresse,
              personneAContacter: p.personne_a_contacter || p.personneAContacter,
            } : undefined,
            dateAdmission: s.date_admission || s.dateAdmission,
            dateSortie: s.date_sortie || s.dateSortie,
            statut: s.statut,
            statutDisplay: s.statut_display || s.statutDisplay || s.statut,
            typePriseEnCharge: s.type_prise_en_charge || s.typePriseEnCharge,
            typePriseEnChargeDisplay: s.type_prise_en_charge_display || s.typePriseEnChargeDisplay || s.type_prise_en_charge,
            serviceDetails: srv ? {
              id: srv.id_service || srv.idService || srv.id,
              nomService: srv.nom_service || srv.nomService,
            } : undefined,
            medecinDetails: med ? {
              id: med.id_medecin || med.idMedecin || med.id,
              nom: med.nom || med.id_utilisateur?.nom || med.idUtilisateur?.nom,
              prenom: med.prenom || med.id_utilisateur?.prenom || med.idUtilisateur?.prenom,
              specialite: med.specialite,
            } : undefined,
          },
          localisationActuelle: raw.localisation_actuelle || raw.localisationActuelle,
          historiqueLocalisations: (raw.historique_localisations || raw.localisations || []).map((l: any) => ({
          ...l,
          id: l.id_localisation ?? l.id,
          dateDebut: l.date_debut || l.dateDebut,
          dateFin: l.date_fin || l.dateFin,
          estActuelle: l.est_actuelle ?? l.estActuelle,
          serviceNom: l.service_nom || l.serviceNom || l.service_details?.nom_service,
          batimentNom: l.batiment_nom || l.batimentNom || l.batiment_details?.nom_batiment,
          chambreNumero: l.chambre_numero || l.chambreNumero || l.chambre_details?.numero_chambre,
          litNumero: l.lit_numero || l.litNumero || l.lit_details?.numero_lit,
        })),
        localisations: (raw.localisations || raw.historique_localisations || []).map((l: any) => ({
          ...l,
          id: l.id_localisation ?? l.id,
          dateDebut: l.date_debut || l.dateDebut,
          dateFin: l.date_fin || l.dateFin,
          estActuelle: l.est_actuelle ?? l.estActuelle,
          serviceNom: l.service_nom || l.serviceNom || l.service_details?.nom_service,
          batimentNom: l.batiment_nom || l.batimentNom || l.batiment_details?.nom_batiment,
          chambreNumero: l.chambre_numero || l.chambreNumero || l.chambre_details?.numero_chambre,
          litNumero: l.lit_numero || l.litNumero || l.lit_details?.numero_lit,
        })),
        mouvements: (raw.mouvements || []).map((m: any) => ({
          ...m,
          id: m.id_mouvement ?? m.id,
          dateMouvement: m.date_mouvement || m.dateMouvement,
          typeMouvement: m.type_mouvement || m.typeMouvement,
          typeMouvementDisplay: m.type_mouvement_display || m.typeMouvementDisplay,
          effectueParNom: m.effectue_par_nom || m.effectueParNom,
        })),
        evenements: (raw.evenements || []).map((e: any) => ({
          ...e,
          id: e.id_evenement ?? e.id,
          dateEvenement: e.date_evenement || e.dateEvenement,
          typeEvenement: e.type_evenement || e.typeEvenement,
          typeEvenementDisplay: e.type_evenement_display || e.typeEvenementDisplay,
          declareParNom: e.declare_par_nom || e.declareParNom,
        })),
        analyses: raw.analyses || [],
      }),
      tap({
        next: (data: DossierSyntheseSejour) => {
          this.activeDossier.set(data);
          this.isLoading.set(false);
        },
        error: (err: any) => {
          this.errorMessage.set(err.message || 'Impossible de charger le dossier synthétique.');
          this.isLoading.set(false);
        },
      })
    );
  }

  admettrePatient(dto: AdmissionPatientDto): Observable<Sejour> {
    this.isLoading.set(true);
    return this.http.post<Sejour>(`${this.baseUrl}/sejours/`, dto).pipe(
      tap({
        next: () => {
          this.isLoading.set(false);
        },
        error: () => this.isLoading.set(false),
      })
    );
  }

  effectuerTransfert(dto: TransfertPatientDto): Observable<MouvementPatient> {
    this.isLoading.set(true);
    return this.http.post<MouvementPatient>(`${this.baseUrl}/mouvements/transfert/`, dto).pipe(
      tap({
        next: () => {
          if (this.activeDossier()) {
            this.getDossierSynthese(dto.sejour).subscribe();
          }
          this.isLoading.set(false);
        },
        error: () => this.isLoading.set(false),
      })
    );
  }

  autoriserSortie(sejourId: number, motif: string): Observable<Sejour> {
    return this.http.post<Sejour>(`${this.baseUrl}/sejours/${sejourId}/autoriser-sortie/`, {
      motifSortie: motif,
    });
  }

  cloturerSejour(sejourId: number, dto: SortiePatientDto): Observable<Sejour> {
    this.isLoading.set(true);
    return this.http.post<Sejour>(`${this.baseUrl}/sejours/${sejourId}/cloturer/`, dto).pipe(
      tap({
        next: () => {
          if (this.activeDossier()) {
            this.getDossierSynthese(sejourId).subscribe();
          }
          this.isLoading.set(false);
        },
        error: () => this.isLoading.set(false),
      })
    );
  }

  consignerEvenement(dto: {
    sejour: number;
    typeEvenement: string;
    titre: string;
    description: string;
    importance?: string;
  }): Observable<EvenementParcours> {
    return this.http.post<EvenementParcours>(`${this.baseUrl}/evenements/`, dto).pipe(
      tap(() => {
        if (this.activeDossier()) {
          this.getDossierSynthese(dto.sejour).subscribe();
        }
      })
    );
  }

  /**
   * Récupère la liste des localisations actives ou filtrées
   */
  getLocalisations(filters?: {
    serviceId?: number;
    chambreId?: number;
    litId?: number;
    estActuelle?: boolean;
    page?: number;
  }): Observable<PaginatedResponse<LocalisationPatient>> {
    this.isLoading.set(true);
    let params = new HttpParams();
    if (filters?.serviceId) params = params.set('service_id', filters.serviceId.toString());
    if (filters?.chambreId) params = params.set('chambre_id', filters.chambreId.toString());
    if (filters?.litId) params = params.set('lit_id', filters.litId.toString());
    if (filters?.estActuelle !== undefined) params = params.set('est_actuelle', filters.estActuelle ? 'true' : 'false');
    if (filters?.page) params = params.set('page', filters.page.toString());

    return this.http.get<any>(`${this.baseUrl}/localisations/`, { params }).pipe(
      map((res: any) => {
        const rawList = res.results || (Array.isArray(res) ? res : []);
        const mappedList: LocalisationPatient[] = rawList.map((l: any) => ({
          id: l.id_localisation ?? l.id,
          sejour: l.sejour,
          sejourReference: l.sejour_reference || l.sejourReference || (typeof l.sejour === 'object' ? l.sejour?.reference : ''),
          patientId: l.patient_id || l.patientId,
          patientNomComplet: l.patient_nom_complet || l.patientNomComplet,
          patientNss: l.patient_nss || l.patientNss,
          service: l.service,
          serviceNom: l.service_nom || l.serviceNom || l.service_details?.nom_service || '',
          batiment: l.batiment,
          batimentNom: l.batiment_nom || l.batimentNom || l.batiment_details?.nom_batiment,
          chambre: l.chambre,
          chambreNumero: l.chambre_numero || l.chambreNumero || l.chambre_details?.numero_chambre,
          lit: l.lit,
          litNumero: l.lit_numero || l.litNumero || l.lit_details?.numero_lit,
          dateDebut: l.date_debut || l.dateDebut,
          dateFin: l.date_fin || l.dateFin,
          estActuelle: l.est_actuelle ?? l.estActuelle,
          commentaire: l.commentaire,
          actif: l.actif,
        }));
        return {
          count: res.count ?? mappedList.length,
          total_pages: res.total_pages ?? res.totalPages ?? 1,
          current_page: res.current_page ?? res.currentPage ?? 1,
          page_size: res.page_size ?? res.pageSize ?? mappedList.length,
          next: res.next ?? null,
          previous: res.previous ?? null,
          results: mappedList,
        };
      }),
      tap({
        next: (res) => {
          this.localisations.set(res.results || []);
          this.lastRefreshed.set(new Date());
          this.isLoading.set(false);
        },
        error: (err) => {
          this.errorMessage.set(err.message || 'Erreur lors du chargement des localisations.');
          this.isLoading.set(false);
        },
      })
    );
  }

  /**
   * Récupère les mouvements récents pour le tableau de bord
   */
  getMouvementsRecents(limit: number = 10): Observable<PaginatedResponse<MouvementPatient>> {
    let params = new HttpParams().set('page_size', limit.toString());
    return this.http.get<any>(`${this.baseUrl}/mouvements/`, { params }).pipe(
      map((res: any) => {
        const rawList = res.results || (Array.isArray(res) ? res : []);
        const mappedList: MouvementPatient[] = rawList.map((m: any) => ({
          id: m.id_mouvement ?? m.id,
          sejour: m.sejour,
          sejourReference: m.sejour_reference || m.sejourReference || (typeof m.sejour === 'object' ? m.sejour?.reference : ''),
          patientId: m.patient_id || m.patientId,
          patientNomComplet: m.patient_nom_complet || m.patientNomComplet,
          dateMouvement: m.date_mouvement || m.dateMouvement,
          typeMouvement: m.type_mouvement || m.typeMouvement,
          typeMouvementDisplay: m.type_mouvement_display || m.typeMouvementDisplay,
          sourceDetails: m.source_details || m.sourceDetails,
          destinationDetails: m.destination_details || m.destinationDetails,
          motif: m.motif,
          commentaire: m.commentaire,
          effectuePar: m.effectue_par || m.effectuePar,
          effectueParNom: m.effectue_par_nom || m.effectueParNom,
          actif: m.actif,
        }));
        return {
          count: res.count ?? mappedList.length,
          total_pages: res.total_pages ?? res.totalPages ?? 1,
          current_page: res.current_page ?? res.currentPage ?? 1,
          page_size: res.page_size ?? res.pageSize ?? mappedList.length,
          next: res.next ?? null,
          previous: res.previous ?? null,
          results: mappedList,
        };
      }),
      tap({
        next: (res) => {
          this.mouvements.set(res.results || []);
        },
      })
    );
  }

  /**
   * Infrastructure hospitalière (pour le formulaire de transfert dynamique)
   */
  getServicesList(): Observable<any[]> {
    return this.http.get<any>(`${this.baseUrl}/services/`).pipe(
      map((res: any) => res.results || (Array.isArray(res) ? res : []))
    );
  }

  getBatimentsList(): Observable<any[]> {
    return this.http.get<any>(`${this.baseUrl}/batiments/`).pipe(
      map((res: any) => res.results || (Array.isArray(res) ? res : []))
    );
  }

  getChambresList(batimentId?: number): Observable<any[]> {
    let params = new HttpParams();
    if (batimentId) params = params.set('batiment', batimentId.toString());
    return this.http.get<any>(`${this.baseUrl}/chambres/`, { params }).pipe(
      map((res: any) => res.results || (Array.isArray(res) ? res : []))
    );
  }

  getLitsDisponibles(chambreId?: number): Observable<any[]> {
    let params = new HttpParams().set('etat', 'DISPONIBLE');
    if (chambreId) params = params.set('chambre', chambreId.toString());
    return this.http.get<any>(`${this.baseUrl}/lits/`, { params }).pipe(
      map((res: any) => res.results || (Array.isArray(res) ? res : []))
    );
  }
}
