import { Routes } from '@angular/router';
import { AdminLayoutComponent } from '../../layout/admin-layout/admin-layout.component';

export const adminRoutes: Routes = [
  {
    path: '',
    component: AdminLayoutComponent,
    children: [
      {
        path: '',
        redirectTo: 'dashboard',
        pathMatch: 'full'
      },
      {
        path: 'dashboard',
        loadComponent: () =>
          import('./pages/dashboard/admin-dashboard.component').then(
            m => m.AdminDashboardComponent
          ),
        title: 'Tableau de bord Administrateur — Santé Numérique'
      },
      {
        path: 'details/:resource/:id',
        loadComponent: () =>
          import('./pages/detail/admin-detail.component').then(
            m => m.AdminDetailComponent
          ),
        title: 'Détail — Espace Administrateur'
      },

      // --- GESTION DES UTILISATEURS ---
      {
        path: 'patients',
        loadComponent: () =>
          import('./pages/users/admin-users.component').then(
            m => m.AdminUsersComponent
          ),
        data: { userType: 'patients' },
        title: 'Dossiers Patients — Espace Administrateur'
      },
      {
        path: 'medecins',
        loadComponent: () =>
          import('./pages/users/admin-users.component').then(
            m => m.AdminUsersComponent
          ),
        data: { userType: 'medecins' },
        title: 'Corps Médical — Espace Administrateur'
      },
      {
        path: 'personnel',
        loadComponent: () =>
          import('./pages/users/admin-users.component').then(
            m => m.AdminUsersComponent
          ),
        data: { userType: 'personnel' },
        title: 'Personnel Soignant — Espace Administrateur'
      },

      // --- GESTION HOSPITALIÈRE ---
      {
        path: 'services',
        loadComponent: () =>
          import('./pages/hospital/admin-hospital.component').then(
            m => m.AdminHospitalComponent
          ),
        data: { hospitalTab: 'services' },
        title: 'Pôles & Services — Espace Administrateur'
      },
      {
        path: 'batiments',
        loadComponent: () =>
          import('./pages/hospital/admin-hospital.component').then(
            m => m.AdminHospitalComponent
          ),
        data: { hospitalTab: 'batiments' },
        title: 'Bâtiments Hospitaliers — Espace Administrateur'
      },
      {
        path: 'chambres',
        loadComponent: () =>
          import('./pages/hospital/admin-hospital.component').then(
            m => m.AdminHospitalComponent
          ),
        data: { hospitalTab: 'chambres' },
        title: 'Chambres Hospitalières — Espace Administrateur'
      },
      {
        path: 'lits',
        loadComponent: () =>
          import('./pages/hospital/admin-hospital.component').then(
            m => m.AdminHospitalComponent
          ),
        data: { hospitalTab: 'lits' },
        title: 'Lits d\'hospitalisation — Espace Administrateur'
      },

      // --- ACTIVITÉS MÉDICALES ---
      {
        path: 'rendezvous',
        loadComponent: () =>
          import('./pages/medical/admin-medical.component').then(
            m => m.AdminMedicalComponent
          ),
        data: { medicalTab: 'rendezvous' },
        title: 'Rendez-vous — Espace Administrateur'
      },
      {
        path: 'consultations',
        loadComponent: () =>
          import('./pages/medical/admin-medical.component').then(
            m => m.AdminMedicalComponent
          ),
        data: { medicalTab: 'consultations' },
        title: 'Consultations — Espace Administrateur'
      },
      {
        path: 'hospitalisations',
        loadComponent: () =>
          import('./pages/medical/admin-medical.component').then(
            m => m.AdminMedicalComponent
          ),
        data: { medicalTab: 'hospitalisations' },
        title: 'Hospitalisations — Espace Administrateur'
      },
      {
        path: 'ordonnances',
        loadComponent: () =>
          import('./pages/medical/admin-medical.component').then(
            m => m.AdminMedicalComponent
          ),
        data: { medicalTab: 'ordonnances' },
        title: 'Ordonnances Médicales — Espace Administrateur'
      },

      // --- FINANCE & FACTURATION ---
      {
        path: 'finances',
        loadComponent: () =>
          import('./pages/finances/admin-finances.component').then(
            m => m.AdminFinancesComponent
          ),
        title: 'Finance & Facturation — Espace Administrateur'
      }
    ]
  }
];
