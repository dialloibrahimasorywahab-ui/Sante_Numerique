export type UserRole = 'ADMINISTRATEUR' | 'MEDECIN' | 'INFIRMIER' | 'PATIENT';

export interface User {
  id_user: number;
  idUser?: number;
  nom: string;
  prenom: string;
  email: string;
  telephone: string;
  login: string;
  role: UserRole;
  date_naissance?: string | null;
  dateNaissance?: string | null;
  actif: boolean;
  is_staff?: boolean;
}

export interface LoginDto {
  login: string;
  motDePasse: string;
}

export interface RegisterDto {
  nom: string;
  prenom: string;
  email: string;
  telephone: string;
  login: string;
  motDePasse: string;
  confirmationMotDePasse?: string;
  date_naissance?: string | null;
  dateNaissance?: string | null;
}
