import { Component, computed, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { formatDate as formatSharedDate } from '../../shared/utils';

interface NavSection {
  title: string;
  items: NavItem[];
}

interface NavItem {
  label: string;
  route: string;
  icon: string;
  badge?: string;
}

@Component({
  selector: 'app-admin-layout',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './admin-layout.component.html',
  styleUrls: ['./admin-layout.component.scss']
})
export class AdminLayoutComponent {
  authService = inject(AuthService);
  private router = inject(Router);

  // État mobile sidebar
  isMobileSidebarOpen = signal<boolean>(false);

  // Date du jour formatée en français
  todayFormatted = computed(() => {
    return formatSharedDate(new Date());
  });

  // Arborescence de navigation structurée
  navSections: NavSection[] = [
    {
      title: 'Vue d\'ensemble',
      items: [
        { label: 'Tableau de bord', route: '/admin/dashboard', icon: 'dashboard' }
      ]
    },
    {
      title: 'Gestion des utilisateurs',
      items: [
        { label: 'Patients', route: '/admin/patients', icon: 'users' },
        { label: 'Médecins', route: '/admin/medecins', icon: 'stethoscope' },
        { label: 'Personnel soignant', route: '/admin/personnel', icon: 'badge' }
      ]
    },
    {
      title: 'Gestion hospitalière',
      items: [
        { label: 'Services & Pôles', route: '/admin/services', icon: 'hospital' },
        { label: 'Bâtiments', route: '/admin/batiments', icon: 'building' },
        { label: 'Chambres', route: '/admin/chambres', icon: 'door' },
        { label: 'Lits d\'hospitalisation', route: '/admin/lits', icon: 'bed' }
      ]
    },
    {
      title: 'Activités médicales',
      items: [
        { label: 'Rendez-vous', route: '/admin/rendezvous', icon: 'calendar' },
        { label: 'Consultations', route: '/admin/consultations', icon: 'clipboard' },
        { label: 'Hospitalisations', route: '/admin/hospitalisations', icon: 'bed-pulse' },
        { label: 'Ordonnances', route: '/admin/ordonnances', icon: 'prescription' }
      ]
    },
    {
      title: 'Finance & Facturation',
      items: [
        { label: 'Frais de consultation', route: '/admin/finances', icon: 'credit-card' }
      ]
    }
  ];

  toggleMobileSidebar(): void {
    this.isMobileSidebarOpen.update(v => !v);
  }

  closeMobileSidebar(): void {
    this.isMobileSidebarOpen.set(false);
  }

  onLogout(): void {
    this.authService.logout().subscribe();
  }
}
