import { Component, inject, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { DoctorService } from '../../features/doctor/services/doctor.service';
import { DoctorProfileDto } from '../../features/doctor/models/doctor.models';

interface NavItem {
  label: string;
  route: string;
  icon: string;
  badge?: string;
}

@Component({
  selector: 'app-doctor-layout',
  standalone: true,
  imports: [CommonModule, RouterModule, RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './doctor-layout.component.html',
  styleUrl: './doctor-layout.component.scss'
})
export class DoctorLayoutComponent implements OnInit {
  authService = inject(AuthService);
  doctorService = inject(DoctorService);
  private router = inject(Router);

  isMobileSidebarOpen = signal<boolean>(false);
  doctorProfile = signal<DoctorProfileDto | null>(null);

  readonly navItems: NavItem[] = [
    { label: 'Tableau de bord', route: '/medecin/dashboard', icon: 'dashboard' },
    { label: 'Mes Rendez-vous', route: '/medecin/rendez-vous', icon: 'calendar' },
    { label: 'Mes Patients', route: '/medecin/patients', icon: 'users' },
    { label: 'Mes Consultations', route: '/medecin/consultations', icon: 'stethoscope' },
    { label: 'Mes Ordonnances', route: '/medecin/ordonnances', icon: 'prescription' },
    { label: 'Disponibilités & Absences', route: '/medecin/disponibilites', icon: 'clock' },
    { label: 'Mon Profil', route: '/medecin/profil', icon: 'user' }
  ];

  ngOnInit(): void {
    this.doctorService.getMyDoctorProfile().subscribe({
      next: (profile) => {
        this.doctorProfile.set(profile);
      }
    });
  }

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
