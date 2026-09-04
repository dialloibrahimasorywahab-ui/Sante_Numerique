import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { ServicesService } from './services/services.service';
import { ServiceHospitalier } from './models/models';
import { HospitalService, BookingFormState, BookingConfirmation } from '../landing/services/hospital.service';

@Component({
  selector: 'app-services-list',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './services-list.component.html',
  styleUrl: './services-list.component.scss'
})
export class ServicesListComponent implements OnInit {
  servicesService = inject(ServicesService);
  hospitalService = inject(HospitalService);
  router = inject(Router);
  route = inject(ActivatedRoute);

  searchQuery = '';
  selectedFilter = 'ALL';

  // Booking Modal State
  isBookingModalOpen = false;
  bookingStep = 1;
  bookingError = '';
  bookingForm: BookingFormState = this.hospitalService.createInitialBookingForm();

  confirmedBooking: BookingConfirmation | null = null;

  get minBookingDate(): string {
    return this.hospitalService.getTodayString();
  }

  isSlotDisabled(slot: string): boolean {
    return this.hospitalService.isSlotPast(this.bookingForm.date, slot);
  }

  onBookingDateChange(): void {
    this.bookingError = '';
    if (this.isSlotDisabled(this.bookingForm.heure)) {
      const validSlot = this.hospitalService.getDefaultSlotForDate(this.bookingForm.date);
      this.bookingForm.heure = validSlot;
    }
  }

  ngOnInit(): void {
    this.route.queryParams.subscribe(params => {
      if (params['search']) {
        this.searchQuery = params['search'];
      }
      this.loadServices();
    });
  }

  loadServices(): void {
    this.servicesService.getServices(this.searchQuery).subscribe({
      next: (services) => {
        // Services loaded into servicesService.servicesList signal
      },
      error: (err) => {
        console.error('Échec chargement services:', err);
      }
    });
  }

  onSearchChange(): void {
    this.loadServices();
  }

  get filteredServices(): ServiceHospitalier[] {
    const list = this.servicesService.servicesList();
    if (!this.searchQuery.trim()) {
      return list;
    }
    const q = this.searchQuery.toLowerCase();
    return list.filter(s =>
      s.displayNom?.toLowerCase().includes(q) ||
      s.nom_service.toLowerCase().includes(q) ||
      s.displayDesc?.toLowerCase().includes(q) ||
      s.bureau_localisation?.toLowerCase().includes(q)
    );
  }

  navigateToDetail(service: ServiceHospitalier): void {
    this.router.navigate(['/services', service.id_service]);
  }

  openBookingModal(serviceCode?: string): void {
    this.bookingStep = 1;
    this.bookingError = '';
    this.confirmedBooking = null;
    this.bookingForm = this.hospitalService.createInitialBookingForm();

    if (serviceCode) {
      this.bookingForm.specialite = serviceCode as any;
    }

    this.isBookingModalOpen = true;
  }

  closeBookingModal(): void {
    this.isBookingModalOpen = false;
  }

  nextBookingStep(): void {
    this.bookingError = '';
    if (this.bookingStep === 1) {
      if (!this.bookingForm.medecinId && this.filteredDoctorsForBooking.length > 0) {
        this.bookingForm.medecinId = this.filteredDoctorsForBooking[0].id;
      }
      this.bookingStep = 2;
    } else if (this.bookingStep === 2) {
      if (!this.bookingForm.date) {
        this.bookingError = 'Veuillez sélectionner une date de rendez-vous.';
        return;
      }
      if (this.bookingForm.date < this.minBookingDate) {
        this.bookingError = 'La date sélectionnée est déjà passée. Veuillez choisir une date future.';
        return;
      }
      if (!this.bookingForm.heure) {
        this.bookingError = 'Veuillez sélectionner un créneau horaire disponible.';
        return;
      }
      if (this.isSlotDisabled(this.bookingForm.heure)) {
        this.bookingError = 'Ce créneau horaire est déjà passé pour aujourd’hui. Veuillez choisir un autre horaire ou une date ultérieure.';
        return;
      }
      this.bookingStep = 3;
    }
  }

  prevBookingStep(): void {
    this.bookingError = '';
    if (this.bookingStep > 1) {
      this.bookingStep--;
    }
  }

  submitBooking(): void {
    this.bookingError = '';
    if (!this.hospitalService.isDateTimeValid(this.bookingForm.date, this.bookingForm.heure)) {
      this.bookingError = 'Impossible de confirmer ce rendez-vous : la date ou l’heure choisie est déjà passée.';
      return;
    }
    this.confirmedBooking = this.hospitalService.bookAppointment(this.bookingForm);
    this.bookingStep = 4;
  }

  get filteredDoctorsForBooking() {
    const spec = this.bookingForm.specialite;
    if (!spec) return this.hospitalService.doctors();
    return this.hospitalService.doctors().filter(d => d.specialite === spec);
  }

  getSelectedDoctorForBooking() {
    return this.hospitalService.doctors().find(d => d.id === this.bookingForm.medecinId);
  }

  printCurrentPage(): void {
    window.print();
  }
}
