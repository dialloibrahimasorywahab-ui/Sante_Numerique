import { Injectable, inject, signal } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, map, catchError, of, throwError } from 'rxjs';
import { ServiceHospitalier } from '../../features/services/models/models';
import { PaginatedResponse } from '../models/models';
import { DoctorProfile, HospitalService } from './hospital.service';

export interface ServiceDetailExtended extends ServiceHospitalier {
  poleCategorie?: string;
  missions?: string[];
  plateauTechnique?: string[];
  horairesConsultations?: string;
  urgencesPriseEnCharge?: boolean;
  medecinsAssocies?: DoctorProfile[];
}

@Injectable({
  providedIn: 'root'
})
export class ServicesService {
  private http = inject(HttpClient);
  private hospitalService = inject(HospitalService);

  private readonly API_BASE_URL = 'http://127.0.0.1:8000';

  // State Signals
  servicesList = signal<ServiceHospitalier[]>([]);
  isLoading = signal<boolean>(false);
  errorMessage = signal<string | null>(null);

  /**
   * Helper mapping for medical icons and refined titles
   */
  private readonly SERVICE_META_MAP: Record<string, {
    icon: string;
    nomClair: string;
    desc: string;
    categorie: string;
    missions: string[];
    plateau: string[];
    horaires: string;
    urgence: boolean;
  }> = {
    'CARDIOLOGIE': {
      icon: 'heart',
      nomClair: 'Cardiologie & Vasculaire',
      desc: 'Prise en charge complète des pathologies cardiovasculaires, coronarographies et réadaptation cardiaque.',
      categorie: 'Pôle Médical Spécialisé',
      missions: ['Consultations d’échocardiographie', 'Suivi de l’hypertension artérielle et insuffisance cardiaque', 'Pose et contrôle de stimulateurs cardiaques (Pacemaker)'],
      plateau: ['Échographe Doppler 4D dernière génération', 'Table de coronarographie numérisée', 'Holter ECG et MAPA 48h'],
      horaires: 'Lun - Ven : 08h00 - 17h30 | Urgences 24/7',
      urgence: true
    },
    'NEUROLOGIE': {
      icon: 'brain',
      nomClair: 'Neurologie & Neurosciences',
      desc: 'Diagnostic, exploration et traitement des affections du système nerveux central et périphérique.',
      categorie: 'Pôle Neurosciences',
      missions: ['Électroencéphalographie (EEG) et Électromyogramme (EMG)', 'Prise en charge des AVC et migraines sévères', 'Bilan cognitif et suivi des neuropathies'],
      plateau: ['Salle d’exploration fonctionnelle EEG haute résolution', 'Accès IRM 3T & Scanner spiralé', 'Unité Neuro-Vasculaire (UNV)'],
      horaires: 'Lun - Ven : 08h30 - 17h00',
      urgence: true
    },
    'PEDIATRIE': {
      icon: 'child',
      nomClair: 'Pédiatrie & Néonatalogie',
      desc: 'Soins médicaux spécialisés pour nouveau-nés, nourrissons, enfants et adolescents.',
      categorie: 'Pôle Mère-Enfant',
      missions: ['Suivi du développement et croissance de l’enfant', 'Vaccinations et bilans pédiatriques', 'Urgences et réanimation pédiatrique'],
      plateau: ['Couveuses néonatales avec monitoring multiparamétrique', 'Unité de photothérapie intensive', 'Espace pédiatrique ludique et rassurant'],
      horaires: 'Lun - Sam : 08h00 - 18h00 | Garde 24/7',
      urgence: true
    },
    'GYNECOLOGIE': {
      icon: 'female',
      nomClair: 'Gynécologie & Obstétrique',
      desc: 'Suivi de grossesse, consultations gynécologiques, échographies et chirurgie de la femme.',
      categorie: 'Pôle Mère-Enfant',
      missions: ['Suivi obstétrical et préparation à la naissance', 'Dépistage gynécologique et frottis', 'Chirurgie gynécologique mini-invasive'],
      plateau: ['Échographes obstétricaux volumiques HD', 'Blocs d’accouchement modernes', 'Salles de monitoring fœtal sans fil'],
      horaires: 'Lun - Sam : 08h00 - 17h30',
      urgence: true
    },
    'MEDECINE_GENERALE': {
      icon: 'stethoscope',
      nomClair: 'Médecine Générale',
      desc: 'Consultations de premier recours, prévention, bilans de santé et soins pour toute la famille.',
      categorie: 'Pôle Consultations Externes',
      missions: ['Diagnostic et traitement des maladies aiguës et chroniques', 'Bilans de santé et dépistage', 'Orientation vers les spécialistes du CHU'],
      plateau: ['Cabinets de consultation modernes', 'Télémédecine intégrée', 'Laboratoire d’analyses rapide sur place'],
      horaires: 'Lun - Sam : 07h30 - 19h00',
      urgence: false
    },
    'CHIRURGIE': {
      icon: 'cut',
      nomClair: 'Chirurgie Générale & Viscérale',
      desc: 'Actes chirurgicaux programmés et d’urgence avec techniques mini-invasives et cœlioscopie.',
      categorie: 'Pôle Chirurgical',
      missions: ['Chirurgie digestive et viscérale', 'Chirurgie ambulatoire', 'Traumatologie et réparations d’urgence'],
      plateau: ['4 Blocs opératoires ISO 5 à flux laminaire', 'Colonnes de cœlioscopie 4K UHD', 'Salle de réveil et soins continus post-opératoires'],
      horaires: 'Consultations : Lun - Ven 08h00 - 16h00 | Bloc 24/7',
      urgence: true
    },
    'DERMATOLOGIE': {
      icon: 'sparkles',
      nomClair: 'Dermatologie & Vénérologie',
      desc: 'Dépistage, diagnostic et traitement des maladies de la peau, des muqueuses, des ongles et des cheveux.',
      categorie: 'Pôle Spécialités Médicales',
      missions: ['Dépistage des lésions cutanées et mélanomes', 'Dermatologie pédiatrique et allergologie', 'Petite chirurgie dermatologique'],
      plateau: ['Dermatoscope numérique haute résolution', 'Plateforme de photothérapie UVB', 'Laser thérapeutique et cryothérapie'],
      horaires: 'Mar - Sam : 08h30 - 16h30',
      urgence: false
    },
    'OPHTALMOLOGIE': {
      icon: 'eye',
      nomClair: 'Ophtalmologie',
      desc: 'Bilan de la vue, correction visuelle, dépistage du glaucome et chirurgie de la cataracte.',
      categorie: 'Pôle Spécialités Médicales',
      missions: ['Réfraction et prescription de verres correcteurs', 'Chirurgie de la cataracte', 'Traitement des rétinopathies et glaucomes'],
      plateau: ['OCT (Tomographie par Cohérence Optique)', 'Laser YAG & Argon', 'Microscope opératoire ophtalmologique'],
      horaires: 'Lun - Ven : 08h00 - 17h00',
      urgence: false
    },
    'RADIOLOGIE': {
      icon: 'radiation',
      nomClair: 'Radiologie & Imagerie Médicale',
      desc: 'Plateau d’imagerie de pointe pour des diagnostics rapides et précis (Scanner, IRM, Radiographie, Échographie).',
      categorie: 'Pôle Médico-Technique',
      missions: ['Radiographies conventionnelles numérisées', 'Scanners hélicoïdaux et angio-scanners', 'Échographies générales et vasculaires'],
      plateau: ['Scanner 64 barrettes multi-coupes', 'IRM haut champ 3T', 'Système PACS de téléradiologie sécurisé'],
      horaires: 'Examens : Lun - Sam 07h30 - 18h30 | Urgences 24/7',
      urgence: true
    },
    'LABORATOIRE': {
      icon: 'microscope',
      nomClair: 'Laboratoire d’Analyses Médicales',
      desc: 'Analyses biologiques, hématologie, biochimie, immunologie et microbiologie médicale.',
      categorie: 'Pôle Médico-Technique',
      missions: ['Analyses sanguines et bilans biologiques complets', 'Bactériologie et antibiogrammes', 'Sérologies et tests de biologie moléculaire'],
      plateau: ['Automates d’hématologie et de biochimie grande cadence', 'Hotte à flux laminaire P2/P3', 'Système d’envoi électronique des résultats sous 2h'],
      horaires: 'Prélèvements : Lun - Sam 07h00 - 18h00 | Analyses 24/7',
      urgence: true
    },
    'PHARMACIE': {
      icon: 'pills',
      nomClair: 'Pharmacie Hospitalière Centrale',
      desc: 'Dispensation des médicaments, dispositifs médicaux stériles et pharmacovigilance.',
      categorie: 'Pôle Médico-Technique',
      missions: ['Gestion des stocks thérapeutiques hospitaliers', 'Préparation des traitements spécifiques', 'Conseil pharmaceutique aux patients'],
      plateau: ['Armoires sécurisées de délivrance nominative', 'Zone de stockage sous température dirigée (2-8°C)', 'Logiciel de traçabilité pharmaceutique'],
      horaires: 'Lun - Dim : Ouverte en continu 24h/24',
      urgence: true
    },
    'URGENCES': {
      icon: 'ambulance',
      nomClair: 'Urgences & Soins Intensifs',
      desc: 'Accueil et prise en charge médicale et chirurgicale 24h/24 et 7j/7 sans interruption.',
      categorie: 'Pôle Soins Critiques',
      missions: ['Triage et régulation médicale immédiate', 'Déchoquage et gestes de survie', 'Hospitalisation de très courte durée (UHCD)'],
      plateau: ['Salles de déchoquage équipées réanimation lourde', 'Radiologie d’urgence intégrée', 'Flotte d’ambulances médicalisées'],
      horaires: 'Tous les jours : 24h/24 et 7j/7',
      urgence: true
    },
    'MATERNITE': {
      icon: 'baby',
      nomClair: 'Maternité & Salle de Naissance',
      desc: 'Accompagnement bienveillant et sécurisé pour l’accueil de la vie et le suivi postnatal.',
      categorie: 'Pôle Mère-Enfant',
      missions: ['Accouchements physiologiques et instrumentalisés', 'Césariennes en urgence ou programmées', 'Suivi post-partum et allaitement'],
      plateau: ['Salles d’accouchement climatisées tout confort', 'Chambres individuelles avec berceau sécurisé', 'Bloc opératoire dédié au sein de la maternité'],
      horaires: 'Admissions & Naissances : 24h/24 et 7j/7',
      urgence: true
    },
    'REANIMATION': {
      icon: 'activity',
      nomClair: 'Réanimation & Soins Continus',
      desc: 'Surveillance continue et suppléance des défaillances viscérales vitales.',
      categorie: 'Pôle Soins Critiques',
      missions: ['Ventilation mécanique et assistance respiratoire', 'Monitoring hémodynamique invasif', 'Nutrition parentérale et dialyse aiguë'],
      plateau: ['Respirateurs d’anesthésie-réanimation haut de gamme', 'Moniteurs multiparamétriques centralisés', 'Isolement stérile à pression positive/négative'],
      horaires: 'Permanence 24h/24 | Visites encadrées',
      urgence: true
    }
  };

  /**
   * Fetch all active hospital services from Django REST API
   */
  getServices(search?: string): Observable<ServiceHospitalier[]> {
    this.isLoading.set(true);
    this.errorMessage.set(null);

    let params = new HttpParams();
    if (search && search.trim()) {
      params = params.set('search', search.trim());
    }

    return this.http.get<PaginatedResponse<ServiceHospitalier> | ServiceHospitalier[]>(
      `${this.API_BASE_URL}/services/`,
      { params }
    ).pipe(
      map(res => {
        let rawList: ServiceHospitalier[] = [];
        if (res && 'results' in res && Array.isArray(res.results)) {
          rawList = res.results;
        } else if (Array.isArray(res)) {
          rawList = res;
        }

        const enriched = rawList.map(s => this.enrichServiceItem(s));
        this.servicesList.set(enriched);
        this.isLoading.set(false);
        return enriched;
      }),
      catchError(err => {
        console.error('Erreur lors de la récupération des services:', err);
        this.isLoading.set(false);
        this.errorMessage.set('Impossible de charger les services depuis le serveur. Vérifiez votre connexion.');
        return throwError(() => err);
      })
    );
  }

  /**
   * Fetch a single service by ID with detailed information
   */
  getServiceById(id: number): Observable<ServiceDetailExtended> {
    return this.http.get<ServiceHospitalier>(`${this.API_BASE_URL}/services/${id}/`).pipe(
      map(rawService => {
        const enriched = this.enrichServiceItem(rawService);
        const meta = this.SERVICE_META_MAP[rawService.nom_service] || {};

        // Find associated doctors from doctors list
        const doctors = this.hospitalService.doctors().filter(d =>
          d.specialite === rawService.nom_service ||
          (rawService.nom_service === 'MEDECINE_GENERALE' && d.specialite === 'GENERALISTE')
        );

        const detail: ServiceDetailExtended = {
          ...enriched,
          poleCategorie: meta.categorie || 'Pôle Hospitalier',
          missions: meta.missions || [
            'Consultations spécialisées et bilans approfondis',
            'Prise en charge diagnostique et thérapeutique',
            'Suivi personnalisé et accompagnement du patient'
          ],
          plateauTechnique: meta.plateau || [
            'Équipements médicaux modernes et conformes aux normes',
            'Système d’information hospitalier et dossier médical informatisé',
            'Laboratoire et imagerie accessibles 24/7'
          ],
          horairesConsultations: meta.horaires || 'Lun - Ven : 08h00 - 17h30',
          urgencesPriseEnCharge: meta.urgence ?? true,
          medecinsAssocies: doctors
        };

        return detail;
      }),
      catchError(err => {
        console.error(`Erreur lors de la récupération du service #${id}:`, err);
        return throwError(() => err);
      })
    );
  }

  /**
   * Enrich a ServiceHospitalier item with clean human-readable name, description, and SVG icon key
   */
  private enrichServiceItem(item: ServiceHospitalier): ServiceHospitalier {
    const code = item.nom_service;
    const meta = this.SERVICE_META_MAP[code];

    return {
      ...item,
      icon: meta?.icon || 'stethoscope',
      displayNom: meta?.nomClair || item.nom_service_display || item.nom_service,
      displayDesc: item.description && item.description.length > 20
        ? item.description
        : (meta?.desc || `Prise en charge spécialisée et soins de qualité au sein du service de ${item.nom_service_display || item.nom_service}.`),
      badgeCountMedecins: this.countDoctorsForService(code)
    };
  }

  private countDoctorsForService(code: string): number {
    return this.hospitalService.doctors().filter(d =>
      d.specialite === code ||
      (code === 'MEDECINE_GENERALE' && d.specialite === 'GENERALISTE')
    ).length;
  }
}
