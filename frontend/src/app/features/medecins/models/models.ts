import { User } from '../../../core/models/user.model';

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
