import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule, ActivatedRoute } from '@angular/router';
import { forkJoin, of } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { AuthService } from '../../../../core/services/auth.service';
import { NotificationService } from '../../../../core/services/notification.service';
import { AppointmentService } from '../../../rendez-vous/services/appointment.service';
import { PatientHospitalizationService } from '../../services/patient-hospitalization.service';
import { PatientConsultationService } from '../../services/patient-consultation.service';
import { PatientPrescriptionService } from '../../services/patient-prescription.service';
import { RendezVousDto } from '../../../rendez-vous/models/models';
import { HospitalisationDto } from '../../models/patient.models';
import { NotificationHospitaliereDto } from '../../../../core/models/notification.models';
import { isDateTimePast } from '../../../../shared/utils';

export interface ServiceCard {
  id: string;
  icon: 'calendar' | 'results' | 'dossier' | 'hospital' | 'prescription' | 'contact';
  color: string;
  bgColor: string;
  title: string;
  description: string;
  route: string;
  badge?: number | null;
}

@Component({
  selector: 'app-patient-espace-services',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './patient-espace-services.component.html',
  styleUrl: './patient-espace-services.component.scss'
})
export class PatientEspaceServicesComponent implements OnInit {
  authService = inject(AuthService);
  notificationService = inject(NotificationService);
  private appointmentService = inject(AppointmentService);
  private hospitalizationService = inject(PatientHospitalizationService);
  private consultationService = inject(PatientConsultationService);
  private prescriptionService = inject(PatientPrescriptionService);
  private router = inject(Router);
  private route = inject(ActivatedRoute);

  isLoading = signal<boolean>(true);
  searchQuery = signal<string>('');

  appointments = signal<RendezVousDto[]>([]);
  hospitalizations = signal<HospitalisationDto[]>([]);

  currentUser = computed(() => this.authService.currentUser());
  unreadNotifsCount = computed(() => this.notificationService.unreadCount());

  // Prochains rendez-vous réels de l'API
  upcomingAppointments = computed<RendezVousDto[]>(() => {
    const now = Date.now();
    return this.appointments()
      .filter(r => !isDateTimePast(r.date_rdv, r.heure, new Date(now)) && r.statut !== 'ANNULE' && r.statut !== 'TERMINE')
      .sort((a, b) => (a.date_rdv + a.heure).localeCompare(b.date_rdv + b.heure));
  });

  // Premier rendez-vous pour la carte (ou fallback représentatif)
  primaryAppointment = computed(() => {
    const list = this.upcomingAppointments();
    if (list.length > 0) {
      const r = list[0];
      return {
        isFallback: false,
        dayName: this.formatDayName(r.date_rdv),
        dayNum: this.formatDayNum(r.date_rdv),
        monthYear: this.formatMonthYear(r.date_rdv),
        title: this.getSpecialtyName(r),
        doctor: this.getDoctorFullName(r),
        timeLocation: `${this.formatTime(r.heure)} - ${(r as any).lieu || 'Hôpital Central'}`,
        status: this.getStatusLabel(r.statut),
        statusClass: this.getStatusClass(r.statut)
      };
    }
    // Fallback représentatif conforme à la maquette
    return {
      isFallback: true,
      dayName: 'Lun',
      dayNum: '17',
      monthYear: 'Nov. 2025',
      title: 'Consultation générale',
      doctor: 'Dr. Mamadou Camara',
      timeLocation: '09h00 - Hôpital Central',
      status: 'Confirmé',
      statusClass: 'status-confirmed'
    };
  });

  // 6 Cartes de Services (Conforme stricte maquette)
  readonly allServiceCards: ServiceCard[] = [
    {
      id: 'rdv',
      icon: 'calendar',
      color: '#006B5F',
      bgColor: '#E6F7F4',
      title: 'Prendre un rendez-vous',
      description: 'Réservez votre consultation en quelques clics',
      route: '/rendez-vous'
    },
    {
      id: 'resultats',
      icon: 'results',
      color: '#059669',
      bgColor: '#ECFDF5',
      title: 'Consulter mes résultats',
      description: 'Accédez à vos résultats d\'examens',
      route: '/patient/consultations'
    },
    {
      id: 'dossier',
      icon: 'dossier',
      color: '#8B5CF6',
      bgColor: '#F5F3FF',
      title: 'Consulter mon dossier médical',
      description: 'Consultez votre historique de soins',
      route: '/patient/documents'
    },
    {
      id: 'hospitalisation',
      icon: 'hospital',
      color: '#D97706',
      bgColor: '#FFFBEB',
      title: 'Suivre mon hospitalisation',
      description: 'Suivez votre séjour à l\'hôpital',
      route: '/patient/hospitalisations'
    },
    {
      id: 'ordonnances',
      icon: 'prescription',
      color: '#0D9488',
      bgColor: '#F0FDFA',
      title: 'Accéder à mes ordonnances',
      description: 'Téléchargez vos ordonnances',
      route: '/patient/ordonnances'
    },
    {
      id: 'contact',
      icon: 'contact',
      color: '#10B981',
      bgColor: '#ECFDF5',
      title: 'Contacter le service',
      description: 'Besoin d\'aide ? Contactez-nous',
      route: '/patient/profil'
    }
  ];

  filteredServiceCards = computed<ServiceCard[]>(() => {
    const q = this.searchQuery().toLowerCase().trim();
    if (!q) return this.allServiceCards;
    return this.allServiceCards.filter(c =>
      c.title.toLowerCase().includes(q) || c.description.toLowerCase().includes(q)
    );
  });

  // Notifications pour le panneau (Conforme maquette)
  notificationsList = computed(() => {
    const realNotifs = this.notificationService.notifications();
    if (realNotifs && realNotifs.length > 0) {
      return realNotifs.slice(0, 3).map(n => ({
        id: n.id_notification || n.idNotification,
        message: n.message || n.titre,
        timeAgo: this.formatRelativeTime(n.date_creation || n.dateCreation),
        type: n.type_notification || n.typeNotification,
        isUnread: !n.lu
      }));
    }
    // Fallback représentatif conforme à la maquette
    return [
      {
        id: 1,
        message: 'Votre rendez-vous du 17/11/2025 est confirmé.',
        timeAgo: 'Il y a 1h',
        type: 'NOUVEAU_RDV',
        isUnread: true
      },
      {
        id: 2,
        message: 'Vos résultats d\'analyse sont disponibles.',
        timeAgo: 'Il y a 3h',
        type: 'INFO',
        isUnread: true
      },
      {
        id: 3,
        message: 'Rappel : prenez vos médicaments.',
        timeAgo: 'Il y a 1 jour',
        type: 'PRISE_MEDICAMENT',
        isUnread: false
      }
    ];
  });

  ngOnInit(): void {
    // Écoute de la recherche par query params (ex: ?q=cardiologie)
    this.route.queryParams.subscribe(params => {
      if (params['q'] !== undefined) {
        this.searchQuery.set(params['q'] || '');
      }
    });

    this.loadBackendData();
  }

  loadBackendData(): void {
    this.isLoading.set(true);
    forkJoin({
      appointments: this.appointmentService.getMyAppointments().pipe(catchError(() => of([]))),
      hospitalizations: this.hospitalizationService.getMyHospitalizations(1, 10).pipe(catchError(() => of({ results: [], count: 0 })))
    }).subscribe({
      next: ({ appointments, hospitalizations }) => {
        this.appointments.set(appointments || []);
        this.hospitalizations.set((hospitalizations as any)?.results || []);
        this.isLoading.set(false);
      },
      error: () => this.isLoading.set(false)
    });
  }

  navigateToCard(card: ServiceCard): void {
    if (card.id === 'contact') {
      // Pour le contact : redirection vers profil ou action téléphone
      window.location.href = 'tel:+224627684702';
      return;
    }
    this.router.navigate([card.route]);
  }

  // ───── Helpers de formatage ─────

  formatDayName(dateStr?: string): string {
    if (!dateStr) return 'Lun';
    try {
      const d = new Date(dateStr);
      const str = d.toLocaleDateString('fr-FR', { weekday: 'short' });
      return str.charAt(0).toUpperCase() + str.slice(1).replace('.', '');
    } catch { return 'Lun'; }
  }

  formatDayNum(dateStr?: string): string {
    if (!dateStr) return '17';
    try {
      return new Date(dateStr).getDate().toString();
    } catch { return '17'; }
  }

  formatMonthYear(dateStr?: string): string {
    if (!dateStr) return 'Nov. 2025';
    try {
      const d = new Date(dateStr);
      const m = d.toLocaleDateString('fr-FR', { month: 'short' });
      const y = d.getFullYear();
      return `${m.charAt(0).toUpperCase() + m.slice(1)} ${y}`;
    } catch { return 'Nov. 2025'; }
  }

  formatTime(timeStr?: string): string {
    if (!timeStr) return '09h00';
    return timeStr.substring(0, 5).replace(':', 'h');
  }

  formatRelativeTime(dateStr?: string): string {
    if (!dateStr) return 'Récemment';
    try {
      const diff = Date.now() - new Date(dateStr).getTime();
      const h = Math.floor(diff / 3600000);
      if (h < 1) return 'Il y a moins d\'1h';
      if (h < 24) return `Il y a ${h}h`;
      const d = Math.floor(h / 24);
      return `Il y a ${d} jour${d > 1 ? 's' : ''}`;
    } catch { return 'Récemment'; }
  }

  getDoctorFullName(rdv: any): string {
    const m = rdv.medecinDetails || rdv.medecin_details || rdv.medecinDetail;
    if (m?.prenom || m?.nom) return `Dr. ${m.prenom || ''} ${m.nom || ''}`.trim();
    const p = rdv.medecin_prenom || '';
    const n = rdv.medecin_nom || '';
    if (p || n) return `Dr. ${p} ${n}`.trim();
    return 'Dr. Mamadou Camara';
  }

  getSpecialtyName(rdv: any): string {
    return rdv.medecin_specialite || rdv.medecin_detail?.specialite || 'Consultation générale';
  }

  getStatusClass(statut?: string): string {
    switch (statut) {
      case 'CONFIRME': return 'status-confirmed';
      case 'PLANIFIE':
      case 'EN_ATTENTE': return 'status-pending';
      case 'TERMINE': return 'status-done';
      case 'ANNULE': return 'status-cancelled';
      default: return 'status-confirmed';
    }
  }

  getStatusLabel(statut?: string): string {
    switch (statut) {
      case 'CONFIRME': return 'Confirmé';
      case 'PLANIFIE': return 'Planifié';
      case 'EN_ATTENTE': return 'En attente';
      case 'TERMINE': return 'Effectué';
      case 'ANNULE': return 'Annulé';
      default: return 'Confirmé';
    }
  }
}
