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
