import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { AdminService } from '../../services/admin.service';
import { formatDate as formatSharedDate } from '../../../../shared/utils';

export type MedicalTab = 'rendezvous' | 'consultations' | 'hospitalisations' | 'ordonnances';

@Component({
  selector: 'app-admin-medical',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './admin-medical.component.html',
  styleUrls: ['./admin-medical.component.scss']
})
export class AdminMedicalComponent implements OnInit {
  private adminService = inject(AdminService);
  private route = inject(ActivatedRoute);

  activeTab = signal<MedicalTab>('rendezvous');
  searchQuery = signal<string>('');
  currentPage = signal<number>(1);
  pageSize = 10;

  isLoading = signal<boolean>(false);
  errorMessage = signal<string | null>(null);

  items = signal<any[]>([]);
  totalCount = signal<number>(0);

  totalPages = computed(() => Math.ceil(this.totalCount() / this.pageSize) || 1);

  ngOnInit(): void {
    this.route.data.subscribe(data => {
      if (data['medicalTab']) {
        this.activeTab.set(data['medicalTab']);
      }
      this.loadData();
    });
  }

  setTab(tab: MedicalTab): void {
    this.activeTab.set(tab);
    this.currentPage.set(1);
    this.searchQuery.set('');
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

    const tab = this.activeTab();
    let resource = 'rendezvous/all';
    if (tab === 'consultations') resource = 'consultations';
    if (tab === 'hospitalisations') resource = 'hospitalisations';
    if (tab === 'ordonnances') resource = 'ordonnances';

    this.adminService.getEntityList(resource, this.currentPage(), this.searchQuery(), { page_size: this.pageSize }).subscribe({
      next: (res) => {
        this.items.set(res.results || []);
        this.totalCount.set(res.count || (res.results ? res.results.length : 0));
        this.isLoading.set(false);
      },
      error: () => {
        this.errorMessage.set('Impossible de charger les activités médicales.');
        this.isLoading.set(false);
      }
    });
  }

  formatDate(dateStr: string): string {
    return formatSharedDate(dateStr);
  }

  getRdvBadgeClass(statut: string): string {
    switch ((statut || '').toUpperCase()) {
      case 'CONFIRME': return 'badge-confirmed';
      case 'EN_ATTENTE': return 'badge-pending';
      case 'TERMINE': return 'badge-completed';
      case 'ANNULE': return 'badge-cancelled';
      case 'EN_COURS': return 'badge-in-progress';
      default: return 'badge-default';
    }
  }

  formatLitName(val: any): string {
    if (!val) return 'Lit';
    const str = String(val).trim();
    if (str.toLowerCase().startsWith('lit')) return str;
    return `Lit ${str}`;
  }

  formatChambre(c: any): string {
    if (!c) return 'Chambre N/D';
    if (typeof c === 'number' || typeof c === 'string') {
      const s = String(c).trim();
      return s.toLowerCase().startsWith('chambre') ? s : `Chambre ${s}`;
    }
    const num = c.numero_chambre || c.numeroChambre || c.id;
    if (!num) return 'Chambre N/D';
    const s = String(num).trim();
    return s.toLowerCase().startsWith('chambre') ? s : `Chambre ${s}`;
  }

  getHospBadgeClass(statut: string): string {
    switch ((statut || '').toUpperCase()) {
      case 'EN_COURS': return 'badge-in-progress';
      case 'TERMINEE':
      case 'TERMINE': return 'badge-completed';
      case 'ANNULEE':
      case 'ANNULE': return 'badge-cancelled';
      default: return 'badge-default';
    }
  }
}
