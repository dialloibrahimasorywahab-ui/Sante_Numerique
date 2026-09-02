import { Injectable, signal } from '@angular/core';
import { SpecialiteMedecin } from '../../features/medecins/models/models';

export interface ServiceSpecialite {
  id: string;
  nom: string;
  code: SpecialiteMedecin;
  icon: string;
  description: string;
  praticiensCount: number;
  delaiMoyen: string;
  urgencesPriseEnCharge: boolean;
  couleur: string;
}

export interface DoctorProfile {
  id: number;
  nom: string;
  prenom: string;
  titre: string;
  specialite: SpecialiteMedecin;
  specialiteLabel: string;
  service: string;
  bureau: string;
  numeroOrdre: string;
  experience: string;
  langues: string[];
  disponibilites: string[];
  avatarUrl: string;
  evaluation: number;
  avisCount: number;
  description: string;
}

export interface BookingFormState {
  specialite: SpecialiteMedecin | '';
  medecinId: number | null;
  date: string;
  heure: string;
  motif: string;
  typeConsultation: 'SUR_PLACE' | 'TELECONSULTATION';
  patientNom: string;
  patientPrenom: string;
  patientEmail: string;
  patientTelephone: string;
  patientGroupeSanguin?: string;
  patientNSS?: string;
}

export interface BookingConfirmation {
  idRdv: string;
  date: string;
  heure: string;
  medecin: DoctorProfile;
  patientNom: string;
  patientPrenom: string;
  motif: string;
  typeConsultation: 'SUR_PLACE' | 'TELECONSULTATION';
  bureau: string;
  codeConfirmation: string;
  qrcodeSimule: string;
}

@Injectable({
  providedIn: 'root'
})
export class HospitalService {

  // Live Hospital KPIs & Capacity signals
  readonly hospitalStats = signal({
    urgencesAttenteMin: 12,
    litsDisponiblesTotal: 28,
    litsOccupesTotal: 46,
    tauxOccupation: 62,
    medecinsDeGarde: 14,
    consultationsAujourdhui: 89,
    satisfactionScore: 99.4,
    patientsPrisEnCharge: 12450
  });

  // Pôles d'excellence / Spécialités hospitalières
  readonly specialites = signal<ServiceSpecialite[]>([
    {
      id: 'cardio',
      nom: 'Cardiologie & Vasculaire',
      code: 'CARDIOLOGIE',
      icon: 'heart-pulse',
      description: 'Dépistage, prise en charge des cardiopathies, coronarographie et réadaptation cardiaque.',
      praticiensCount: 6,
      delaiMoyen: '24h',
      urgencesPriseEnCharge: true,
      couleur: '#0284c7'
    },
    {
      id: 'pediatrie',
      nom: 'Pédiatrie & Néonatalogie',
      code: 'PEDIATRIE',
      icon: 'baby',
      description: 'Suivi de croissance, urgences pédiatriques, vaccinations et soins néonataux intensifs.',
      praticiensCount: 5,
      delaiMoyen: 'Immédiat',
      urgencesPriseEnCharge: true,
      couleur: '#0d9488'
    },
    {
      id: 'gyneco',
      nom: 'Maternité & Gynécologie',
      code: 'GYNECOLOGIE',
      icon: 'sparkles',
      description: 'Accouchements physiologiques et de haute technicité, suivi de grossesse et chirurgie gynécologique.',
      praticiensCount: 7,
      delaiMoyen: '48h',
      urgencesPriseEnCharge: true,
      couleur: '#e11d48'
    },
    {
      id: 'generaliste',
      nom: 'Médecine Générale & Urgences',
      code: 'GENERALISTE',
      icon: 'stethoscope',
      description: 'Consultations de premier recours, bilans de santé complets et triage d’urgence 24/7.',
      praticiensCount: 12,
      delaiMoyen: 'Sans RDV',
      urgencesPriseEnCharge: true,
      couleur: '#10b981'
    },
    {
      id: 'chirurgie',
      nom: 'Chirurgie & Bloc Opératoire',
      code: 'CHIRURGIE',
      icon: 'scissors',
      description: 'Chirurgie viscérale, orthopédique et ambulatoire avec plateau technique de pointe.',
      praticiensCount: 8,
      delaiMoyen: '3 jours',
      urgencesPriseEnCharge: true,
      couleur: '#6366f1'
    },
    {
      id: 'neuro',
      nom: 'Neurologie & Neurosciences',
      code: 'NEUROLOGIE',
      icon: 'brain',
      description: 'Diagnostic des affections cérébrales, accidents vasculaires, épilepsie et suivi cognitif.',
      praticiensCount: 4,
      delaiMoyen: '48h',
      urgencesPriseEnCharge: true,
      couleur: '#8b5cf6'
    },
    {
      id: 'dermato',
      nom: 'Dermatologie & Vénérologie',
      code: 'DERMATOLOGIE',
      icon: 'shield-check',
      description: 'Soins des pathologies cutanées, dépistage mélanome et dermatologie interventionnelle.',
      praticiensCount: 4,
      delaiMoyen: '3 jours',
      urgencesPriseEnCharge: false,
      couleur: '#f59e0b'
    },
    {
      id: 'radio',
      nom: 'Radiologie & Imagerie',
      code: 'RADIOLOGIE',
      icon: 'scan',
      description: 'IRM 3T, Scanner multibarrette, échographie doppler et radiologie interventionnelle.',
      praticiensCount: 6,
      delaiMoyen: '24h',
      urgencesPriseEnCharge: true,
      couleur: '#06b6d4'
    }
  ]);

  // Liste des Praticiens Spécialistes
  readonly doctors = signal<DoctorProfile[]>([
    {
      id: 1,
      nom: 'Sow',
      prenom: 'Ibrahima',
      titre: 'Professeur',
      specialite: 'CARDIOLOGIE',
      specialiteLabel: 'Cardiologie & Rythmologie',
      service: 'Pavillon Spécialités C',
      bureau: 'Cabinet 101 - 1er Étage',
      numeroOrdre: 'CNOM-84210',
      experience: '18 ans d’expérience',
      langues: ['Français', 'Anglais', 'Peul'],
      disponibilites: ['08:30', '09:30', '11:00', '14:30', '16:00'],
      avatarUrl: 'assets/doctors/dr_sow.jpg',
      evaluation: 4.9,
      avisCount: 142,
      description: 'Spécialiste des cardiopathies ischémiques, de l’hypertension artérielle et du cathétérisme cardiaque.'
    },
    {
      id: 2,
      nom: 'Camara',
      prenom: 'Aissatou',
      titre: 'Dr.',
      specialite: 'PEDIATRIE',
      specialiteLabel: 'Pédiatrie & Soins Néonataux',
      service: 'Bâtiment Maternité & Pédiatrie',
      bureau: 'Cabinet 102 - RDC',
      numeroOrdre: 'CNOM-81204',
      experience: '12 ans d’expérience',
      langues: ['Français', 'Soussou', 'Anglais'],
      disponibilites: ['09:00', '10:15', '11:30', '15:00', '16:30'],
      avatarUrl: 'assets/doctors/dr_camara.jpg',
      evaluation: 5.0,
      avisCount: 98,
      description: 'Prise en charge pédiatrique globale, urgences du nourrisson et néonatalogie avancée.'
    },
    {
      id: 3,
      nom: 'Bah',
      prenom: 'Fatoumata',
      titre: 'Dr.',
      specialite: 'GYNECOLOGIE',
      specialiteLabel: 'Gynécologie-Obstétrique',
      service: 'Bâtiment Maternité B',
      bureau: 'Cabinet 201 - 2e Étage',
      numeroOrdre: 'CNOM-88741',
      experience: '15 ans d’expérience',
      langues: ['Français', 'Malinké', 'Peul'],
      disponibilites: ['08:00', '10:00', '13:30', '15:30', '17:00'],
      avatarUrl: 'assets/doctors/dr_bah.jpg',
      evaluation: 4.9,
      avisCount: 215,
      description: 'Suivi de grossesse à haut risque, accouchements et chirurgie mini-invasive.'
    },
    {
      id: 4,
      nom: 'Diallo',
      prenom: 'Ousmane',
      titre: 'Dr.',
      specialite: 'NEUROLOGIE',
      specialiteLabel: 'Neurologie & Neurophysiologie',
      service: 'Pavillon Spécialités C',
      bureau: 'Cabinet 103 - 1er Étage',
      numeroOrdre: 'CNOM-86329',
      experience: '14 ans d’expérience',
      langues: ['Français', 'Anglais'],
      disponibilites: ['09:30', '11:00', '14:00', '16:00'],
      avatarUrl: 'assets/doctors/dr_diallo.jpg',
      evaluation: 4.8,
      avisCount: 76,
      description: 'Expertise des céphalées chroniques, épilepsie et exploration électroencéphalographique.'
    },
    {
      id: 5,
      nom: 'Barry',
      prenom: 'Boubacar',
      titre: 'Professeur',
      specialite: 'CHIRURGIE',
      specialiteLabel: 'Chirurgie Générale & Viscérale',
      service: 'Bloc Opératoire & Chirurgie',
      bureau: 'Bureau Chirurgie 2 - 3e Étage',
      numeroOrdre: 'CNOM-83905',
      experience: '22 ans d’expérience',
      langues: ['Français', 'Anglais'],
      disponibilites: ['08:30', '10:30', '14:30'],
      avatarUrl: 'assets/doctors/dr_barry.jpg',
      evaluation: 4.9,
      avisCount: 164,
      description: 'Chirurgie laparoscopique avancée, urgences chirurgicales et oncologie digestive.'
    },
    {
      id: 6,
      nom: 'Touré',
      prenom: 'Alpha',
      titre: 'Dr.',
      specialite: 'GENERALISTE',
      specialiteLabel: 'Médecine Générale & Prévention',
      service: 'Bâtiment Principal A',
      bureau: 'Cabinet 301 - RDC',
      numeroOrdre: 'CNOM-82190',
      experience: '10 ans d’expérience',
      langues: ['Français', 'Malinké'],
      disponibilites: ['08:00', '09:00', '10:00', '11:00', '14:00', '15:00', '16:00'],
      avatarUrl: 'assets/doctors/dr_toure.jpg',
      evaluation: 4.8,
      avisCount: 188,
      description: 'Consultations de synthèse, suivi des maladies chroniques et bilan de santé approfondi.'
    }
  ]);

  // Dernières réservations créées en mémoire pour affichage immédiat
  readonly recentBookings = signal<BookingConfirmation[]>([]);

  // Simulation d'une prise de rendez-vous avec ticket de confirmation
  bookAppointment(form: BookingFormState): BookingConfirmation {
    const doctor = this.doctors().find(d => d.id === form.medecinId) || this.doctors()[0];
    const idGen = 'RDV-' + Math.floor(100000 + Math.random() * 900000);
    const codeSecu = 'SN-' + Math.random().toString(36).substring(2, 8).toUpperCase();

    const confirmation: BookingConfirmation = {
      idRdv: idGen,
      date: form.date,
      heure: form.heure,
      medecin: doctor,
      patientNom: form.patientNom,
      patientPrenom: form.patientPrenom,
      motif: form.motif || 'Consultation standard',
      typeConsultation: form.typeConsultation,
      bureau: doctor.bureau,
      codeConfirmation: codeSecu,
      qrcodeSimule: `https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=${idGen}-${codeSecu}`
    };

    this.recentBookings.update(prev => [confirmation, ...prev]);
    return confirmation;
  }
}
