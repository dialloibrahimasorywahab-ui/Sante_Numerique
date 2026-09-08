import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { AppointmentService } from '../../services/appointment.service';
import { ServicesService } from '../../../services-hospitaliers/services/services.service';
import { MedecinService } from '../../../medecins/services/medecin.service';
import { AuthService } from '../../../../core/services/auth.service';
import { ServiceHospitalier } from '../../../services-hospitaliers/models/models';
import { MedecinDto } from '../../../medecins/models/models';
import { TimeSlot, RendezVousDto, CreateAppointmentDto } from '../../models/models';
import { HospitalService } from '../../../landing/services/hospital.service';

@Component({
  selector: 'app-book-appointment',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  templateUrl: './book-appointment.component.html',
  styleUrl: './book-appointment.component.scss'
})
export class BookAppointmentComponent implements OnInit {
  private fb = inject(FormBuilder);
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private appointmentService = inject(AppointmentService);
  private servicesService = inject(ServicesService);
  private medecinService = inject(MedecinService);
  private hospitalService = inject(HospitalService);
  authService = inject(AuthService);

  // Loading and error states
  isLoadingServices = signal<boolean>(false);
  isLoadingDoctors = signal<boolean>(false);
  isLoadingSlots = signal<boolean>(false);
  isSubmitting = signal<boolean>(false);
  errorMessage = signal<string | null>(null);

  // Success state & result
  isSuccess = signal<boolean>(false);
  confirmedAppointment = signal<RendezVousDto | null>(null);
  confirmedServiceNom = signal<string>('');
  confirmedDoctorNom = signal<string>('');

  // Data lists
  servicesList = signal<ServiceHospitalier[]>([]);
  doctorsList = signal<MedecinDto[]>([]);
  availableSlots = signal<TimeSlot[]>([]);
  selectedServiceId = signal<string>('');
  selectedDoctorId = signal<string>('');

  // Min date (today)
  todayString = this.hospitalService.getTodayString();

  // Reactive Formulaire unique
  bookingForm!: FormGroup;

  // Doctors filtered according to selected service
  filteredDoctors = computed(() => {
    const sId = this.selectedServiceId();
    const docs = this.doctorsList();
    if (!sId) return docs;

    const serv = this.servicesList().find(s => String(s.id_service || s.idService) === String(sId));
    if (!serv) return [];

    return docs.filter(doc => this.isDoctorInService(doc, serv));
  });

  /**
   * Determine whether a doctor strictly belongs to a hospital service / department
   */
  isDoctorInService(doc: MedecinDto, serv: ServiceHospitalier): boolean {
    if (!doc || !serv) return false;

    const servCode = (serv.nom_service || serv.nomService || '').toUpperCase().trim();
    const specCode = (doc.specialite || '').toUpperCase().trim();

    // 1. Direct code equality
    if (servCode && specCode && servCode === specCode) return true;

    // 2. Specific canonical aliases
    if (
      (servCode === 'MEDECINE_GENERALE' || servCode === 'URGENCES' || servCode === 'GENERALISTE') &&
      (specCode === 'GENERALISTE' || specCode === 'MEDECINE_GENERALE')
    ) {
      return true;
    }
    if (
      (servCode === 'MATERNITE' || servCode === 'GYNECOLOGIE') &&
      (specCode === 'GYNECOLOGIE' || specCode === 'MATERNITE')
    ) {
      return true;
    }
    if (
      (servCode === 'CHIRURGIE' || servCode === 'CHIRURGIE_GENERALE') &&
      (specCode === 'CHIRURGIE' || specCode === 'CHIRURGIE_GENERALE')
    ) {
      return true;
    }

    // 3. String normalization / keyword match
    const normServName = this.normalizeStr(serv.displayNom || serv.nom_service_display || serv.nom_service || serv.nomService || '');
    const normSpecName = this.normalizeStr(doc.specialiteDisplay || doc.specialiteLabel || doc.specialite || '');

    const rootMatches: [RegExp, RegExp][] = [
      [/general|urgence/, /general/],
      [/cardio/, /cardio/],
      [/pedia/, /pedia/],
      [/gyneco|mater/, /gyneco|mater/],
      [/neuro/, /neuro/],
      [/dermat/, /dermat/],
      [/chirurg/, /chirurg/],
      [/ophtalm/, /ophtalm/],
      [/psychiat/, /psychiat/],
      [/radio|imager/, /radio|imager/]
    ];

    for (const [servRegex, specRegex] of rootMatches) {
      if (servRegex.test(normServName) && specRegex.test(normSpecName)) {
        return true;
      }
    }

    return false;
  }

  private normalizeStr(str: string): string {
    return (str || '')
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .trim();
  }

  findServiceForDoctor(doc: MedecinDto): ServiceHospitalier | undefined {
    if (!doc) return undefined;
    return this.servicesList().find(serv => this.isDoctorInService(doc, serv));
  }

  ngOnInit(): void {
    this.initForm();
    this.loadInitialData();
  }

  private initForm(): void {
    this.bookingForm = this.fb.group({
      serviceId: ['', Validators.required],
      doctorId: ['', Validators.required],
      date: [this.hospitalService.getDefaultBookingDate(), Validators.required],
      time: ['', Validators.required],
      appointmentType: ['consultation_presentiel', Validators.required],
      reason: ['', [Validators.required, Validators.minLength(4)]],
      notes: ['']
    });

    // Listen to form value changes
    this.bookingForm.get('serviceId')?.valueChanges.subscribe(sId => {
      this.selectedServiceId.set(sId || '');
      this.onServiceChange(sId);
    });

    this.bookingForm.get('doctorId')?.valueChanges.subscribe(dId => {
      this.selectedDoctorId.set(dId || '');
      this.onDoctorChange(dId);
    });

    this.bookingForm.get('date')?.valueChanges.subscribe(date => {
      this.onDateChange(date);
    });
  }

  private loadInitialData(): void {
    // 1. Load Services
    this.isLoadingServices.set(true);
    this.servicesService.getServices().subscribe({
      next: (services: ServiceHospitalier[]) => {
        this.servicesList.set(services);
        this.isLoadingServices.set(false);
        this.checkQueryParams();
      },
      error: () => {
        this.isLoadingServices.set(false);
      }
    });

    // 2. Load Doctors
    this.isLoadingDoctors.set(true);
    this.medecinService.getMedecins({ page_size: 100 }).subscribe({
      next: (res: { results?: MedecinDto[] }) => {
        const docs = res.results || [];
        this.doctorsList.set(docs);
        this.isLoadingDoctors.set(false);
        this.checkQueryParams();
      },
      error: () => {
        this.isLoadingDoctors.set(false);
      }
    });
  }

  private checkQueryParams(): void {
    const docs = this.doctorsList();
    const services = this.servicesList();
    if (docs.length === 0 || services.length === 0) return;

    this.route.queryParams.subscribe(params => {
      const medId = params['medecin'] || params['medecin_id'] || params['id'];
      const servId = params['service'] || params['service_id'];

      if (medId) {
        const targetDoc = docs.find((d: MedecinDto) => String(d.idMedecin) === String(medId));
        if (targetDoc) {
          const matchedService = this.findServiceForDoctor(targetDoc);
          if (matchedService) {
            const sIdStr = String(matchedService.id_service || matchedService.idService);
            this.selectedServiceId.set(sIdStr);
            this.bookingForm.patchValue({ serviceId: sIdStr }, { emitEvent: false });
          }
          this.selectedDoctorId.set(String(targetDoc.idMedecin));
          this.bookingForm.patchValue({ doctorId: String(targetDoc.idMedecin) });
        }
      } else if (servId) {
        const foundServ = services.find(s =>
          String(s.id_service || s.idService) === String(servId) ||
          (s.nom_service || s.nomService || '').toUpperCase() === String(servId).toUpperCase()
        );
        if (foundServ) {
          const sIdStr = String(foundServ.id_service || foundServ.idService);
          this.selectedServiceId.set(sIdStr);
          this.bookingForm.patchValue({ serviceId: sIdStr });
        }
      }
    });
  }

  onServiceChange(serviceId: string): void {
    this.selectedServiceId.set(serviceId || '');
    this.errorMessage.set(null);
    const currentDocId = this.bookingForm.get('doctorId')?.value;
    const availableDocs = this.filteredDoctors();

    // If currently selected doctor does not belong to new service, reset doctor and slots
    if (currentDocId && !availableDocs.some(d => String(d.idMedecin) === String(currentDocId))) {
      this.bookingForm.patchValue({ doctorId: '', time: '' });
      this.selectedDoctorId.set('');
      this.availableSlots.set([]);
    } else if (currentDocId) {
      this.loadSlotsForDoctor(Number(currentDocId), this.bookingForm.get('date')?.value);
    }
  }

  onDoctorChange(doctorId: string): void {
    this.selectedDoctorId.set(doctorId || '');
    this.errorMessage.set(null);
    this.bookingForm.patchValue({ time: '' });
    if (doctorId) {
      const doc = this.doctorsList().find(d => String(d.idMedecin) === String(doctorId));
      if (doc) {
        const currentServiceId = this.selectedServiceId();
        const currentService = this.servicesList().find(s => String(s.id_service || s.idService) === String(currentServiceId));
        if (!currentService || !this.isDoctorInService(doc, currentService)) {
          const matchedService = this.findServiceForDoctor(doc);
          if (matchedService) {
            const matchedId = String(matchedService.id_service || matchedService.idService);
            this.selectedServiceId.set(matchedId);
            this.bookingForm.patchValue({ serviceId: matchedId }, { emitEvent: false });
          }
        }
      }
      const date = this.bookingForm.get('date')?.value;
      this.loadSlotsForDoctor(Number(doctorId), date);
    } else {
      this.availableSlots.set([]);
    }
  }

  onDateChange(date: string): void {
    this.errorMessage.set(null);
    this.bookingForm.patchValue({ time: '' });
    const doctorId = this.bookingForm.get('doctorId')?.value;
    if (doctorId && date) {
      this.loadSlotsForDoctor(Number(doctorId), date);
    }
  }

  loadSlotsForDoctor(medecinId: number, date: string): void {
    if (!medecinId || !date) return;
    this.isLoadingSlots.set(true);

    this.appointmentService.getAvailableSlots(medecinId, date).subscribe({
      next: (res) => {
        const slots = (res.creneaux || []).filter(slot => !this.isPastDateTime(date, slot.heure));
        this.availableSlots.set(slots);
        this.isLoadingSlots.set(false);
      },
      error: () => {
        this.isLoadingSlots.set(false);
      }
    });
  }

  selectTimeSlot(heure: string): void {
    this.bookingForm.patchValue({ time: heure });
    this.bookingForm.get('time')?.markAsTouched();
    this.errorMessage.set(null);
  }

  get selectedDoctorObj(): MedecinDto | null {
    const docId = this.bookingForm.get('doctorId')?.value;
    if (!docId) return null;
    return this.doctorsList().find(d => String(d.idMedecin) === String(docId)) || null;
  }

  get selectedServiceObj(): ServiceHospitalier | null {
    const sId = this.bookingForm.get('serviceId')?.value;
    if (!sId) return null;
    return this.servicesList().find(s => String(s.id_service || s.idService) === String(sId)) || null;
  }

  submitAppointment(): void {
    this.errorMessage.set(null);

    // 1. Validation user login
    const currentUser = this.authService.currentUser();
    if (!currentUser) {
      this.errorMessage.set('Veuillez vous connecter avec votre compte patient pour planifier ce rendez-vous.');
      this.router.navigate(['/login'], { queryParams: { returnUrl: '/rendez-vous' } });
      return;
    }

    // 2. Form validation
    if (this.bookingForm.invalid) {
      this.bookingForm.markAllAsTouched();
      if (this.bookingForm.get('serviceId')?.invalid) {
        this.errorMessage.set('Veuillez sélectionner un pôle de soins.');
      } else if (this.bookingForm.get('doctorId')?.invalid) {
        this.errorMessage.set('Veuillez sélectionner un médecin.');
      } else if (this.bookingForm.get('date')?.invalid) {
        this.errorMessage.set('Veuillez choisir une date valide.');
      } else if (this.bookingForm.get('time')?.invalid) {
        this.errorMessage.set('Veuillez sélectionner un créneau horaire disponible.');
      } else if (this.bookingForm.get('reason')?.invalid) {
        this.errorMessage.set('Veuillez renseigner le motif de consultation (au moins 4 caractères).');
      } else {
        this.errorMessage.set('Veuillez compléter l\'ensemble des champs obligatoires marqués d\'un astérisque (*).');
      }
      return;
    }

    const val = this.bookingForm.value;

    // Check slot is not past
    if (this.isPastDateTime(val.date, val.time)) {
      this.bookingForm.patchValue({ time: '' });
      this.errorMessage.set('L\'horaire sélectionné est déjà passé. Veuillez choisir un autre créneau disponible.');
      return;
    }

    this.isSubmitting.set(true);

    const docObj = this.selectedDoctorObj;
    const servObj = this.selectedServiceObj;

    const dto: CreateAppointmentDto = {
      patient: currentUser.id_user,
      doctor: Number(val.doctorId),
      service: val.serviceId,
      id_patient: currentUser.id_user,
      id_medecin: Number(val.doctorId),
      date: val.date,
      date_rdv: val.date,
      time: val.time,
      heure: val.time,
      appointment_type: val.appointmentType,
      type_consultation: val.appointmentType === 'teleconsultation' ? 'TELECONSULTATION' : 'SUR_PLACE',
      reason: val.reason.trim(),
      motif: val.reason.trim(),
      notes: (val.notes || '').trim(),
      patient_nom: currentUser.nom,
      patient_prenom: currentUser.prenom,
      patient_telephone: currentUser.telephone,
      patient_email: currentUser.email
    };

    this.appointmentService.createAppointment(dto).subscribe({
      next: (rdv) => {
        this.isSubmitting.set(false);
        this.confirmedAppointment.set(rdv);
        this.confirmedServiceNom.set(servObj?.displayNom || servObj?.nom_service || 'Consultation');
        this.confirmedDoctorNom.set(docObj ? `Dr. ${docObj.prenom} ${docObj.nom}` : 'Médecin traitant');
        this.isSuccess.set(true);
        window.scrollTo({ top: 100, behavior: 'smooth' });
      },
      error: (err) => {
        this.isSubmitting.set(false);
        console.error('Erreur lors de la réservation du rendez-vous:', err);

        if (err?.status === 409) {
          this.errorMessage.set('Ce créneau horaire vient d\'être réservé par un autre patient. Veuillez choisir un autre horaire.');
        } else if (err?.status === 401) {
          this.errorMessage.set('Votre session a expiré. Veuillez vous reconnecter pour confirmer votre rendez-vous.');
          this.router.navigate(['/login'], { queryParams: { returnUrl: '/rendez-vous' } });
        } else if (err?.status === 403) {
          this.errorMessage.set('Vous n\'avez pas les autorisations requises pour effectuer cette réservation.');
        } else if (err?.error?.heure) {
          const h = Array.isArray(err.error.heure) ? err.error.heure[0] : err.error.heure;
          this.errorMessage.set(h);
        } else if (err?.error?.date_rdv) {
          const d = Array.isArray(err.error.date_rdv) ? err.error.date_rdv[0] : err.error.date_rdv;
          this.errorMessage.set(d);
        } else if (err?.error?.motif) {
          const m = Array.isArray(err.error.motif) ? err.error.motif[0] : err.error.motif;
          this.errorMessage.set(m);
        } else if (err?.error?.detail) {
          this.errorMessage.set(err.error.detail);
        } else if (err?.error?.error) {
          this.errorMessage.set(err.error.error);
        } else if (err?.friendlyMessage) {
          this.errorMessage.set(err.friendlyMessage);
        } else {
          this.errorMessage.set('Une erreur est survenue lors de l\'enregistrement de votre rendez-vous. Veuillez vérifier les informations et réessayer.');
        }
      }
    });
  }

  resetBooking(): void {
    this.isSuccess.set(false);
    this.confirmedAppointment.set(null);
    this.errorMessage.set(null);
    this.selectedServiceId.set('');
    this.selectedDoctorId.set('');
    this.bookingForm.reset({
      serviceId: '',
      doctorId: '',
      date: this.hospitalService.getDefaultBookingDate(),
      time: '',
      appointmentType: 'consultation_presentiel',
      reason: '',
      notes: ''
    });
    this.availableSlots.set([]);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  printConfirmation(): void {
    window.print();
  }

  private isPastDateTime(date: string, time: string): boolean {
    return this.hospitalService.isSlotPast(date, time);
  }
}
