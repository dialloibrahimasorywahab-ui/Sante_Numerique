import { Component, inject, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterModule, RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';
import { DoctorService } from '../../services/doctor.service';
import {
  DoctorPatientDto,
  DoctorConsultationDto,
  DoctorPrescriptionDto,
  DoctorAppointmentDto
} from '../../models/doctor.models';

type TabType = 'CONSULTATIONS' | 'ORDONNANCES' | 'RENDEZ_VOUS';

@Component({
  selector: 'app-doctor-patient-detail',
  standalone: true,
  imports: [CommonModule, RouterModule, RouterLink],
  templateUrl: './doctor-patient-detail.component.html',
  styleUrl: './doctor-patient-detail.component.scss'
})
export class DoctorPatientDetailComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private doctorService = inject(DoctorService);

  isLoading = signal<boolean>(true);
  errorMessage = signal<string | null>(null);

  patientId = signal<number>(0);
  patient = signal<DoctorPatientDto | null>(null);

  activeTab = signal<TabType>('CONSULTATIONS');

  consultations = signal<DoctorConsultationDto[]>([]);
  prescriptions = signal<DoctorPrescriptionDto[]>([]);
  appointments = signal<DoctorAppointmentDto[]>([]);

  ngOnInit(): void {
    const idParam = this.route.snapshot.paramMap.get('id');
    if (idParam) {
      this.patientId.set(+idParam);
      this.loadPatientDossier(+idParam);
    }
  }

  loadPatientDossier(id: number): void {
    this.isLoading.set(true);
    this.errorMessage.set(null);

    forkJoin({
      patient: this.doctorService.getPatientDetail(id),
      consultations: this.doctorService.getConsultations(1, '', id),
      appointments: this.doctorService.getAppointments(1, '', '')
    }).subscribe({
      next: ({ patient, consultations, appointments }) => {
        this.patient.set(patient);
        const consList = consultations.results || [];
        this.consultations.set(consList);

        // Filter appointments for this patient
        const allRdvs = appointments.results || [];
        this.appointments.set(allRdvs.filter(r => r.patient === id));

        // Load prescriptions for this patient's consultations
        if (consList.length > 0) {
          this.doctorService.getPrescriptions(1, '', undefined).subscribe({
            next: (pRes) => {
              const pList = pRes.results || [];
              const consIds = new Set(consList.map(c => c.id || c.idConsultation));
              this.prescriptions.set(pList.filter(p => consIds.has(p.consultation)));
            }
          });
        }

        this.isLoading.set(false);
      },
      error: () => {
        this.errorMessage.set('Impossible de charger le dossier médical de ce patient.');
        this.isLoading.set(false);
      }
    });
  }

  setActiveTab(tab: TabType): void {
    this.activeTab.set(tab);
  }

  calculateAge(dateStr?: string | null): string {
    if (!dateStr) return 'Non renseigné';
    const birth = new Date(dateStr);
    if (isNaN(birth.getTime())) return 'Non renseigné';
    const diff = Date.now() - birth.getTime();
    const ageDate = new Date(diff);
    return `${Math.abs(ageDate.getUTCFullYear() - 1970)} ans`;
  }
}
