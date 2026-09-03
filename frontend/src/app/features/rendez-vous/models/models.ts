import { Patient } from '../../patients/models/models';
import { Medecin, MedecinDto } from '../../medecins/models/models';

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
}

export interface CreateAppointmentDto {
  id_patient?: number;
  id_medecin: number;
  date_rdv: string;
  heure: string;
  motif: string;
  patient_nom?: string;
  patient_prenom?: string;
  patient_telephone?: string;
  patient_email?: string;
  type_consultation?: 'SUR_PLACE' | 'TELECONSULTATION';
}
