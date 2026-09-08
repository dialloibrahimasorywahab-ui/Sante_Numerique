import { User } from '../../../core/models/user.model';
import { MedecinDto } from '../../medecins/models/models';
import { RendezVousDto } from '../../rendez-vous/models/models';

export interface PatientRecord {
  id_patient: number;
  idPatient?: number;
  id_utilisateur: User | number;
  idUtilisateur?: User | number;
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

export interface FraisConsultationDto {
  id: number;
  idFrais?: number;
  montant: number | string;
  description?: string | null;
  date_paiement?: string | null;
  statut: 'EN_ATTENTE' | 'PAYE' | 'ANNULE' | string;
  actif?: boolean;
}

export interface ConsultationDto {
  id: number;
  idConsultation?: number;
  patient: number;
  patient_details?: PatientRecord;
  medecin: number;
  medecin_details?: MedecinDto;
  rdv?: number | null;
  rdv_details?: RendezVousDto | null;
  frais?: number | null;
  frais_details?: FraisConsultationDto | null;
  date_cons: string;
  symptomes?: string;
  diagnostic?: string;
  observations?: string;
  actif: boolean;
}

export interface OrdonnanceDto {
  id: number;
  idOrdonnance?: number;
  consultation: number;
  consultation_details?: ConsultationDto;
  reference: string;
  date_ordonnance: string;
  observation?: string | null;
  actif: boolean;
}

export interface ChambreShortDto {
  id: number;
  numero_chambre: string;
  type_chambre?: string;
  bureau_localisation?: string;
  service?: any;
}

export interface LitDetailsDto {
  id: number;
  idLit?: number;
  numero_lit: string;
  etat?: string;
  etatDisplay?: string;
  chambre_detail?: ChambreShortDto;
}

export interface HospitalisationDto {
  id: number;
  idHospitalisation?: number;
  patient: number;
  patient_details?: PatientRecord;
  medecin: number;
  medecin_details?: MedecinDto;
  lit: number;
  lit_details?: LitDetailsDto;
  date_entree: string;
  date_sortie?: string | null;
  motif: string;
  statut: 'PROGRAMMEE' | 'EN_COURS' | 'TERMINEE' | 'ANNULEE' | string;
  observation?: string | null;
  actif: boolean;
}

export interface UpdateProfileDto {
  nom: string;
  prenom: string;
  email: string;
  telephone: string;
  date_naissance?: string | null;
  dateNaissance?: string | null;
}

export interface ChangePasswordDto {
  ancienMotDePasse: string;
  nouveauMotDePasse: string;
  confirmationMotDePasse: string;
}

export interface PatientDashboardStats {
  upcomingAppointmentsCount: number;
  totalConsultationsCount: number;
  totalPrescriptionsCount: number;
  activeHospitalizationsCount: number;
}
