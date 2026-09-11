import { Component, inject, signal, computed, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { DoctorService } from '../../services/doctor.service';
import { DoctorConsultationDto } from '../../models/doctor.models';
import { formatDate as formatSharedDate } from '../../../../shared/utils';

@Component({
  selector: 'app-doctor-consultations',
  standalone: true,
  imports: [CommonModule, RouterModule, RouterLink, FormsModule],
  templateUrl: './doctor-consultations.component.html',
  styleUrl: './doctor-consultations.component.scss'
})
export class DoctorConsultationsComponent implements OnInit {
  private doctorService = inject(DoctorService);

  isLoading = signal<boolean>(true);
  errorMessage = signal<string | null>(null);

  consultations = signal<DoctorConsultationDto[]>([]);
  searchQuery = signal<string>('');

  currentPage = signal<number>(1);
  pageSize = 10;

  ngOnInit(): void {
    this.loadConsultations();
  }

  loadConsultations(): void {
    this.isLoading.set(true);
    this.errorMessage.set(null);

    this.doctorService.getConsultations(1, '', undefined).subscribe({
      next: (res) => {
        this.consultations.set(res.results || []);
        this.isLoading.set(false);
      },
      error: () => {
        this.errorMessage.set('Erreur lors du chargement des consultations.');
        this.isLoading.set(false);
      }
    });
  }

  filteredConsultations = computed(() => {
    let list = this.consultations();
    const query = this.searchQuery().trim().toLowerCase();
    if (!query) return list;

    return list.filter(c => {
      const nom = (c.patient_details?.nom || '').toLowerCase();
      const prenom = (c.patient_details?.prenom || '').toLowerCase();
      const diag = (c.diagnostic || '').toLowerCase();
      const symp = (c.symptomes || '').toLowerCase();
      const obs = (c.observations || '').toLowerCase();
      const date = (c.date_cons || '').toLowerCase();
      return nom.includes(query) || prenom.includes(query) || diag.includes(query) || symp.includes(query) || obs.includes(query) || date.includes(query);
    });
  });

  paginatedConsultations = computed(() => {
    const list = this.filteredConsultations();
    const start = (this.currentPage() - 1) * this.pageSize;
    return list.slice(start, start + this.pageSize);
  });

  totalPages = computed(() => {
    return Math.ceil(this.filteredConsultations().length / this.pageSize) || 1;
  });

  setPage(p: number): void {
    if (p >= 1 && p <= this.totalPages()) {
      this.currentPage.set(p);
    }
  }

  getPatientId(c: DoctorConsultationDto): number {
    return Number(c.patient || c.patient_details?.id_patient || c.patient_details?.idPatient || 0);
  }

  formatDate(dateStr?: string): string {
    return formatSharedDate(dateStr);
  }
}
