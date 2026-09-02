import { Patient } from '../../patients/models/models';
import { Medecin } from '../../medecins/models/models';

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
