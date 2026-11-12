import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { PatientHospitalizationService } from '../../services/patient-hospitalization.service';
import { HospitalisationDto } from '../../models/patient.models';

@Component({
  selector: 'app-patient-hospitalizations',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './patient-hospitalizations.component.html',
  styleUrl: './patient-hospitalizations.component.scss'
})
export class PatientHospitalizationsComponent implements OnInit {
  private hospitalizationService = inject(PatientHospitalizationService);

  isLoading = signal<boolean>(true);
  errorMessage = signal<string | null>(null);

  hospitalizations = signal<HospitalisationDto[]>([]);
  totalCount = signal<number>(0);
  totalPages = signal<number>(1);

  // Pagination à 5 par page pour un meilleur confort de lecture
  readonly pageSize = 5;
  currentPage = signal<number>(1);

  // Séjour actif en cours s'il y en a un
  activeHospitalization = computed(() => {
    return this.hospitalizations().find(h => h.statut === 'EN_COURS') || null;
  });

  ngOnInit(): void {
    this.loadHospitalizations(1);
  }

  loadHospitalizations(page: number): void {
    this.isLoading.set(true);
    this.errorMessage.set(null);

    this.hospitalizationService.getMyHospitalizations(page, this.pageSize).subscribe({
      next: (resp) => {
        this.hospitalizations.set(resp.results || []);
        this.totalCount.set(resp.count);
        this.totalPages.set(resp.total_pages || Math.max(1, Math.ceil(resp.count / this.pageSize)));
        this.currentPage.set(page);
        this.isLoading.set(false);
      },
      error: () => {
        this.errorMessage.set('Impossible de charger votre historique d’hospitalisations. Veuillez réessayer.');
        this.isLoading.set(false);
      }
    });
  }

  changePage(page: number): void {
    if (page >= 1 && page <= this.totalPages() && page !== this.currentPage()) {
      this.loadHospitalizations(page);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }

  /**
   * Formate la date d'admission détaillée avec heure
   */
  formatAdmissionDate(dateStr?: string | null): string {
    if (!dateStr) return 'Date non renseignée';
    try {
      const d = new Date(dateStr);
      if (isNaN(d.getTime())) return dateStr;
      return d.toLocaleDateString('fr-FR', {
        day: 'numeric',
        month: 'long',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return dateStr;
    }
  }

  /**
   * Formate une date courte (JJ/MM/AAAA)
   */
  formatShortDate(dateStr?: string | null): string {
    if (!dateStr) return 'Non renseignée';
    try {
      const d = new Date(dateStr);
      if (isNaN(d.getTime())) return dateStr;
      return d.toLocaleDateString('fr-FR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      });
    } catch {
      return dateStr;
    }
  }

  /**
   * Formate la date de sortie : si en cours ou non définie, affiche "Non encore terminée"
   * Règle absolue : ne JAMAIS afficher "En cours" comme une date !
   */
  formatExitDate(dateStr?: string | null, statut?: string): string {
    if (statut === 'EN_COURS' || !dateStr) {
      return 'Non encore terminée';
    }
    return this.formatShortDate(dateStr);
  }

  /**
   * Résout le nom du praticien de manière professionnelle avec civilité "Dr."
   */
  getDoctorName(h: HospitalisationDto): string {
    if (h.medecin_nom && h.medecin_nom !== 'Non assigné') {
      return h.medecin_nom.startsWith('Dr.') ? h.medecin_nom : `Dr. ${h.medecin_nom}`;
    }
    if (h.medecin_details) {
      const prenom = h.medecin_details.prenom || '';
      const nom = h.medecin_details.nom || '';
      if (prenom || nom) {
        return `Dr. ${prenom} ${nom}`.trim();
      }
      if (h.medecin_details.idMedecin) {
        return `Dr. Médecin #${h.medecin_details.idMedecin}`;
      }
    }
    if (h.medecin) {
      return `Dr. Médecin #${h.medecin}`;
    }
    return 'Praticien hospitalier référent';
  }

  /**
   * Service hospitalier rattaché au séjour
   */
  getServiceName(h: HospitalisationDto): string {
    if (h.service_nom) return h.service_nom;
    if (h.serviceNom) return h.serviceNom;
    if (h.lit_details?.chambre_detail?.service?.nom) return h.lit_details.chambre_detail.service.nom;
    if (h.lit_details?.chambre_detail?.bureau_localisation) return h.lit_details.chambre_detail.bureau_localisation;
    return 'Médecine hospitalière';
  }

  /**
   * Vérifie si des informations de chambre ou de lit sont disponibles
   */
  hasRoomOrBed(h: HospitalisationDto): boolean {
    const ch = h.chambre_numero || h.chambreNumero || h.lit_details?.chambre_detail?.numero_chambre;
    const lit = h.lit_numero || h.litNumero || h.lit_details?.numero_lit;
    return !!((ch && ch !== 'N/D') || (lit && lit !== 'Non assigné'));
  }

  /**
   * Libellé formaté Chambre & Lit
   */
  getRoomBedLabel(h: HospitalisationDto): string {
    const parts: string[] = [];
    const ch = h.chambre_numero || h.chambreNumero || h.lit_details?.chambre_detail?.numero_chambre;
    const lit = h.lit_numero || h.litNumero || h.lit_details?.numero_lit;
    const bat = h.batiment_nom || h.batimentNom;

    if (ch && ch !== 'N/D') {
      parts.push(ch.startsWith('Chambre') ? ch : `Chambre ${ch}`);
    }
    if (lit && lit !== 'Non assigné') {
      parts.push(lit.startsWith('Lit') ? lit : `Lit ${lit}`);
    }
    if (bat) {
      parts.push(bat);
    }
    return parts.length > 0 ? parts.join(' • ') : 'Affectation en cours';
  }

  /**
   * Extrait les instructions de service sans tags techniques bruts
   */
  getCleanInstructions(obs?: string | null): string | null {
    if (!obs) return null;
    const cleaned = obs
      .replace(/\[(Priorité|Service|Diagnostic provisoire|Symptômes|Antécédents|Allergies|Traitements en cours)\]:[^\n]*/gi, '')
      .trim();
    return cleaned || null;
  }

  /**
   * Classe CSS pour le badge de statut
   */
  getStatusBadgeClass(statut?: string): string {
    switch (statut) {
      case 'EN_COURS': return 'badge-status-encours';
      case 'TERMINEE': return 'badge-status-terminee';
      case 'ANNULEE': return 'badge-status-annulee';
      case 'PROGRAMMEE': return 'badge-status-programmee';
      default: return 'badge-status-default';
    }
  }

  /**
   * Libellé lisible du statut
   */
  getStatusLabel(statut?: string): string {
    switch (statut) {
      case 'EN_COURS': return 'En cours';
      case 'TERMINEE': return 'Terminé';
      case 'ANNULEE': return 'Annulé';
      case 'PROGRAMMEE': return 'Programmé';
      default: return statut || 'Hospitalisation';
    }
  }
}
