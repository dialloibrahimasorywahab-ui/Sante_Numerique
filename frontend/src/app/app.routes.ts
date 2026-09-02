import { Routes } from '@angular/router';
import { HomeComponent } from './views/home/home.component';
import { ServicesListComponent } from './views/services/services-list.component';
import { ServiceDetailComponent } from './views/services/service-detail/service-detail.component';

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
    path: '**',
    redirectTo: ''
  }
];
