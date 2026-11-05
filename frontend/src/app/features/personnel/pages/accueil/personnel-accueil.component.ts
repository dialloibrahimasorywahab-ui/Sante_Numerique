import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, RouterLink } from '@angular/router';
import { AuthService } from '../../../../core/services/auth.service';
import { PersonnelService } from '../../services/personnel.service';
import { HospitalisePatientItem, UpcomingAppointmentItem } from '../../models/personnel.model';

@Component({
  selector: 'app-personnel-accueil',
  standalone: true,
  imports: [CommonModule, RouterModule, RouterLink],
  templateUrl: './personnel-accueil.component.html',
  styleUrl: './personnel-accueil.component.scss'
})
export class PersonnelAccueilComponent implements OnInit {
  authService = inject(AuthService);
  private personnelService = inject(PersonnelService);

  isLoadingHospitalises = signal<boolean>(true);
  isLoadingRdv = signal<boolean>(true);

  hospitalises = signal<HospitalisePatientItem[]>([]);
  prochainsRdv = signal<UpcomingAppointmentItem[]>([]);

  ngOnInit(): void {
    this.loadHospitalises();
    this.loadProchainsRdv();
  }

  loadHospitalises(): void {
    this.isLoadingHospitalises.set(true);
    this.personnelService.getHospitalisationsEnCours(6).subscribe({
      next: (data) => {
        this.hospitalises.set(data);
        this.isLoadingHospitalises.set(false);
      },
      error: () => {
        this.hospitalises.set([]);
        this.isLoadingHospitalises.set(false);
      }
    });
  }

  loadProchainsRdv(): void {
    this.isLoadingRdv.set(true);
    this.personnelService.getProchainsRendezVous(6).subscribe({
      next: (data) => {
        this.prochainsRdv.set(data);
        this.isLoadingRdv.set(false);
      },
      error: () => {
        this.prochainsRdv.set([]);
        this.isLoadingRdv.set(false);
      }
    });
  }
}
