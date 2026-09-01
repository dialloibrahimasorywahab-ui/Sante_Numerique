import { Injectable, signal } from '@angular/core';
import { User, UserRole } from '../models/models';

export interface PersonaAccount {
  role: UserRole;
  roleLabel: string;
  nomComplet: string;
  titre: string;
  service: string;
  login: string;
  badgeClass: string;
  avatarInitials: string;
  description: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  readonly personas: PersonaAccount[] = [
    {
      role: 'PATIENT',
      roleLabel: 'Espace Patient',
      nomComplet: 'Marie Dupont',
      titre: 'Patiente assurée',
      service: 'Dossier Médical N° 45892',
      login: 'marie.dupont',
      badgeClass: 'badge-sky',
      avatarInitials: 'MD',
      description: 'Accédez à vos rendez-vous, ordonnances électroniques et pass santé.'
    },
    {
      role: 'MEDECIN',
      roleLabel: 'Espace Praticien',
      nomComplet: 'Pr. Ibrahima Sow',
      titre: 'Chef de Service Cardiologie',
      service: 'Pavillon Spécialités C',
      login: 'dr.sow',
      badgeClass: 'badge-teal',
      avatarInitials: 'IS',
      description: 'Atelier de consultation, file d’attente du jour et e-prescriptions.'
    },
    {
      role: 'INFIRMIER',
      roleLabel: 'Personnel Soignant',
      nomComplet: 'Claire Camara',
      titre: 'Infirmière Major',
      service: 'Pavillon des Urgences & Lits',
      login: 'infirmiere.claire',
      badgeClass: 'badge-warning',
      avatarInitials: 'CC',
      description: 'Suivi des admissions en direct, constantes vitales et gestion des lits.'
    },
    {
      role: 'ADMINISTRATEUR',
      roleLabel: 'Administration SaaS',
      nomComplet: 'Direction Médicale CHU',
      titre: 'Administrateur Système',
      service: 'Direction Hospitalière',
      login: 'admin_hopital',
      badgeClass: 'badge-danger',
      avatarInitials: 'AD',
      description: 'Pilotage global, KPIs, cartographie des lits et registres d’état civil.'
    }
  ];

  // Current active logged-in persona (defaults to Patient for friendly public browsing)
  readonly currentUser = signal<User | null>({
    id_user: 1,
    nom: 'Dupont',
    prenom: 'Marie',
    email: 'marie.dupont@santenumerique.com',
    telephone: '+224 621 45 89 20',
    login: 'marie.dupont',
    role: 'PATIENT',
    actif: true
  });

  readonly activePersona = signal<PersonaAccount>(this.personas[0]);
  readonly isAuthenticated = signal<boolean>(true);

  // Switch persona in 1 click for seamless live demonstration
  switchPersona(persona: PersonaAccount): void {
    this.activePersona.set(persona);
    const [prenom, ...nomParts] = persona.nomComplet.split(' ');
    const nom = nomParts.join(' ');

    this.currentUser.set({
      id_user: persona.role === 'ADMINISTRATEUR' ? 99 : (persona.role === 'MEDECIN' ? 2 : 1),
      nom: nom,
      prenom: prenom,
      email: `${persona.login}@santenumerique.com`,
      telephone: '+224 620 00 00 00',
      login: persona.login,
      role: persona.role,
      actif: true
    });
    this.isAuthenticated.set(true);
  }

  logout(): void {
    this.currentUser.set(null);
    this.isAuthenticated.set(false);
  }
}
