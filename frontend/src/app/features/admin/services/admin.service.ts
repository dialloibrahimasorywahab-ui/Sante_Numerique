import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, forkJoin, of } from 'rxjs';
import { map, catchError } from 'rxjs/operators';
import { environment } from '../../../../environments/environment';
import {
  AdminGlobalStats,
  BedOccupancyStats,
  FinancialStats,
  RecentAppointmentItem,
  CurrentHospitalizationItem,
  HospitalServiceSummary,
  RecentActivityItem,
  PaginatedResponse
} from '../models/admin.model';

@Injectable({
  providedIn: 'root'
})
export class AdminService {
  private http = inject(HttpClient);

  private get apiUrl(): string {
    return environment.apiUrl;
  }

  private get httpOptions() {
    return { withCredentials: true };
  }

  /**
   * Récupère le comptage global pour l'ensemble des modules hospitaliers.
   */
  getGlobalStats(): Observable<AdminGlobalStats> {
    return forkJoin({
      users: this.http.get<PaginatedResponse<any> | any[]>(`${this.apiUrl}/users/all/?page_size=1`, this.httpOptions).pipe(catchError(() => of({ count: 0 }))),
      medecins: this.http.get<PaginatedResponse<any> | any[]>(`${this.apiUrl}/medecins/all/?page_size=1`, this.httpOptions).pipe(catchError(() => of({ count: 0 }))),
      personnel: this.http.get<PaginatedResponse<any> | any[]>(`${this.apiUrl}/personnel/all/?page_size=1`, this.httpOptions).pipe(catchError(() => of({ count: 0 }))),
      patients: this.http.get<PaginatedResponse<any> | any[]>(`${this.apiUrl}/patients/all/?page_size=1`, this.httpOptions).pipe(catchError(() => of({ count: 0 }))),
      rendezvous: this.http.get<PaginatedResponse<any> | any[]>(`${this.apiUrl}/rendezvous/all/?page_size=1`, this.httpOptions).pipe(catchError(() => of({ count: 0 }))),
      consultations: this.http.get<PaginatedResponse<any> | any[]>(`${this.apiUrl}/consultations/?page_size=1`, this.httpOptions).pipe(catchError(() => of({ count: 0 }))),
      hospitalisations: this.http.get<PaginatedResponse<any> | any[]>(`${this.apiUrl}/hospitalisations/?page_size=1`, this.httpOptions).pipe(catchError(() => of({ count: 0 }))),
      ordonnances: this.http.get<PaginatedResponse<any> | any[]>(`${this.apiUrl}/ordonnances/?page_size=1`, this.httpOptions).pipe(catchError(() => of({ count: 0 }))),
      batiments: this.http.get<PaginatedResponse<any> | any[]>(`${this.apiUrl}/batiments/all/?page_size=1`, this.httpOptions).pipe(catchError(() => of({ count: 0 }))),
      chambres: this.http.get<PaginatedResponse<any> | any[]>(`${this.apiUrl}/chambres/all/?page_size=1`, this.httpOptions).pipe(catchError(() => of({ count: 0 }))),
      lits: this.http.get<PaginatedResponse<any> | any[]>(`${this.apiUrl}/lits/all/?page_size=1`, this.httpOptions).pipe(catchError(() => of({ count: 0 }))),
      services: this.http.get<PaginatedResponse<any> | any[]>(`${this.apiUrl}/services/all/?page_size=1`, this.httpOptions).pipe(catchError(() => of({ count: 0 })))
    }).pipe(
      map(res => ({
        usersCount: this.extractCount(res.users),
        medecinsCount: this.extractCount(res.medecins),
        personnelCount: this.extractCount(res.personnel),
        patientsCount: this.extractCount(res.patients),
        rendezvousCount: this.extractCount(res.rendezvous),
        consultationsCount: this.extractCount(res.consultations),
        hospitalisationsCount: this.extractCount(res.hospitalisations),
        ordonnancesCount: this.extractCount(res.ordonnances),
        batimentsCount: this.extractCount(res.batiments),
        chambresCount: this.extractCount(res.chambres),
        litsCount: this.extractCount(res.lits),
        servicesCount: this.extractCount(res.services)
      }))
    );
  }

  /**
   * Calcule les statistiques réelles d'occupation des lits à partir de l'API.
   */
  getBedOccupancyStats(): Observable<BedOccupancyStats> {
    return this.http.get<PaginatedResponse<any> | any[]>(`${this.apiUrl}/lits/all/?page_size=100`, this.httpOptions).pipe(
      map(res => {
        const items: any[] = Array.isArray(res) ? res : (res?.results || []);
        const totalLits = items.length;
        let litsDisponibles = 0;
        let litsOccupes = 0;
        let litsReserves = 0;
        let litsMaintenance = 0;

        items.forEach(lit => {
          const etat = (lit.etat || '').toUpperCase();
          if (etat === 'DISPONIBLE') {
            litsDisponibles++;
          } else if (etat === 'OCCUPE') {
            litsOccupes++;
          } else if (etat === 'RESERVE') {
            litsReserves++;
          } else if (etat === 'EN_NETTOYAGE' || etat === 'HORS_SERVICE') {
            litsMaintenance++;
          } else {
            litsDisponibles++;
          }
        });

        const tauxOccupation = totalLits > 0 ? Math.round((litsOccupes / totalLits) * 100) : 0;

        return {
          totalLits,
          litsDisponibles,
          litsOccupes,
          litsReserves,
          litsMaintenance,
          tauxOccupation
        };
      }),
      catchError(() => of({
        totalLits: 0,
        litsDisponibles: 0,
        litsOccupes: 0,
        litsReserves: 0,
        litsMaintenance: 0,
        tauxOccupation: 0
      }))
    );
  }

  /**
   * Calcule le bilan financier réel des frais de consultations.
   */
  getFinancialStats(): Observable<FinancialStats> {
    return this.http.get<PaginatedResponse<any> | any[]>(`${this.apiUrl}/frais_consultations/?page_size=100`, this.httpOptions).pipe(
      map(res => {
        const items: any[] = Array.isArray(res) ? res : (res?.results || []);
        let totalMontant = 0;
        let montantPaye = 0;
        let montantEnAttente = 0;
        let montantAnnule = 0;
        let countPaye = 0;
        let countEnAttente = 0;

        items.forEach(item => {
          const montant = parseFloat(item.montant) || 0;
          const statut = (item.statut || '').toUpperCase();
          totalMontant += montant;

          if (statut === 'PAYE') {
            montantPaye += montant;
            countPaye++;
          } else if (statut === 'EN_ATTENTE') {
            montantEnAttente += montant;
            countEnAttente++;
          } else if (statut === 'ANNULE') {
            montantAnnule += montant;
          }
        });

        const tauxRecouvrement = totalMontant > 0 ? Math.round((montantPaye / totalMontant) * 100) : 0;

        return {
          totalMontant,
          montantPaye,
          montantEnAttente,
          montantAnnule,
          countPaye,
          countEnAttente,
          tauxRecouvrement
        };
      }),
      catchError(() => of({
        totalMontant: 0,
        montantPaye: 0,
        montantEnAttente: 0,
        montantAnnule: 0,
        countPaye: 0,
        countEnAttente: 0,
        tauxRecouvrement: 0
      }))
    );
  }

  /**
   * Récupère les rendez-vous récents.
   */
  getRecentAppointments(limit: number = 6): Observable<RecentAppointmentItem[]> {
    return this.http.get<PaginatedResponse<any> | any[]>(`${this.apiUrl}/rendezvous/all/?page_size=${limit}`, this.httpOptions).pipe(
      map(res => {
        const items: any[] = Array.isArray(res) ? res : (res?.results || []);
        return items.slice(0, limit).map(rdv => {
          const patientUser = rdv.patient_details || rdv.patient_detail || rdv.patient?.idUtilisateur || rdv.patient?.id_utilisateur;
          const medecinUser = rdv.medecin_details || rdv.medecin_detail || rdv.medecin?.idUtilisateur || rdv.medecin?.id_utilisateur;

          const pPrenom = patientUser?.prenom || '';
          const pNom = patientUser?.nom || '';
          const patientNom = (pPrenom || pNom) ? `${pPrenom} ${pNom}`.trim() : `Patient #${rdv.patient_id || rdv.patient || ''}`;

          const mPrenom = medecinUser?.prenom || '';
          const mNom = medecinUser?.nom || '';
          const medecinNom = (mPrenom || mNom) ? `Dr. ${mPrenom} ${mNom}`.trim() : `Dr. Médecin #${rdv.medecin_id || rdv.medecin || ''}`;

          return {
            id: rdv.id,
            patientNom,
            patientTelephone: patientUser?.telephone || '',
            medecinNom,
            medecinSpecialite: rdv.medecin?.specialiteDisplay || rdv.medecin?.specialite || '',
            dateRdv: rdv.date_rdv,
            heure: rdv.heure ? rdv.heure.substring(0, 5) : '',
            motif: rdv.motif || 'Consultation générale',
            statut: rdv.statut || 'EN_ATTENTE',
            statutDisplay: this.getRdvStatutLabel(rdv.statut)
          };
        });
      }),
      catchError(() => of([]))
    );
  }

  /**
   * Récupère les hospitalisations actuellement en cours.
   */
  getCurrentHospitalizations(limit: number = 6): Observable<CurrentHospitalizationItem[]> {
    return this.http.get<PaginatedResponse<any> | any[]>(`${this.apiUrl}/hospitalisations/?statut=EN_COURS&page_size=${limit}`, this.httpOptions).pipe(
      map(res => {
        const items: any[] = Array.isArray(res) ? res : (res?.results || []);
        return items.slice(0, limit).map(hosp => {
          const patientUser = hosp.patient_details || hosp.patient?.idUtilisateur || hosp.patient?.id_utilisateur;
          const medecinUser = hosp.medecin_details || hosp.medecin?.idUtilisateur || hosp.medecin?.id_utilisateur;

          const pPrenom = patientUser?.prenom || '';
          const pNom = patientUser?.nom || '';
          const patientNom = (pPrenom || pNom) ? `${pPrenom} ${pNom}`.trim() : `Patient #${hosp.patient_id || hosp.patient || ''}`;

          const mPrenom = medecinUser?.prenom || '';
          const mNom = medecinUser?.nom || '';
          const medecinNom = (mPrenom || mNom) ? `Dr. ${mPrenom} ${mNom}`.trim() : 'Non assigné';

          const lit = hosp.lit_details || hosp.lit;
          const litNumero = lit?.numero_lit || (lit?.id ? `Lit #${lit.id}` : 'Lit N/D');
          const chambre = lit?.chambre || hosp.chambre_details;
          const chambreNumero = chambre?.numero_chambre ? `Chambre ${chambre.numero_chambre}` : '';
          const batimentNom = chambre?.batiment?.nom || '';

          return {
            id: hosp.id,
            patientNom,
            patientId: hosp.patient_id || hosp.patient?.id_patient || hosp.patient?.id,
            medecinNom,
            litNumero,
            chambreNumero,
            batimentNom,
            dateEntree: hosp.date_entree,
            motif: hosp.motif || 'Soins hospitaliers',
            statut: hosp.statut || 'EN_COURS'
          };
        });
      }),
      catchError(() => of([]))
    );
  }

  /**
   * Récupère les pôles de soins et calcule la répartition des effectifs.
   */
  getHospitalServicesSummary(): Observable<HospitalServiceSummary[]> {
    return forkJoin({
      services: this.http.get<PaginatedResponse<any> | any[]>(`${this.apiUrl}/services/all/?page_size=100`, this.httpOptions).pipe(catchError(() => of([]))),
      medecins: this.http.get<PaginatedResponse<any> | any[]>(`${this.apiUrl}/medecins/all/?page_size=100`, this.httpOptions).pipe(catchError(() => of([]))),
      personnel: this.http.get<PaginatedResponse<any> | any[]>(`${this.apiUrl}/personnel/all/?page_size=100`, this.httpOptions).pipe(catchError(() => of([])))
    }).pipe(
      map(({ services, medecins, personnel }) => {
        const sList: any[] = Array.isArray(services) ? services : (services?.results || []);
        const mList: any[] = Array.isArray(medecins) ? medecins : (medecins?.results || []);
        const pList: any[] = Array.isArray(personnel) ? personnel : (personnel?.results || []);

        return sList.map(srv => {
          const srvId = srv.id_service || srv.id;
          const srvName = (srv.nom_service || srv.nomService || '').toUpperCase();

          // Compter médecins
          const medecinsCount = mList.filter(m => {
            const spec = (m.specialite || '').toUpperCase();
            return spec === srvName || spec.includes(srvName) || srvName.includes(spec);
          }).length;

          // Compter personnel
          const personnelCount = pList.filter(p => {
            const pSrvId = p.id_service || p.idService || (p.service?.id_service);
            const pSrvHop = (p.service_hopital || p.serviceHopital || '').toUpperCase();
            return pSrvId === srvId || pSrvHop === srvName || pSrvHop.includes(srvName);
          }).length;

          return {
            id: srvId,
            nom: srv.nom_service_display || srv.nom_service || srv.nomService || 'Service Hospitalier',
            description: srv.description || 'Pôle de soins spécialisé',
            bureauLocalisation: srv.bureau_localisation || srv.bureauLocalisation || 'Bâtiment Principal',
            medecinsCount,
            personnelCount
          };
        });
      }),
      catchError(() => of([]))
    );
  }

  /**
   * Construit un flux d'activité récente combiné à partir des données réelles de l'API.
   */
  getRecentActivityFeed(): Observable<RecentActivityItem[]> {
    return forkJoin({
      rdvs: this.getRecentAppointments(4),
      hosps: this.getCurrentHospitalizations(4),
      consultations: this.http.get<PaginatedResponse<any> | any[]>(`${this.apiUrl}/consultations/?page_size=4`, this.httpOptions).pipe(catchError(() => of([])))
    }).pipe(
      map(({ rdvs, hosps, consultations }) => {
        const activities: RecentActivityItem[] = [];

        // RDV
        rdvs.forEach(r => {
          activities.push({
            id: `rdv-${r.id}`,
            type: 'RENDEZVOUS',
            title: `Rendez-vous : ${r.patientNom}`,
            subtitle: `Avec ${r.medecinNom} — ${r.motif}`,
            date: r.dateRdv ? `${r.dateRdv} à ${r.heure}` : 'Récemment',
            badge: r.statutDisplay,
            badgeClass: this.getRdvBadgeClass(r.statut),
            icon: 'calendar'
          });
        });

        // Hospitalisations
        hosps.forEach(h => {
          activities.push({
            id: `hosp-${h.id}`,
            type: 'HOSPITALISATION',
            title: `Admission : ${h.patientNom}`,
            subtitle: `${h.litNumero} (${h.chambreNumero}) — Dr. ${h.medecinNom}`,
            date: h.dateEntree ? h.dateEntree.substring(0, 10) : 'En cours',
            badge: 'Hospitalisé',
            badgeClass: 'badge-hospitalise',
            icon: 'hospital'
          });
        });

        // Consultations
        const cList: any[] = Array.isArray(consultations) ? consultations : (consultations?.results || []);
        cList.slice(0, 4).forEach((c: any) => {
          const pUser = c.patient_details || c.patient?.idUtilisateur;
          const pNom = pUser ? `${pUser.prenom} ${pUser.nom}` : `Patient #${c.patient_id || ''}`;
          activities.push({
            id: `cons-${c.id}`,
            type: 'CONSULTATION',
            title: `Consultation : ${pNom}`,
            subtitle: c.diagnostic || c.symptomes || 'Examen clinique',
            date: c.date_cons ? c.date_cons.substring(0, 10) : 'Récemment',
            badge: 'Consultation',
            badgeClass: 'badge-consultation',
            icon: 'stethoscope'
          });
        });

        // Tri chronologique descendant
        return activities.slice(0, 8);
      }),
      catchError(() => of([]))
    );
  }

  /**
   * Méthode générique pour lister les entités paginées avec recherche et filtres.
   */
  getEntityList(resource: string, page: number = 1, search: string = '', extraParams: any = {}): Observable<PaginatedResponse<any>> {
    let params: any = { page: page.toString() };
    if (search && search.trim()) {
      params.search = search.trim();
    }
    if (extraParams) {
      params = { ...params, ...extraParams };
    }

    return this.http.get<any>(`${this.apiUrl}/${resource}/`, {
      params,
      ...this.httpOptions
    }).pipe(
      map(res => {
        if (Array.isArray(res)) {
          return { count: res.length, results: res, next: null, previous: null };
        }
        return {
          count: res.count ?? res.results?.length ?? 0,
          next: res.next,
          previous: res.previous,
          results: res.results || []
        };
      }),
      catchError(() => of({ count: 0, results: [], next: null, previous: null }))
    );
  }

  getEntityDetail(resource: string, id: string | number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/${resource}/${id}/`, this.httpOptions);
  }

  /**
   * Marquer un frais de consultation comme Payé.
   */
  markFraisAsPaid(id: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/frais_consultations/${id}/payer/`, {}, this.httpOptions);
  }

  /**
   * Créer une entité (Patient, Médecin, Personnel, Bâtiment, etc.).
   */
  createEntity(resource: string, data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/${resource}/`, data, this.httpOptions);
  }

  /**
   * Suspendre ou réactiver le compte d'un utilisateur.
   */
  toggleUserStatus(userId: number, actif: boolean): Observable<any> {
    return this.http.patch(`${this.apiUrl}/users/${userId}/`, { actif }, this.httpOptions);
  }

  /**
   * Changer le statut actif/inactif d'un bâtiment.
   */
  toggleBatimentStatus(batimentId: number, actif: boolean): Observable<any> {
    return this.http.patch(`${this.apiUrl}/batiments/${batimentId}/update/`, { actif }, this.httpOptions).pipe(
      catchError(() => this.http.patch(`${this.apiUrl}/batiments/${batimentId}/`, { actif }, this.httpOptions))
    );
  }

  /**
   * Mettre à jour une entité.
   */
  updateEntity(resource: string, id: number, data: any): Observable<any> {
    return this.http.patch(`${this.apiUrl}/${resource}/${id}/update/`, data, this.httpOptions).pipe(
      catchError(() => this.http.patch(`${this.apiUrl}/${resource}/${id}/`, data, this.httpOptions))
    );
  }

  /**
   * Supprimer une entité (soft delete ou hard delete).
   */
  deleteEntity(resource: string, id: number, hard: boolean = false): Observable<any> {
    const url = `${this.apiUrl}/${resource}/${id}/delete/${hard ? '?hard=true' : ''}`;
    return this.http.delete(url, this.httpOptions).pipe(
      catchError(() => this.http.delete(`${this.apiUrl}/${resource}/${id}/`, this.httpOptions))
    );
  }

  private extractCount(res: any): number {
    if (res && typeof res.count === 'number') {
      return res.count;
    }
    if (Array.isArray(res)) {
      return res.length;
    }
    if (res && Array.isArray(res.results)) {
      return res.results.length;
    }
    return 0;
  }

  private getRdvStatutLabel(statut: string): string {
    switch ((statut || '').toUpperCase()) {
      case 'CONFIRME': return 'Confirmé';
      case 'EN_ATTENTE': return 'En attente';
      case 'PROGRAMME': return 'Programmé';
      case 'EN_COURS': return 'En cours';
      case 'TERMINE': return 'Terminé';
      case 'ANNULE': return 'Annulé';
      case 'ABSENT': return 'Absent';
      default: return statut || 'Prévu';
    }
  }

  private getRdvBadgeClass(statut: string): string {
    switch ((statut || '').toUpperCase()) {
      case 'CONFIRME': return 'badge-confirmed';
      case 'EN_ATTENTE': return 'badge-pending';
      case 'TERMINE': return 'badge-completed';
      case 'ANNULE': return 'badge-cancelled';
      case 'EN_COURS': return 'badge-in-progress';
      default: return 'badge-default';
    }
  }
}
