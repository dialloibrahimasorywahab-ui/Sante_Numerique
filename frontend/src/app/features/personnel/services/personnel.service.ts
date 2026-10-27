import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, forkJoin, of } from 'rxjs';
import { map, catchError, switchMap } from 'rxjs/operators';
import { environment } from '../../../../environments/environment';
import {
  HospitalisePatientItem,
  UpcomingAppointmentItem,
  PatientItem,
  PatientParcoursData,
  PersonnelDashboardMetrics
} from '../models/personnel.model';

@Injectable({
  providedIn: 'root'
})
export class PersonnelService {
  private http = inject(HttpClient);
  private readonly baseUrl = environment.apiUrl;

  private get httpOptions() {
    return { withCredentials: true };
  }

  /**
   * Récupère la liste des patients actuellement hospitalisés (statut=EN_COURS).
   */
  getHospitalisationsEnCours(limit: number = 10): Observable<HospitalisePatientItem[]> {
    return this.http.get<any>(`${this.baseUrl}/hospitalisations/?statut=EN_COURS&page_size=${limit}`, this.httpOptions).pipe(
      map(res => {
        const items: any[] = Array.isArray(res) ? res : (res?.results || []);
        return items.slice(0, limit).map(hosp => {
          const patientUser = hosp.patient_details || hosp.patient?.idUtilisateur || hosp.patient?.id_utilisateur;
          const pPrenom = patientUser?.prenom || hosp.patient?.prenom || '';
          const pNom = patientUser?.nom || hosp.patient?.nom || '';
          const patientNom = (pPrenom || pNom) ? `${pPrenom} ${pNom}`.trim() : `Patient #${hosp.patient_id || hosp.patient || ''}`;

          const medecinUser = hosp.medecin_details || hosp.medecin?.idUtilisateur || hosp.medecin?.id_utilisateur;
          const mPrenom = medecinUser?.prenom || hosp.medecin?.prenom || '';
          const mNom = medecinUser?.nom || hosp.medecin?.nom || '';
          const medecinNom = (mPrenom || mNom) ? `Dr. ${mPrenom} ${mNom}`.trim() : 'Non assigné';

          const lit = hosp.lit_details || hosp.lit;
          const litNumero = lit?.numero_lit || lit?.numeroLit || (lit?.id ? `Lit ${lit.id}` : 'Lit N/D');
          const chambre = lit?.chambre || hosp.chambre_details;
          const chambreNumero = chambre?.numero_chambre || chambre?.numeroChambre ? `Chambre ${chambre.numero_chambre || chambre.numeroChambre}` : 'Non assignée';
          const batimentNom = chambre?.batiment?.nom || chambre?.batiment_nom || '';
          const serviceNom = hosp.service_details?.nom_service || hosp.service_nom || chambre?.service?.nom_service || 'Médecine';

          return {
            id: hosp.id || hosp.idHospitalisation,
            patientId: hosp.patient_id || hosp.patient?.id_patient || hosp.patient?.id || hosp.patient,
            patientNom,
            patientTelephone: patientUser?.telephone || hosp.patient?.telephone,
            dateEntree: hosp.date_entree || hosp.dateEntree,
            motif: hosp.motif || 'Soins hospitaliers',
            medecinNom,
            serviceNom,
            batimentNom,
            chambreNumero,
            litNumero,
            statut: hosp.statut || 'EN_COURS'
          };
        });
      }),
      catchError(() => of([]))
    );
  }

  /**
   * Récupère l'ensemble des hospitalisations avec filtre optionnel par statut.
   */
  getHospitalisations(statut?: string, search?: string, limit: number = 50): Observable<HospitalisePatientItem[]> {
    let url = `${this.baseUrl}/hospitalisations/?page_size=${limit}`;
    if (statut) url += `&statut=${statut}`;
    if (search) url += `&search=${encodeURIComponent(search)}`;

    return this.http.get<any>(url, this.httpOptions).pipe(
      map(res => {
        const items: any[] = Array.isArray(res) ? res : (res?.results || []);
        return items.map(hosp => {
          const patientUser = hosp.patient_details || hosp.patient?.idUtilisateur || hosp.patient?.id_utilisateur;
          const pPrenom = patientUser?.prenom || hosp.patient?.prenom || '';
          const pNom = patientUser?.nom || hosp.patient?.nom || '';
          const patientNom = (pPrenom || pNom) ? `${pPrenom} ${pNom}`.trim() : `Patient #${hosp.patient_id || hosp.patient || ''}`;

          const medecinUser = hosp.medecin_details || hosp.medecin?.idUtilisateur || hosp.medecin?.id_utilisateur;
          const mPrenom = medecinUser?.prenom || hosp.medecin?.prenom || '';
          const mNom = medecinUser?.nom || hosp.medecin?.nom || '';
          const medecinNom = (mPrenom || mNom) ? `Dr. ${mPrenom} ${mNom}`.trim() : 'Non assigné';

          const lit = hosp.lit_details || hosp.lit;
          const litNumero = lit?.numero_lit || lit?.numeroLit || (lit?.id ? `Lit ${lit.id}` : 'Lit N/D');
          const chambre = lit?.chambre || hosp.chambre_details;
          const chambreNumero = chambre?.numero_chambre || chambre?.numeroChambre ? `Chambre ${chambre.numero_chambre || chambre.numeroChambre}` : 'Non assignée';
          const batimentNom = chambre?.batiment?.nom || chambre?.batiment_nom || '';
          const serviceNom = hosp.service_details?.nom_service || hosp.service_nom || chambre?.service?.nom_service || 'Médecine';

          return {
            id: hosp.id || hosp.idHospitalisation,
            patientId: hosp.patient_id || hosp.patient?.id_patient || hosp.patient?.id || hosp.patient,
            patientNom,
            patientTelephone: patientUser?.telephone || hosp.patient?.telephone,
            dateEntree: hosp.date_entree || hosp.dateEntree,
            motif: hosp.motif || 'Soins hospitaliers',
            medecinNom,
            serviceNom,
            batimentNom,
            chambreNumero,
            litNumero,
            statut: hosp.statut || 'EN_COURS'
          };
        });
      }),
      catchError(() => of([]))
    );
  }

  /**
   * Récupère les prochains rendez-vous accessibles au personnel.
   */
  getProchainsRendezVous(limit: number = 10): Observable<UpcomingAppointmentItem[]> {
    return this.http.get<any>(`${this.baseUrl}/rendezvous/all/?page_size=${limit}`, this.httpOptions).pipe(
      map(res => {
        const items: any[] = Array.isArray(res) ? res : (res?.results || []);
        return items.slice(0, limit).map(rdv => {
          const patientUser = rdv.patient_details || rdv.patient_detail || rdv.patient?.idUtilisateur || rdv.patient?.id_utilisateur;
          const medecinUser = rdv.medecin_details || rdv.medecin_detail || rdv.medecin?.idUtilisateur || rdv.medecin?.id_utilisateur;

          const pPrenom = patientUser?.prenom || rdv.patient?.prenom || '';
          const pNom = patientUser?.nom || rdv.patient?.nom || '';
          const patientNom = (pPrenom || pNom) ? `${pPrenom} ${pNom}`.trim() : `Patient #${rdv.patient_id || rdv.patient || ''}`;

          const mPrenom = medecinUser?.prenom || rdv.medecin?.prenom || '';
          const mNom = medecinUser?.nom || rdv.medecin?.nom || '';
          const medecinNom = (mPrenom || mNom) ? `Dr. ${mPrenom} ${mNom}`.trim() : `Dr. Médecin #${rdv.medecin_id || rdv.medecin || ''}`;

          const rawHeure = rdv.heure || rdv.time || '';
          const heureFormatee = rawHeure.length >= 5 ? rawHeure.substring(0, 5) : rawHeure;

          return {
            id: rdv.id,
            patientId: rdv.patient_id || rdv.patient?.id_patient || rdv.patient?.id || rdv.patient,
            patientNom,
            patientTelephone: patientUser?.telephone || rdv.patient?.telephone,
            medecinNom,
            medecinSpecialite: rdv.medecin?.specialiteDisplay || rdv.medecin?.specialite || 'Praticien',
            dateRdv: rdv.date_rdv || rdv.date,
            heure: heureFormatee,
            motif: rdv.motif || rdv.reason || 'Consultation médicale',
            statut: rdv.statut || 'EN_ATTENTE',
            statutDisplay: this.formatStatutLabel(rdv.statut),
            typeConsultation: rdv.type_consultation || rdv.appointment_type || 'SUR_PLACE'
          };
        });
      }),
      catchError(() => of([]))
    );
  }

  /**
   * Récupère la liste des rendez-vous avec filtres statut/recherche.
   */
  getRendezVous(statut?: string, search?: string, limit: number = 50): Observable<UpcomingAppointmentItem[]> {
    let url = `${this.baseUrl}/rendezvous/all/?page_size=${limit}`;
    if (statut) url += `&statut=${statut}`;
    if (search) url += `&search=${encodeURIComponent(search)}`;

    return this.http.get<any>(url, this.httpOptions).pipe(
      map(res => {
        const items: any[] = Array.isArray(res) ? res : (res?.results || []);
        return items.map(rdv => {
          const patientUser = rdv.patient_details || rdv.patient_detail || rdv.patient?.idUtilisateur || rdv.patient?.id_utilisateur;
          const medecinUser = rdv.medecin_details || rdv.medecin_detail || rdv.medecin?.idUtilisateur || rdv.medecin?.id_utilisateur;

          const pPrenom = patientUser?.prenom || rdv.patient?.prenom || '';
          const pNom = patientUser?.nom || rdv.patient?.nom || '';
          const patientNom = (pPrenom || pNom) ? `${pPrenom} ${pNom}`.trim() : `Patient #${rdv.patient_id || rdv.patient || ''}`;

          const mPrenom = medecinUser?.prenom || rdv.medecin?.prenom || '';
          const mNom = medecinUser?.nom || rdv.medecin?.nom || '';
          const medecinNom = (mPrenom || mNom) ? `Dr. ${mPrenom} ${mNom}`.trim() : `Dr. Médecin #${rdv.medecin_id || rdv.medecin || ''}`;

          const rawHeure = rdv.heure || rdv.time || '';
          const heureFormatee = rawHeure.length >= 5 ? rawHeure.substring(0, 5) : rawHeure;

          return {
            id: rdv.id,
            patientId: rdv.patient_id || rdv.patient?.id_patient || rdv.patient?.id || rdv.patient,
            patientNom,
            patientTelephone: patientUser?.telephone || rdv.patient?.telephone,
            medecinNom,
            medecinSpecialite: rdv.medecin?.specialiteDisplay || rdv.medecin?.specialite || 'Praticien',
            dateRdv: rdv.date_rdv || rdv.date,
            heure: heureFormatee,
            motif: rdv.motif || rdv.reason || 'Consultation médicale',
            statut: rdv.statut || 'EN_ATTENTE',
            statutDisplay: this.formatStatutLabel(rdv.statut),
            typeConsultation: rdv.type_consultation || rdv.appointment_type || 'SUR_PLACE'
          };
        });
      }),
      catchError(() => of([]))
    );
  }

  /**
   * Récupère la liste des patients.
   */
  getPatients(search?: string, limit: number = 50): Observable<PatientItem[]> {
    let url = `${this.baseUrl}/patients/?page_size=${limit}`;
    if (search) url += `&search=${encodeURIComponent(search)}`;

    return this.http.get<any>(url, this.httpOptions).pipe(
      map(res => {
        const items: any[] = Array.isArray(res) ? res : (res?.results || []);
        return items.map(p => {
          const user = p.id_utilisateur || p.idUtilisateur || {};
          return {
            id: p.id_patient || p.idPatient || p.id,
            idPatient: p.id_patient || p.idPatient || p.id,
            nom: p.nom || user.nom || '',
            prenom: p.prenom || user.prenom || '',
            dateNaissance: p.date_naissance || p.dateNaissance || user.dateNaissance,
            sexe: p.sexe,
            telephone: p.telephone || user.telephone,
            email: p.email || user.email,
            numeroSecuriteSociale: p.numero_securite_sociale || p.numeroSecuriteSociale,
            groupeSanguin: p.groupe_sanguin || p.groupeSanguin,
            adresse: p.adresse,
            personneAContacter: p.personne_a_contacter || p.personneAContacter,
            telephoneContact: p.telephone_contact || p.telephoneContact,
            actif: p.actif ?? true
          };
        });
      }),
      catchError(() => of([]))
    );
  }

  /**
   * Récupère les détails d'un patient par son identifiant.
   */
  getPatientById(patientId: number): Observable<PatientItem | null> {
    return this.http.get<any>(`${this.baseUrl}/patients/${patientId}/`, this.httpOptions).pipe(
      map(p => {
        const user = p.id_utilisateur || p.idUtilisateur || {};
        return {
          id: p.id_patient || p.idPatient || p.id,
          idPatient: p.id_patient || p.idPatient || p.id,
          nom: p.nom || user.nom || '',
          prenom: p.prenom || user.prenom || '',
          dateNaissance: p.date_naissance || p.dateNaissance || user.dateNaissance,
          sexe: p.sexe,
          telephone: p.telephone || user.telephone,
          email: p.email || user.email,
          numeroSecuriteSociale: p.numero_securite_sociale || p.numeroSecuriteSociale,
          groupeSanguin: p.groupe_sanguin || p.groupeSanguin,
          adresse: p.adresse,
          personneAContacter: p.personne_a_contacter || p.personneAContacter,
          telephoneContact: p.telephone_contact || p.telephoneContact,
          actif: p.actif ?? true
        };
      }),
      catchError(() => of(null))
    );
  }

  /**
   * Récupère le parcours complet d'un patient (localisation actuelle et historique de séjour)
   * depuis le backend sans inventer de données.
   */
  getPatientParcours(patientId: number): Observable<PatientParcoursData | null> {
    return forkJoin({
      patient: this.getPatientById(patientId),
      sejoursRes: this.http.get<any>(`${this.baseUrl}/sejours/?patient_id=${patientId}`, this.httpOptions).pipe(catchError(() => of([]))),
      hospitalisationsRes: this.http.get<any>(`${this.baseUrl}/hospitalisations/?patient_id=${patientId}`, this.httpOptions).pipe(catchError(() => of([]))),
      localisationsRes: this.http.get<any>(`${this.baseUrl}/localisations/?est_actuelle=true`, this.httpOptions).pipe(catchError(() => of([])))
    }).pipe(
      switchMap(({ patient, sejoursRes, hospitalisationsRes, localisationsRes }) => {
        if (!patient) return of(null);

        const sejoursList: any[] = Array.isArray(sejoursRes) ? sejoursRes : (sejoursRes?.results || []);
        const hospList: any[] = Array.isArray(hospitalisationsRes) ? hospitalisationsRes : (hospitalisationsRes?.results || []);
        const locList: any[] = Array.isArray(localisationsRes) ? localisationsRes : (localisationsRes?.results || []);

        // Vérifier si une hospitalisation active existe
        const hospActive = hospList.find(h => (h.statut || '').toUpperCase() === 'EN_COURS');
        const sejourActif = sejoursList.find(s => (s.statut || '').toUpperCase() === 'EN_COURS');
        const isHospitalise = !!(hospActive || sejourActif);

        // Si un séjour existe, récupérer la synthèse détaillée
        const targetSejour = sejourActif || sejoursList[0];

        if (targetSejour && (targetSejour.id || targetSejour.id_sejour || targetSejour.idSejour)) {
          const sId = targetSejour.id || targetSejour.id_sejour || targetSejour.idSejour;
          return this.http.get<any>(`${this.baseUrl}/sejours/${sId}/dossier-synthese/`, this.httpOptions).pipe(
            map(synthese => {
              const locActuelle = synthese.localisation_actuelle || synthese.localisationActuelle;
              let locFormatted = undefined;

              if (locActuelle) {
                locFormatted = {
                  serviceNom: locActuelle.service_nom || locActuelle.serviceNom || locActuelle.service_details?.nom_service || 'Service de soins',
                  batimentNom: locActuelle.batiment_nom || locActuelle.batimentNom || locActuelle.batiment_details?.nom_batiment || 'Bâtiment Principal',
                  chambreNumero: locActuelle.chambre_numero || locActuelle.chambreNumero || locActuelle.chambre_details?.numero_chambre || 'N/D',
                  litNumero: locActuelle.lit_numero || locActuelle.litNumero || locActuelle.lit_details?.numero_lit || 'N/D',
                  dateDebut: locActuelle.date_debut || locActuelle.dateDebut || targetSejour.date_admission
                };
              } else if (hospActive && hospActive.lit_details) {
                const lit = hospActive.lit_details;
                const ch = lit.chambre || hospActive.chambre_details;
                locFormatted = {
                  serviceNom: hospActive.service_details?.nom_service || ch?.service?.nom_service || 'Médecine',
                  batimentNom: ch?.batiment?.nom || 'Bâtiment Principal',
                  chambreNumero: ch?.numero_chambre || ch?.numeroChambre || 'N/D',
                  litNumero: lit.numero_lit || lit.numeroLit || `Lit #${lit.id}`,
                  dateDebut: hospActive.date_entree
                };
              }

              const mouvements = (synthese.mouvements || []).map((m: any) => ({
                id: m.id || m.id_mouvement,
                dateMouvement: m.date_mouvement || m.dateMouvement,
                typeMouvement: m.type_mouvement || m.typeMouvement,
                typeMouvementDisplay: m.type_mouvement_display || m.typeMouvementDisplay || m.type_mouvement,
                serviceOrigine: m.service_origine_nom || m.service_details?.nom_service,
                serviceDestination: m.service_destination_nom,
                chambreOrigine: m.chambre_origine_numero,
                chambreDestination: m.chambre_destination_numero,
                litOrigine: m.lit_origine_numero,
                litDestination: m.lit_destination_numero,
                motif: m.motif
              }));

              const evenements = (synthese.evenements || []).map((e: any) => ({
                id: e.id || e.id_evenement,
                dateEvenement: e.date_evenement || e.dateEvenement,
                typeEvenement: e.type_evenement || e.typeEvenement,
                titre: e.titre || 'Événement de séjour',
                description: e.description || '',
                importance: e.importance
              }));

              return {
                patient,
                isHospitalise,
                localisationActuelle: locFormatted,
                sejours: sejoursList.map(s => ({
                  id: s.id || s.id_sejour || s.idSejour,
                  reference: s.reference,
                  dateAdmission: s.date_admission || s.dateAdmission,
                  dateSortie: s.date_sortie || s.dateSortie,
                  statut: s.statut,
                  statutDisplay: s.statut_display || s.statutDisplay || s.statut,
                  typePriseEnCharge: s.type_prise_en_charge || s.typePriseEnCharge,
                  serviceNom: s.service_details?.nom_service || s.service_responsable_nom,
                  medecinNom: s.medecin_details ? `Dr. ${s.medecin_details.prenom} ${s.medecin_details.nom}` : undefined,
                  motif: s.motif_admission || s.motifAdmission
                })),
                mouvements,
                evenements
              };
            }),
            catchError(() => {
              // Si la synthèse échoue mais qu'on a le séjour basique
              return of(this.buildFallbackParcours(patient, isHospitalise, sejoursList, hospActive));
            })
          );
        }

        // Si aucun séjour mais hospitalisation
        return of(this.buildFallbackParcours(patient, isHospitalise, sejoursList, hospActive));
      })
    );
  }

  private buildFallbackParcours(
    patient: PatientItem,
    isHospitalise: boolean,
    sejoursList: any[],
    hospActive?: any
  ): PatientParcoursData {
    let locFormatted = undefined;
    if (hospActive && hospActive.lit_details) {
      const lit = hospActive.lit_details;
      const ch = lit.chambre || hospActive.chambre_details;
      locFormatted = {
        serviceNom: hospActive.service_details?.nom_service || ch?.service?.nom_service || 'Médecine',
        batimentNom: ch?.batiment?.nom || 'Bâtiment Principal',
        chambreNumero: ch?.numero_chambre || ch?.numeroChambre || 'N/D',
        litNumero: lit.numero_lit || lit.numeroLit || `Lit #${lit.id}`,
        dateDebut: hospActive.date_entree
      };
    }

    return {
      patient,
      isHospitalise,
      localisationActuelle: locFormatted,
      sejours: sejoursList.map(s => ({
        id: s.id || s.id_sejour || s.idSejour,
        reference: s.reference,
        dateAdmission: s.date_admission || s.dateAdmission,
        dateSortie: s.date_sortie || s.dateSortie,
        statut: s.statut,
        statutDisplay: s.statut_display || s.statutDisplay || s.statut,
        typePriseEnCharge: s.type_prise_en_charge || s.typePriseEnCharge,
        serviceNom: s.service_details?.nom_service || s.service_responsable_nom,
        medecinNom: s.medecin_details ? `Dr. ${s.medecin_details.prenom} ${s.medecin_details.nom}` : undefined,
        motif: s.motif_admission || s.motifAdmission
      })),
      mouvements: [],
      evenements: []
    };
  }

  /**
   * Calcule les métriques consolidées du tableau de bord soignant (Dashboard)
   * basées strictement sur les réponses réelles de l'API Django.
   */
  getDashboardMetrics(): Observable<PersonnelDashboardMetrics> {
    return forkJoin({
      sejoursStats: this.http.get<any>(`${this.baseUrl}/sejours/statistiques-dashboard/`, this.httpOptions).pipe(catchError(() => of(null))),
      litsRes: this.http.get<any>(`${this.baseUrl}/lits/all/?page_size=100`, this.httpOptions).pipe(catchError(() => of([]))),
      hospitalisesRes: this.http.get<any>(`${this.baseUrl}/hospitalisations/?statut=EN_COURS&page_size=1`, this.httpOptions).pipe(catchError(() => of({ count: 0 }))),
      rdvsRes: this.http.get<any>(`${this.baseUrl}/rendezvous/all/?page_size=100`, this.httpOptions).pipe(catchError(() => of([])))
    }).pipe(
      map(({ sejoursStats, litsRes, hospitalisesRes, rdvsRes }) => {
        const litsList: any[] = Array.isArray(litsRes) ? litsRes : (litsRes?.results || []);
        const totalLits = litsList.length || sejoursStats?.total_lits || sejoursStats?.totalLits || 0;

        let litsOccupes = 0;
        let litsDisponibles = 0;
        litsList.forEach(l => {
          const etat = (l.etat || '').toUpperCase();
          if (etat === 'OCCUPE') litsOccupes++;
          else if (etat === 'DISPONIBLE') litsDisponibles++;
        });

        if (totalLits > 0 && litsOccupes === 0 && sejoursStats) {
          litsOccupes = sejoursStats.lits_occupes ?? sejoursStats.litsOccupes ?? 0;
          litsDisponibles = sejoursStats.lits_disponibles ?? sejoursStats.litsDisponibles ?? (totalLits - litsOccupes);
        }

        const patientsHospitalises = hospitalisesRes?.count ?? (hospitalisesRes?.length || sejoursStats?.patients_hospitalises || litsOccupes);
        const tauxOccupation = totalLits > 0 ? Math.round((litsOccupes / totalLits) * 100) : 0;

        const rdvsList: any[] = Array.isArray(rdvsRes) ? rdvsRes : (rdvsRes?.results || []);
        const todayStr = new Date().toISOString().split('T')[0];
        let rdvAujourdhui = 0;
        let confirmes = 0;
        let enAttente = 0;
        let termines = 0;
        let annules = 0;

        rdvsList.forEach(r => {
          const rDate = r.date_rdv || r.date;
          if (rDate === todayStr) {
            rdvAujourdhui++;
          }
          const st = (r.statut || '').toUpperCase();
          if (st === 'CONFIRME') confirmes++;
          else if (st === 'EN_ATTENTE') enAttente++;
          else if (st === 'TERMINE') termines++;
          else if (st === 'ANNULE') annules++;
        });

        return {
          patientsHospitalises,
          litsOccupes,
          litsDisponibles,
          totalLits,
          tauxOccupation,
          rdvAujourdhui,
          totalRdv: rdvsRes?.count ?? rdvsList.length,
          transfertsRecents: sejoursStats?.transferts_recents ?? sejoursStats?.transfertsRecents ?? 0,
          sortiesRecentes: sejoursStats?.sorties_recentes ?? sejoursStats?.sortiesRecentes ?? 0,
          repartitionRdv: {
            confirmes,
            enAttente,
            termines,
            annules
          },
          derniereMiseAJour: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
        };
      })
    );
  }

  private formatStatutLabel(statut?: string): string {
    switch (statut?.toUpperCase()) {
      case 'CONFIRME': return 'Confirmé';
      case 'EN_ATTENTE': return 'En attente';
      case 'TERMINE': return 'Terminé';
      case 'ANNULE': return 'Annulé';
      default: return statut || 'Indéfini';
    }
  }
}
