import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';
import { roleGuard } from './core/guards/role.guard';

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
    path: 'patient',
    canActivate: [authGuard, roleGuard],
    data: { roles: ['PATIENT'] },
    loadChildren: () => import('./features/patient/patient.routes').then(m => m.patientRoutes)
  },
  {
    path: 'medecin',
    canActivate: [authGuard, roleGuard],
    data: { roles: ['MEDECIN'] },
    loadChildren: () => import('./features/doctor/doctor.routes').then(m => m.doctorRoutes)
  },
  {
    path: 'personnel',
    redirectTo: 'medecin/dashboard'
  },
  {
    path: 'personnel/dashboard',
    redirectTo: 'medecin/dashboard',
    pathMatch: 'full'
  },
  {
    path: 'admin/dashboard',
    redirectTo: 'medecins',
    pathMatch: 'full'
  },
  {
    path: '**',
    redirectTo: ''
  }
];
