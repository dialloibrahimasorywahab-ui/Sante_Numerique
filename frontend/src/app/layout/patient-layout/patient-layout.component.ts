import { Component, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule, RouterLink, RouterLinkActive, RouterOutlet, ActivatedRoute } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { NotificationService } from '../../core/services/notification.service';
import { FormsModule } from '@angular/forms';

export interface NavItem {
  label: string;
  route?: string;
  icon: string;
  isAction?: boolean;
}

@Component({
  selector: 'app-patient-layout',
  standalone: true,
  imports: [CommonModule, RouterModule, RouterOutlet, RouterLink, RouterLinkActive, FormsModule],
  templateUrl: './patient-layout.component.html',
  styleUrl: './patient-layout.component.scss'
})
export class PatientLayoutComponent {
  authService = inject(AuthService);
  notificationService = inject(NotificationService);
  private router = inject(Router);
  private route = inject(ActivatedRoute);

  isMobileSidebarOpen = signal<boolean>(false);
  isUserMenuOpen = signal<boolean>(false);
  searchQuery = signal<string>('');

  currentUser = computed(() => this.authService.currentUser());
  unreadCount = computed(() => this.notificationService.unreadCount());

  readonly navItems: NavItem[] = [
    { label: 'Accueil', route: '/patient/dashboard', icon: 'home' },
    { label: 'Mes Services', route: '/patient/espace-services', icon: 'grid' },
    { label: 'Mes Rendez-vous', route: '/patient/rendez-vous', icon: 'calendar' },
    { label: 'Mes Consultations', route: '/patient/consultations', icon: 'stethoscope' },
    { label: 'Mon Dossier', route: '/patient/documents', icon: 'folder' },
    { label: 'Notifications', icon: 'bell', isAction: true },
    { label: 'Contact', icon: 'headset', isAction: true },
    { label: 'Aide & FAQ', icon: 'help', isAction: true }
  ];

  toggleMobileSidebar(): void {
    this.isMobileSidebarOpen.update(v => !v);
  }

  closeMobileSidebar(): void {
    this.isMobileSidebarOpen.set(false);
  }

  toggleUserMenu(): void {
    this.isUserMenuOpen.update(v => !v);
  }

  closeUserMenu(): void {
    this.isUserMenuOpen.set(false);
  }

  onActionClick(item: NavItem): void {
    this.closeMobileSidebar();
    if (item.label === 'Notifications') {
      const el = document.querySelector('.panel-notifications');
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
      } else {
        this.router.navigate(['/patient/espace-services'], { fragment: 'notifications' });
      }
    } else if (item.label === 'Contact') {
      window.location.href = 'tel:+224627684702';
    } else if (item.label === 'Aide & FAQ') {
      this.router.navigate(['/patient/profil']);
    }
  }

  onSearchSubmit(): void {
    const q = this.searchQuery().trim();
    if (q) {
      this.router.navigate(['/patient/espace-services'], { queryParams: { q } });
    }
  }

  onSearchInput(event: Event): void {
    const val = (event.target as HTMLInputElement).value;
    this.searchQuery.set(val);
    if (this.router.url.includes('/patient/espace-services')) {
      this.router.navigate([], {
        relativeTo: this.route,
        queryParams: { q: val || null },
        queryParamsHandling: 'merge'
      });
    }
  }

  getUserDisplayName(): string {
    const u = this.currentUser();
    if (u?.prenom || u?.nom) {
      return `${u.prenom || ''} ${u.nom || ''}`.trim();
    }
    return 'Ibrahima Sory Diallo';
  }

  getUserInitials(): string {
    const u = this.currentUser();
    if (u?.prenom && u?.nom) {
      return `${u.prenom.charAt(0)}${u.nom.charAt(0)}`.toUpperCase();
    }
    return 'IS';
  }

  onLogout(): void {
    this.closeUserMenu();
    this.authService.logout().subscribe({
      next: () => this.router.navigate(['/login']),
      error: () => this.router.navigate(['/login'])
    });
  }
}
