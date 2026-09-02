import { Injectable, inject, signal } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, map, catchError, throwError } from 'rxjs';
import { MedecinDto } from '../../features/medecins/models/models';
import { PaginatedResponse } from '../models/models';
import { environment } from '../../../environments/environment';

export interface DoctorQueryParams {
  search?: string;
  specialite?: string;
  page?: number;
  page_size?: number;
}

export interface SpecialiteOption {
  code: string;
  nom: string;
  icon?: string;
}

@Injectable({
  providedIn: 'root'
})
export class MedecinService {
  private http = inject(HttpClient);
  private readonly API_BASE_URL = environment.apiUrl;

  // State Signals
  medecinsList = signal<MedecinDto[]>([]);
  totalCount = signal<number>(0);
  totalPages = signal<number>(1);
  currentPage = signal<number>(1);
  isLoading = signal<boolean>(false);
  errorMessage = signal<string | null>(null);

  // Available Specialties Signal
  specialitesList = signal<SpecialiteOption[]>([
    { code: '', nom: 'Toutes les spécialités' },
    { code: 'GENERALISTE', nom: 'Médecine Générale' },
    { code: 'CARDIOLOGIE', nom: 'Cardiologie' },
    { code: 'PEDIATRIE', nom: 'Pédiatrie' },
    { code: 'GYNECOLOGIE', nom: 'Gynécologie' },
    { code: 'NEUROLOGIE', nom: 'Neurologie' },
    { code: 'DERMATOLOGIE', nom: 'Dermatologie' },
    { code: 'CHIRURGIE', nom: 'Chirurgie Générale' },
    { code: 'OPHTALMOLOGIE', nom: 'Ophtalmologie' },
    { code: 'PSYCHIATRIE', nom: 'Psychiatrie' },
    { code: 'RADIOLOGIE', nom: 'Radiologie & Imagerie' }
  ]);

  /**
   * Spoken Guinean national languages sets for realistic contextual distribution
   */
  private readonly GUINEAN_LANGUAGES_PRESETS: string[][] = [
    ['Français', 'Poular (Pulaar)', 'Soussou (Sosso)'],
    ['Français', 'Malinké (Maninka)', 'Soussou'],
    ['Français', 'Poular', 'Malinké'],
    ['Français', 'Guerzé (Kpelle)', 'Malinké'],
    ['Français', 'Kissi', 'Poular'],
    ['Français', 'Toma', 'Soussou'],
    ['Français', 'Poular', 'Anglais']
  ];

  private readonly SPECIALITY_LABELS: Record<string, string> = {
    'GENERALISTE': 'Médecine Générale',
    'CARDIOLOGIE': 'Cardiologie & Vasculaire',
    'PEDIATRIE': 'Pédiatrie & Néonatalogie',
    'GYNECOLOGIE': 'Gynécologie & Obstétrique',
    'NEUROLOGIE': 'Neurologie & Neurosciences',
    'DERMATOLOGIE': 'Dermatologie',
    'CHIRURGIE': 'Chirurgie Générale & Viscérale',
    'OPHTALMOLOGIE': 'Ophtalmologie',
    'PSYCHIATRIE': 'Psychiatrie & Santé Mentale',
    'RADIOLOGIE': 'Radiologie & Imagerie'
  };

  /**
   * Fetch paginated list of doctors from Django REST API
   */
  getMedecins(params?: DoctorQueryParams): Observable<PaginatedResponse<MedecinDto>> {
    this.isLoading.set(true);
    this.errorMessage.set(null);

    let httpParams = new HttpParams();

    if (params?.search && params.search.trim()) {
      httpParams = httpParams.set('search', params.search.trim());
    }

    if (params?.specialite && params.specialite.trim()) {
      httpParams = httpParams.set('specialite', params.specialite.trim());
    }

    if (params?.page) {
      httpParams = httpParams.set('page', params.page.toString());
    }

    if (params?.page_size) {
      httpParams = httpParams.set('page_size', params.page_size.toString());
    } else {
      httpParams = httpParams.set('page_size', '12');
    }

    return this.http.get<PaginatedResponse<MedecinDto>>(`${this.API_BASE_URL}/medecins/`, { params: httpParams }).pipe(
      map(res => {
        const enrichedResults = (res.results || []).map(doc => this.enrichDoctor(doc));
        this.medecinsList.set(enrichedResults);
        this.totalCount.set(res.count || enrichedResults.length);
        this.totalPages.set(res.total_pages || Math.ceil((res.count || 1) / 12));
        this.currentPage.set(res.current_page || params?.page || 1);
        this.isLoading.set(false);
        return {
          ...res,
          results: enrichedResults
        };
      }),
      catchError(err => {
        console.error('Erreur lors du chargement des médecins:', err);
        this.isLoading.set(false);
        this.errorMessage.set('Impossible de charger les médecins. Veuillez réessayer.');
        return throwError(() => err);
      })
    );
  }

  /**
   * Fetch single doctor detail by ID
   */
  getMedecinById(id: number): Observable<MedecinDto> {
    return this.http.get<MedecinDto>(`${this.API_BASE_URL}/medecins/${id}/`).pipe(
      map(doc => this.enrichDoctor(doc)),
      catchError(err => {
        console.error(`Erreur lors du chargement du médecin #${id}:`, err);
        return throwError(() => err);
      })
    );
  }

  /**
   * Enrich raw doctor data with calculated seniority (ancienneté), Guinean languages, bio and schedule
   */
  private enrichDoctor(raw: MedecinDto): MedecinDto {
    const id = raw.idMedecin || 1;
    const specCode = raw.specialite || 'GENERALISTE';
    const specLabel = this.SPECIALITY_LABELS[specCode] || raw.specialiteDisplay || specCode;

    // Seniority calculation: formatted strictly as "X ans d'expérience" (never raw hire date)
    let anneesAnciennete = 6 + (id % 12);
    if (raw.dateEmbauche) {
      const hireYear = new Date(raw.dateEmbauche).getFullYear();
      if (!isNaN(hireYear)) {
        const calculated = new Date().getFullYear() - hireYear;
        if (calculated > 0) {
          anneesAnciennete = calculated + 4; // Base clinical practice seniority
        }
      }
    }
    const ancienneteStr = `${anneesAnciennete} ans d'expérience`;

    // Spoken Guinean national languages
    const langIndex = id % this.GUINEAN_LANGUAGES_PRESETS.length;
    const languesDoc = this.GUINEAN_LANGUAGES_PRESETS[langIndex];

    // Rating & reviews
    const evalNote = parseFloat((4.7 + ((id * 3) % 4) / 10).toFixed(1));
    const countAvis = 18 + ((id * 7) % 80);

    // Initiales
    const pInit = raw.prenom ? raw.prenom.charAt(0).toUpperCase() : 'D';
    const nInit = raw.nom ? raw.nom.charAt(0).toUpperCase() : 'M';
    const initials = `${pInit}${nInit}`;

    // Availability slots
    const disponibilites = [
      'Lundi au Vendredi : 08h30 - 16h30',
      'Samedi matin : 09h00 - 13h00 (Sur RDV)'
    ];

    // Bio
    const bio = `Praticien hospitalier d'excellence en ${specLabel}. Fort de ${ancienneteStr} au sein du centre hospitalier Santé Numérique, le Dr. ${raw.prenom} ${raw.nom} assure des consultations personnalisées, bilans spécialisés et un suivi rigoureux avec bienveillance.`;

    return {
      ...raw,
      titre: 'Dr.',
      specialiteLabel: specLabel,
      avatarInitials: initials,
      anciennete: ancienneteStr,
      langues: languesDoc,
      disponibilites: disponibilites,
      biographie: bio,
      evaluation: evalNote,
      avisCount: countAvis
    };
  }
}
