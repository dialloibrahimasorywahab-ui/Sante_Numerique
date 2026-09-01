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
