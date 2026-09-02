import { User } from '../../../core/models/user.model';

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
