import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { AdminService } from '../../services/admin.service';

export type HospitalTab = 'services' | 'batiments' | 'chambres' | 'lits';

@Component({
  selector: 'app-admin-hospital',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './admin-hospital.component.html',
  styleUrls: ['./admin-hospital.component.scss']
})
export class AdminHospitalComponent implements OnInit {
  private adminService = inject(AdminService);
  private route = inject(ActivatedRoute);

  activeTab = signal<HospitalTab>('services');
  searchQuery = signal<string>('');
  currentPage = signal<number>(1);
  pageSize = 10;

  isLoading = signal<boolean>(false);
  isActionLoading = signal<number | null>(null);
  errorMessage = signal<string | null>(null);
  toastMessage = signal<{ type: 'success' | 'error'; text: string } | null>(null);

  // Modal Bâtiment
  showBatimentModal = signal<boolean>(false);
  isSubmitting = signal<boolean>(false);
  formError = signal<string | null>(null);

  batimentForm = {
    nom: '',
    description: '',
    nombre_chambre: 10,
    actif: true
  };

  items = signal<any[]>([]);
  totalCount = signal<number>(0);

  totalPages = computed(() => Math.ceil(this.totalCount() / this.pageSize) || 1);

  ngOnInit(): void {
    this.route.data.subscribe(data => {
      if (data['hospitalTab']) {
        this.activeTab.set(data['hospitalTab']);
      }
      this.loadData();
    });
  }

  setTab(tab: HospitalTab): void {
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
    let resource = 'services/all';
    let extraParams: any = { page_size: this.pageSize };

    if (tab === 'batiments') {
      resource = 'batiments/all';
      extraParams.all = 'true';
    }
    if (tab === 'chambres') resource = 'chambres/all';
    if (tab === 'lits') resource = 'lits/all';

    this.adminService.getEntityList(resource, this.currentPage(), this.searchQuery(), extraParams).subscribe({
      next: (res) => {
        this.items.set(res.results || []);
        this.totalCount.set(res.count || (res.results ? res.results.length : 0));
        this.isLoading.set(false);
      },
      error: () => {
        this.errorMessage.set('Impossible de charger les données pour cette section.');
        this.isLoading.set(false);
      }
    });
  }

  // --- STATUT BÂTIMENT ---
  isBatimentActive(b: any): boolean {
    return b.actif !== false;
  }

  toggleBatimentStatus(b: any): void {
    const id = b.id_batiment || b.id || b.idBatiment;
    if (!id) return;

    const currentStatus = this.isBatimentActive(b);
    const targetStatus = !currentStatus;

    this.isActionLoading.set(id);

    this.adminService.toggleBatimentStatus(id, targetStatus).subscribe({
      next: () => {
        this.isActionLoading.set(null);
        const statusLabel = targetStatus ? 'Opérationnel / Actif' : 'En travaux / Inactif';
        this.showToast('success', `Le statut du bâtiment "${b.nom}" a été mis à jour : ${statusLabel}.`);
        this.loadData();
      },
      error: () => {
        this.isActionLoading.set(null);
        this.showToast('error', `Erreur lors de la mise à jour du statut du bâtiment "${b.nom}".`);
      }
    });
  }

  // --- MODAL BÂTIMENT ---
  openBatimentModal(): void {
    this.batimentForm = {
      nom: '',
      description: '',
      nombre_chambre: 10,
      actif: true
    };
    this.formError.set(null);
    this.showBatimentModal.set(true);
  }

  closeModals(): void {
    this.showBatimentModal.set(false);
    this.formError.set(null);
    this.isSubmitting.set(false);
  }

  submitBatiment(): void {
    if (!this.batimentForm.nom.trim()) {
      this.formError.set('Le nom du bâtiment est obligatoire.');
      return;
    }

    this.isSubmitting.set(true);
    this.formError.set(null);

    const payload = {
      nom: this.batimentForm.nom.trim(),
      description: this.batimentForm.description?.trim() || 'Pavillon hospitalier de soins',
      nombre_chambre: Number(this.batimentForm.nombre_chambre) || 0,
      actif: this.batimentForm.actif
    };

    this.adminService.createEntity('batiments', payload).subscribe({
      next: () => {
        this.isSubmitting.set(false);
        this.closeModals();
        this.showToast('success', `Bâtiment "${payload.nom}" créé avec succès.`);
        this.loadData();
      },
      error: (err) => {
        this.isSubmitting.set(false);
        const detail = err.error?.error || err.error?.message || 'Erreur lors de la création du bâtiment.';
        this.formError.set(detail);
      }
    });
  }

  showToast(type: 'success' | 'error', text: string): void {
    this.toastMessage.set({ type, text });
    setTimeout(() => {
      this.toastMessage.set(null);
    }, 4500);
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

  getBatimentName(item: any): string {
    return item?.chambre_detail?.batiment_detail?.nom ||
      item?.batiment_detail?.nom ||
      item?.batiment?.nom ||
      item?.batiment_nom ||
      'Bâtiment Principal A';
  }

  getBedBadgeClass(etat: string): string {
    switch ((etat || '').toUpperCase()) {
      case 'DISPONIBLE': return 'badge-disponible';
      case 'OCCUPE': return 'badge-occupe';
      case 'RESERVE': return 'badge-reserve';
      case 'EN_NETTOYAGE': return 'badge-maintenance';
      case 'HORS_SERVICE': return 'badge-hors-service';
      default: return 'badge-disponible';
    }
  }
}
