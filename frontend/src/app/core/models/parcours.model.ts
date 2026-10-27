export type TypePriseEnCharge =
  | 'URGENCE'
  | 'CONSULTATION'
  | 'HOSPITALISATION_PROGRAMMEE'
  | 'TRANSFERT_EXTERNE'
  | 'AUTRE';

export type StatutSejour =
  | 'EN_ATTENTE'
  | 'EN_COURS'
  | 'TRANSFERE'
  | 'SORTIE_AUTORISEE'
  | 'TERMINE'
  | 'ANNULE';

export type TypeMouvement =
  | 'ADMISSION'
  | 'TRANSFERT_SERVICE'
  | 'CHANGEMENT_CHAMBRE'
  | 'CHANGEMENT_LIT'
  | 'DEPART_EXAMEN'
  | 'RETOUR_EXAMEN'
  | 'SORTIE_TEMPORAIRE'
  | 'RETOUR_SORTIE_TEMPO'
  | 'SORTIE_DEFINITIVE';

export type TypeEvenement =
  | 'ADMISSION'
  | 'CONSULTATION'
  | 'PRESCRIPTION_EXAMEN'
  | 'EXAMEN_EN_COURS'
  | 'RESULTAT_EXAMEN'
  | 'TRANSFERT_INTERNE'
  | 'ATTRIBUTION_LIT'
  | 'LIBERATION_LIT'
  | 'SOIN_ADMINISTRE'
  | 'OBSERVATION'
  | 'SORTIE_AUTORISEE'
  | 'SORTIE_DEFINITIVE'
  | 'AUTRE';

export type NiveauImportance = 'INFO' | 'ATTENTION' | 'CRITIQUE';

export interface DashboardStats {
  patientsPresents: number;
  sejoursEnCours: number;
  patientsUrgences: number;
  patientsHospitalises: number;
  litsOccupes: number;
  litsDisponibles: number;
  litsIndisponibles?: number;
  totalLits: number;
  transfertsRecents: number;
  sortiesRecentes: number;
  timestamp: string;
}

export interface LocalisationActuelleInfo {
  id: number;
  serviceId: number;
  serviceNom: string;
  batimentId?: number | null;
  batimentNom?: string | null;
  chambreId?: number | null;
  chambreNumero?: string | number | null;
  litId?: number | null;
  litNumero?: string | null;
  dateDebut: string;
}

export interface Sejour {
  idSejour: number;
  reference: string;
  patient: number;
  patientDetails?: any;
  serviceResponsable: number;
  serviceDetails?: any;
  medecinResponsable?: number | null;
  medecinDetails?: any;
  enregistrePar?: number | null;
  typePriseEnCharge: TypePriseEnCharge;
  typePriseEnChargeDisplay?: string;
  statut: StatutSejour;
  statutDisplay?: string;
  dateAdmission: string;
  motifAdmission: string;
  dateSortie?: string | null;
  motifSortie?: string | null;
  localisationActuelleInfo?: LocalisationActuelleInfo | null;
  actif: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface LocalisationPatient {
  id: number;
  sejour: number;
  sejourReference?: string;
  patientNom?: string;
  patientPrenom?: string;
  patientNomComplet?: string;
  patientNss?: string;
  service: number;
  serviceDetails?: any;
  batiment?: number | null;
  batimentDetails?: any;
  chambre?: number | null;
  chambreDetails?: any;
  lit?: number | null;
  litDetails?: any;
  dateDebut: string;
  dateFin?: string | null;
  estActuelle: boolean;
  motif?: string;
  commentaire?: string;
  enregistrePar?: number | null;
}

export interface MouvementPatient {
  id: number;
  sejour: number;
  sejourReference?: string;
  localisationOrigine?: number | null;
  localisationOrigineDetails?: LocalisationPatient | null;
  localisationDestination?: number | null;
  localisationDestinationDetails?: LocalisationPatient | null;
  dateMouvement: string;
  typeMouvement: TypeMouvement;
  typeMouvementDisplay?: string;
  motif?: string;
  commentaire?: string;
  enregistrePar?: number | null;
  effectueParNom?: string;
  effectueParRole?: string;
  sourceDetails?: any;
  destinationDetails?: any;
}

export interface EvenementParcours {
  id: number;
  sejour: number;
  sejourReference?: string;
  typeEvenement: TypeEvenement;
  typeEvenementDisplay?: string;
  titre: string;
  description: string;
  dateEvenement: string;
  declarePar?: number | null;
  declareParNom?: string | null;
  importance: NiveauImportance;
  importanceDisplay?: string;
  donneesAdditionnelles?: Record<string, any>;
  actif: boolean;
  createdAt: string;
}

export interface DemandeAnalyse {
  id: number;
  patient: number;
  patientId?: number;
  sejour?: number | null;
  sejourReference?: string;
  prescripteur?: number | null;
  typeAnalyse: string;
  datePrescription: string;
  statut: string;
  statutDisplay?: string;
  datePrelevement?: string | null;
  dateResultat?: string | null;
  commentaire?: string;
  actif: boolean;
}

export interface DossierSyntheseSejour {
  sejour: Sejour;
  localisationActuelle: LocalisationPatient | null;
  historiqueLocalisations: LocalisationPatient[];
  localisations?: LocalisationPatient[];
  mouvements: MouvementPatient[];
  evenements: EvenementParcours[];
  analyses: DemandeAnalyse[];
}

export interface AdmissionPatientDto {
  patient: number;
  serviceResponsable: number;
  medecinResponsable?: number | null;
  batiment?: number | null;
  chambre?: number | null;
  lit?: number | null;
  typePriseEnCharge?: TypePriseEnCharge;
  dateAdmission?: string;
  motifAdmission: string;
}

export interface TransfertPatientDto {
  sejour: number;
  service: number;
  batiment?: number | null;
  chambre?: number | null;
  lit?: number | null;
  typeMouvement?: TypeMouvement;
  dateMouvement?: string;
  motif: string;
  commentaire?: string;
}

export interface SortiePatientDto {
  dateSortie?: string;
  motifSortie: string;
}
