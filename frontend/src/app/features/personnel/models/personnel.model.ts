export interface HospitalisePatientItem {
  id: number;
  patientId: number;
  patientNom: string;
  patientTelephone?: string;
  patientAge?: number;
  dateEntree: string;
  motif: string;
  medecinNom: string;
  serviceNom: string;
  batimentNom: string;
  chambreNumero: string;
  litNumero: string;
  statut: string;
}

export interface UpcomingAppointmentItem {
  id: number;
  patientId: number;
  patientNom: string;
  patientTelephone?: string;
  medecinNom: string;
  medecinSpecialite?: string;
  dateRdv: string;
  heure: string;
  motif: string;
  statut: string;
  statutDisplay: string;
  typeConsultation?: string;
}

export interface PatientItem {
  id: number;
  idPatient: number;
  nom: string;
  prenom: string;
  dateNaissance?: string;
  sexe?: string;
  telephone?: string;
  email?: string;
  numeroSecuriteSociale?: string;
  groupeSanguin?: string;
  adresse?: string;
  personneAContacter?: string;
  telephoneContact?: string;
  actif: boolean;
}

export interface PatientParcoursData {
  patient: PatientItem;
  isHospitalise: boolean;
  localisationActuelle?: {
    serviceNom: string;
    batimentNom: string;
    chambreNumero: string;
    litNumero: string;
    dateDebut: string;
  };
  sejours: Array<{
    id: number;
    reference?: string;
    dateAdmission: string;
    dateSortie?: string;
    statut: string;
    statutDisplay: string;
    typePriseEnCharge?: string;
    serviceNom?: string;
    medecinNom?: string;
    motif?: string;
  }>;
  mouvements: Array<{
    id: number;
    dateMouvement: string;
    typeMouvement: string;
    typeMouvementDisplay: string;
    serviceOrigine?: string;
    serviceDestination?: string;
    chambreOrigine?: string;
    chambreDestination?: string;
    litOrigine?: string;
    litDestination?: string;
    motif?: string;
  }>;
  evenements: Array<{
    id: number;
    dateEvenement: string;
    typeEvenement: string;
    titre: string;
    description: string;
    importance?: string;
  }>;
}

export interface PersonnelDashboardMetrics {
  patientsHospitalises: number;
  litsOccupes: number;
  litsDisponibles: number;
  totalLits: number;
  tauxOccupation: number;
  rdvAujourdhui: number;
  totalRdv: number;
  transfertsRecents: number;
  sortiesRecentes: number;
  repartitionRdv: {
    confirmes: number;
    enAttente: number;
    termines: number;
    annules: number;
  };
  derniereMiseAJour: string;
}
