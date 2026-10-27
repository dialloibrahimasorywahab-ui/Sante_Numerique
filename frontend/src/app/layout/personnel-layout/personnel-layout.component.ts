import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';

interface NavItem {
  label: string;
  route: string;
  icon: string;
  emoji: string;
}

@Component({
  selector: 'app-personnel-layout',
  standalone: true,
  imports: [CommonModule, RouterModule, RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './personnel-layout.component.html',
  styleUrl: './personnel-layout.component.scss'
})
export class PersonnelLayoutComponent {
  authService = inject(AuthService);
  private router = inject(Router);

  isMobileSidebarOpen = signal<boolean>(false);

  readonly navItems: NavItem[] = [
    { label: 'Accueil', route: '/personnel/accueil', icon: 'home', emoji: '🏠' },
    { label: 'Dashboard', route: '/personnel/dashboard', icon: 'dashboard', emoji: '📊' },
    { label: 'Patients', route: '/personnel/patients', icon: 'users', emoji: '👥' },
    { label: 'Rendez-vous', route: '/personnel/rendez-vous', icon: 'calendar', emoji: '📅' },
    { label: 'Hospitalisations', route: '/personnel/hospitalisations', icon: 'hospital', emoji: '🏥' },
    { label: 'Mon profil', route: '/personnel/profil', icon: 'user', emoji: '👤' }
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
