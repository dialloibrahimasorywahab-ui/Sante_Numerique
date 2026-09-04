import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { MedecinService } from './services/medecin.service';
import { MedecinDto } from './models/models';
import { HospitalService, BookingFormState, BookingConfirmation } from '../landing/services/hospital.service';
import { AuthService } from '../../core/services/auth.service';

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
  authService = inject(AuthService);
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
    heure: '09:15',
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

  get todayString(): string {
    return this.hospitalService.getTodayString();
  }

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
    if (!this.authService.isAuthenticated()) {
      this.router.navigate(['/login'], { queryParams: { returnUrl: '/medecins' } });
      return;
    }

    this.selectedDoctorForBooking = doc;
    this.bookingStep = 1;
    this.confirmedBooking = null;
    this.bookingForm = this.hospitalService.createInitialBookingForm();

    if (doc.specialite) {
      this.bookingForm.specialite = doc.specialite as any;
      this.selectedSpecialite = doc.specialite;
    }
    this.bookingForm.medecinId = doc.idMedecin;
    const currentUser = this.authService.currentUser();
    if (currentUser) {
      this.bookingForm.patientNom = currentUser.nom;
      this.bookingForm.patientPrenom = currentUser.prenom;
      this.bookingForm.patientTelephone = currentUser.telephone || '';
      this.bookingForm.patientEmail = currentUser.email || '';
    }

    const initialDate = this.hospitalService.getDefaultBookingDate();
    this.bookingForm.date = initialDate;
    this.bookingForm.heure = this.hospitalService.getDefaultSlotForDate(initialDate);

    this.isBookingModalOpen = true;
  }

  onBookingDateChange(date: string): void {
    this.bookingForm.date = date;
    const availableSlots = this.getAvailableBookingSlots();
    if (!availableSlots.includes(this.bookingForm.heure)) {
      this.bookingForm.heure = availableSlots[0] || '';
    }
  }

  getAvailableBookingSlots(): string[] {
    return this.hospitalService.getAvailableSlotsForDate(this.bookingForm.date);
  }

  closeBookingModal(): void {
    this.isBookingModalOpen = false;
  }

  nextBookingStep(): void {
    if (this.bookingStep === 1) {
      this.bookingStep = 2;
    } else if (this.bookingStep === 2) {
      if (!this.bookingForm.date || !this.bookingForm.heure || !this.hospitalService.isDateTimeValid(this.bookingForm.date, this.bookingForm.heure)) {
        return;
      }
      this.bookingStep = 3;
    }
  }

  prevBookingStep(): void {
    if (this.bookingStep > 1) {
      this.bookingStep--;
    }
  }

  submitBooking(): void {
    const currentUser = this.authService.currentUser();
    if (!currentUser) {
      this.closeBookingModal();
      this.router.navigate(['/login'], { queryParams: { returnUrl: '/medecins' } });
      return;
    }

    if (!this.hospitalService.isDateTimeValid(this.bookingForm.date, this.bookingForm.heure)) {
      return;
    }

    this.bookingForm.patientNom = currentUser.nom;
    this.bookingForm.patientPrenom = currentUser.prenom;
    this.bookingForm.patientTelephone = currentUser.telephone || '';
    this.bookingForm.patientEmail = currentUser.email || '';
    this.confirmedBooking = this.hospitalService.bookAppointment(this.bookingForm);
    this.bookingStep = 4;
  }

  printCurrentPage(): void {
    window.print();
  }
}
