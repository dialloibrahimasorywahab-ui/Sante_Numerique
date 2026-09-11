export interface PaginatedResponse<T> {
  count: number;
  total_pages?: number;
  current_page?: number;
  page_size?: number;
  next?: string | null;
  previous?: string | null;
  results: T[];
}

export interface AdminGlobalStats {
  usersCount: number;
  medecinsCount: number;
  personnelCount: number;
  patientsCount: number;
  rendezvousCount: number;
  consultationsCount: number;
  hospitalisationsCount: number;
  ordonnancesCount: number;
  batimentsCount: number;
  chambresCount: number;
  litsCount: number;
  servicesCount: number;
}

export interface BedOccupancyStats {
  totalLits: number;
  litsDisponibles: number;
  litsOccupes: number;
  litsReserves: number;
  litsMaintenance: number;
  tauxOccupation: number;
}

export interface FinancialStats {
  totalMontant: number;
  montantPaye: number;
  montantEnAttente: number;
  montantAnnule: number;
  countPaye: number;
  countEnAttente: number;
  tauxRecouvrement: number;
}

export interface RecentAppointmentItem {
  id: number;
  patientNom: string;
  patientTelephone?: string;
  medecinNom: string;
  medecinSpecialite?: string;
  dateRdv: string;
  heure: string;
  motif: string;
  statut: string;
  statutDisplay: string;
}

export interface CurrentHospitalizationItem {
  id: number;
  patientNom: string;
  patientId?: number;
  medecinNom: string;
  litNumero: string;
  chambreNumero: string;
  batimentNom: string;
  dateEntree: string;
  motif: string;
  statut: string;
}

export interface HospitalServiceSummary {
  id: number;
  nom: string;
  description: string;
  bureauLocalisation: string;
  medecinsCount: number;
  personnelCount: number;
}

export interface RecentActivityItem {
  id: string;
  type: 'PATIENT' | 'RENDEZVOUS' | 'CONSULTATION' | 'HOSPITALISATION' | 'ORDONNANCE';
  title: string;
  subtitle: string;
  date: string;
  badge: string;
  badgeClass: string;
  icon: string;
}
