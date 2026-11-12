export type CategorieDocument =
  | 'RADIO'
  | 'SCANNER'
  | 'IRM'
  | 'ECHOGRAPHIE'
  | 'ANALYSE_SANG'
  | 'ANALYSE_URINE'
  | 'ANAPATH'
  | 'COMPTE_RENDU'
  | 'CERTIFICAT'
  | 'ORDONNANCE'
  | 'AUTRE';

export interface DocumentMedicalDto {
  // Identifiant (support camelCase & snake_case)
  idDocument?: number;
  id_document?: number;
  id?: number;

  patient: number;
  patientNom?: string;
  patient_nom?: string;
  patientPrenom?: string;
  patient_prenom?: string;

  medecin?: number | null;
  medecinNom?: string;
  medecin_nom?: string;

  consultation?: number | null;
  titre: string;
  categorie: CategorieDocument;
  categorieDisplay?: string;
  categorie_display?: string;

  nomOriginal?: string;
  nom_original?: string;

  tailleOctets?: number;
  taille_octets?: number;

  typeMime?: string;
  type_mime?: string;

  checksumSha256?: string;
  checksum_sha256?: string;

  chiffre?: boolean;

  dateDocument?: string;
  date_document?: string;

  dateUpload?: string;
  date_upload?: string;

  observation?: string;

  downloadUrl?: string;
  download_url?: string;

  actif?: boolean;
}

export interface DocumentFilterParams {
  patient_id?: number;
  categorie?: string;
  search?: string;
  page?: number;
  page_size?: number;
}
