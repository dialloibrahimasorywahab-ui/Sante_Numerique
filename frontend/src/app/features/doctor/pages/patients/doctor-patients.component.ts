import { Component, inject, signal, computed, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { DoctorService } from '../../services/doctor.service';
import { DoctorPatientDto } from '../../models/doctor.models';

@Component({
  selector: 'app-doctor-patients',
  standalone: true,
  imports: [CommonModule, RouterModule, RouterLink, FormsModule],
  templateUrl: './doctor-patients.component.html',
  styleUrl: './doctor-patients.component.scss'
})
export class DoctorPatientsComponent implements OnInit {
  private doctorService = inject(DoctorService);

  isLoading = signal<boolean>(true);
  errorMessage = signal<string | null>(null);

  patients = signal<DoctorPatientDto[]>([]);
  searchQuery = signal<string>('');

  currentPage = signal<number>(1);
  pageSize = 10;

  ngOnInit(): void {
    this.loadPatients();
  }

  loadPatients(): void {
    this.isLoading.set(true);
    this.errorMessage.set(null);

    this.doctorService.getPatients(1, '').subscribe({
      next: (res) => {
        this.patients.set(res.results || []);
        this.isLoading.set(false);
      },
      error: () => {
        this.errorMessage.set('Impossible de charger les dossiers patients.');
        this.isLoading.set(false);
      }
    });
  }

  filteredPatients = computed(() => {
    let list = this.patients();
    const query = this.searchQuery().trim().toLowerCase();
    if (!query) return list;

    return list.filter(p => {
      const nom = (p.nom || '').toLowerCase();
      const prenom = (p.prenom || '').toLowerCase();
      const tel = (p.telephone || '').toLowerCase();
      const email = (p.email || '').toLowerCase();
      const secu = (p.numero_securite_sociale || p.numeroSecuriteSociale || '').toLowerCase();
      const id = String(p.id_patient || p.idPatient || '');
      return nom.includes(query) || prenom.includes(query) || tel.includes(query) || email.includes(query) || secu.includes(query) || id.includes(query);
    });
  });

  paginatedPatients = computed(() => {
    const list = this.filteredPatients();
    const start = (this.currentPage() - 1) * this.pageSize;
    return list.slice(start, start + this.pageSize);
  });

  totalPages = computed(() => {
    return Math.ceil(this.filteredPatients().length / this.pageSize) || 1;
  });

  setPage(p: number): void {
    if (p >= 1 && p <= this.totalPages()) {
      this.currentPage.set(p);
    }
  }

  calculateAge(dateStr?: string | null): string {
    if (!dateStr) return 'Non renseigné';
    const birth = new Date(dateStr);
    if (isNaN(birth.getTime())) return 'Non renseigné';
    const diff = Date.now() - birth.getTime();
    const ageDate = new Date(diff);
    const age = Math.abs(ageDate.getUTCFullYear() - 1970);
    return `${age} ans`;
  }
}
