export type StatutActualite = 'BROUILLON' | 'PUBLIE';

export interface CategorieActualite {
  id: number;
  nom: string;
  slug: string;
  description: string;
  couleur: string;
  icone: string;
  actif: boolean;
  dateCreation?: string;
  totalArticles?: number;
}

export interface Actualite {
  id: number;
  titre: string;
  slug: string;
  resume: string;
  contenu?: string;
  image: string;
  imageCouverture?: string | null;
  imageUrl?: string;
  categorie: number;
  categorieNom: string;
  categorieSlug: string;
  categorieCouleur: string;
  auteur?: number | null;
  auteurNom: string;
  statut: StatutActualite;
  estALaUne: boolean;
  tempsLecture: number;
  vues: number;
  datePublication?: string | null;
  dateCreation: string;
  dateModification?: string;
}

export interface ActualitePayload {
  titre: string;
  resume: string;
  contenu: string;
  categorie: number;
  imageCouverture?: File | null;
  imageUrl?: string;
  statut: StatutActualite;
  estALaUne?: boolean;
  datePublication?: string | null;
}

export interface ActualiteFilterParams {
  search?: string;
  categorie?: string | number;
  statut?: string;
  estALaUne?: boolean;
  ordering?: string;
  page?: number;
  pageSize?: number;
}

