import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { AppointmentService } from '../../../../core/services/appointment.service';
import { ServicesService } from '../../../../core/services/services.service';
import { MedecinService } from '../../../../core/services/medecin.service';
import { AuthService } from '../../../../core/services/auth.service';
import {
  ServiceHospitalier,
  MedecinDto,
  TimeSlot,
  RendezVousDto,
  CreateAppointmentDto
} from '../../../../core/models/models';

@Component({
  selector: 'app-book-appointment',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './book-appointment.component.html',
  styleUrl: './book-appointment.component.scss'
})
export class BookAppointmentComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private appointmentService = inject(AppointmentService);
  private servicesService = inject(ServicesService);
  private medecinService = inject(MedecinService);
  authService = inject(AuthService);

  // Wizard state
  currentStep = signal<number>(1);
  isLoadingServices = signal<boolean>(false);
  isLoadingDoctors = signal<boolean>(false);
  isLoadingSlots = signal<boolean>(false);
  isSubmitting = signal<boolean>(false);
  errorMessage = signal<string | null>(null);

  // Data lists
  servicesList = signal<ServiceHospitalier[]>([]);
  doctorsList = signal<MedecinDto[]>([]);
  availableSlots = signal<TimeSlot[]>([]);

  // Selection model
  selectedService = signal<ServiceHospitalier | null>(null);
  selectedDoctor = signal<MedecinDto | null>(null);
  selectedDate = signal<string>(new Date().toISOString().split('T')[0]);
  selectedTime = signal<string>('');
  selectedConsultationType = signal<'SUR_PLACE' | 'TELECONSULTATION'>('SUR_PLACE');
  motif = signal<string>('');
  motifTouched = signal<boolean>(false);

  // Patient info for booking
  patientNom = signal<string>('Dupont');
  patientPrenom = signal<string>('Marie');
  patientTelephone = signal<string>('+224 621 45 89 20');
  patientEmail = signal<string>('marie.dupont@santenumerique.com');

  // Confirmation result
  confirmedRdv = signal<RendezVousDto | null>(null);

  // Min selectable date (today)
  todayString = new Date().toISOString().split('T')[0];

  // Filtered doctors for selected service
  filteredDoctors = computed(() => {
    const service = this.selectedService();
    const docs = this.doctorsList();
    if (!service) return docs;
    const servName = (service.nom_service || service.nomService || '').toLowerCase();
    
    // Map service to doctor specialty keyword
    return docs.filter(d => {
      const spec = (d.specialite || d.specialiteDisplay || '').toLowerCase();
      if (servName.includes('cardio') && spec.includes('cardio')) return true;
      if (servName.includes('pédia') && spec.includes('pedia')) return true;
      if (servName.includes('gynéco') && spec.includes('gyneco')) return true;
      if (servName.includes('neuro') && spec.includes('neuro')) return true;
      if (servName.includes('chirurg') && spec.includes('chirurg')) return true;
      if (servName.includes('dermat') && spec.includes('dermat')) return true;
      if (servName.includes('général') && spec.includes('general')) return true;
      return true; // Return all if no direct specialty restriction
    });
  });

  ngOnInit(): void {
    this.loadInitialData();

    // Check if user is logged in to prefill patient info
    const currentUser = this.authService.currentUser();
    if (currentUser) {
      this.patientNom.set(currentUser.nom);
      this.patientPrenom.set(currentUser.prenom);
      if (currentUser.telephone) this.patientTelephone.set(currentUser.telephone);
      if (currentUser.email) this.patientEmail.set(currentUser.email);
    }
  }

  private loadInitialData(): void {
    // 1. Load Services
    this.isLoadingServices.set(true);
    this.servicesService.getServices().subscribe({
      next: (services: ServiceHospitalier[]) => {
        this.servicesList.set(services);
        this.isLoadingServices.set(false);
      },
      error: () => {
        this.isLoadingServices.set(false);
      }
    });

    // 2. Load Doctors
    this.isLoadingDoctors.set(true);
    this.medecinService.getMedecins({ page_size: 50 }).subscribe({
      next: (res: { results?: MedecinDto[] }) => {
        const docs = res.results || [];
        this.doctorsList.set(docs);
        this.isLoadingDoctors.set(false);

        // Check query param ?medecin=12
        this.route.queryParams.subscribe(params => {
          const medId = params['medecin'] || params['medecin_id'] || params['id'];
          if (medId) {
            const targetDoc = docs.find((d: MedecinDto) => d.idMedecin === parseInt(medId, 10));
            if (targetDoc) {
              this.selectDoctor(targetDoc);
              this.currentStep.set(3); // Jump straight to Date & Heure
            }
          }
        });
      },
      error: () => {
        this.isLoadingDoctors.set(false);
      }
    });
  }

  // --- Step 1: Service Selection ---
  selectService(service: ServiceHospitalier): void {
    this.selectedService.set(service);
    this.errorMessage.set(null);
    this.currentStep.set(2);
  }

  // --- Step 2: Doctor Selection ---
  selectDoctor(doctor: MedecinDto): void {
    this.selectedDoctor.set(doctor);
    this.errorMessage.set(null);
    this.loadSlotsForDoctor(doctor.idMedecin, this.selectedDate());
    this.currentStep.set(3);
  }

  // --- Step 3: Date & Slots ---
  onDateChange(newDate: string): void {
    this.selectedDate.set(newDate);
    this.selectedTime.set('');
    const doc = this.selectedDoctor();
    if (doc) {
      this.loadSlotsForDoctor(doc.idMedecin, newDate);
    }
  }

  loadSlotsForDoctor(medecinId: number, date: string): void {
    this.isLoadingSlots.set(true);
    this.appointmentService.getAvailableSlots(medecinId, date).subscribe({
      next: (res) => {
        this.availableSlots.set(res.creneaux || []);
        this.isLoadingSlots.set(false);
      },
      error: () => {
        this.isLoadingSlots.set(false);
      }
    });
  }

  selectSlot(slot: TimeSlot): void {
    if (!slot.disponible) return;
    this.selectedTime.set(slot.heure);
  }

  goToStep4(): void {
    this.motifTouched.set(true);
    if (!this.selectedTime()) {
      this.errorMessage.set('Veuillez choisir un horaire de consultation.');
      return;
    }
    if (!this.motif() || !this.motif().trim()) {
      this.errorMessage.set('Le motif de consultation est obligatoire pour planifier votre rendez-vous.');
      return;
    }
    this.errorMessage.set(null);
    this.currentStep.set(4);
  }

  // --- Step 4: Submission ---
  submitAppointment(): void {
    const doc = this.selectedDoctor();
    if (!doc) {
      this.errorMessage.set('Veuillez sélectionner un médecin.');
      return;
    }
    if (!this.selectedDate() || !this.selectedTime()) {
      this.errorMessage.set('Veuillez choisir une date et une heure valides.');
      return;
    }
    if (!this.motif().trim()) {
      this.errorMessage.set('Le motif du rendez-vous est obligatoire.');
      return;
    }

    this.isSubmitting.set(true);
    this.errorMessage.set(null);

    const dto: CreateAppointmentDto = {
      id_medecin: doc.idMedecin,
      date_rdv: this.selectedDate(),
      heure: this.selectedTime(),
      motif: this.motif().trim(),
      patient_nom: this.patientNom(),
      patient_prenom: this.patientPrenom(),
      patient_telephone: this.patientTelephone(),
      patient_email: this.patientEmail(),
      type_consultation: this.selectedConsultationType()
    };

    this.appointmentService.createAppointment(dto).subscribe({
      next: (rdv) => {
        this.confirmedRdv.set(rdv);
        this.isSubmitting.set(false);
        this.currentStep.set(5); // Success step
      },
      error: (err) => {
        this.isSubmitting.set(false);
        console.error('Erreur de création du rendez-vous:', err);
        if (err.status === 409) {
          this.errorMessage.set('Ce créneau horaire vient d\'être réservé par un autre patient. Veuillez choisir un autre horaire.');
        } else if (err.status === 401) {
          this.errorMessage.set('Votre session a expiré. Veuillez vous reconnecter.');
        } else if (err.status === 400 && err.error?.motif) {
          this.errorMessage.set(err.error.motif[0]);
        } else if (err.status === 400 && err.error?.heure) {
          this.errorMessage.set(err.error.heure[0]);
        } else {
          this.errorMessage.set('Une erreur est survenue lors de l\'enregistrement. Veuillez réessayer.');
        }
      }
    });
  }

  goToStep(step: number): void {
    if (step < this.currentStep()) {
      this.currentStep.set(step);
      this.errorMessage.set(null);
    }
  }

  printReceipt(): void {
    window.print();
  }

  resetBooking(): void {
    this.currentStep.set(1);
    this.selectedService.set(null);
    this.selectedDoctor.set(null);
    this.selectedTime.set('');
    this.motif.set('');
    this.confirmedRdv.set(null);
    this.errorMessage.set(null);
  }
}
