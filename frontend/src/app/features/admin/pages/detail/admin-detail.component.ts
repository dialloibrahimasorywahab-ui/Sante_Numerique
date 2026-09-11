import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { AdminService } from '../../services/admin.service';

@Component({
  selector: 'app-admin-detail',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './admin-detail.component.html',
  styleUrls: ['./admin-detail.component.scss']
})
export class AdminDetailComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly adminService = inject(AdminService);

  resource = signal('');
  entity = signal<any | null>(null);
  isLoading = signal(true);
  errorMessage = signal<string | null>(null);

  ngOnInit(): void {
    const resource = this.route.snapshot.paramMap.get('resource') || '';
    const id = this.route.snapshot.paramMap.get('id');
    this.resource.set(resource);

    if (!id) {
      this.errorMessage.set('Identifiant introuvable.');
      this.isLoading.set(false);
      return;
    }

    this.adminService.getEntityDetail(resource, id).subscribe({
      next: entity => {
        this.entity.set(entity);
        this.isLoading.set(false);
      },
      error: () => {
        this.errorMessage.set('Impossible de charger toutes les informations de cet élément.');
        this.isLoading.set(false);
      }
    });
  }

  get title(): string {
    const labels: Record<string, string> = {
      patients: 'Dossier médical du patient',
      medecins: 'Dossier du médecin',
      personnel: 'Dossier du personnel',
      services: 'Détail du pôle / service',
      batiments: 'Détail du bâtiment',
      chambres: 'Détail de la chambre',
      lits: "Détail du lit d'hospitalisation",
      rendezvous: 'Détail du rendez-vous',
      consultations: 'Détail de la consultation',
      hospitalisations: "Détail de l'hospitalisation",
      ordonnances: "Détail de l'ordonnance",
      frais_consultations: 'Détail des frais de consultation'
    };
    return labels[this.resource()] || 'Détail de l’élément';
  }

  get listRoute(): string {
    return this.resource() === 'frais_consultations' ? 'finances' : this.resource();
  }

  formatValue(value: unknown): string {
    if (value === null || value === undefined || value === '') return 'Non renseigné';
    if (typeof value === 'object') return JSON.stringify(value, null, 2);
    return String(value);
  }
}