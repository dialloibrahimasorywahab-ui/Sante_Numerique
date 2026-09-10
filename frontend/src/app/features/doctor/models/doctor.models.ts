import { User } from '../../../core/models/user.model';

export type AppointmentStatus = 'EN_ATTENTE' | 'CONFIRME' | 'EN_COURS' | 'TERMINE' | 'ANNULE' | 'ABSENT';

export interface DoctorProfileDto {
  idMedecin: number;
  idUtilisateur?: number;
  nom?: string;
  prenom?: string;
  email?: string;
  telephone?: string;
  specialite: string;
  specialiteDisplay?: string;
  matricule?: string;
  numeroOrdre: string;
  telephonePro?: string;
  emailPro?: string;
  bureau?: string;
  dateEmbauche?: string;
}

export interface DoctorPatientDto {
  id_patient: number;
  idPatient?: number;
  nom?: string;
  prenom?: string;
  email?: string;
  telephone?: string;
  date_naissance?: string | null;
  dateNaissance?: string | null;
  sexe?: 'M' | 'F' | string;
  adresse?: string;
  groupe_sanguin?: string;
  groupeSanguin?: string;
  numero_securite_sociale?: string | null;
  numeroSecuriteSociale?: string | null;
  personne_a_contacter?: string;
  personneAContacter?: string;
  date_inscription?: string;
  dateInscription?: string;
}

export interface CreatePatientDto {
  nom: string;
  prenom: string;
  email: string;
  telephone: string;
  dateNaissance?: string | null;
  date_naissance?: string | null;
  sexe?: 'M' | 'F' | string;
  adresse?: string;
  groupeSanguin?: string;
  groupe_sanguin?: string;
  numeroSecuriteSociale?: string | null;
  numero_securite_sociale?: string | null;
  personneAContacter?: string | null;
  personne_a_contacter?: string | null;
  login?: string;
  motDePasse?: string;
  mot_de_passe?: string;
}


export interface DoctorAppointmentDto {
  id: number;
  idRendezVous?: number;
  patient: number;
  id_patient?: number;
  patient_details?: DoctorPatientDto;
  patient_detail?: DoctorPatientDto;
  medecin: number;
  id_medecin?: number;
  medecin_details?: DoctorProfileDto;
  medecin_detail?: DoctorProfileDto;
  date_rdv: string;
  dateRdv?: string;
  heure: string;
  motif?: string;
  statut: AppointmentStatus;
}

export interface DoctorConsultationDto {
  id: number;
  idConsultation?: number;
  patient: number;
  id_patient?: number;
  patient_details?: DoctorPatientDto;
  patient_detail?: DoctorPatientDto;
  medecin: number;
  id_medecin?: number;
  medecin_details?: DoctorProfileDto;
  medecin_detail?: DoctorProfileDto;
  rdv?: number | null;
  rdv_details?: DoctorAppointmentDto | null;
  frais?: number | null;
  date_cons: string;
  symptomes?: string;
  diagnostic?: string;
  observations?: string;
  actif: boolean;
}

export interface CreateConsultationDto {
  patient: number;
  medecin: number;
  rdv?: number | null;
  date_cons: string;
  symptomes?: string;
  diagnostic?: string;
  observations?: string;
}

export interface DoctorPrescriptionDto {
  id: number;
  idOrdonnance?: number;
  consultation: number;
  consultation_details?: DoctorConsultationDto;
  reference: string;
  date_ordonnance: string;
  observation?: string | null;
  actif: boolean;
}

export interface CreatePrescriptionDto {
  consultation: number;
  reference?: string;
  date_ordonnance?: string;
  observation?: string | null;
}

export interface DisponibiliteMedecinDto {
  id?: number;
  medecin?: number;
  jour_semaine: number; // 0=Lundi, ..., 6=Dimanche
  jourSemaine?: number;
  jourSemaineDisplay?: string;
  heure_debut: string; // HH:MM
  heureDebut?: string;
  heure_fin: string; // HH:MM
  heureFin?: string;
  pause_debut?: string | null;
  pauseDebut?: string | null;
  pause_fin?: string | null;
  pauseFin?: string | null;
  duree_creneau: number;
  dureeCreneau?: number;
  actif: boolean;
}

export interface IndisponibiliteMedecinDto {
  id?: number;
  medecin?: number;
  date_debut: string; // YYYY-MM-DD
  dateDebut?: string;
  date_fin: string; // YYYY-MM-DD
  dateFin?: string;
  toute_la_journee: boolean;
  touteLaJournee?: boolean;
  heure_debut?: string | null;
  heureDebut?: string | null;
  heure_fin?: string | null;
  heureFin?: string | null;
  motif?: string | null;
  actif: boolean;
}

export interface CreneauItemDto {
  heure: string;
  disponible: boolean;
  raison?: string | null;
}

export interface CreneauxResponseDto {
  medecin_id: number;
  date: string;
  jour_semaine?: number;
  est_indisponible?: boolean;
  motif_indisponibilite?: string | null;
  creneaux: CreneauItemDto[];
}

export interface DoctorDashboardStats {
  appointmentsTodayCount: number;
  appointmentsUpcomingCount: number;
  consultationsTotalCount: number;
  patientsFollowedCount: number;
}

export interface PaginatedResult<T> {
  count: number;
  next?: string | null;
  previous?: string | null;
  results: T[];
}
