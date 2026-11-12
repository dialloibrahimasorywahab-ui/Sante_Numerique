import { Routes } from '@angular/router';
import { DoctorLayoutComponent } from '../../layout/doctor-layout/doctor-layout.component';

export const doctorRoutes: Routes = [
  {
    path: '',
    component: DoctorLayoutComponent,
    children: [
      {
        path: '',
        redirectTo: 'dashboard',
        pathMatch: 'full'
      },
      {
        path: 'dashboard',
        loadComponent: () =>
          import('./pages/dashboard/doctor-dashboard.component').then(
            m => m.DoctorDashboardComponent
          ),
        title: 'Tableau de bord — Espace Médecin'
      },
      {
        path: 'rendez-vous',
        loadComponent: () =>
          import('./pages/appointments/doctor-appointments.component').then(
            m => m.DoctorAppointmentsComponent
          ),
        title: 'Mes Rendez-vous — Espace Médecin'
      },
      {
        path: 'patients',
        loadComponent: () =>
          import('./pages/patients/doctor-patients.component').then(
            m => m.DoctorPatientsComponent
          ),
        title: 'Mes Patients — Espace Médecin'
      },
      {
        path: 'patients/:id',
        loadComponent: () =>
          import('./pages/patients/doctor-patient-detail.component').then(
            m => m.DoctorPatientDetailComponent
          ),
        title: 'Dossier Patient — Espace Médecin'
      },
      {
        path: 'hospitalisations',
        loadComponent: () =>
          import('./pages/hospitalisations/doctor-hospitalisations.component').then(
            m => m.DoctorHospitalisationsComponent
          ),
        title: 'Admissions & Lits — Espace Médecin'
      },
      {
        path: 'admissions',
        redirectTo: 'hospitalisations',
        pathMatch: 'full'
      },
      {
        path: 'admissions/nouveau',
        loadComponent: () =>
          import('./pages/admissions/doctor-admission-create.component').then(
            m => m.DoctorAdmissionCreateComponent
          ),
        title: 'Nouvelle Admission — Espace Médecin'
      },
      {
        path: 'admissions/:id',
        loadComponent: () =>
          import('./pages/admissions/doctor-admission-detail.component').then(
            m => m.DoctorAdmissionDetailComponent
          ),
        title: 'Détail Admission — Espace Médecin'
      },
      {
        path: 'hospitalisations/nouveau',
        redirectTo: 'admissions/nouveau',
        pathMatch: 'full'
      },
      {
        path: 'consultations',
        loadComponent: () =>
          import('./pages/consultations/doctor-consultations.component').then(
            m => m.DoctorConsultationsComponent
          ),
        title: 'Mes Consultations — Espace Médecin'
      },
      {
        path: 'consultations/nouveau',
        loadComponent: () =>
          import('./pages/consultations/doctor-consultation-create.component').then(
            m => m.DoctorConsultationCreateComponent
          ),
        title: 'Nouvelle Consultation — Espace Médecin'
      },
      {
        path: 'consultations/:id',
        loadComponent: () =>
          import('./pages/consultations/doctor-consultation-detail.component').then(
            m => m.DoctorConsultationDetailComponent
          ),
        title: 'Compte-rendu de Consultation — Espace Médecin'
      },
      {
        path: 'ordonnances',
        loadComponent: () =>
          import('./pages/prescriptions/doctor-prescriptions.component').then(
            m => m.DoctorPrescriptionsComponent
          ),
        title: 'Mes Ordonnances — Espace Médecin'
      },
      {
        path: 'ordonnances/nouveau',
        loadComponent: () =>
          import('./pages/prescriptions/doctor-prescription-create.component').then(
            m => m.DoctorPrescriptionCreateComponent
          ),
        title: 'Rédiger une Ordonnance — Espace Médecin'
      },
      {
        path: 'documents',
        loadComponent: () =>
          import('./pages/documents/doctor-documents.component').then(
            m => m.DoctorDocumentsComponent
          ),
        title: 'Imagerie & Documents Médicaux — Espace Médecin'
      },
      {
        path: 'disponibilites',
        loadComponent: () =>
          import('./pages/availability/doctor-availability.component').then(
            m => m.DoctorAvailabilityComponent
          ),
        title: 'Créneaux & Disponibilités — Espace Médecin'
      },
      {
        path: 'profil',
        loadComponent: () =>
          import('./pages/profile/doctor-profile.component').then(
            m => m.DoctorProfileComponent
          ),
        title: 'Mon Profil Praticien — Espace Médecin'
      }
    ]
  }
];
