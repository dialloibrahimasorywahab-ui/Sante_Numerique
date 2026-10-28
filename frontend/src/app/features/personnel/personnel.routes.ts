import { Routes } from '@angular/router';
import { PersonnelLayoutComponent } from '../../layout/personnel-layout/personnel-layout.component';

export const personnelRoutes: Routes = [
  {
    path: '',
    component: PersonnelLayoutComponent,
    children: [
      {
        path: '',
        redirectTo: 'accueil',
        pathMatch: 'full'
      },
      {
        path: 'accueil',
        loadComponent: () =>
          import('./pages/accueil/personnel-accueil.component').then(
            m => m.PersonnelAccueilComponent
          ),
        title: 'Accueil Soignant — Santé Numérique'
      },
      {
        path: 'dashboard',
        loadComponent: () =>
          import('./pages/dashboard/personnel-dashboard.component').then(
            m => m.PersonnelDashboardComponent
          ),
        title: 'Tableau de bord — Espace Soignant'
      },
      {
        path: 'patients',
        loadComponent: () =>
          import('./pages/patients/personnel-patients.component').then(
            m => m.PersonnelPatientsComponent
          ),
        title: 'Patients — Espace Soignant'
      },
      {
        path: 'patients/:id/parcours',
        loadComponent: () =>
          import('./pages/parcours/personnel-patient-parcours.component').then(
            m => m.PersonnelPatientParcoursComponent
          ),
        title: 'Parcours Patient — Espace Soignant'
      },
      {
        path: 'rendez-vous',
        loadComponent: () =>
          import('./pages/rendez-vous/personnel-rendez-vous.component').then(
            m => m.PersonnelRendezVousComponent
          ),
        title: 'Rendez-vous — Espace Soignant'
      },
      {
        path: 'hospitalisations',
        loadComponent: () =>
          import('./pages/hospitalisations/personnel-hospitalisations.component').then(
            m => m.PersonnelHospitalisationsComponent
          ),
        title: 'Hospitalisations — Espace Soignant'
      },
      {
        path: 'profil',
        loadComponent: () =>
          import('./pages/profil/personnel-profil.component').then(
            m => m.PersonnelProfilComponent
          ),
        title: 'Mon Profil — Espace Soignant'
      }
    ]
  }
];
