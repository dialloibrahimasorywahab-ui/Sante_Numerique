import { Routes } from '@angular/router';
import { HomeComponent } from './views/home/home.component';
import { ServicesListComponent } from './views/services/services-list.component';
import { ServiceDetailComponent } from './views/services/service-detail/service-detail.component';
import { MedecinsListComponent } from './views/medecins/medecins-list.component';
import { MedecinDetailComponent } from './views/medecins/medecin-detail/medecin-detail.component';
import { BookAppointmentComponent } from './features/appointment/pages/book-appointment/book-appointment.component';
import { MyAppointmentsComponent } from './features/appointment/pages/my-appointments/my-appointments.component';

export const routes: Routes = [
  {
    path: '',
    component: HomeComponent,
    title: 'Santé Numérique — Centre Hospitalier Universitaire'
  },
  {
    path: 'services',
    component: ServicesListComponent,
    title: 'Nos Pôles de Soins & Spécialités — Santé Numérique'
  },
  {
    path: 'services/:id',
    component: ServiceDetailComponent,
    title: 'Détails du Service — Santé Numérique'
  },
  {
    path: 'medecins',
    component: MedecinsListComponent,
    title: 'Notre Équipe Médicale — Santé Numérique'
  },
  {
    path: 'medecins/:id',
    component: MedecinDetailComponent,
    title: 'Profil Médecin — Santé Numérique'
  },
  {
    path: 'rendez-vous',
    component: BookAppointmentComponent,
    title: 'Prendre Rendez-vous — Santé Numérique'
  },
  {
    path: 'mes-rendez-vous',
    component: MyAppointmentsComponent,
    title: 'Mes Rendez-vous — Santé Numérique'
  },
  {
    path: '**',
    redirectTo: ''
  }
];
