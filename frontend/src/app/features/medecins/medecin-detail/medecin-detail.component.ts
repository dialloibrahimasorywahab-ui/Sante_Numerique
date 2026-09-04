import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { MedecinService } from '../services/medecin.service';
import { MedecinDto } from '../models/models';
import { HospitalService, BookingFormState, BookingConfirmation } from '../../landing/services/hospital.service';

@Component({
  selector: 'app-medecin-detail',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './medecin-detail.component.html',
  styleUrl: './medecin-detail.component.scss'
})
export class MedecinDetailComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private medecinService = inject(MedecinService);
  hospitalService = inject(HospitalService);

  medecinId = signal<number | null>(null);
  doctor = signal<MedecinDto | null>(null);
  isLoading = signal<boolean>(true);
  errorMessage = signal<string | null>(null);

  // Booking modal state
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
        this.medecinId.set(id);
        this.loadDoctor(id);
      } else {
        this.errorMessage.set('Identifiant de médecin invalide.');
        this.isLoading.set(false);
      }
    });
  }

  loadDoctor(id: number): void {
    this.isLoading.set(true);
    this.errorMessage.set(null);

    this.medecinService.getMedecinById(id).subscribe({
      next: (doc) => {
        this.doctor.set(doc);
        this.isLoading.set(false);
        if (doc.specialite) {
          this.bookingForm.specialite = doc.specialite as any;
        }
        this.bookingForm.medecinId = doc.idMedecin;
      },
      error: (err) => {
        console.error(`Erreur de chargement du médecin #${id}:`, err);
        this.errorMessage.set('Impossible de charger les informations de ce praticien.');
        this.isLoading.set(false);
      }
    });
  }

  openBooking(): void {
    this.bookingStep = 1;
    this.bookingError = '';
    this.confirmedBooking = null;
    this.bookingForm = this.hospitalService.createInitialBookingForm();
    if (this.doctor()?.specialite) {
      this.bookingForm.specialite = this.doctor()!.specialite as any;
    }
    if (this.doctor()?.idMedecin) {
      this.bookingForm.medecinId = this.doctor()!.idMedecin;
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

  printCurrentPage(): void {
    window.print();
  }

  goBack(): void {
    this.router.navigate(['/medecins']);
  }
}
