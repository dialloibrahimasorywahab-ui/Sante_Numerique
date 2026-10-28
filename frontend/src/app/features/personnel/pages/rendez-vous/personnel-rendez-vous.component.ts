import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { PersonnelService } from '../../services/personnel.service';
import { UpcomingAppointmentItem } from '../../models/personnel.model';

@Component({
  selector: 'app-personnel-rendez-vous',
  standalone: true,
  imports: [CommonModule, RouterModule, RouterLink, FormsModule],
  templateUrl: './personnel-rendez-vous.component.html',
  styleUrl: './personnel-rendez-vous.component.scss'
})
export class PersonnelRendezVousComponent implements OnInit {
  private personnelService = inject(PersonnelService);

  isLoading = signal<boolean>(true);
  rendezVous = signal<UpcomingAppointmentItem[]>([]);
  activeStatut: string = '';
  searchTerm: string = '';

  readonly statusOptions = [
    { label: 'Tous les rendez-vous', value: '' },
    { label: 'Confirmés', value: 'CONFIRME' },
    { label: 'En attente', value: 'EN_ATTENTE' },
    { label: 'Terminés', value: 'TERMINE' },
    { label: 'Annulés', value: 'ANNULE' },
  ];

  ngOnInit(): void {
    this.loadRendezVous();
  }

  loadRendezVous(): void {
    this.isLoading.set(true);
    this.personnelService.getRendezVous(this.activeStatut, this.searchTerm).subscribe({
      next: (data) => {
        this.rendezVous.set(data);
        this.isLoading.set(false);
      },
      error: () => {
        this.rendezVous.set([]);
        this.isLoading.set(false);
      }
    });
  }

  setStatut(statut: string): void {
    this.activeStatut = statut;
    this.loadRendezVous();
  }

  onSearch(): void {
    this.loadRendezVous();
  }

  clearSearch(): void {
    this.searchTerm = '';
    this.loadRendezVous();
  }
}
