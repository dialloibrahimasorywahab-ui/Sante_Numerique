import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { ServicesService, ServiceDetailExtended } from '../../../core/services/services.service';
import { HospitalService, DoctorProfile, BookingFormState, BookingConfirmation } from '../../../core/services/hospital.service';

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
    this.confirmedBooking = null;

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
