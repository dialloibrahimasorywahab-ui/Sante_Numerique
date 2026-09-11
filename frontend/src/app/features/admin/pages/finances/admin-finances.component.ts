import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { AdminService } from '../../services/admin.service';
import { FinancialStats } from '../../models/admin.model';
import { formatDate as formatSharedDate } from '../../../../shared/utils';

export type FinanceFilter = 'ALL' | 'EN_ATTENTE' | 'PAYE' | 'ANNULE';

@Component({
  selector: 'app-admin-finances',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './admin-finances.component.html',
  styleUrls: ['./admin-finances.component.scss']
})
export class AdminFinancesComponent implements OnInit {
  private adminService = inject(AdminService);

  activeFilter = signal<FinanceFilter>('ALL');
  searchQuery = signal<string>('');
  currentPage = signal<number>(1);
  pageSize = 10;

  isLoading = signal<boolean>(false);
  isActionLoading = signal<number | null>(null);
  errorMessage = signal<string | null>(null);
  successMessage = signal<string | null>(null);

  stats = signal<FinancialStats>({
    totalMontant: 0,
    montantPaye: 0,
    montantEnAttente: 0,
    montantAnnule: 0,
    countPaye: 0,
    countEnAttente: 0,
    tauxRecouvrement: 0
  });

  items = signal<any[]>([]);
  totalCount = signal<number>(0);

  totalPages = computed(() => Math.ceil(this.totalCount() / this.pageSize) || 1);

  ngOnInit(): void {
    this.loadStats();
    this.loadData();
  }

  loadStats(): void {
    this.adminService.getFinancialStats().subscribe(data => {
      this.stats.set(data);
    });
  }

  setFilter(filter: FinanceFilter): void {
    this.activeFilter.set(filter);
    this.currentPage.set(1);
    this.loadData();
  }

  onSearchChange(val: string): void {
    this.searchQuery.set(val);
    this.currentPage.set(1);
    this.loadData();
  }

  setPage(p: number): void {
    if (p < 1 || p > this.totalPages()) return;
    this.currentPage.set(p);
    this.loadData();
  }

  loadData(): void {
    this.isLoading.set(true);
    this.errorMessage.set(null);

    const extraParams: any = { page_size: this.pageSize };
    if (this.activeFilter() !== 'ALL') {
      extraParams.statut = this.activeFilter();
    }

    this.adminService.getEntityList('frais_consultations', this.currentPage(), this.searchQuery(), extraParams).subscribe({
      next: (res) => {
        this.items.set(res.results || []);
        this.totalCount.set(res.count || (res.results ? res.results.length : 0));
        this.isLoading.set(false);
      },
      error: () => {
        this.errorMessage.set('Impossible de charger les frais de consultation.');
        this.isLoading.set(false);
      }
    });
  }

  markAsPaid(item: any): void {
    const id = item.id || item.idFrais;
    if (!id) return;

    this.isActionLoading.set(id);
    this.successMessage.set(null);

    this.adminService.markFraisAsPaid(id).subscribe({
      next: () => {
        this.isActionLoading.set(null);
        this.successMessage.set(`Le règlement des frais #${id} (${item.montant} FCFA) a été validé.`);
        this.loadData();
        this.loadStats();

        // Effacer le message après 4 secondes
        setTimeout(() => {
          this.successMessage.set(null);
        }, 4000);
      },
      error: () => {
        this.isActionLoading.set(null);
        this.errorMessage.set(`Erreur lors de l'encaissement des frais #${id}.`);
      }
    });
  }

  formatDate(dateStr: string): string {
    return formatSharedDate(dateStr);
  }

  getStatutBadgeClass(statut: string): string {
    switch ((statut || '').toUpperCase()) {
      case 'PAYE': return 'badge-paye';
      case 'EN_ATTENTE': return 'badge-attente';
      case 'ANNULE': return 'badge-annule';
      default: return 'badge-attente';
    }
  }
}
