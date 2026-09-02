import { Patient } from '../../patients/models/models';
import { Medecin } from '../../medecins/models/models';
import { RendezVous } from '../../appointment/models/models';

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
