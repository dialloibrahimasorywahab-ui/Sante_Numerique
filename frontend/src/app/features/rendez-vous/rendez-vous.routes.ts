import { Routes } from '@angular/router';
import { authGuard } from '../../core/guards/auth.guard';

export const rendezVousRoutes: Routes = [
	{
		path: '',
		loadComponent: () => import('./pages/book-appointment/book-appointment.component')
			.then(module => module.BookAppointmentComponent),
		canActivate: [authGuard],
		title: 'Prendre Rendez-vous — Santé Numérique'
	},
	{
		path: 'mes-rendez-vous',
		loadComponent: () => import('./pages/my-appointments/my-appointments.component')
			.then(module => module.MyAppointmentsComponent),
		canActivate: [authGuard],
		title: 'Mes Rendez-vous — Santé Numérique'
	}
];
