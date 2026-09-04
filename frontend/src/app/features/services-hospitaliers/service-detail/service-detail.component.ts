import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { ServicesService, ServiceDetailExtended } from '../services/services.service';
import { HospitalService, DoctorProfile, BookingFormState, BookingConfirmation } from '../../landing/services/hospital.service';

@Component({
  selector: 'app-service-detail',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './service-detail.component.html',
  styleUrl: './service-detail.component.scss'
})
export class ServiceDetailComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private servicesService = inject(ServicesService);
  hospitalService = inject(HospitalService);

  serviceId = signal<number | null>(null);
  service = signal<ServiceDetailExtended | null>(null);
  isLoading = signal<boolean>(true);
  errorMessage = signal<string | null>(null);

  // Booking modal
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
    this.route.paramMap.subscribe(params => {
      const idParam = params.get('id');
      if (idParam) {
        const id = parseInt(idParam, 10);
        this.serviceId.set(id);
        this.loadServiceDetail(id);
      } else {
        this.errorMessage.set('Identifiant de service invalide.');
        this.isLoading.set(false);
      }
    });
  }

  loadServiceDetail(id: number): void {
    this.isLoading.set(true);
    this.errorMessage.set(null);

    this.servicesService.getServiceById(id).subscribe({
      next: (detail) => {
        this.service.set(detail);
        this.isLoading.set(false);
        if (detail.nom_service) {
          this.bookingForm.specialite = detail.nom_service as any;
        }
      },
      error: (err) => {
        console.error(`Erreur de chargement du service #${id}:`, err);
        this.errorMessage.set('Impossible de charger les détails de ce service hospitalier.');
        this.isLoading.set(false);
      }
    });
  }

  openBooking(doctorId?: number): void {
    this.bookingStep = 1;
    this.bookingError = '';
    this.confirmedBooking = null;
    this.bookingForm = this.hospitalService.createInitialBookingForm();

    if (this.service()?.nom_service) {
      this.bookingForm.specialite = this.service()!.nom_service as any;
    }

    if (doctorId) {
      this.bookingForm.medecinId = doctorId;
    } else if (this.service()?.medecinsAssocies && this.service()!.medecinsAssocies!.length > 0) {
      this.bookingForm.medecinId = this.service()!.medecinsAssocies![0].id;
    }

    this.isBookingModalOpen = true;
  }

  closeBooking(): void {
    this.isBookingModalOpen = false;
  }

  nextBookingStep(): void {
    this.bookingError = '';
    if (this.bookingStep === 1) {
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

  getSelectedDoctor() {
    return this.hospitalService.doctors().find(d => d.id === this.bookingForm.medecinId);
  }

  printCurrentPage(): void {
    window.print();
  }

  goBack(): void {
    this.router.navigate(['/services']);
  }
}
