import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () => import('./features/landing/landing.component').then(m => m.HomeComponent),
    title: 'Santé Numérique — Centre Hospitalier Universitaire'
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
    loadComponent: () => import('./features/rendez-vous/pages/book-appointment/book-appointment.component').then(m => m.BookAppointmentComponent),
    title: 'Prendre Rendez-vous — Santé Numérique'
  },
  {
    path: 'mes-rendez-vous',
    loadComponent: () => import('./features/rendez-vous/pages/my-appointments/my-appointments.component').then(m => m.MyAppointmentsComponent),
    title: 'Mes Rendez-vous — Santé Numérique'
  },
  {
    path: '**',
    redirectTo: ''
  }
];
