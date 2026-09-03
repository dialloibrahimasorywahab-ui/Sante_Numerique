import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () => import('./features/landing/landing.component').then(m => m.HomeComponent),
    title: 'Santé Numérique — Centre Hospitalier Universitaire'
  },
  {
    path: 'login',
    loadComponent: () => import('./features/auth/login/login.component').then(m => m.LoginComponent),
    title: 'Connexion — Santé Numérique'
  },
  {
    path: 'register',
    loadComponent: () => import('./features/auth/register/register.component').then(m => m.RegisterComponent),
    title: 'Créer un compte — Santé Numérique'
  },
  {
    path: 'services',
    loadComponent: () => import('./features/services-hospitaliers/services-list.component').then(m => m.ServicesListComponent),
    title: 'Nos Pôles de Soins & Spécialités — Santé Numérique'
  },
  {
    path: 'services/:id',
    loadComponent: () => import('./features/services-hospitaliers/service-detail/service-detail.component').then(m => m.ServiceDetailComponent),
    title: 'Détails du Service — Santé Numérique'
  },
  {
    path: 'medecins',
    loadComponent: () => import('./features/medecins/medecins-list.component').then(m => m.MedecinsListComponent),
    title: 'Notre Équipe Médicale — Santé Numérique'
  },
  {
    path: 'medecins/:id',
    loadComponent: () => import('./features/medecins/medecin-detail/medecin-detail.component').then(m => m.MedecinDetailComponent),
    title: 'Profil Médecin — Santé Numérique'
  },
  {
    path: 'rendez-vous',
    loadChildren: () => import('./features/rendez-vous/rendez-vous.routes').then(module => module.rendezVousRoutes)
  },
  {
    path: 'mes-rendez-vous',
    redirectTo: 'rendez-vous/mes-rendez-vous',
    pathMatch: 'full'
  },
  {
    path: 'patient/dashboard',
    redirectTo: 'rendez-vous/mes-rendez-vous',
    pathMatch: 'full'
  },
  {
    path: '**',
    redirectTo: ''
  }
];
