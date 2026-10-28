import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { PersonnelService } from '../../services/personnel.service';
import { PatientParcoursData } from '../../models/personnel.model';

@Component({
  selector: 'app-personnel-patient-parcours',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './personnel-patient-parcours.component.html',
  styleUrl: './personnel-patient-parcours.component.scss'
})
export class PersonnelPatientParcoursComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private personnelService = inject(PersonnelService);

  patientId = signal<number>(0);
  isLoading = signal<boolean>(true);
  parcoursData = signal<PatientParcoursData | null>(null);

  ngOnInit(): void {
    this.route.paramMap.subscribe(params => {
      const idParam = params.get('id');
      if (idParam) {
        const id = parseInt(idParam, 10);
        this.patientId.set(id);
        this.loadParcours(id);
      }
    });
  }

  loadParcours(patientId: number): void {
    this.isLoading.set(true);
    this.personnelService.getPatientParcours(patientId).subscribe({
      next: (data) => {
        this.parcoursData.set(data);
        this.isLoading.set(false);
      },
      error: () => {
        this.parcoursData.set(null);
        this.isLoading.set(false);
      }
    });
  }
}
