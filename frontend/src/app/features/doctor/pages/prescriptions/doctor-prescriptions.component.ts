import { Component, inject, signal, computed, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { DoctorService } from '../../services/doctor.service';
import { DoctorPrescriptionDto } from '../../models/doctor.models';

@Component({
  selector: 'app-doctor-prescriptions',
  standalone: true,
  imports: [CommonModule, RouterModule, RouterLink, FormsModule],
  templateUrl: './doctor-prescriptions.component.html',
  styleUrl: './doctor-prescriptions.component.scss'
})
export class DoctorPrescriptionsComponent implements OnInit {
  private doctorService = inject(DoctorService);

  isLoading = signal<boolean>(true);
  errorMessage = signal<string | null>(null);

  prescriptions = signal<DoctorPrescriptionDto[]>([]);
  searchQuery = signal<string>('');

  currentPage = signal<number>(1);
  pageSize = 10;

  ngOnInit(): void {
    this.loadPrescriptions();
  }

  loadPrescriptions(): void {
    this.isLoading.set(true);
    this.errorMessage.set(null);

    this.doctorService.getPrescriptions(1, '', undefined).subscribe({
      next: (res) => {
        this.prescriptions.set(res.results || []);
        this.isLoading.set(false);
      },
      error: () => {
        this.errorMessage.set('Erreur lors du chargement des ordonnances.');
        this.isLoading.set(false);
      }
    });
  }

  filteredPrescriptions = computed(() => {
    let list = this.prescriptions();
    const query = this.searchQuery().trim().toLowerCase();
    if (!query) return list;

    return list.filter(p => {
      const ref = (p.reference || '').toLowerCase();
      const obs = (p.observation || '').toLowerCase();
      const date = (p.date_ordonnance || '').toLowerCase();
      const patNom = (p.consultation_details?.patient_details?.nom || '').toLowerCase();
      const patPrenom = (p.consultation_details?.patient_details?.prenom || '').toLowerCase();
      return ref.includes(query) || obs.includes(query) || date.includes(query) || patNom.includes(query) || patPrenom.includes(query);
    });
  });

  paginatedPrescriptions = computed(() => {
    const list = this.filteredPrescriptions();
    const start = (this.currentPage() - 1) * this.pageSize;
    return list.slice(start, start + this.pageSize);
  });

  totalPages = computed(() => {
    return Math.ceil(this.filteredPrescriptions().length / this.pageSize) || 1;
  });

  setPage(p: number): void {
    if (p >= 1 && p <= this.totalPages()) {
      this.currentPage.set(p);
    }
  }

  getPatientId(p: DoctorPrescriptionDto): number {
    return Number(
      p.consultation_details?.patient ||
      p.consultation_details?.patient_details?.id_patient ||
      p.consultation_details?.patient_details?.idPatient ||
      0
    );
  }

  formatDate(dateStr?: string): string {
    if (!dateStr) return '—';
    try {
      const d = new Date(dateStr);
      if (isNaN(d.getTime())) {
        return dateStr.split('T')[0] || dateStr;
      }
      return d.toLocaleDateString('fr-FR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      });
    } catch {
      return dateStr;
    }
  }
}
