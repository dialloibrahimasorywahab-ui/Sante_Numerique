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
  patientDetails?: DoctorPatientDto;
  patientDetail?: DoctorPatientDto;
  medecin: number;
  id_medecin?: number;
  medecin_details?: DoctorProfileDto;
  medecin_detail?: DoctorProfileDto;
  medecinDetails?: DoctorProfileDto;
  medecinDetail?: DoctorProfileDto;
  date_rdv: string;
  dateRdv?: string;
  heure: string;
  motif?: string;
  statut: AppointmentStatus;
}

export interface FraisConsultationDto {
  id?: number;
  idFrais?: number;
  montant: string | number;
  description?: string;
  date_paiement?: string | null;
  statut: 'EN_ATTENTE' | 'PAYE' | 'ANNULE' | string;
  statut_display?: string;
  actif?: boolean;
}

export interface DoctorConsultationDto {
  id: number;
  idConsultation?: number;
  patient: number;
  id_patient?: number;
  patient_details?: DoctorPatientDto;
  patient_detail?: DoctorPatientDto;
  patientDetails?: DoctorPatientDto;
  patientDetail?: DoctorPatientDto;
  medecin: number;
  id_medecin?: number;
  medecin_details?: DoctorProfileDto;
  medecin_detail?: DoctorProfileDto;
  medecinDetails?: DoctorProfileDto;
  medecinDetail?: DoctorProfileDto;
  rdv?: number | null;
  rdv_details?: DoctorAppointmentDto | null;
  frais?: number | null;
  frais_details?: FraisConsultationDto | null;
  date_cons: string;
  dateCons?: string;
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
  dateCons?: string;
  symptomes?: string;
  diagnostic?: string;
  observations?: string;
  montant_frais?: number | string | null;
  description_frais?: string | null;
}

export interface DoctorPrescriptionDto {
  id: number;
  idOrdonnance?: number;
  consultation: number;
  consultation_details?: DoctorConsultationDto;
  consultationDetails?: DoctorConsultationDto;
  medecin_nom?: string;
  medecinNom?: string;
  patient_nom?: string;
  patientNom?: string;
  reference: string;
  date_ordonnance?: string;
  dateOrdonnance?: string;
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


export type StatutHospitalisation = 'PROGRAMMEE' | 'EN_COURS' | 'TERMINEE' | 'ANNULEE';
export type PrioriteAdmission = 'NORMAL' | 'URGENT' | 'TRES_URGENT';

export interface DoctorHospitalisationDto {
  id: number;
  idHospitalisation?: number;
  id_admission?: number;
  patient: number;
  patient_nom?: string;
  patientNom?: string;
  patient_details?: DoctorPatientDto;
  medecin?: number;
  medecin_nom?: string;
  medecinNom?: string;
  medecin_details?: DoctorProfileDto;
  lit?: number;
  lit_numero?: string;
  litNumero?: string;
  lit_details?: any;
  chambre_numero?: string;
  chambreNumero?: string;
  batiment_nom?: string;
  batimentNom?: string;
  date_entree: string;
  dateEntree?: string;
  date_sortie?: string | null;
  dateSortie?: string | null;
  motif?: string;
  statut: StatutHospitalisation;
  statut_display?: string;
  priorite?: PrioriteAdmission;
  priorite_display?: string;
  diagnostic_provisoire?: string;
  diagnosticProvisoire?: string;
  symptomes?: string;
  service_nom?: string;
  serviceNom?: string;
  antecedents?: string;
  allergies?: string;
  traitements_en_cours?: string;
  traitementsEnCours?: string;
  observation?: string;
  actif?: boolean;
  patient_identifiants?: any;
  nouveau_patient_cree?: boolean;
}

export interface CreateHospitalisationDto {
  patient?: number | null;
  medecin?: number | null;
  lit?: number | null;
  date_entree?: string;
  date_sortie?: string | null;
  motif?: string;
  statut?: StatutHospitalisation;
  observation?: string;
  priorite?: PrioriteAdmission | string;
  diagnostic_provisoire?: string;
  diagnosticProvisoire?: string;
  symptomes?: string;
  service_nom?: string;
  serviceNom?: string;
  antecedents?: string;
  allergies?: string;
  traitements_en_cours?: string;
  traitementsEnCours?: string;
  nouveau_patient?: boolean;
  nom?: string;
  prenom?: string;
  telephone?: string;
  email?: string;
  date_naissance?: string | null;
  sexe?: string;
  adresse?: string;
  groupe_sanguin?: string;
  numero_securite_sociale?: string;
  personne_a_contacter?: string;
}

export interface AdmissionConfirmationDto {
  id: number;
  id_admission: number;
  patient_id?: number;
  patient_nom?: string;
  patient_telephone?: string;
  lit_label?: string;
  service_nom?: string;
  statut: string;
  priorite?: string;
  date_entree: string;
  nouveau_patient_cree?: boolean;
  patient_identifiants?: {
    login: string;
    email: string;
    mot_de_passe_initial: string;
    patient_id: number;
    nom: string;
    prenom: string;
    message?: string;
  };
}

export interface AvailableBedDto {
  id_lit: number;
  numero_lit: number | string;
  etat: string;
  chambre?: {
    id_chambre: number;
    numero_chambre: number | string;
    type_chambre?: string;
    batiment?: {
      id_batiment: number;
      nom: string;
    };
  };
}
