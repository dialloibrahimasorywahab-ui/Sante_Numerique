import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
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

  searchQuery = '';
  selectedFilter = 'ALL';

  // Booking Modal State
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
    this.loadServices();
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
    this.confirmedBooking = null;

    if (serviceCode) {
      this.bookingForm.specialite = serviceCode as any;
    }

    this.isBookingModalOpen = true;
  }

  closeBookingModal(): void {
    this.isBookingModalOpen = false;
  }

  nextBookingStep(): void {
    if (this.bookingStep === 1) {
      if (!this.bookingForm.medecinId && this.filteredDoctorsForBooking.length > 0) {
        this.bookingForm.medecinId = this.filteredDoctorsForBooking[0].id;
      }
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
