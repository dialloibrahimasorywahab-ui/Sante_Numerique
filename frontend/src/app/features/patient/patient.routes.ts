import { Routes } from '@angular/router';
import { PatientLayoutComponent } from '../../layout/patient-layout/patient-layout.component';

export const patientRoutes: Routes = [
  {
    path: '',
    component: PatientLayoutComponent,
    children: [
      {
        path: '',
        redirectTo: 'dashboard',
        pathMatch: 'full'
      },
      {
        path: 'dashboard',
        loadComponent: () =>
          import('./pages/dashboard/patient-dashboard.component').then(
            m => m.PatientDashboardComponent
          ),
        title: 'Tableau de bord — Espace Patient'
      },
      {
        path: 'rendez-vous',
        loadComponent: () =>
          import('./pages/appointments/patient-appointments.component').then(
            m => m.PatientAppointmentsComponent
          ),
        title: 'Mes Rendez-vous — Espace Patient'
      },
      {
        path: 'rendez-vous/:id',
        loadComponent: () =>
          import('./pages/appointments/patient-appointment-detail.component').then(
            m => m.PatientAppointmentDetailComponent
          ),
        title: 'Détail du Rendez-vous — Espace Patient'
      },
      {
        path: 'consultations',
        loadComponent: () =>
          import('./pages/consultations/patient-consultations.component').then(
            m => m.PatientConsultationsComponent
          ),
        title: 'Mes Consultations — Espace Patient'
      },
      {
        path: 'consultations/:id',
        loadComponent: () =>
          import('./pages/consultations/patient-consultation-detail.component').then(
            m => m.PatientConsultationDetailComponent
          ),
        title: 'Compte-rendu de Consultation — Espace Patient'
      },
      {
        path: 'ordonnances',
        loadComponent: () =>
          import('./pages/prescriptions/patient-prescriptions.component').then(
            m => m.PatientPrescriptionsComponent
          ),
        title: 'Mes Ordonnances — Espace Patient'
      },
      {
        path: 'ordonnances/:id',
        loadComponent: () =>
          import('./pages/prescriptions/patient-prescription-detail.component').then(
            m => m.PatientPrescriptionDetailComponent
          ),
        title: 'Détail de l’Ordonnance — Espace Patient'
      },
      {
        path: 'hospitalisations',
        loadComponent: () =>
          import('./pages/hospitalizations/patient-hospitalizations.component').then(
            m => m.PatientHospitalizationsComponent
          ),
        title: 'Mes Hospitalisations — Espace Patient'
      },
      {
        path: 'profil',
        loadComponent: () =>
          import('./pages/profile/patient-profile.component').then(
            m => m.PatientProfileComponent
          ),
        title: 'Mon Profil — Espace Patient'
      }
    ]
  }
];
