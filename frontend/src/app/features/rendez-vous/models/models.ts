import { User } from '../../../core/models/user.model';
import { Medecin, MedecinDto } from '../../medecins/models/models';

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

export type StatutRendezVous =
  | 'PROGRAMME'
  | 'CONFIRME'
  | 'EN_ATTENTE'
  | 'EN_COURS'
  | 'TERMINE'
  | 'ANNULE'
  | 'ABSENT';

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

export interface RendezVous {
  id: number;
  patient: Patient;
  medecin: Medecin;
  date_rdv: string;
  heure: string;
  motif?: string;
  statut: StatutRendezVous;
}

export interface RendezVousDto {
  id: number;
  idRendezVous?: number;
  id_patient?: number;
  id_medecin?: number;
  patient_detail?: Patient;
  medecin_detail?: MedecinDto;
  patient_nom?: string;
  patient_prenom?: string;
  patient_email?: string;
  patient_telephone?: string;
  date_rdv: string;
  heure: string;
  motif: string;
  statut: StatutRendezVous;
  statutDisplay?: string;
  typeConsultation?: 'SUR_PLACE' | 'TELECONSULTATION';
  codeConfirmation?: string;
  medecin_nom?: string;
  medecin_prenom?: string;
  medecin_specialite?: string;
  medecin_telephone?: string;
  medecin_email?: string;
  service_nom?: string;
  bureau?: string;
  type_consultation?: string;
  appointment_type?: string;
  reason?: string;
  notes?: string;
  date?: string;
  time?: string;
}

export interface CreateAppointmentDto {
  id_patient?: number;
  id_medecin?: number;
  patient?: number;
  doctor?: number;
  service?: number | string;
  date?: string;
  date_rdv?: string;
  time?: string;
  heure?: string;
  appointment_type?: string;
  type_consultation?: string;
  reason?: string;
  motif?: string;
  notes?: string;
  patient_nom?: string;
  patient_prenom?: string;
  patient_telephone?: string;
  patient_email?: string;
}
