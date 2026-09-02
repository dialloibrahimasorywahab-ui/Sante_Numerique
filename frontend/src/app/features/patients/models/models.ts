import { User } from '../../auth/models/models';

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
