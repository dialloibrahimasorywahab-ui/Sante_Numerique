import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { MedecinService } from '../../../core/services/medecin.service';
import { MedecinDto } from '../../../core/models/models';
import { HospitalService, BookingFormState, BookingConfirmation } from '../../../core/services/hospital.service';

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
    this.confirmedBooking = null;
    this.isBookingModalOpen = true;
  }

  closeBooking(): void {
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

  goBack(): void {
    this.router.navigate(['/medecins']);
  }
}
