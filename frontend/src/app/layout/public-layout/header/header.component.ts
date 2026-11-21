import { Component, inject, signal, HostListener, ElementRef, output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';

export interface ServiceDropdownItem {
  nom: string;
  route: string;
  code?: string;
  search?: string;
}

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './header.component.html',
  styleUrl: './header.component.scss'
})
export class HeaderComponent {
  authService = inject(AuthService);
  router = inject(Router);
  private elementRef = inject(ElementRef);

  openBookingModal = output<void>();
  openPrescriptionModal = output<void>();
  scrollToSection = output<string>();

  isMobileMenuOpen = false;
  isServicesDropdownOpen = signal<boolean>(false);

    readonly servicesList: ServiceDropdownItem[] = [
    { nom: 'Cardiologie',       route: '/services/CARDIOLOGIE' },
    { nom: 'Neurologie',        route: '/services/NEUROLOGIE' },
    { nom: 'Pédiatrie',         route: '/services/PEDIATRIE' },
    { nom: 'Gynécologie',       route: '/services/GYNECOLOGIE' },
    { nom: 'Médecine générale', route: '/services/MEDECINE_GENERALE' },
    { nom: 'Tous les services', route: '/services' }
  ];

  toggleServicesDropdown(event?: MouseEvent): void {
    if (event) {
      event.stopPropagation();
    }
    this.isServicesDropdownOpen.update(v => !v);
  }

  closeServicesDropdown(): void {
    this.isServicesDropdownOpen.set(false);
  }

  toggleMobileMenu(): void {
    this.isMobileMenuOpen = !this.isMobileMenuOpen;
  }

  closeAllMenus(): void {
    this.isMobileMenuOpen = false;
    this.isServicesDropdownOpen.set(false);
  }

  onNavigate(sectionId: string): void {
    this.closeAllMenus();
    this.scrollToSection.emit(sectionId);
    if (this.router.url !== '/') {
      this.router.navigate(['/']).then(() => {
        setTimeout(() => {
          const el = document.getElementById(sectionId);
          if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 120);
      });
    } else {
      const el = document.getElementById(sectionId);
      if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  onLogout(): void {
    this.closeAllMenus();
    this.authService.logout().subscribe();
  }

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: MouseEvent): void {
    const clickedInside = this.elementRef.nativeElement.contains(event.target);
    if (!clickedInside) {
      this.isServicesDropdownOpen.set(false);
    }
  }
}
