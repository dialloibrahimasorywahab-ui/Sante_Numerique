import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { MedecinService } from '../../core/services/medecin.service';
import { MedecinDto } from './models/models';
import { HospitalService, BookingFormState, BookingConfirmation } from '../../core/services/hospital.service';

@Component({
  selector: 'app-medecins-list',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './medecins-list.component.html',
  styleUrl: './medecins-list.component.scss'
})
export class MedecinsListComponent implements OnInit {
  medecinService = inject(MedecinService);
  hospitalService = inject(HospitalService);
  router = inject(Router);

  searchQuery = '';
  selectedSpecialite = '';
  currentPage = 1;

  // Booking Modal Wizard
  isBookingModalOpen = false;
  bookingStep = 1;
  selectedDoctorForBooking: MedecinDto | null = null;
  bookingForm: BookingFormState = {
    specialite: '',
    medecinId: null,
    date: new Date().toISOString().split('T')[0],
    heure: '09:30',
    motif: '',
    typeConsultation: 'SUR_PLACE',
    patientNom: 'Dupont',
    patientPrenom: 'Marie',
    patientEmail: 'marie.dupont@santenumerique.com',
    patientTelephone: '+224 621 45 89 20',
    patientGroupeSanguin: 'O+',
    patientNSS: '1890425789123'
  };

  confirmedBooking: BookingConfirmation | null = null;

  ngOnInit(): void {
    this.fetchDoctors();
  }

  fetchDoctors(page: number = 1): void {
    this.currentPage = page;
    this.medecinService.getMedecins({
      search: this.searchQuery,
      specialite: this.selectedSpecialite,
      page: this.currentPage,
      page_size: 12
    }).subscribe();
  }

  onSearchChange(): void {
    this.currentPage = 1;
    this.fetchDoctors(1);
  }

  onSpecialiteChange(specCode: string): void {
    this.selectedSpecialite = specCode;
    this.currentPage = 1;
    this.fetchDoctors(1);
  }

  resetFilters(): void {
    this.searchQuery = '';
    this.selectedSpecialite = '';
    this.currentPage = 1;
    this.fetchDoctors(1);
  }

  changePage(page: number): void {
    if (page >= 1 && page <= this.medecinService.totalPages()) {
      this.fetchDoctors(page);
      window.scrollTo({ top: 400, behavior: 'smooth' });
    }
  }

  get pagesArray(): number[] {
    const total = this.medecinService.totalPages();
    return Array.from({ length: total }, (_, i) => i + 1);
  }

  navigateToDetail(doc: MedecinDto): void {
    this.router.navigate(['/medecins', doc.idMedecin]);
  }

  openBookingModal(doc: MedecinDto): void {
    this.selectedDoctorForBooking = doc;
    this.bookingStep = 1;
    this.confirmedBooking = null;

    if (doc.specialite) {
      this.bookingForm.specialite = doc.specialite as any;
    }
    this.bookingForm.medecinId = doc.idMedecin;

    this.isBookingModalOpen = true;
  }

  closeBookingModal(): void {
    this.isBookingModalOpen = false;
  }

  nextBookingStep(): void {
    if (this.bookingStep === 1) {
      this.bookingStep = 2;
    } else if (this.bookingStep === 2) {
      this.bookingStep = 3;
    }
  }

  prevBookingStep(): void {
    if (this.bookingStep > 1) {
      this.bookingStep--;
    }
  }

  submitBooking(): void {
    this.confirmedBooking = this.hospitalService.bookAppointment(this.bookingForm);
    this.bookingStep = 4;
  }

  printCurrentPage(): void {
    window.print();
  }
}
