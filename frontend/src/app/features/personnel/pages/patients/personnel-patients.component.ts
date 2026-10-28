import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { PersonnelService } from '../../services/personnel.service';
import { PatientItem } from '../../models/personnel.model';

@Component({
  selector: 'app-personnel-patients',
  standalone: true,
  imports: [CommonModule, RouterModule, RouterLink, FormsModule],
  templateUrl: './personnel-patients.component.html',
  styleUrl: './personnel-patients.component.scss'
})
export class PersonnelPatientsComponent implements OnInit {
  private personnelService = inject(PersonnelService);

  isLoading = signal<boolean>(true);
  patients = signal<PatientItem[]>([]);
  searchTerm: string = '';

  ngOnInit(): void {
    this.loadPatients();
  }

  loadPatients(): void {
    this.isLoading.set(true);
    this.personnelService.getPatients(this.searchTerm).subscribe({
      next: (data) => {
        this.patients.set(data);
        this.isLoading.set(false);
      },
      error: () => {
        this.patients.set([]);
        this.isLoading.set(false);
      }
    });
  }

  onSearch(): void {
    this.loadPatients();
  }

  clearSearch(): void {
    this.searchTerm = '';
    this.loadPatients();
  }
}
