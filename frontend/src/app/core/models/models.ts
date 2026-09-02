export type UserRole = 'ADMINISTRATEUR' | 'MEDECIN' | 'INFIRMIER' | 'PATIENT';

export interface User {
  id_user: number;
  nom: string;
  prenom: string;
  email: string;
  telephone: string;
  login: string;
  role: UserRole;
  date_naissance?: string | null;
  actif: boolean;
  is_staff?: boolean;
}

export interface Patient {
  id_patient: number;
  id_utilisateur: User;
  date_naissance?: string;
  sexe: 'M' | 'F';
  adresse: string;
  groupe_sanguin: 'A+' | 'A-' | 'B+' | 'B-' | 'AB+' | 'AB-' | 'O+' | 'O-';
  numero_securite_sociale?: string;
  personne_a_contacter: string;
  date_inscription: string;
}

export type SpecialiteMedecin =
  | 'GENERALISTE'
  | 'CARDIOLOGIE'
  | 'PEDIATRIE'
  | 'GYNECOLOGIE'
  | 'NEUROLOGIE'
  | 'DERMATOLOGIE'
  | 'CHIRURGIE'
  | 'OPHTALMOLOGIE'
  | 'PSYCHIATRIE'
  | 'RADIOLOGIE';

export interface MedecinDto {
  idMedecin: number;
  idUtilisateur?: number;
  nom: string;
  prenom: string;
  email?: string;
  telephone?: string;
  specialite: string;
  specialiteDisplay?: string;
  matricule?: string | null;
  numeroOrdre: string;
  telephonePro?: string | null;
  emailPro?: string | null;
  bureau?: string | null;
  dateEmbauche?: string;
  // Computed fields
  titre?: string;
  specialiteLabel?: string;
  avatarInitials?: string;
  anciennete?: string;
  langues?: string[];
  disponibilites?: string[];
  biographie?: string;
  evaluation?: number;
  avisCount?: number;
}

export interface Medecin {
  id_medecin: number;
  id_utilisateur: User;
  specialite: SpecialiteMedecin;
  matricule?: string;
  numero_ordre: string;
  telephone_pro?: string;
  email_pro?: string;
  bureau?: string;
  date_embauche: string;
}

export interface PaginatedResponse<T> {
  count: number;
  total_pages?: number;
  current_page?: number;
  page_size?: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface ServiceHospitalier {
  id_service: number;
  idService?: number;
  nom_service: string;
  nomService?: string;
  nom_service_display?: string;
  nomServiceDisplay?: string;
  description?: string | null;
  bureau_localisation?: string | null;
  bureauLocalisation?: string | null;
  actif: boolean;
  // Computed / UI properties
  icon?: string;
  displayNom?: string;
  displayDesc?: string;
  badgeCountMedecins?: number;
}

export type StatutRendezVous =
  | 'PROGRAMME'
  | 'CONFIRME'
  | 'EN_ATTENTE'
  | 'EN_COURS'
  | 'TERMINE'
  | 'ANNULE'
  | 'ABSENT';

export interface RendezVous {
  id: number;
  patient: Patient;
  medecin: Medecin;
  date_rdv: string;
  heure: string;
  motif?: string;
  statut: StatutRendezVous;
}

export interface Consultation {
  id: number;
  patient: Patient;
  medecin?: Medecin;
  rdv?: RendezVous;
  date_cons: string;
  symptomes?: string;
  diagnostic?: string;
  observations?: string;
  frais?: FraisConsultation;
  actif: boolean;
  ordonnances?: Ordonnance[];
}

export interface Ordonnance {
  id: number;
  consultation: number | Consultation;
  reference: string;
  date_ordonnance: string;
  observation?: string;
  actif: boolean;
  medecin_nom?: string;
  patient_nom?: string;
}

export interface FraisConsultation {
  id: number;
  montant: number;
  statut_paiement: 'EN_ATTENTE' | 'PAYE' | 'ANNULE';
  mode_paiement?: string;
}

export interface Batiment {
  id_batiment: number;
  nom: string;
  nombre_chambre: number;
  description?: string;
  actif: boolean;
}

export type TypeChambre = 'INDIVIDUELLE' | 'DOUBLE' | 'COMMUNE' | 'SUITE' | 'URGENCES' | 'REANIMATION';

export interface Chambre {
  id_chambre: number;
  batiment: Batiment;
  numero_chambre: number;
  type_chambre: TypeChambre;
  capacite: number;
  prix_par_jour?: number;
  actif: boolean;
}

export type EtatLit = 'DISPONIBLE' | 'OCCUPE' | 'RESERVE' | 'EN_NETTOYAGE' | 'HORS_SERVICE';

export interface Lit {
  id_lit: number;
  chambre: Chambre;
  numero_lit: number;
  etat: EtatLit;
}

export type StatutHospitalisation = 'PROGRAMMEE' | 'EN_COURS' | 'TERMINEE' | 'ANNULEE';

export interface Hospitalisation {
  id: number;
  patient: Patient;
  medecin?: Medecin;
  lit?: Lit;
  date_entree: string;
  date_sortie?: string | null;
  motif?: string;
  statut: StatutHospitalisation;
  observation?: string;
  actif: boolean;
}

// -----------------------------------------------------------------------------
// Rendez-vous & Créneaux Interfaces
// -----------------------------------------------------------------------------
export interface TimeSlot {
  heure: string;
  disponible: boolean;
  raison?: string | null;
}

export interface AvailableSlotsResponse {
  medecin_id: number;
  date: string;
  creneaux: TimeSlot[];
}

export interface RendezVousDto {
  id: number;
  idRendezVous?: number;
  id_patient?: number;
  id_medecin?: number;
  patient_detail?: Patient;
  medecin_detail?: MedecinDto;
  date_rdv: string;
  heure: string;
  motif: string;
  statut: StatutRendezVous;
  statutDisplay?: string;
  // Computed / UI helpers
  typeConsultation?: 'SUR_PLACE' | 'TELECONSULTATION';
  codeConfirmation?: string;
}

export interface CreateAppointmentDto {
  id_patient?: number;
  id_medecin: number;
  date_rdv: string;
  heure: string;
  motif: string;
  // Patient details for guest / new patient
  patient_nom?: string;
  patient_prenom?: string;
  patient_telephone?: string;
  patient_email?: string;
  type_consultation?: 'SUR_PLACE' | 'TELECONSULTATION';
}

