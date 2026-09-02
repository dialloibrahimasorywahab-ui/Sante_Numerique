import { Component, inject, output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';
import { HospitalService } from '../../../core/services/hospital.service';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './header.component.html',
  styleUrl: './header.component.scss'
})
export class HeaderComponent {
  authService = inject(AuthService);
  hospitalService = inject(HospitalService);
  router = inject(Router);

  openBookingModal = output<void>();
  openPrescriptionModal = output<void>();
  scrollToSection = output<string>();

  isMobileMenuOpen = false;

  toggleMobileMenu(): void {
    this.isMobileMenuOpen = !this.isMobileMenuOpen;
  }

  onNavigate(sectionId: string): void {
    this.isMobileMenuOpen = false;
    if (this.router.url !== '/') {
      this.router.navigate(['/']).then(() => {
        setTimeout(() => {
          this.scrollToSection.emit(sectionId);
        }, 100);
      });
    } else {
      this.scrollToSection.emit(sectionId);
    }
  }

  triggerBooking(): void {
    this.isMobileMenuOpen = false;
    this.openBookingModal.emit();
  }
}
