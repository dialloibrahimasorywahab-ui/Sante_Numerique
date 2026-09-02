import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule, Router } from '@angular/router';
import { HospitalService, ServiceSpecialite, DoctorProfile, BookingFormState, BookingConfirmation } from '../../core/services/hospital.service';
import { AuthService } from '../../core/services/auth.service';
import { SpecialiteMedecin } from '../medecins/models/models';

export interface MedicalServicePole {
  id: string;
  nom: string;
  code: SpecialiteMedecin;
  icon: string;
  description: string;
}

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss'
})
export class HomeComponent {
  hospitalService = inject(HospitalService);
  authService = inject(AuthService);
  router = inject(Router);

  // 6 Medical Care Poles as in reference design
  readonly polesDeSoins: MedicalServicePole[] = [
    {
      id: 'cardio',
      nom: 'Cardiologie',
      code: 'CARDIOLOGIE',
      icon: 'heart',
      description: 'Prise en charge complète des maladies cardiovasculaires.'
    },
    {
      id: 'neuro',
      nom: 'Neurologie',
      code: 'NEUROLOGIE',
      icon: 'brain',
      description: 'Diagnostic et traitement des troubles neurologiques.'
    },
    {
      id: 'dentiste',
      nom: 'Dentisterie',
      code: 'CHIRURGIE',
      icon: 'tooth',
      description: 'Soins dentaires modernes et chirurgies buccales.'
    },
    {
      id: 'gyneco',
      nom: 'Gynécologie',
      code: 'GYNECOLOGIE',
      icon: 'female',
      description: 'Suivi de grossesse, accouchement et soins pour femmes.'
    },
    {
      id: 'pediatrie',
      nom: 'Pédiatrie',
      code: 'PEDIATRIE',
      icon: 'child',
      description: 'Soins médicaux spécialisés pour enfants.'
    },
    {
      id: 'generaliste',
      nom: 'Médecine générale',
      code: 'GENERALISTE',
      icon: 'briefcase-med',
      description: 'Consultations et soins pour toute la famille.'
    }
  ];

  // Active selected service for detail view
  selectedPole = signal<MedicalServicePole | null>(null);
  isServiceModalOpen = false;

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

  // Doctor search modal
  isDoctorModalOpen = false;
  doctorSearchQuery = '';

  // Prescription Modal State
  isPrescriptionModalOpen = false;
  activeSamplePrescription = {
    reference: 'ORD-20260901-084',
    date: '01 Septembre 2026',
    medecinNom: 'Pr. Ibrahima Sow',
    medecinTitre: 'Chef de Service Cardiologie - CNOM-84210',
    patientNom: 'Marie Dupont',
    patientAge: '37 ans',
    patientNSS: '1890425789123',
    patientSexe: 'Féminin',
    medicaments: [
      {
        nom: 'Bisoprolol 5mg',
        forme: 'Comprimé pelliculé sécable',
        posologie: '1 comprimé chaque matin au petit-déjeuner',
        duree: 'Pendant 3 mois (renouvelable 1 fois)'
      },
      {
        nom: 'Ramipril 2.5mg',
        forme: 'Gélule',
        posologie: '1 gélule le soir au coucher',
        duree: 'Pendant 3 mois'
      },
      {
        nom: 'Kardégic 75mg (Acide Acétylsalicylique)',
        forme: 'Sachet pour solution buvable',
        posologie: '1 sachet le midi au cours du repas',
        duree: 'Pendant 3 mois'
      }
    ],
    recommandations: 'Surveillance tensionnelle bimensuelle. Contrôle biologique (ionogramme et créatinine) dans 4 semaines. Activité physique modérée recommandée.',
    signatureElectronique: 'Certifié Numériquement par Pr. Ibrahima Sow - Clé publique SHA256: 8f4e2b1c9a0d3f7e'
  };

  openBooking(specialiteCode?: SpecialiteMedecin, doctorId?: number): void {
    this.bookingStep = 1;
    this.confirmedBooking = null;

    if (specialiteCode) {
      this.bookingForm.specialite = specialiteCode;
    }
    if (doctorId) {
      this.bookingForm.medecinId = doctorId;
      const doc = this.hospitalService.doctors().find(d => d.id === doctorId);
      if (doc) {
        this.bookingForm.specialite = doc.specialite;
      }
    }

    this.isDoctorModalOpen = false;
    this.isServiceModalOpen = false;
    this.isBookingModalOpen = true;
  }

  closeBooking(): void {
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

  get filteredDoctorsForBooking(): DoctorProfile[] {
    const spec = this.bookingForm.specialite;
    if (!spec) return this.hospitalService.doctors();
    return this.hospitalService.doctors().filter(d => d.specialite === spec);
  }

  getSelectedDoctorForBooking(): DoctorProfile | undefined {
    return this.hospitalService.doctors().find(d => d.id === this.bookingForm.medecinId);
  }

  openDoctorSearch(): void {
    this.router.navigate(['/medecins']);
  }

  closeDoctorSearch(): void {
    this.isDoctorModalOpen = false;
  }

  openServiceDetails(pole: MedicalServicePole): void {
    this.selectedPole.set(pole);
    this.isServiceModalOpen = true;
  }

  closeServiceDetails(): void {
    this.isServiceModalOpen = false;
  }

  openPrescription(): void {
    this.isPrescriptionModalOpen = true;
  }

  closePrescription(): void {
    this.isPrescriptionModalOpen = false;
  }

  get searchFilteredDoctors(): DoctorProfile[] {
    if (!this.doctorSearchQuery) return this.hospitalService.doctors();
    const q = this.doctorSearchQuery.toLowerCase();
    return this.hospitalService.doctors().filter(d =>
      d.nom.toLowerCase().includes(q) ||
      d.prenom.toLowerCase().includes(q) ||
      d.specialiteLabel.toLowerCase().includes(q) ||
      d.service.toLowerCase().includes(q)
    );
  }

  printCurrentPage(): void {
    window.print();
  }

  scrollToSection(sectionId: string): void {
    const el = document.getElementById(sectionId);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }
}
