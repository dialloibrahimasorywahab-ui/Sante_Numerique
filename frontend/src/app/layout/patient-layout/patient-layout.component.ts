import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';

interface NavItem {
  label: string;
  route: string;
  icon: string;
  badge?: string;
}

@Component({
  selector: 'app-patient-layout',
  standalone: true,
  imports: [CommonModule, RouterModule, RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './patient-layout.component.html',
  styleUrl: './patient-layout.component.scss'
})
export class PatientLayoutComponent {
  authService = inject(AuthService);
  private router = inject(Router);

  isMobileSidebarOpen = signal<boolean>(false);

  readonly navItems: NavItem[] = [
    { label: 'Tableau de bord', route: '/patient/dashboard', icon: 'dashboard' },
    { label: 'Mes Rendez-vous', route: '/patient/rendez-vous', icon: 'calendar' },
    { label: 'Mes Consultations', route: '/patient/consultations', icon: 'stethoscope' },
    { label: 'Mes Ordonnances', route: '/patient/ordonnances', icon: 'prescription' },
    { label: 'Mes Hospitalisations', route: '/patient/hospitalisations', icon: 'hospital' },
    { label: 'Mon Profil', route: '/patient/profil', icon: 'user' }
  ];

  toggleMobileSidebar(): void {
    this.isMobileSidebarOpen.update(v => !v);
  }

  closeMobileSidebar(): void {
    this.isMobileSidebarOpen.set(false);
  }

  onLogout(): void {
    this.authService.logout().subscribe({
      next: () => {
        this.router.navigate(['/login']);
      },
      error: () => {
        this.router.navigate(['/login']);
      }
    });
  }
}
