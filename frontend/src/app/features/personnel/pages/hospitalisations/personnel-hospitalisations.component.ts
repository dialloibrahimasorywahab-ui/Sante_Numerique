import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { PersonnelService } from '../../services/personnel.service';
import { HospitalisePatientItem } from '../../models/personnel.model';

@Component({
  selector: 'app-personnel-hospitalisations',
  standalone: true,
  imports: [CommonModule, RouterModule, RouterLink, FormsModule],
  templateUrl: './personnel-hospitalisations.component.html',
  styleUrl: './personnel-hospitalisations.component.scss'
})
export class PersonnelHospitalisationsComponent implements OnInit {
  private personnelService = inject(PersonnelService);

  isLoading = signal<boolean>(true);
  hospitalisations = signal<HospitalisePatientItem[]>([]);
  activeStatut: string = '';
  searchTerm: string = '';

  readonly statusOptions = [
    { label: 'Toutes', value: '' },
    { label: 'En cours', value: 'EN_COURS' },
    { label: 'Terminées', value: 'TERMINEE' },
    { label: 'Programmées', value: 'PROGRAMMEE' },
    { label: 'Annulées', value: 'ANNULEE' }
  ];

  ngOnInit(): void {
    this.loadHospitalisations();
  }

  loadHospitalisations(): void {
    this.isLoading.set(true);
    this.personnelService.getHospitalisations(this.activeStatut, this.searchTerm).subscribe({
      next: (data) => {
        this.hospitalisations.set(data);
        this.isLoading.set(false);
      },
      error: () => {
        this.hospitalisations.set([]);
        this.isLoading.set(false);
      }
    });
  }

  setStatut(statut: string): void {
    this.activeStatut = statut;
    this.loadHospitalisations();
  }

  onSearch(): void {
    this.loadHospitalisations();
  }

  clearSearch(): void {
    this.searchTerm = '';
    this.loadHospitalisations();
  }
}
