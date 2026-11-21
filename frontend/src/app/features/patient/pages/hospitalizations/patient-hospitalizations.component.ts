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
   * Formate la date de sortie : si en cours ou non définie, affiche "En cours d'hospitalisation"
   */
  formatExitDate(dateStr?: string | null, statut?: string): string {
    if (statut === 'EN_COURS' || !dateStr) {
      return 'En cours d’hospitalisation';
    }
    return this.formatShortDate(dateStr);
  }

  /**
   * Durée du séjour en cours (en jours)
   */
  getStayDurationDays(dateEntree?: string | null): number {
    if (!dateEntree) return 1;
    try {
      const d = new Date(dateEntree);
      if (isNaN(d.getTime())) return 1;
      const now = new Date();
      const diffMs = Math.max(0, now.getTime() - d.getTime());
      return Math.max(1, Math.ceil(diffMs / (1000 * 60 * 60 * 24)));
    } catch {
      return 1;
    }
  }

  /**
   * Résout le nom du praticien de manière professionnelle et lisible.
   * Ne JAMAIS afficher un identifiant brut type "Dr. Médecin #12".
   */
  getDoctorName(h: HospitalisationDto | any): string {
    if (!h) return 'Praticien hospitalier référent';

    // 1. Nom direct (camelCase ou snake_case)
    const directNom = h.medecinNom || h.medecin_nom;
    if (directNom && directNom !== 'Non assigné' && !directNom.includes('#')) {
      return directNom.startsWith('Dr.') ? directNom : `Dr. ${directNom}`;
    }

    // 2. Détails du médecin (supporte camelCase medecinDetails et snake_case medecin_details)
    const m = h.medecinDetails || h.medecin_details || h.medecinDetail || h.medecin_detail || (typeof h.medecin === 'object' ? h.medecin : null);
    if (m) {
      const u = m.idUtilisateur || m.id_utilisateur || m.user;
      const prenom = m.prenom || u?.prenom || '';
      const nom = m.nom || u?.nom || '';
      if (prenom || nom) {
        return `Dr. ${prenom} ${nom}`.trim();
      }
    }

    // 3. Fallback élégant et professionnel
    return 'Dr. Praticien hospitalier';
  }

  /**
   * Spécialité médicale du praticien
   */
  getDoctorSpecialty(h: HospitalisationDto | any): string {
    if (!h) return 'Médecine hospitalière';
    const m = h.medecinDetails || h.medecin_details || h.medecinDetail || h.medecin_detail || (typeof h.medecin === 'object' ? h.medecin : null);
    return m?.specialiteDisplay || m?.specialite_display || m?.specialiteLabel || m?.specialite || 'Médecine hospitalière';
  }

  /**
   * Service hospitalier rattaché au séjour
   */
  getServiceName(h: HospitalisationDto | any): string {
    if (!h) return 'Service de Médecine';
    const sNom = h.serviceNom || h.service_nom;
    if (sNom && sNom.trim()) return sNom.trim();

    const litDetails = h.litDetails || h.lit_details;
    const chambre = litDetails?.chambreDetail || litDetails?.chambre_detail || h.chambreDetails || h.chambre_details;
    if (chambre?.service?.nom) return chambre.service.nom;
    if (chambre?.service?.nom_service) return chambre.service.nom_service;
    if (chambre?.bureau_localisation) return chambre.bureau_localisation;

    return 'Médecine Hospitalière';
  }

  /**
   * Établissement ou Pôle de localisation
   */
  getHospitalFacility(h: HospitalisationDto | any): string {
    const bat = h?.batimentNom || h?.batiment_nom;
    if (bat) return bat;
    return 'Centre Hospitalier';
  }

  /**
   * Vérifie si des informations de chambre ou de lit sont disponibles
   */
  hasRoomOrBed(h: HospitalisationDto | any): boolean {
    if (!h) return false;
    const litDetails = h.litDetails || h.lit_details;
    const chambre = litDetails?.chambreDetail || litDetails?.chambre_detail;
    const ch = h.chambreNumero || h.chambre_numero || chambre?.numeroChambre || chambre?.numero_chambre;
    const lit = h.litNumero || h.lit_numero || litDetails?.numeroLit || litDetails?.numero_lit;
    return !!((ch && ch !== 'N/D') || (lit && lit !== 'Non assigné'));
  }

  /**
   * Libellé complet et non tronqué Chambre & Lit & Bâtiment
   */
  getRoomBedLabel(h: HospitalisationDto | any): string {
    if (!h) return 'Affectation en cours';
    const parts: string[] = [];
    const litDetails = h.litDetails || h.lit_details;
    const chambre = litDetails?.chambreDetail || litDetails?.chambre_detail;

    const ch = h.chambreNumero || h.chambre_numero || chambre?.numeroChambre || chambre?.numero_chambre;
    const lit = h.litNumero || h.lit_numero || litDetails?.numeroLit || litDetails?.numero_lit;
    const bat = h.batimentNom || h.batiment_nom || chambre?.batiment?.nom || chambre?.batimentNom;

    if (ch && ch !== 'N/D') {
      const chStr = String(ch);
      parts.push(chStr.toLowerCase().startsWith('chambre') ? chStr : `Chambre ${chStr}`);
    }
    if (lit && lit !== 'Non assigné') {
      const litStr = String(lit);
      parts.push(litStr.toLowerCase().startsWith('lit') ? litStr : `Lit ${litStr}`);
    }
    if (bat) {
      parts.push(String(bat));
    }
    return parts.length > 0 ? parts.join(' • ') : 'Affectation en cours';
  }

  /**
   * Niveau de priorité clinique
   */
  getPriority(h: HospitalisationDto | any): string {
    if (!h) return 'NORMAL';
    if (h.priorite) return h.priorite;
    const obs = h.observation || '';
    const m = obs.match(/\[Priorité\]:\s*([^\n]+)/i);
    return m ? m[1].trim() : 'NORMAL';
  }

  getPriorityLabel(priorite: string): string {
    switch (priorite?.toUpperCase()) {
      case 'TRES_URGENT': return 'Urgence Vitale / Prioritaire';
      case 'URGENT': return 'Prise en charge Urgente';
      case 'NORMAL': return 'Prise en charge Standard';
      default: return priorite || 'Standard';
    }
  }

  getPriorityBadgeClass(priorite: string): string {
    switch (priorite?.toUpperCase()) {
      case 'TRES_URGENT': return 'badge-priority-critical';
      case 'URGENT': return 'badge-priority-urgent';
      default: return 'badge-priority-normal';
    }
  }

  /**
   * Données médicales complémentaires exploitables
   */
  getSymptoms(h: HospitalisationDto | any): string | null {
    if (!h) return null;
    if (h.symptomes && h.symptomes.trim()) return h.symptomes.trim();
    const obs = h.observation || '';
    const m = obs.match(/\[Symptômes\]:\s*([^\n]+)/i);
    return m ? m[1].trim() : null;
  }

  getDiagnostic(h: HospitalisationDto | any): string | null {
    if (!h) return null;
    if (h.diagnosticProvisoire && h.diagnosticProvisoire.trim()) return h.diagnosticProvisoire.trim();
    if (h.diagnostic_provisoire && h.diagnostic_provisoire.trim()) return h.diagnostic_provisoire.trim();
    const obs = h.observation || '';
    const m = obs.match(/\[Diagnostic provisoire\]:\s*([^\n]+)/i);
    return m ? m[1].trim() : null;
  }

  getAllergies(h: HospitalisationDto | any): string | null {
    if (!h) return null;
    if (h.allergies && h.allergies.trim()) return h.allergies.trim();
    const obs = h.observation || '';
    const m = obs.match(/\[Allergies\]:\s*([^\n]+)/i);
    return m ? m[1].trim() : null;
  }

  getAntecedents(h: HospitalisationDto | any): string | null {
    if (!h) return null;
    if (h.antecedents && h.antecedents.trim()) return h.antecedents.trim();
    const obs = h.observation || '';
    const m = obs.match(/\[Antécédents\]:\s*([^\n]+)/i);
    return m ? m[1].trim() : null;
  }

  getTreatments(h: HospitalisationDto | any): string | null {
    if (!h) return null;
    if (h.traitementsEnCours && h.traitementsEnCours.trim()) return h.traitementsEnCours.trim();
    if (h.traitements_en_cours && h.traitements_en_cours.trim()) return h.traitements_en_cours.trim();
    const obs = h.observation || '';
    const m = obs.match(/\[Traitements en cours\]:\s*([^\n]+)/i);
    return m ? m[1].trim() : null;
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
      case 'TERMINEE': return 'Séjour terminé';
      case 'ANNULEE': return 'Annulé';
      case 'PROGRAMMEE': return 'Programmé';
      default: return statut || 'Hospitalisation';
    }
  }
}
