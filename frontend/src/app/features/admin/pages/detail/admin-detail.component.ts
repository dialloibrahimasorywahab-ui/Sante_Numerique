import { Component, OnInit, computed, inject, signal } from '@angular/core';
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

  isLit = computed(() => this.resource() === 'lits');
  isChambre = computed(() => this.resource() === 'chambres');
  isBatiment = computed(() => this.resource() === 'batiments');
  isFrais = computed(() => this.resource() === 'frais_consultations' || this.resource() === 'finances');

  // Helpers pour les lits
  chambreDuLit = computed(() => {
    const e = this.entity();
    if (!e) return null;
    return e.chambre_detail || e.chambreDetail || (typeof e.chambre === 'object' ? e.chambre : null);
  });

  chambreId = computed(() => {
    const ch = this.chambreDuLit();
    if (ch) return ch.id ?? ch.idChambre ?? ch.id_chambre ?? null;
    const e = this.entity();
    return e?.id_chambre ?? e?.chambre_id ?? (typeof e?.chambre === 'number' ? e.chambre : null);
  });

  batimentDuLit = computed(() => {
    const ch = this.chambreDuLit();
    if (ch) {
      return ch.batiment_detail || ch.batimentDetail || (typeof ch.batiment === 'object' ? ch.batiment : null);
    }
    const e = this.entity();
    return e?.batiment_detail || e?.batimentDetail || (typeof e?.batiment === 'object' ? e.batiment : null);
  });

  batimentId = computed(() => {
    const bat = this.batimentDuLit();
    if (bat) return bat.id ?? bat.idBatiment ?? bat.id_batiment ?? null;
    const ch = this.chambreDuLit();
    if (ch) return ch.id_batiment ?? ch.batiment_id ?? (typeof ch.batiment === 'number' ? ch.batiment : null);
    const e = this.entity();
    return e?.id_batiment ?? e?.batiment_id ?? (typeof e?.batiment === 'number' ? e.batiment : null);
  });

  // Helper pour les chambres
  batimentDeLaChambre = computed(() => {
    const e = this.entity();
    if (!e) return null;
    return e.batiment_detail || e.batimentDetail || (typeof e.batiment === 'object' ? e.batiment : null);
  });

  batimentDeLaChambreId = computed(() => {
    const bat = this.batimentDeLaChambre();
    if (bat) return bat.id ?? bat.idBatiment ?? bat.id_batiment ?? null;
    const e = this.entity();
    return e?.id_batiment ?? e?.batiment_id ?? (typeof e?.batiment === 'number' ? e.batiment : null);
  });

  getRoomStateBadge(room: any): { label: string; class: string } {
    if (!room) return { label: 'Opérationnelle', class: 'badge-disponible' };
    const dispo = room.litsDisponiblesCount ?? room.lits_disponibles_count;
    const occup = room.litsOccupesCount ?? room.lits_occupes_count;
    if (dispo !== undefined && dispo > 0) {
      return { label: `${dispo} lit(s) disponible(s)`, class: 'badge-disponible' };
    }
    if (occup !== undefined && occup > 0) {
      return { label: 'Chambre complète', class: 'badge-occupe' };
    }
    const stat = (room.statutDisplay || room.statut || '').toUpperCase();
    if (stat.includes('MAINTENANCE') || stat.includes('ENTRETIEN')) {
      return { label: 'En maintenance', class: 'badge-entretien' };
    }
    return { label: room.statutDisplay || room.statut || 'Opérationnelle', class: 'badge-disponible' };
  }

  ngOnInit(): void {
    this.route.paramMap.subscribe(params => {
      const resource = params.get('resource') || '';
      const id = params.get('id');
      this.resource.set(resource);

      if (!id) {
        this.errorMessage.set('Identifiant introuvable.');
        this.isLoading.set(false);
        return;
      }

      this.isLoading.set(true);
      this.errorMessage.set(null);
      this.entity.set(null);

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
    });
  }

  get title(): string {
    const labels: Record<string, string> = {
      patients: 'Dossier médical du patient',
      medecins: 'Dossier du médecin',
      personnel: 'Dossier du personnel',
      services: 'Détail du pôle / service',
      batiments: 'Fiche du pavillon / bâtiment',
      chambres: 'Fiche d’information de la chambre',
      lits: "Fiche d'information du lit",
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

  get eyebrow(): string {
    if (this.isFrais()) return 'Santé Numérique — Facturation & Règlements';
    if (this.isLit() || this.isChambre() || this.isBatiment()) return 'Santé Numérique — Infrastructure Hospitalière';
    return 'Santé Numérique — Dossier Médical';
  }

  get subtitle(): string {
    if (this.isFrais()) return 'Consultez le montant, l’acte médical couvert et le statut de la transaction.';
    if (this.isLit() || this.isChambre() || this.isBatiment()) return "Consultez l'état d'occupation, l'attribution et l'emplacement hospitalier.";
    return 'Consultez et vérifiez les informations détaillées de cet enregistrement.';
  }

  formatCurrency(val: any): string {
    if (val === null || val === undefined || val === '') return '0 GNF';
    const num = Number(val);
    if (isNaN(num)) return `${val} GNF`;
    return new Intl.NumberFormat('fr-FR', { maximumFractionDigits: 0 }).format(num) + ' GNF';
  }

  formatDateFrench(dateStr: any): string {
    if (!dateStr) return 'Non renseignée';
    try {
      const d = new Date(dateStr);
      if (isNaN(d.getTime())) return String(dateStr);
      return new Intl.DateTimeFormat('fr-FR', {
        day: 'numeric',
        month: 'long',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }).format(d);
    } catch {
      return String(dateStr);
    }
  }

  getFraisStatusClass(statut: string | undefined): string {
    const s = (statut || '').toUpperCase();
    if (s.includes('PAYE') || s.includes('VALIDE') || s.includes('REGL')) return 'badge-disponible';
    if (s.includes('ATTENTE') || s.includes('EN_COURS') || s.includes('IMPAYE')) return 'badge-reserve';
    if (s.includes('ANNULE') || s.includes('REJET')) return 'badge-entretien';
    return 'badge-neutral';
  }

  formatKeyLabel(key: string | number | symbol): string {
    const strKey = String(key);
    const k = strKey.toLowerCase();
    const labels: Record<string, string> = {
      id: 'Identifiant #',
      numero_lit: 'Numéro du lit',
      numerolit: 'Numéro du lit',
      etat: 'État d’occupation',
      etatdisplay: 'État d’occupation',
      etat_display: 'État d’occupation',
      numero_chambre: 'Numéro de chambre',
      numerochambre: 'Numéro de chambre',
      type_chambre: 'Catégorie de chambre',
      typechambredisplay: 'Catégorie de chambre',
      typechambre: 'Catégorie de chambre',
      capacite: 'Capacité d’accueil',
      statut: 'Statut du règlement',
      statutdisplay: 'Statut du règlement',
      statut_display: 'Statut du règlement',
      montant: 'Montant facturé',
      date_paiement: 'Date de règlement',
      datepaiement: 'Date de règlement',
      nom: 'Nom officiel',
      nom_service: 'Nom du service',
      nomservice: 'Nom du service',
      reference: 'Référence campus',
      description: 'Désignation de l’acte médical',
      nombre_chambre: 'Nombre de chambres prévues',
      nombrechambre: 'Nombre de chambres prévues',
      total_chambres_effectif: 'Total chambres effectif',
      totalchambreseffectif: 'Total chambres effectif',
      actif: 'Statut d’activité',
      etage: 'Étage',
      date_admission: 'Date d’admission',
      date_sortie: 'Date de sortie',
      motif_admission: 'Motif d’admission',
      created_at: 'Date d’enregistrement',
      updated_at: 'Dernière mise à jour'
    };
    if (labels[k]) return labels[k];
    const words = strKey.replace(/_/g, ' ').replace(/([A-Z])/g, ' $1').trim();
    return words.charAt(0).toUpperCase() + words.slice(1);
  }

  shouldShowField(key: string | number | symbol, value: unknown): boolean {
    const k = String(key).toLowerCase();
    const hiddenKeys = [
      'idlit', 'idchambre', 'idbatiment', 'id_batiment', 'id_lit', 'id_chambre',
      'chambre_detail', 'chambredetail', 'batiment_detail', 'batimentdetail',
      'patient_details', 'patientdetails', 'service_details', 'servicedetails',
      'medecin_details', 'medecindetails', 'litsoccupescount', 'litsdisponiblescount',
      'lits_occupes_count', 'lits_disponibles_count',
      'idfrais', 'id_frais', 'statut_display', 'statutdisplay'
    ];
    if (this.isFrais() && (k === 'actif' || k === 'id')) return false;
    if (hiddenKeys.includes(k)) return false;
    return value !== null && value !== undefined && value !== '';
  }

  formatValue(value: unknown): string {
    if (value === null || value === undefined || value === '') return 'Non renseigné';
    if (typeof value === 'boolean') return value ? 'Oui / Opérationnel' : 'Non / Inactif';
    if (typeof value === 'string' && /^\d{4}-\d{2}-\d{2}T/.test(value)) {
      return this.formatDateFrench(value);
    }
    if (typeof value === 'object') {
      if (Array.isArray(value)) {
        return value.length > 0
          ? value.map(v => typeof v === 'object' ? (v?.nom || v?.libelle || v?.id || JSON.stringify(v)) : String(v)).join(', ')
          : 'Aucun';
      }
      const obj: any = value;
      if (obj.nom || obj.reference) {
        return `${obj.nom || ''} (${obj.reference || ''})`.trim() + (obj.description ? ` — ${obj.description}` : '');
      }
      if (obj.numero_chambre || obj.numeroChambre) {
        return `Chambre ${obj.numero_chambre || obj.numeroChambre} (${obj.typeChambreDisplay || obj.type_chambre || 'Standard'})`;
      }
      return obj.nom || obj.nom_service_display || obj.nom_service || JSON.stringify(value);
    }
    return String(value);
  }

  getBedStateClass(etat: string | undefined): string {
    const s = (etat || '').toUpperCase();
    if (s.includes('DISPONIBLE') || s.includes('LIBRE')) return 'badge-disponible';
    if (s.includes('OCCUPE')) return 'badge-occupe';
    if (s.includes('RESERVE')) return 'badge-reserve';
    if (s.includes('ENTRETIEN') || s.includes('NETTOYAGE')) return 'badge-entretien';
    return 'badge-neutral';
  }
}