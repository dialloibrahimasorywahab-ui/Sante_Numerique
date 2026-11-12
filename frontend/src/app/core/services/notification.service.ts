import { Injectable, inject, signal, effect, NgZone } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, forkJoin, of, tap, catchError } from 'rxjs';
import { environment } from '../../../environments/environment';
import { NotificationHospitaliereDto, LiveAlertToast, TypeNotification } from '../models/notification.models';
import { PaginatedResponse } from '../models/models';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class NotificationService {
  private http = inject(HttpClient);
  private ngZone = inject(NgZone);
  private authService = inject(AuthService);
  private readonly API_BASE_URL = environment.apiUrl;

  private eventSource: EventSource | null = null;
  private reconnectTimeout: any = null;

  // Signaux réactifs
  notifications = signal<NotificationHospitaliereDto[]>([]);
  unreadCount = signal<number>(0);
  isConnected = signal<boolean>(false);
  activeToasts = signal<LiveAlertToast[]>([]);

  constructor() {
    // Réaction automatique aux changements d'utilisateur (connexion, déconnexion, changement de rôle)
    effect(() => {
      const user = this.authService.currentUser();
      const role = user?.role;
      const isStaff = !!user && ['MEDECIN', 'INFIRMIER', 'ADMINISTRATEUR'].includes(role || '');
      const isPatient = !!user && role === 'PATIENT';

      if (isStaff) {
        this.loadStaffNotifications();
        this.initEventSource();
      } else if (isPatient) {
        this.loadPatientAlerts();
        this.initEventSource();
      } else {
        // Déconnecté : purger immédiatement les alertes
        this.closeEventSource();
        this.notifications.set([]);
        this.unreadCount.set(0);
        this.activeToasts.set([]);
      }
    });
  }

  /**
   * Initialise la connexion Server-Sent Events (SSE) temps réel
   */
  initEventSource(): void {
    if (typeof window === 'undefined') return;

    const user = this.authService.currentUser();
    const role = user?.role;
    if (!user) return;

    this.closeEventSource();

    try {
      const sseUrl = `${this.API_BASE_URL}/notifications/stream/`;
      this.eventSource = new EventSource(sseUrl, { withCredentials: true } as any);

      this.eventSource.onopen = () => {
        this.ngZone.run(() => {
          this.isConnected.set(true);
        });
      };

      this.eventSource.onmessage = (event: MessageEvent) => {
        this.ngZone.run(() => {
          try {
            const data = JSON.parse(event.data);
            if (data.type === 'CONNECTED') {
              return;
            }

            const currentUser = this.authService.currentUser();
            const currentRole = currentUser?.role;

            // Cloisonnement strict des rôles :
            if (currentRole === 'PATIENT') {
              // Un patient ne doit recevoir QUE des notifications qui le concernent directement
              const isForPatient =
                data.destinataireRole === 'PATIENT' ||
                data.type === 'RAPPEL_RDV' ||
                data.type === 'PRISE_MEDICAMENT' ||
                (data.destinataireUserId && data.destinataireUserId === currentUser?.id_user);
              if (!isForPatient) return;
            } else if (!['MEDECIN', 'INFIRMIER', 'ADMINISTRATEUR'].includes(currentRole || '')) {
              return;
            }

            // Création d'une nouvelle notification locale
            const notif: NotificationHospitaliereDto = {
              id_notification: data.id || Date.now(),
              idNotification: data.id || Date.now(),
              type_notification: data.type || 'INFO',
              typeNotification: data.type || 'INFO',
              type_display: this.formatTypeDisplay(data.type),
              titre: data.titre || (currentRole === 'PATIENT' ? 'Rappel Santé' : 'Alerte Hospitalière'),
              message: data.message || '',
              donnees: data.donnees || {},
              destinataire_role: data.destinataireRole || (currentRole === 'PATIENT' ? 'PATIENT' : 'TOUS'),
              destinataireRole: data.destinataireRole || (currentRole === 'PATIENT' ? 'PATIENT' : 'TOUS'),
              lu: false,
              date_creation: data.dateCreation || new Date().toISOString(),
              dateCreation: data.dateCreation || new Date().toISOString(),
              actif: true
            };

            // Ajout en haut de liste
            this.notifications.update(current => [notif, ...current]);
            this.unreadCount.update(c => c + 1);

            // Déclenchement d'un toast d'alerte en direct
            this.showToast({
              id: `toast-${Date.now()}-${Math.random().toString(36).substring(2, 6)}`,
              type: notif.type_notification,
              titre: notif.titre,
              message: notif.message,
              timestamp: new Date(),
              donnees: notif.donnees
            });
          } catch (e) {
            console.error('Erreur parsing SSE notification:', e);
          }
        });
      };

      this.eventSource.onerror = () => {
        this.ngZone.run(() => {
          this.isConnected.set(false);
          this.closeEventSource();
          // Tentative de reconnexion automatique après 6 secondes
          this.reconnectTimeout = setTimeout(() => {
            this.initEventSource();
          }, 6000);
        });
      };
    } catch (e) {
      console.error('Erreur initialisation EventSource SSE:', e);
      this.isConnected.set(false);
    }
  }

  /**
   * Ferme proprement le flux SSE
   */
  closeEventSource(): void {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
  }

  /**
   * Charge les notifications depuis l'API REST pour le personnel soignant et administratif
   */
  loadStaffNotifications(): void {
    const user = this.authService.currentUser();
    const role = user?.role;
    if (!user || !['MEDECIN', 'INFIRMIER', 'ADMINISTRATEUR'].includes(role || '')) {
      this.notifications.set([]);
      this.unreadCount.set(0);
      return;
    }

    this.http.get<PaginatedResponse<NotificationHospitaliereDto>>(`${this.API_BASE_URL}/notifications/?page_size=20`, { withCredentials: true }).subscribe({
      next: (res) => {
        const notifs = res.results || [];
        this.notifications.set(notifs);
        const unread = notifs.filter(n => !n.lu).length;
        this.unreadCount.set(unread);
      },
      error: () => {
        // En cas d'erreur de chargement (ex: non authentifié), ignorer silencieusement
      }
    });
  }

  /**
   * Charge les alertes dédiées au patient :
   * - Prochains rendez-vous médicaux
   * - Prochaines prises de médicaments et traitements en cours (ordonnances)
   * - Notifications enregistrées en base pour ce patient
   */
  loadPatientAlerts(): void {
    const user = this.authService.currentUser();
    if (!user || user.role !== 'PATIENT') return;

    forkJoin({
      dbNotifs: this.http.get<PaginatedResponse<NotificationHospitaliereDto>>(`${this.API_BASE_URL}/notifications/?page_size=30`, { withCredentials: true }).pipe(catchError(() => of({ results: [], count: 0 }))),
      appointments: this.http.get<any>(`${this.API_BASE_URL}/rendezvous/mes-rendezvous/`, { withCredentials: true }).pipe(catchError(() => of([]))),
      prescriptions: this.http.get<any>(`${this.API_BASE_URL}/ordonnances/`, { withCredentials: true }).pipe(catchError(() => of({ results: [] })))
    }).subscribe({
      next: ({ dbNotifs, appointments, prescriptions }) => {
        const rawDbNotifs = (dbNotifs?.results || []).filter(n =>
          n.destinataire_role === 'PATIENT' ||
          n.destinataire_user === user.id_user ||
          ['RAPPEL_RDV', 'PRISE_MEDICAMENT'].includes(n.type_notification)
        );

        // Rendez-vous à venir (non annulés et non passés)
        const rawAppts = Array.isArray(appointments) ? appointments : (appointments?.results || []);
        const now = new Date();
        const generatedRdvNotifs: NotificationHospitaliereDto[] = [];

        rawAppts.forEach((rdv: any) => {
          if (rdv.statut === 'ANNULE' || rdv.statut === 'TERMINE') return;
          const rdvDate = rdv.date_rdv || rdv.date;
          if (!rdvDate) return;
          const rdvTime = (rdv.heure || rdv.time || '00:00').substring(0, 5);
          const rdvDateTime = new Date(`${rdvDate}T${rdvTime.length === 5 ? rdvTime + ':00' : '00:00:00'}`);

          // Si le RDV n'est pas expiré depuis plus de 2 heures
          if (rdvDateTime.getTime() + (2 * 3600 * 1000) >= now.getTime()) {
            const medecinNom = rdv.medecin_nom
              ? `Dr. ${rdv.medecin_prenom || ''} ${rdv.medecin_nom}`.trim()
              : (rdv.medecin_detail ? `Dr. ${rdv.medecin_detail.prenom || ''} ${rdv.medecin_detail.nom || ''}`.trim() : 'Votre praticien');
            const lieu = rdv.bureau || rdv.service_nom || 'Cabinet médical';
            const motif = rdv.motif || rdv.reason || 'Consultation médicale';

            generatedRdvNotifs.push({
              id_notification: 100000 + (rdv.id || 1),
              idNotification: 100000 + (rdv.id || 1),
              type_notification: 'RAPPEL_RDV',
              typeNotification: 'RAPPEL_RDV',
              type_display: 'Rappel Rendez-vous',
              titre: `RDV : ${motif}`,
              message: `${medecinNom} • ${this.formatReadableDate(rdvDate)} à ${rdvTime.replace(':', 'h')} (${lieu})`,
              donnees: {
                id_rdv: rdv.id,
                medecin: medecinNom,
                date_rdv: rdvDate,
                heure: rdvTime,
                lieu: lieu,
                statut: rdv.statut
              },
              destinataire_role: 'PATIENT',
              destinataireRole: 'PATIENT',
              lu: false,
              date_creation: rdvDate,
              dateCreation: rdvDate,
              actif: true
            });
          }
        });

        // Ordonnances & prises de médicaments en cours
        const rawPresc = Array.isArray(prescriptions) ? prescriptions : (prescriptions?.results || []);
        const generatedMedsNotifs: NotificationHospitaliereDto[] = [];

        rawPresc.forEach((ord: any) => {
          if (!ord.actif) return;
          const lignes = ord.lignes || [];
          lignes.forEach((ligne: any, idx: number) => {
            if (!ligne.actif && ligne.actif !== undefined) return;
            const medNom = `${ligne.medicament || 'Médicament'}${ligne.dosage ? ' ' + ligne.dosage : ''}`;
            const posologie = ligne.posologie || 'Prendre selon la prescription';
            const instructions = ligne.instructions ? ` • ${ligne.instructions}` : '';
            const duree = ligne.duree_traitement ? ` • Durée : ${ligne.duree_traitement}` : '';

            generatedMedsNotifs.push({
              id_notification: 200000 + (ligne.id || (ord.id * 100 + idx)),
              idNotification: 200000 + (ligne.id || (ord.id * 100 + idx)),
              type_notification: 'PRISE_MEDICAMENT',
              typeNotification: 'PRISE_MEDICAMENT',
              type_display: 'Prise de Médicament',
              titre: `Traitement : ${medNom}`,
              message: `${posologie}${instructions}${duree}`,
              donnees: {
                id_ordonnance: ord.id,
                reference: ord.reference,
                medicament: medNom,
                posologie: ligne.posologie,
                instructions: ligne.instructions,
                duree: ligne.duree_traitement,
                forme: ligne.forme
              },
              destinataire_role: 'PATIENT',
              destinataireRole: 'PATIENT',
              lu: false,
              date_creation: ord.date_ordonnance || new Date().toISOString(),
              dateCreation: ord.date_ordonnance || new Date().toISOString(),
              actif: true
            });
          });
        });

        // Fusionner avec la base sans doublons
        const allItems: NotificationHospitaliereDto[] = [...rawDbNotifs];

        // Ajouter les rappels RDV s'ils ne sont pas déjà en base
        for (const g of generatedRdvNotifs) {
          const exists = allItems.some(n =>
            n.type_notification === 'RAPPEL_RDV' &&
            (n.donnees?.['id_rdv'] === g.donnees?.['id_rdv'] || n.titre.includes(g.donnees?.['medecin'] || ''))
          );
          if (!exists) {
            allItems.push(g);
          }
        }

        // Ajouter les prises de médicaments si non présentes
        for (const m of generatedMedsNotifs) {
          const exists = allItems.some(n =>
            n.type_notification === 'PRISE_MEDICAMENT' &&
            n.donnees?.['medicament'] === m.donnees?.['medicament']
          );
          if (!exists) {
            allItems.push(m);
          }
        }

        this.notifications.set(allItems);
        this.unreadCount.set(allItems.filter(n => !n.lu).length);
      }
    });
  }

  /**
   * Marque une notification comme lue
   */
  markAsRead(notificationId: number): Observable<{ message: string }> {
    this.notifications.update(notifs =>
      notifs.map(n => n.id_notification === notificationId ? { ...n, lu: true } : n)
    );
    this.unreadCount.update(c => Math.max(0, c - 1));

    if (notificationId >= 100000) {
      return of({ message: 'Alerte acquittée.' });
    }

    return this.http.post<{ message: string }>(`${this.API_BASE_URL}/notifications/${notificationId}/read/`, {}, { withCredentials: true }).pipe(
      catchError(() => of({ message: 'Notification marquée comme lue.' }))
    );
  }

  /**
   * Marque toutes les notifications comme lues
   */
  markAllAsRead(): Observable<{ message: string }> {
    this.notifications.update(notifs => notifs.map(n => ({ ...n, lu: true })));
    this.unreadCount.set(0);

    return this.http.post<{ message: string }>(`${this.API_BASE_URL}/notifications/read-all/`, {}, { withCredentials: true }).pipe(
      catchError(() => of({ message: 'Toutes les alertes ont été marquées comme lues.' }))
    );
  }

  /**
   * Déclenche une alerte manuelle (ex: Lit d'urgence, Alerte clinique)
   */
  triggerUrgentAlert(
    type: TypeNotification,
    titre: string,
    message: string,
    destinataireRole: string = 'TOUS',
    donnees: Record<string, any> = {}
  ): Observable<NotificationHospitaliereDto> {
    const payload = {
      type_notification: type,
      titre,
      message,
      destinataire_role: destinataireRole,
      donnees
    };
    return this.http.post<NotificationHospitaliereDto>(`${this.API_BASE_URL}/notifications/trigger/`, payload, { withCredentials: true });
  }

  /**
   * Gestion des toasts d'alertes en direct
   */
  showToast(toast: LiveAlertToast, durationMs: number = 7000): void {
    this.activeToasts.update(toasts => [toast, ...toasts.slice(0, 3)]);
    setTimeout(() => {
      this.dismissToast(toast.id);
    }, durationMs);
  }

  dismissToast(toastId: string): void {
    this.activeToasts.update(toasts => toasts.filter(t => t.id !== toastId));
  }

  formatTypeDisplay(type?: string): string {
    switch (type) {
      case 'LIT_URGENCE': return 'Lit d’Urgence';
      case 'PATIENT_ARRIVE': return 'Salle d’attente';
      case 'NOUVEAU_RDV': return 'Nouveau RDV';
      case 'HOSPITALISATION': return 'Hospitalisation';
      case 'ALERTE_CLINIQUE': return 'Alerte Clinique';
      case 'RAPPEL_RDV': return 'Rappel Rendez-vous';
      case 'PRISE_MEDICAMENT': return 'Prise de Médicament';
      default: return 'Notification';
    }
  }

  formatReadableDate(dateStr?: string): string {
    if (!dateStr) return '';
    try {
      const d = new Date(dateStr);
      return d.toLocaleDateString('fr-FR', { weekday: 'short', day: 'numeric', month: 'short' });
    } catch {
      return dateStr;
    }
  }
}
